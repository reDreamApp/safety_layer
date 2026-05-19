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
| Cell B — LLM seg + META off | ✅ run 2026-05-19 | `data/benchmarks/cell_B_meta_off_s1_dev.csv` |
| Cell C — naive splitter + no META | ✅ run 2026-05-19 | `data/benchmarks/cell_C_naive_s1_dev.csv` |
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

> **Update 2026-05-19:** Cell B is now run (below). The pre-registered
> Cell B vs Ablation B comparison resolves this — see "Pre-registered
> comparisons resolved" in the Cell B section. Short version: on the dev
> set, segmentation is **not independently beneficial** — its value is
> conditional on META filtering being on.

---

## Cell B — LLM segmenter + META filter OFF (2026-05-19)

CSV: `data/benchmarks/cell_B_meta_off_s1_dev.csv` (480 rows, integrity OK:
gt_safe 240T/180F/60∅, no empty preds). MAL+MAL: `cell_B_meta_off_s1_mal_mal.csv`.
"META off" disables filtering **and** the sanity check (documented coupling,
spec §"Cell B").

### Three-way dev table (480, scored 420; joined on `user_input`)

| Condition | stratum | safety acc | unsafe recall | FP | mal-node |
|---|---|---|---|---|---|
| **Cell A** (full) | ALL | 97.86% | 99.44% | 8/240 | 93.3% |
| | clean (360) | 97.50% | 99.33% | 8 | 92.7% |
| | multipart (60) | 100.00% | 100.00% | 0 | 96.7% |
| **Cell B** (seg, META off) | ALL | 95.48% | 99.44% | 18/240 | 89.4% |
| | clean (360) | 97.50% | 99.33% | 8 | 93.3% |
| | multipart (60) | **83.33%** | 100.00% | **10** | **70.0%** |
| **Ablation B** (no seg) | ALL | 98.33% | 96.11% | 0/240 | 95.6% |
| | clean (360) | 98.06% | 95.33% | 0 | 95.3% |
| | multipart (60) | 100.00% | 100.00% | 0 | 96.7% |

### Pre-registered comparisons resolved

**Cell A vs Cell B — "Does META filtering contribute?"** (held: LLM seg,
structured classifier, graph triage)
→ **Yes, and its entire contribution is on multi-part inputs.**
single-part is *identical* (97.50% / 99.33% / FP 8) — META filtering is a no-op
when the segmenter produces no META segments. On multi-part, removing the
filter drops safety 100% → **83.33%** (−16.7 pp), explodes false positives
0 → **10**, and craters node accuracy 96.7% → **70.0%**. Mechanism: multi-part
inputs contain conversational asides the segmenter labels META; unfiltered,
those segments get classified and bucketed — often as maladaptive — producing
false alarms. **META filtering exists to neutralise a cost the segmenter itself
introduces.**

**Cell B vs Ablation B — "Does *any* segmentation matter?"** (PRE-REGISTERED
Ablation B comparator; held: no META filter, structured classifier, triage)
→ **On the dev set, segmentation is NOT independently beneficial — and on
multi-part it is actively harmful without META filtering.** With META off in
both arms: multi-part safety is **Ablation B 100% vs Cell B 83.33%** (no
segmentation *beats* segmentation), node 96.7% vs 70.0%. single-part is a
recall↔precision wash (Cell B 99.33% recall / FP 8 vs Ablation B 95.33% / FP 0).
So the segmenter's clause-splitting benefit does not stand alone; its
META-segment by-product makes seg-without-filter worse than no-seg.

### Synthesis (dev + MAL+MAL together)

The two components are **synergistic, not independently additive**:

- **Segmentation's value** = correctly splitting composite maladaptive content.
  Proven on MAL+MAL: Cell A & Cell B both 100% recall / 100% node, Ablation B
  88.6% / 71.4% — there segmentation *is* independently decisive (+11.4 pp
  recall) because MAL+MAL has no META noise to confound it.
- **Segmentation's cost** = it emits META segments that, unfiltered, cause
  false positives on conversational multi-part inputs (dev Cell B multipart
  83% vs Ablation B 100%).
- **META filtering's job** = neutralise exactly that cost (Cell A multipart
  back to 100%).
- **Neither ablation improves on Cell A.** Drop META filter → multi-part
  collapses; drop segmentation → MAL+MAL recall collapses. The architecture's
  performance is the *pair* (segment-then-META-filter) operating together.

Honest §4.X claim this supports: *"Segmentation and META filtering are not
separable contributors; the safety pipeline's multi-part / composite-input
performance comes from their conjunction. Segmentation alone (META off) does
not beat no-segmentation on the dev set; it is independently decisive only on
composite maladaptive content free of conversational noise (MAL+MAL: +11.4 pp
unsafe recall). META filtering alone contributes +16.7 pp safety accuracy on
multi-part inputs, zero on single-part."* Narrow, mechanistic, quantified.

### MAL+MAL supplementary (35, all unsafe)

| | unsafe recall | node acc |
|---|---|---|
| Cell A | 100% (35/35) | 100% |
| **Cell B** | **100% (35/35)** | **100%** |
| Ablation B | 88.6% (31/35) | 71.4% |

Cell A == Cell B on MAL+MAL (META off costs nothing — no META content in pure
composite inputs), confirming the dev-set mechanism.

### Caveats

- Cell C (naive splitter vs LLM segmenter, META off) still pending — needed for
  the "Cell B vs Cell C" pre-registered comparison and to separate
  *LLM-segmentation quality* from *segmentation-existence*.
- Single-shot S1 only. Boundary cases unscored in all arms (no confound).

---

## Cell C — Naive sentence-splitter + no META (2026-05-19)

CSV: `data/benchmarks/cell_C_naive_s1_dev.csv` (480 rows, integrity OK).
MAL+MAL: `cell_C_naive_s1_mal_mal.csv`. Sentence-level split only (`re` on
`[.!?]+ws`), all-ACTION, META inert by absence (spec §"Cell C"; clause/comma
splitting deliberately excluded — locked, see §"Don'ts").

### Dataset artifact (must be reported in §4.X — drives the Cell C reading)

Applying the naive splitter to all 480 dev inputs:

| Stratum | Naive split result |
|---|---|
| `clean` (360) | **always exactly 2 sentences** (splits every case) |
| `multipart` (60) | **always 1 sentence** (never splits) |
| `boundary` (60) | 48× 2-sent, 12× 1-sent (unscored) |
| MAL+MAL (35) | **always 1 sentence** (never splits) |

The dataset's multi-part / composite content is **comma/conjunction-joined
within a single sentence** (e.g. *"…instead of freezing I yell for my mom,
grab the fire extinguisher, and back him out…"*). A sentence-level splitter
therefore returns one segment = whole input on exactly those cases →
**Cell C ≡ Ablation B on `multipart` and MAL+MAL by construction** (verified:
0/60 multipart pred disagreements vs Ablation B; 16/360 on `clean`, where naive
does split). Consequence: on this dataset, sentence-level segmentation cannot
exercise on the inputs where segmentation matters. This is a property of the
dataset's writing style, not a bug — reported as a limitation.

### Four-way dev table (480, scored 420)

| Condition | stratum | safety | unsafe recall | FP | mal-node |
|---|---|---|---|---|---|
| Cell A (full) | ALL | 97.86% | 99.44% | 8 | 93.3% |
| | clean | 97.50% | 99.33% | 8 | 92.7% |
| | multipart | 100.00% | 100.00% | 0 | 96.7% |
| Cell B (seg, META off) | ALL | 95.48% | 99.44% | 18 | 89.4% |
| | clean | 97.50% | 99.33% | 8 | 93.3% |
| | multipart | 83.33% | 100.00% | 10 | 70.0% |
| **Cell C** (naive split) | ALL | 97.38% | 98.89% | 9 | 93.9% |
| | clean | 96.94% | 98.67% | 9 | 93.3% |
| | multipart | 100.00% | 100.00% | 0 | 96.7% |
| Ablation B (no seg) | ALL | 98.33% | 96.11% | 0 | 95.6% |
| | clean | 98.06% | 95.33% | 0 | 95.3% |
| | multipart | 100.00% | 100.00% | 0 | 96.7% |

### Pre-registered comparison resolved — Cell B vs Cell C

**"Does the LLM segmenter beat sentence-level splitting?"** (held: no META
filter, structured classifier, triage). Cleanly answerable **only on `clean`**
(the only stratum where naive actually splits):

- `clean`: Cell B (LLM seg) **97.50% / 99.33% recall / node 93.3%** vs Cell C
  (naive) **96.94% / 98.67% / 93.3%**. The LLM segmenter's edge over a regex
  sentence-splitter is **~0.5 pp safety, ~0.7 pp recall, identical node
  accuracy**. On single-action clean inputs, **sentence-level splitting
  captures essentially all the value the LLM segmenter provides.**
- `multipart`: comparison is *confounded and uninformative* — Cell B's 83.33%
  reflects the META-off artifact (LLM segmenter emits META segments that, with
  the filter off, cause FPs), not segmentation quality; and Cell C ≡ no-seg
  here by construction. Do not read "Cell C 100% > Cell B 83%" as "naive beats
  LLM segmenter."
- Aggregate ALL (Cell C 97.38% > Cell B 95.48%) is likewise dragged by Cell B's
  multipart META artifact — not a real Cell C advantage. Report the `clean`
  stratum as the load-bearing Cell B vs Cell C number.

### MAL+MAL supplementary (35, all unsafe)

| | unsafe recall | node acc |
|---|---|---|
| Cell A | 100% (35/35) | 100% |
| Cell B | 100% (35/35) | 100% |
| **Cell C** | **88.6% (31/35)** | **71.4%** |
| Ablation B | 88.6% (31/35) | 71.4% |

Cell C misses the **identical 4 cases** as Ablation B (composite VIOLENT_REVENGE
clauses comma-joined inside one sentence — naive never splits them; the LLM
segmenter splits at the "but"/"," clause boundary and isolates the revenge
clause). **This is where "LLM segmenter > naive splitting" is actually
demonstrable: +11.4 pp recall, +28.6 pp node** — and the mechanism is
specifically clause-level (sub-sentence) splitting.

### Synthesis update (segmentation-quality axis)

- **Single-action clean inputs:** LLM segmenter ≈ naive sentence-split
  (~0.5 pp). Segmentation *granularity* is near-irrelevant when each input is
  one action.
- **Composite / multi-part inputs:** the LLM segmenter's advantage is
  **clause-level splitting**, which no sentence-level rule can replicate on
  this dataset (multi-part is intra-sentence). Demonstrated on MAL+MAL
  (100% vs 88.6% recall); invisible on dev `multipart` because there
  naive ≡ no-seg *and* the dominant-signal effect lifts even no-seg to 100%.
- **Dev-set whole:** the LLM segmenter buys ~0.5 pp over a regex splitter
  (Cell C ALL 97.38% vs Cell A 97.86%). The architectural case for the LLM
  segmenter rests on composite content (MAL+MAL), not the dev set headline —
  consistent with the Ablation B / Cell B findings.
