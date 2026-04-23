# Handoff: Apply segmenter determinism fix + rerun dev benchmarks

You're taking over a ReDream AI thesis project mid-stream. The previous session identified the root cause of run-to-run variance in the safety pipeline and wrote it up. Your job is to apply a one-line fix and rerun the dev benchmarks on the deterministic pipeline.

## Context (read once, then act)

ReDream AI is a Master's thesis (Ramon Zacharias) — neuro-symbolic safety layer for an IRT nightmare-rescripting chatbot. Project root: `/Users/sunray/projects/thesis/claude`. Repo conventions in `CLAUDE.md`. All commands use `uv`.

The safety pipeline in `safety/critic.py`:

1. **Segment** user input (currently Mistral Nemo via OpenRouter, temp=0.1)
2. **Classify** each segment to a graph node
3. **Triage** + constraint synthesis

**Architectural note:** the segmenter runs **once per case** in both baseline and consistency modes — N=5 stochastic samples in consistency mode are classifier-level only, sharing a single segment set. Pre-fix, this made consistency UQ blind to segmenter drift (see §10.3). Post-fix, the segmenter is deterministic, so "once per case" and "N times per case" are equivalent in output and the architecture is correct as-is.

Full-set semantic-consistency benchmarks (2026-04-20 → 04-22) showed 6 S1 regressions vs baseline, including one clinically-critical unsafe→safe miss. Per-case investigation traced all 6 to the **segmenter producing different outputs between runs on identical input** — not to vote aggregation.

## What the determinism probe found (2026-04-22)

Script: `experiments/determinism_probe/probe_segmenter.py`. Raw data: `data/benchmarks/segmenter_determinism_probe.md`. 2×2 factorial on 6 regression cases, N=5 repeats per cell:

| Condition | Mean unique sigs / 5 | Cases with drift |
|---|---|---|
| OR + temp=0.1 (current) | 2.33 | 5/6 |
| OR + temp=0 | 2.33 | 6/6 |
| SW + temp=0.1 | 1.17 | 1/6 |
| **SW + temp=0** | **1.00** | **0/6** |

**Conclusion.** OpenRouter's aggregator routing across heterogeneous upstream backends is the dominant driver of segmenter non-determinism. Temperature is secondary. Scaleway-direct at temp=0 is fully deterministic (0 drift over 30 calls). The `[META]` misclassification that caused the unsafe-miss on "Same locked room" reproduces only on OR.

Full write-up: `docs/planning/System2_CoT_Findings.md` §10.3.1.

## Your task

### Step 1 — Apply the fix

Edit `safety/critic.py`, around line 197–202:

```python
# Initialize segmenter agent (Mistral Nemo via OpenRouter for speed)
self.segmenter = Agent(
    model_config=MODELS["OR_MISTRAL_NEMO"],
    system_prompt=SEGMENTER_PROMPT,
    temperature=0.1
)
```

Change to:

```python
# Mistral Nemo via Scaleway-direct + greedy decoding for deterministic
# segmentation. OR aggregator causes non-deterministic routing across
# backends (see System2_CoT_Findings.md §10.3.1).
self.segmenter = Agent(
    model_config=MODELS["MISTRAL_NEMO"],
    system_prompt=SEGMENTER_PROMPT,
    temperature=0
)
```

`MISTRAL_NEMO` is the Scaleway-direct key (see `AI/agent.py` MODELS dict, line 240). Do not change anything else in `safety/`. In particular, do NOT change `safety/classifier.py` or `safety/classifier_cot.py` temperatures — those are intentionally 0.1 and classifier-level determinism is not the bottleneck.

### Step 2 — Archive pre-fix benchmark CSVs

Create `data/benchmarks/archive/pre_fix/` and move these into it so they can't be mistakenly read as current:

- `benchmark_results.csv` (today's S1 baseline rerun, OR + temp=0.1)
- `benchmark_results_s1_consistency.csv`
- `benchmark_results_s2.csv` (stale Mar 25 run on pre-affect-fix dataset)
- `benchmark_results_s2_consistency.csv`
- `_test_noconsistency.csv`

Write `data/benchmarks/archive/pre_fix/README.md` noting these are pre-fix runs on the non-deterministic OR config, retained for provenance only.

### Step 3 — Smoke-test the fix

Before kicking off ~21h of benchmarks, rerun the determinism probe to confirm the SW+temp=0 cell is still 0/6 drift on the current code:

```bash
uv run python experiments/determinism_probe/probe_segmenter.py
```

If the SW+temp=0 condition shows any drift, stop and investigate. The expected output is `Mean unique sigs / 5 = 1.00, Cases with drift = 0/6` for that condition.

### Step 4 — Run the four dev benchmarks

In sequence (total ~21h — can run overnight):

```bash
# S1 baseline (~1.5h) → benchmark_results.csv
uv run python experiments/run_benchmark.py --classifier s1

# S1 consistency (~1.5h) → benchmark_results_s1_consistency.csv
uv run python experiments/run_benchmark.py --classifier s1 --consistency 5

# S2 baseline (~5h) → benchmark_results_s2.csv (overwrites the stale file)
uv run python experiments/run_benchmark.py --classifier s2

# S2 consistency (~13h) → benchmark_results_s2_consistency.csv
uv run python experiments/run_benchmark.py --classifier s2 --consistency 5
```

Each run writes to the default output path; no `--output` override needed.

### Step 5 — Update docs & commit

After all four runs finish:

1. **Append a §11 to `docs/planning/System2_CoT_Findings.md`** titled "Post-fix deterministic benchmarks (2026-04-23 or whatever date)", with:
   - Headline table: 4 rows (S1 baseline, S1 consistency, S2 baseline, S2 consistency) × columns (safety accuracy, unsafe recall, node accuracy, notable changes vs archive).
   - One-paragraph note that these supersede §10's numbers as the thesis-anchoring results, and that §10 remains as the diagnosis / motivation for the fix.
2. **Update `CLAUDE.md` "Completed" section** — replace the Mar 23–25 / Apr 20–22 headline lines with the new post-fix numbers. Keep the determinism-probe and segmenter-drift bullets.
3. **Commit** (conventional commits): `fix(safety): switch segmenter to Scaleway-direct + temp=0 for deterministic segmentation`. Include the benchmark CSVs and doc updates in the same commit. Reference §10.3.1.

### Step 6 — Verification & report back

- Row-count sanity: each of the four new CSVs should have 480 test rows and 420 safety-evaluable rows.
- Diff the new S1 baseline against `archive/pre_fix/benchmark_results.csv`. Report:
  - Safety accuracy Δ
  - Unsafe recall Δ
  - Whether "Same locked room" is now correctly classified unsafe (it was the unsafe-miss on the pre-fix run)
  - Count of cases that flipped (both directions)
- Spot-check 2 of the 6 known regression cases ("Realize I am safe", "Lift above the city") — confirm the `segments` column now matches across S1 baseline and S1 consistency rows.

## Report template (paste into final message)

```
Segmenter fix applied and benchmarks rerun.

| Metric | S1 baseline | S1 consistency | S2 baseline | S2 consistency |
|---|---|---|---|---|
| Safety accuracy | X% | X% | X% | X% |
| Unsafe recall | X% | X% | X% | X% |
| Node accuracy | X% | X% | X% | X% |

Diff vs pre-fix S1 baseline: safety Δ=…, unsafe recall Δ=…, N flipped=…
"Same locked room" case: now unsafe / still safe (✓/✗)
Segmentation stable across baseline/consistency on spot-checked regression cases: ✓/✗
Commit: <sha>
```

## Don'ts

- Don't touch the test set. Test-set evaluation is a separate one-shot run after thesis config is finalized.
- Don't change `safety/classifier.py` or `safety/classifier_cot.py`.
- Don't add new features or refactors. The fix is strictly the two-line segmenter config change.
- Don't delete the pre-fix CSVs — archive them.

## Reference files (read if you need depth)

- `docs/planning/System2_CoT_Findings.md` §10, especially §10.3 and §10.3.1
- `data/benchmarks/segmenter_determinism_probe.md` (raw probe results)
- `experiments/determinism_probe/probe_segmenter.py` (probe script)
- `CLAUDE.md` (repo conventions, current project state)
- `/sessions/gallant-zealous-brown/mnt/.auto-memory/project_segmenter_drift.md` (mechanism summary)
