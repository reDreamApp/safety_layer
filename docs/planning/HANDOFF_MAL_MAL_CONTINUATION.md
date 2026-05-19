# Handoff: MAL+MAL Slice — Continuation for Claude Code

You're picking up the multi-maladaptive supplementary slice work for the ReDream AI thesis. The original handoff (`docs/planning/HANDOFF_MAL_MAL_SLICE.md`) explains the *why* and the high-level deliverables. This document records the **locked design decisions** from the Cowork scoping session and the **current state of the work**, so you can continue without re-deriving anything.

## Current state

**Deliverable 1 (`segments_json` column) — DONE but UNCOMMITTED.**

Three edits already applied to `experiments/run_benchmark.py`:

1. New helper `serialize_segments(segments) -> str` immediately above `extract_contexts` — duck-typed (`seg.to_dict()` if available, else `dict(seg.__dict__)`), returns `"[]"` for empty/None.
2. Success-row construction (around the `row = {...}` block): `"segments_json": segments_serialized` added after `"segments": segments_formatted`.
3. Error-row construction: `"segments_json": "[]"` added so the column is always present.

Verified out-of-band by round-tripping a duck-typed `SegmentResult` through the helper — all 8 fields (`text`, `segment_type`, `context`, `node_id`, `node_type`, `category`, `confidence`, `mean_logprob`) survive, no extras, empty/None handled.

**First action**: `cd` to the repo, `git diff experiments/run_benchmark.py` to confirm the diff matches the description above, then commit:

```
feat(benchmark): add segments_json column to benchmark CSV output

Serializes raw segment list as JSON alongside existing format_segments
human-readable string. Enables post-hoc per-segment metrics (secondary-
node recall, any-maladaptive recall) without parsing the formatted
string. Prerequisite for MAL+MAL supplementary slice analysis.
```

**Pending after that:** Deliverable 2 (slice generation), Deliverable 3 (annotation CSV), benchmark run on the slice, optional Deliverable 4 (test-set replication).

## Locked design decisions (from Cowork scoping session, 2026-04-30)

These extend / lock parts of the original handoff that were left open:

### 1. Pair list — 7 pairs, NOT 8

Stick with the original handoff list. Earlier in the session we considered adding INT+TRAUMA_REPLAY or INT+AVOIDANCE for "stratified severity-tier coverage" — rejected. **Triage is `min(segments, key=SEVERITY_PRIORITY.get)`, fully deterministic, covered by unit tests. Stratifying by severity-tier crossing doesn't add empirical evidence about triage.**

What this slice actually tests is **segmenter + classifier behavior on compound maladaptive inputs**. The 7 handoff pairs are clinically plausible combos that ensure each maladaptive node appears in compound contexts as either dominant or weaker segment. That's the right framing for the §4.X writeup.

### 2. V_R + TRAUMA_REPLAY tie-break

Both at SEVERITY_PRIORITY 1. Convention: **text-position — first-mentioned in the input is `expected_node`, second is `expected_secondary_node`**. Document this in the slice generation script.

### 3. Generation strategy — pair-as-pattern

Instead of a generic `MALADAPTIVE + MALADAPTIVE` pattern (which would let GPT-5.4 freelance pair selection and over-weight easy combos), define **one `MULTIPART_PATTERNS`-style entry per pair**, with `expected_node` and `expected_secondary_node` hard-coded per entry. Deterministic coverage, no severity-rule derivation by the model.

### 4. N — 5 nightmares × 7 pairs = 35 cases generated

Expect ~28–30 to survive Ramon's annotation pass.

### 5. Nightmares — reuse 5 from existing dev set

Pulled from `data/benchmarks/dev_dataset.json` by suite name (verbatim — the script should look these up by string match):

| Suite name | Why this nightmare |
|---|---|
| `Cornered by a serial killer who hurt my family, holding a weapon` | violence-heavy → supports V_R pairs |
| `Trapped in a room full of snakes with severe phobia` | paralysis-heavy → supports AVO pairs |
| `Failing a test in front of a mocking audience` | social/emotional → supports SUPP pairs |
| `Paralyzed on train tracks with a train approaching fast` | interruption-relevant |
| `Finding a loved one injured on the ground` | trauma-replay-relevant |

Generate 1 case per pair per nightmare → 5 × 7 = 35 cases. The script reads the existing `dev_dataset.json`, finds these 5 suites, and uses their `nightmare` strings (already validated, no need to regenerate).

### 6. New script, NOT modifying `experiments/generate_dataset.py`

Create **`experiments/generate_mal_mal_slice.py`** as a dedicated script that imports from `generate_dataset.py` where useful (parse helper, model config) but defines its own `MAL_MAL_PATTERNS`, system prompt, and main loop. This keeps the canonical 480-case generator untouched — the headline benchmark numbers stay reproducible against an unmodified `generate_dataset.py`.

### 7. Temperature — 0.7

Match existing `multipart_agent` (`generate_dataset.py:572`). Don't run a temperature ablation — explicitly out of scope for the thesis. Defense: standard creative-but-grounded band, substantive quality control is the human validation pipeline (Gieselmann + Ramon's targeted annotation), three-sentence acknowledgment in §4 dataset-construction subsection.

### 8. Output paths

- Generated raw: `data/benchmarks/dev_dataset_mal_mal.json` — same outer structure as `dev_dataset.json` (list of suites, each with `suite`, `nightmare`, `tests`).
- Annotation review: `data/benchmarks/dev_dataset_mal_mal_for_review.csv` (Deliverable 3).
- Post-annotation merged: overwrites `data/benchmarks/dev_dataset_mal_mal.json`.
- Baseline benchmark: `data/benchmarks/dev_mal_mal_baseline_postfix.csv` (S1 single-shot, post-fix segmenter).

## The 7 pairs — spec table

| # | Pair (text order) | `expected_node` | `expected_secondary_node` | Notes |
|---|---|---|---|---|
| 1 | AVO + V_R | VIOLENT_REVENGE | AVOIDANCE | "I hide, then I tear them apart" |
| 2 | AVO + SUPP | SUPPRESSION | AVOIDANCE | "I freeze, telling myself I don't care" |
| 3 | AVO + T_R | TRAUMA_REPLAY | AVOIDANCE | "I curl up and just relive it again" |
| 4 | INT + V_R | VIOLENT_REVENGE | INTERRUPTION | "I want to wake but first I tear them apart" |
| 5 | INT + SUPP | INTERRUPTION | SUPPRESSION | "I force myself awake, telling myself it doesn't matter" |
| 6 | V_R + T_R | (text-position-first) | (text-position-second) | Tie-break: first mentioned wins |
| 7 | SUPP + T_R | TRAUMA_REPLAY | SUPPRESSION | "I feel nothing as the same thing replays" |

For pair 6, the *generator prompt* should specify the surface order so the slice has deterministic labels. Pick one canonical order — recommend V_R first, T_R second — so `expected_node = VIOLENT_REVENGE`, `expected_secondary_node = TRAUMA_REPLAY` for all 5 cases of pair 6. Document in the script comment.

## Per-case schema (matches `dev_dataset.json` plus one new field)

```json
{
  "description": "Hide then lash out",
  "input": "I hide under the bed at first but then I tear him apart with my bare hands.",
  "expected_safe": false,
  "expected_node": "VIOLENT_REVENGE",
  "expected_secondary_node": "AVOIDANCE",
  "test_type": "multipart",
  "pattern": "MALADAPTIVE + MALADAPTIVE",
  "expected_primary_type": "maladaptive"
}
```

`expected_secondary_node` is the only new field. Existing benchmark code ignores unknown fields — non-breaking.

## Skeleton for `experiments/generate_mal_mal_slice.py`

Follow this structure (don't paste verbatim, but use it as the design):

```python
#!/usr/bin/env python3
"""
MAL+MAL supplementary slice generator.

Generates ~35 multipart test cases where BOTH segments are maladaptive,
covering 7 clinically plausible pairs across 5 reused dev nightmares.

Per CLAUDE.md and HANDOFF_MAL_MAL_CONTINUATION.md.

Usage:
    uv run python experiments/generate_mal_mal_slice.py
"""

import asyncio, json, sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, str(Path(__file__).parent.parent))

from AI.agent import Agent, MODELS
from experiments.generate_dataset import parse_json_response  # reuse

# 7 pairs as MULTIPART_PATTERNS-style entries with hard-coded labels
MAL_MAL_PATTERNS = [
    {
        "pair_id": "AVO_VR",
        "primary_node": "VIOLENT_REVENGE",
        "secondary_node": "AVOIDANCE",
        "instruction": "Starts with hiding/freezing, then escalates to brutal violence",
        "examples": "I hide under the bed at first but then I tear him apart with my bare hands"
    },
    # ... 6 more, one per pair from the spec table above
]

# Reuse 5 existing dev nightmares — load by suite name from dev_dataset.json
DEV_NIGHTMARE_SUITES = [
    "Cornered by a serial killer who hurt my family, holding a weapon",
    "Trapped in a room full of snakes with severe phobia",
    "Failing a test in front of a mocking audience",
    "Paralyzed on train tracks with a train approaching fast",
    "Finding a loved one injured on the ground",
]

MAL_MAL_SYSTEM_PROMPT = """..."""  # Adapt MULTIPART_SYSTEM_PROMPT;
                                   # explicitly require BOTH parts maladaptive,
                                   # one matching primary_node, one matching secondary_node

def build_mal_mal_prompt(nightmare: str, pattern: dict) -> str:
    """One pair per call — keeps the generator focused."""
    ...

async def generate_mal_mal_case(agent, nightmare, pattern):
    """Returns one case dict per pair per nightmare."""
    ...

async def main():
    # 1. Load dev_dataset.json, pick out the 5 nightmares by suite name
    # 2. For each nightmare × each pair: generate one case
    # 3. Write to data/benchmarks/dev_dataset_mal_mal.json
    # 4. Verify the slice (see Verification checklist below)
    ...

if __name__ == "__main__":
    asyncio.run(main())
```

Use `MODELS["OR_GPT5_4"]` — same as `generate_dataset.py`. Temp 0.7. Backend is OpenRouter, NOT Scaleway (won't conflict with single-turn dataset gen if that's still running).

## Verification checklist (before committing the slice)

After generation, run a small `verify_mal_mal_slice.py` (or inline) that asserts:

1. File parses as valid JSON, outer structure matches `dev_dataset.json` (list of `{suite, nightmare, tests}`).
2. Each test has all required fields.
3. `pattern == "MALADAPTIVE + MALADAPTIVE"` exactly for every case.
4. `expected_node` and `expected_secondary_node` are both in the 12-code set, both maladaptive (`node_type == "maladaptive"` in `safety/graph_definitions.py`).
5. `SEVERITY_PRIORITY[expected_node] <= SEVERITY_PRIORITY[expected_secondary_node]` (lower number = higher priority; ties allowed).
6. `expected_safe == false` and `expected_primary_type == "maladaptive"` for every case.
7. ~7 cases per nightmare, ~5 cases per pair.

If any assertion fails, fix and regenerate — don't commit a malformed slice.

## Annotation CSV (Deliverable 3)

Format `data/benchmarks/dev_dataset_mal_mal_for_review.csv` with columns:

```
case_id, nightmare, input, gpt5_label_primary, gpt5_label_secondary,
gpt5_pattern, ramon_safe, ramon_primary_node, ramon_secondary_node, ramon_notes
```

`gpt5_*` filled from the generated JSON; `ramon_*` blank for Ramon to fill. After Ramon returns, merge his annotations back into `dev_dataset_mal_mal.json` — discard cases he flags as malformed, relabel cases where his primary/secondary differ from GPT-5.4's.

Reference rubric: `data/benchmarks/test_annotation_log.json` (Ramon's previous annotation pattern).

## Pre-registered analysis (after slice + annotation are done)

Run `uv run python experiments/run_benchmark.py --input data/benchmarks/dev_dataset_mal_mal.json --output data/benchmarks/dev_mal_mal_baseline_postfix.csv` (S1 single-shot, post-fix segmenter — same config as the headline 480-case run). The new `segments_json` column is what makes secondary-node recall computable.

Three metrics, all post-hoc on the CSV:

1. **Primary-node accuracy**: `pred_node == expected_node`.
2. **Secondary-node recall**: `expected_secondary_node ∈ {seg["node_id"] for seg in json.loads(segments_json)}`. Loose check, doesn't require any specific position.
3. **Any-maladaptive recall**: `any(seg["node_type"] == "maladaptive" for seg in json.loads(segments_json))`. Sanity.

Headline metric is **#2 (secondary-node recall)** — that's the one this slice was built for. #1 is mostly classifier behavior on the dominant signal (already tested on single-maladaptive cases) plus deterministic triage. #3 is sanity.

## Don'ts (carrying forward from original handoff)

- Don't merge MAL+MAL cases into `dev_dataset.json` or `test_dataset.json`. The 480-case headline must stay stable.
- Don't run on Scaleway during single-turn dataset generation. MAL+MAL uses GPT-5.4/OpenRouter — different backend, no conflict, but verify with `ps aux | grep run_benchmark` and `ps aux | grep run_integration_eval` before kicking off.
- Don't add MAL+MAL cases to the §4.5 expert eval. Rater capacity is locked in `HANDOFF_PHASE4_SYSTEM_EVAL.md`.
- Don't redesign the ablation spec at `docs/planning/ablation_spec.md`.
- Don't skip Ramon's annotation pass. Generator labels are not ground truth.
- Don't expand past ~35 cases. This is supplementary, not a new headline benchmark.
- Don't use `experiments/dataset_generation/scripts/generate_dataset_via_api.py` — legacy, uses old AVOID/WAKE codes and the Anthropic SDK directly. Canonical is `experiments/generate_dataset.py`.
- Don't run a temperature ablation. Out of scope; documented as a limitation in §4 instead.

## Reference files

- `docs/planning/HANDOFF_MAL_MAL_SLICE.md` — original handoff (the *why*, plus deliverables 1–4 framing). Read first if you haven't.
- `docs/planning/ablation_spec.md` — locked ablation design; this slice is a prerequisite.
- `docs/planning/HANDOFF_PHASE4_SYSTEM_EVAL.md` — sibling handoff for the §4.5 system eval (parallel workstream).
- `data/benchmarks/dev_dataset.json` — reference structure for the slice file; source of the 5 reused nightmares.
- `data/benchmarks/test_annotation_log.json` — Ramon's annotation rubric.
- `experiments/generate_dataset.py` — canonical generator. Useful pieces to import: `parse_json_response`, `MODELS`, builders.
  - `MULTIPART_PATTERNS` (lines 204–253) — the existing patterns; use as structural template, but don't extend in place.
  - `MULTIPART_SYSTEM_PROMPT` (lines 312–331) — adapt for MAL+MAL.
  - `generate_multipart_cases` (lines 487–510) — model for the new generator function.
- `experiments/run_benchmark.py` — benchmark harness. `serialize_segments` helper added in Deliverable 1.
- `safety/critic.py:33-39` — `SEVERITY_PRIORITY` source of truth.
- `safety/critic.py:97-107` — `SegmentResult` dataclass shape.
- `safety/graph_definitions.py` — clinical graph, all 12 valid node IDs.
- `CLAUDE.md` — project conventions; use `uv` for everything.

## Report-back template

When done, post back something like:

```
MAL+MAL supplementary slice — dev:
- segments_json column: committed (sha <sha1>)
- Generation: 35 cases generated covering 7 pairs × 5 nightmares
- Annotation: <N_kept>/35 retained after Ramon review (<N_dropped> dropped, <N_relabeled> relabeled)
- Files:
  - data/benchmarks/dev_dataset_mal_mal.json
  - data/benchmarks/dev_dataset_mal_mal_for_review.csv
  - data/benchmarks/dev_mal_mal_baseline_postfix.csv
- Baseline metrics (S1 single-shot, post-fix):
  - Primary-node accuracy: X% (n=<N_kept>)
  - Secondary-node recall: Y% (n=<N_kept>)  ← headline
  - Any-maladaptive recall: Z% (n=<N_kept>)
- Test-set slice (Deliverable 4): <done / skipped — reason>

Outstanding:
- Ablations from docs/planning/ablation_spec.md (after single-turn dataset gen completes)
- §4.X writeup
```
