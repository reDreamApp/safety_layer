# Ablation Study — Results Log (§4.X)

Running log of ablation-condition results. Spec: `ablation_spec.md` (locked 2026-04-29).
Methodology, scope, and pre-registered comparisons are defined there; this file
only records outcomes. Started 2026-05-19.

## Conditions status

| Condition | Status | Result CSV |
|---|---|---|
| Cell A — full pipeline (S1 baseline) | ✅ reused (verified post-fix Apr 23) | `data/benchmarks/benchmark_results.csv` |
| Ablation B — no segmentation | ✅ run 2026-05-19 | `data/benchmarks/ablation_B_no_segment_s1_dev.csv` |
| Cell B — LLM seg + META off | ⏳ pending | — |
| Cell C — naive splitter + no META | ⏳ pending | — |
| Ablation A — stage-merge | ⏳ pending | — |

Cell A integrity re-verified: 480 rows, reproduces CLAUDE.md headline exactly
(safety 411/420 = 97.86%, unsafe recall 179/180 = 99.44%).

All metrics below join Ablation B ↔ Cell A on `user_input` (exact, unique per
case; the `(suite,test)` key fails because the CSV truncates the suite string).
Scoring matches the existing benchmark: 420 labelled cases scored, 60 boundary
cases unlabelled and excluded in both arms (identical exclusion → no confound).

---

## Ablation B — No Segmentation (2026-05-19)

**⚠ Pre-registered comparator is Cell B, not Cell A.** Per spec §"Pre-registered
comparisons": *"Ablation B → compare against Cell B (not Cell A — META is held
constant at 'off')."* Cell B is not yet run. **The Cell A comparison below is
descriptive context only; it is NOT the §4.X finding.** The locked claim
("does *any* segmentation matter?") is Cell B vs Ablation B and is pending Cell B.

### Headline (vs Cell A, descriptive)

| Metric | Cell A (full) | Ablation B (no-seg) | Δ |
|---|---|---|---|
| Safety accuracy (420 scored) | 97.86% | 98.33% | **+0.48 pp** |
| **Unsafe recall (180)** | **99.44%** | **96.11%** | **−3.33 pp** |
| False positives (/240 safe) | 8 | 0 | −8 |

### Stratified (mandatory per spec §B.3)

| Stratum | Metric | Cell A | Ablation B |
|---|---|---|---|
| **single-part** (`clean`, n=360) | safety acc | 97.50% | 98.06% |
| | unsafe recall (150) | 99.33% (149/150) | 95.33% (143/150) |
| | false positives (/210) | 8 | 0 |
| | maladaptive-node acc (150) | 92.7% | 95.3% |
| **multi-part** (`multipart`, n=60) | safety acc | 100.00% | 100.00% |
| | unsafe recall (30) | 100.00% | 100.00% |
| | maladaptive-node acc (30) | 96.7% | 96.7% |
| **boundary** (n=60) | — | unscored (unlabelled) | unscored (unlabelled) |

Per-node (maladaptive, clean stratum):

| Node | Cell A | Ablation B |
|---|---|---|
| AVOIDANCE | 28/30 | 30/30 |
| INTERRUPTION | 26/30 | 30/30 |
| SUPPRESSION | 27/30 | 30/30 |
| TRAUMA_REPLAY | 30/30 | 30/30 |
| VIOLENT_REVENGE | 28/30 | **23/30** |

### Findings

1. **The spec's central prediction did NOT materialise.** Spec §B.2 predicted
   Ablation B "is expected to fail [on multipart] by design" (single-label
   classifier forced to pick one label, losing information). On this dev set,
   multipart is **identical in both arms** — 100%/100% safety *and* 96.7%/96.7%
   node accuracy. Mechanism: safety is a *disjunction* over content — flagging
   unsafe needs only the dominant maladaptive signal to survive, and on these
   multipart cases it does even when the whole input is one segment. The
   predicted information-loss does not bite for the safety verdict here.
   Documented as a negative finding, per the spec's "document and proceed"
   discipline — not redesigned.

2. **Segmentation's real contribution is unsafe *recall* on single-part cases:
   +4.0 pp (95.33% → 99.33%).** Removing segmentation causes 7 missed unsafe
   `clean` cases (vs 1) but eliminates all 8 false positives — a precision↔recall
   trade. For a safety layer, unsafe recall is the clinically load-bearing metric
   (the harness itself labels it "clinically important"), so the architectural
   justification reads: *segmentation buys unsafe sensitivity at a small
   precision cost.*

3. **Error-profile shift, not uniform.** Without segmentation, clean node
   accuracy *rises* overall (92.7→95.3%) yet VIOLENT_REVENGE node accuracy
   *collapses* (28/30 → 23/30) while the other four go perfect. Segmentation
   redistributes errors rather than strictly adding/removing them.

### Caveats

- Not the pre-registered finding (needs Cell B). Treat §4.X numbers as pending.
- Single-shot S1 only, per locked scope. No UQ, no S2.
- Boundary cases unscored in both arms (no gold label) — correct, no confound.

### Supplementary — MAL+MAL composite-pattern slice (35 cases, all unsafe)

Per `ablation_spec.md` Addendum (2026-05-19). **Separate robustness table —
never pooled with the 480-case numbers; no pre-registered comparison.** Cell A
reuses `benchmark_results_mal_mal_s1.csv` (verified: 35/35 safety, 35/35 node —
matches CLAUDE.md). Result CSV: `ablation_B_no_segment_s1_mal_mal.csv`.

| Metric | Cell A (full) | Ablation B (no-seg) | Δ |
|---|---|---|---|
| Unsafe recall (35) | 100.0% (35/35) | 88.6% (31/35) | **−11.4 pp** |
| Primary-node acc (35) | 100.0% (35/35) | 71.4% (25/35) | **−28.6 pp** |

All 4 unsafe misses are the **same failure mode**: a composite input pairing an
avoidance/cower clause with a violent-revenge clause ("Cower then crush snakes",
"Hiding then brutal revenge", "Force wake and butcher", "Wake and destroy
train"). gt_node = VIOLENT_REVENGE in every case; the whole-input classifier
instead picks **BEHAVIORAL_MASTERY** (safe) — the "wake / destroy / crush" verb
reads as mastery once it is *not* isolated from the revenge framing.

**This is the spec's predicted by-design information-loss — and on the composite
slice it bites hard (−11.4 pp recall), exactly where the dev-set multipart
stratum showed ~0 effect.** The two strata are complementary, not contradictory:

- Dev `multipart`: one maladaptive pattern + benign filler → the dominant
  maladaptive signal survives whole-input classification → segmentation
  contributes ~0 to the *safety verdict* there.
- MAL+MAL: two *competing* patterns, one maladaptive-but-reads-safe-in-isolation
  → without segmentation a safe-looking clause masks the dangerous one →
  segmentation contributes +11.4 pp recall, +28.6 pp node accuracy.

Narrow honest claim this supports: *segmentation's safety contribution is
specifically the prevention of a safe-looking clause masking a co-occurring
maladaptive one; it is invisible on single-pattern inputs and large on
genuinely composite ones.* Still pending the Cell B pre-registered comparator
before this enters §4.X as a claim rather than an observation.
</content>
