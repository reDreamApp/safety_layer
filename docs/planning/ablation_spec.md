# Ablation Study Specification — Architectural Justification (§4.X)

**Status:** Locked 2026-04-29. No post-hoc design edits — same discipline as the §4.5 system-eval handoff. If something turns out to be wrong mid-experiment, document and proceed; don't redesign mid-stream.

## Purpose

The structured-S1 safety pipeline (`safety/critic.py`) was designed by intuition first and validated on the dev benchmark afterwards. The thesis presents the architecture as a deliberate set of design choices; an ablation study justifies that framing by isolating which choices are doing the work. Without ablations, the architecture reads as decorative.

**Scope of claim this study supports:** the explicit *neural* decomposition of the pipeline (separate segmenter and classifier stages) contributes to safety classification accuracy on the dev set. The claim is *narrow on purpose*. See "Scope and limits" below.

## Configuration (locked)

- **Dataset:** `data/benchmarks/dev_dataset.json` (480 cases, 12 nodes — post-Mar-19 regeneration with affect fix).
- **Classifier:** S1 only (`MISTRAL_SMALL` via Scaleway-direct, `temperature=0`). Same backend as production. S2 is out of scope; ablation results apply to the S1 pipeline. Note in writeup: "Ablation findings are specific to the S1 pipeline; S1 and S2 have known divergent error profiles (`docs/planning/project_postfix_unsafe_miss_decomposition.md`)."
- **Run mode:** single-shot (no semantic consistency, no logprobs UQ for the ablations). UQ is treated separately as a property of the full pipeline in the consistency chapter.
- **Output format:** reuse `experiments/run_benchmark.py` CSV schema for apples-to-apples comparison with the existing baseline runs.
- **Backend identical across all conditions** — same model, same temperature, same Scaleway-direct routing — so observed deltas are attributable to architectural choices, not model differences.

## Ablations

### Ablation A — Stage-Merge (formerly "monolithic")

Single LLM call performs both segmentation and classification on the full input. Triage is applied externally using the same `SEVERITY_PRIORITY` logic the structured pipeline uses programmatically.

**Renamed from "monolithic" because the experiment was narrowed during design.** The LLM is *not* doing constraint synthesis or correction generation — those layers aren't tested on the dev benchmark in either arm. What's varying is whether the neural workload (segment + classify) is decomposed into two sequential LLM calls or merged into one.

#### A.1 LLM input

User-message portion (matches what the standard segmenter receives):
```
Context: "<nightmare_context>"
Input: "<user_input>"
```

#### A.2 LLM output (JSON only)

```json
{
  "segments": [
    {"text": "this is dumb", "label": "META", "type": "meta"},
    {"text": "I hide", "label": "AVOIDANCE", "type": "maladaptive"}
  ]
}
```

Validation rules:
- `segments` must be a JSON array. Should not be empty (every input has at least one segment, even if it's pure META).
- Each segment object must have keys `text`, `label`, `type` (extras don't fail the parse but are ignored).
- `type` ∈ {maladaptive, adaptive, neutral, **meta**}.
- If `type ∈ {maladaptive, adaptive, neutral}`: `label` must be one of the 12 valid codes (AVOIDANCE, INTERRUPTION, VIOLENT_REVENGE, SUPPRESSION, TRAUMA_REPLAY, BEHAVIORAL_MASTERY, SOCIAL_MASTERY, ENVIRONMENTAL_MASTERY, EMOTIONAL_MASTERY, MYTHICAL_MASTERY, NARRATIVE_SETTING, AFFECT_EXPRESSION) **and** `type` must match the label's category in the graph (e.g., `label=AVOIDANCE` requires `type=maladaptive`). Internal inconsistency triggers retry.
- If `type == "meta"`: `label` must be the sentinel `"META"` (not one of the 12 clinical codes).
- META content is **labeled, not omitted** — strict parity with the structured pipeline, where the segmenter labels META and the critic filters post-hoc (`safety/critic.py:296`). Asking the LLM to omit META would sneak a filtering step into the neural component that the structured pipeline doesn't have there. Labeling-then-filtering is also a recoverable failure mode: if the LLM mislabels content as META (or fails to label something that should be), it's visible in the output.

The prompt instructs explicitly: *"For conversational/meta content (e.g., 'this is dumb', 'I hate this therapy', questions about therapy), output `type: 'meta'` and `label: 'META'`. Do not omit any segments from the output."*

No `is_safe`, `primary_node`, `context`, `severity`, or `correction` fields. All derived post-hoc.

#### A.3 Prompt knowledge (locked — strict parity with structured classifier)

Include in the system prompt:
- **Codes + classification rules** — reuse the body of `CLINICAL_CODER_PROMPT` from `safety/classifier.py` (12 codes with definitions, violence threshold rule, mastery priority rule, negation rule, mental-actions rule, emotional-regulation rule, trauma-replay rule).

Do **not** include:
- Severity priorities (the `SEVERITY_PRIORITY` dict). Triage is done post-hoc, identically to the structured pipeline. The structured classifier never sees these either.
- Correction edges / redirection strategies (`get_correction_strategies()` output). The structured classifier never sees these either; they're consumed only by `_build_constraint_message`, which isn't being tested.

The principle: each component sees the same knowledge its structurally-equivalent counterpart in the other pipeline sees. The structured classifier sees codes+rules; the stage-merge LLM sees codes+rules. Triage is symbolic in both arms.

#### A.4 JSON parse-failure policy

Two-attempt fail-closed:

1. First call at `temperature=0` with the schema spec in the prompt.
2. If response fails any of {valid JSON, required fields present, label/type valid, type matches label's graph category, segments is array} → retry once at `temperature=0` with appended reminder: `"Return ONLY a valid JSON object matching the specified schema. No markdown, no explanation."`
3. If second attempt also fails → record `pred_safe=False, pred_node="PARSE_FAILURE", segments=[]`. Counts as wrong prediction on safe cases (false positive) and wrong-node prediction on unsafe cases.
4. Report `parse_failure_rate` as a separate column in the ablation results CSV alongside accuracy/recall.

Distinct from `UNCLASSIFIED` (which stays a per-segment low-confidence signal in the structured pipeline). Parse failure = whole-response failure; UNCLASSIFIED = per-segment low confidence. Keep them separate so the failure-mode analysis is clean.

#### A.5 Post-hoc derivation (in scoring code, not in LLM output)

After parsing the LLM's `segments` array, mirror the structured pipeline's META filter (`safety/critic.py:296`) before triage:

```python
# Step 1: Filter META segments (mirrors safety/critic.py:296)
dream_segments = [s for s in segments if s["type"] != "meta"]

# Step 2: Derive is_safe from remaining (non-META) segments
is_safe = not any(s["type"] == "maladaptive" for s in dream_segments)

# Step 3: Derive primary_node — highest-severity maladaptive, else first
# adaptive/neutral, else META_ONLY (when all segments were META)
maladaptive = [s for s in dream_segments if s["type"] == "maladaptive"]
if maladaptive:
    primary = min(maladaptive, key=lambda s: SEVERITY_PRIORITY[s["label"]])
    primary_node = primary["label"]
elif dream_segments:
    primary_node = dream_segments[0]["label"]
else:
    primary_node = "META_ONLY"
    is_safe = True
```

Identical filter-then-triage sequence to the structured pipeline.

### Ablation B — No Segmentation

Force the whole user input as a single `ACTION` segment in the structured pipeline. Classifier called once; triage and constraint synthesis run unchanged.

#### B.1 Implementation

Add a `skip_segmentation: bool = False` flag to `SafetyCritic.__init__`. When `True`, replace the segmenter call in `evaluate_intervention` with:

```python
segments = [SegmentResult(text=user_input, segment_type="ACTION", context=nightmare_context)]
```

Everything downstream runs unchanged. The META sanity check (which only fires when `dream_segments` is empty) effectively never fires in this configuration — that's a design feature, controlled for by comparing against Cell B (see "Pre-registered comparisons" below), not against Cell A.

#### B.2 What this tests (and the design constraint)

The structured classifier (`safety/classifier.py`) is **single-label by design** — it outputs one of 12 codes as a single token. That design is integrated with the segmenter: the segmenter produces multiple short segments, the classifier outputs one label per segment. You cannot cleanly remove the segmenter without leaving the classifier with a job it wasn't designed for.

So Ablation B is **not** a clean test of "does segmentation matter." On multi-part inputs ("I hide for a moment, then I turn and fight"), the classifier necessarily picks one label and loses information by design. That's expected behavior, not surprising failure. To make the result meaningful, **Ablation B's report is stratified by case type.**

#### B.3 Stratified reporting (mandatory)

Stratify the dev-set evaluation results by `test_type` (or equivalent multi-part flag in `dev_dataset.json`):

- **Single-part cases**: Cases where the user input is naturally one action/feeling. Ablation B should perform comparably to Cell A here — segmentation isn't doing real work when the input is already "one segment's worth." If Ablation B underperforms substantially on single-part inputs, that's a separate finding (the structured classifier isn't robust to the absence of pre-extracted context).
- **Multi-part cases**: Cases tagged as `test_type=multipart` in the dataset (or equivalent). Ablation B is expected to fail here by design. The interesting quantity is *how much* — this number tells you what fraction of the segmentation contribution is specifically attributable to multi-part input handling.

Report both strata in the §4.X table. Do not report a single aggregate Ablation B number — it would conflate two distinct effects (classifier robustness on long inputs + multi-label handling on multi-part inputs).

The reframed claim Ablation B supports: *"Segmentation contributes X% accuracy on multi-part inputs (where the structured classifier's single-label design forces information loss without it) and Y% accuracy on single-part inputs (where any contribution comes from focused-context effects)."* Honest, narrow, and quantified.

### Ablation C — META 1D Comparison

Three benchmark runs that decompose the contribution of META filtering and segmentation strategy along two axes (without doing the full 2×2, which would require regex META filtering for the naive+META cell — explicitly avoided).

#### Cell A — Full pipeline (LLM segmenter + META filter on)

Already run. Reuse existing post-fix S1 baseline from `data/benchmarks/`. **Verify the run is post-segmenter-fix (Apr 22-23, 2026) before reusing.**

#### Cell B — LLM segmenter + META filter off

LLM segmenter labels segments normally; the META filter (`dream_segments = [s for s in segments if s.segment_type != "META"]` in `safety/critic.py:296`) is bypassed. META segments are passed to the classifier and bucketed alongside dream content.

The META sanity check is implicitly disabled in this configuration too (it only fires when `dream_segments` is empty, which never happens when META filtering is off). Document this coupling: "META off" means both filtering and the sanity check are inactive. They're conceptually distinct features but coupled by the current implementation.

#### Cell C — Naive splitter + no META filter

Replace the LLM segmenter with sentence-level rule-based splitting:

```python
import re
from safety.critic import SegmentResult

def naive_segment(text: str, nightmare_context: Optional[str]) -> List[SegmentResult]:
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    parts = [p.strip() for p in parts if p.strip()]
    if not parts:
        parts = [text.strip() or text]
    return [
        SegmentResult(text=p, segment_type="ACTION", context=nightmare_context)
        for p in parts
    ]
```

Sentence-level only. No clause-level splitting on conjunctions ("but/and/so") — that would muddy the contrast with the LLM segmenter's clause-level granularity. All segments labeled `ACTION` (no META detection by design — Option A from the design discussion). META filter is "off" by absence: there are no META-typed segments to drop.

## Pre-registered comparisons

Each comparison isolates one variable; pair the runs accordingly when reporting.

| Comparison | Question | Held constant |
|---|---|---|
| Cell A vs Cell B | Does META filtering contribute? | LLM segmentation, structured classifier, graph triage |
| Cell B vs Cell C | Does the LLM segmenter beat sentence-level splitting? | No META filter, structured classifier, graph triage |
| Cell B vs Ablation B | Does *any* segmentation matter? | No META filter, structured classifier, graph triage |
| Cell A vs Ablation A | Does explicit two-stage neural decomposition help? | Same backend, same knowledge, same triage logic |

The "right" baseline for each ablation:
- Ablation B → compare against Cell B (not Cell A — META is held constant at "off").
- Ablation A → compare against Cell A (the full pipeline is the natural reference; META content is implicitly excluded in both arms, just by different mechanisms — by the LLM internally in Ablation A, by the explicit filter in Cell A).

## Reported metrics

For each run, report the same metrics the existing dev benchmark reports:

- **Safety accuracy** (`pred_safe == expected_safe`)
- **Unsafe recall** (recall on `expected_safe == False` cases)
- **Per-node accuracy** for the 5 maladaptive nodes (matching the existing benchmark breakdown)
- **Parse failure rate** (Ablation A only; expected to be ~0% for the structured pipeline arms)

**Stratification (Ablation B only):** report safety accuracy and unsafe recall separately for single-part vs multi-part cases (split by `test_type` in the dataset). Do not report a single aggregate Ablation B number — see §B.3 for rationale.

Do **not** report:
- Consistency / agreement metrics — UQ is out of scope for these ablations.
- Confidence scores — only the structured pipeline produces clean logprobs; Ablation A doesn't, and we deliberately chose not to scaffold it for fairness.
- Correction quality — that's the §4.5 system eval, not this.

## Scope and limits (write this into §4.X verbatim)

What these ablations *do* support:
- A claim that explicit decomposition of the neural workload (segmenter as a separate LLM call) improves safety classification on the S1 pipeline.
- A claim that META filtering contributes (or doesn't) to S1 safety classification accuracy.
- A claim that LLM-based segmentation outperforms (or doesn't) naive sentence-level segmentation on this dev set.

What these ablations do *not* support:
- A claim that the symbolic constraint-synthesis layer (graph-based correction edges + Validate+Correct templates) contributes to anything. That's tested qualitatively in §4.5 (system-level eval), not separately ablated here.
- A claim that the architectural choices generalize to S2. Findings are specific to the S1 pipeline.
- A claim that the *graph* (as a knowledge structure beyond the codes themselves) is necessary. Codes + rules are in the prompt of every arm; the graph's edge structure is only used by `_build_constraint_message`, which isn't tested.

Write the §4.X discussion in scoped terms. The architecture-justification chapter should *not* claim "the neuro-symbolic structure matters" generally — it should claim "two-stage neural decomposition contributes X percentage points of safety accuracy at S1; the symbolic correction layer is evaluated separately in §4.5."

## Implementation order

Cheapest first, so any infrastructure issues surface early:

1. **Ablation B (no-segmentation)** — ~30 minutes. Add `skip_segmentation` flag to `SafetyCritic`; add `--no-segment` flag to `run_benchmark.py`. Run on dev set.
2. **Cell B (LLM seg + META off)** — ~30 minutes. Add a `skip_meta_filter` flag to `SafetyCritic`. Run on dev set.
3. **Cell C (naive segmenter + no META)** — ~1-2 hours. Add `naive_segment` function, plumb through a `--segmenter naive` option in `run_benchmark.py`. Run on dev set.
4. **Ablation A (stage-merge)** — ~half day. New class `StageMergeCritic` exposing the same `evaluate_intervention(...)` interface as `SafetyCritic`; new prompt with the 12 codes + rules + JSON schema; JSON parser with retry-once policy; post-hoc derivation of `is_safe` and `primary_node`. Wire as `--critic merged` flag in `run_benchmark.py`. Run on dev set.

Total: ~1 day of coding + overnight compute on dev (single-shot S1 ≈ 30-60 min per condition × 4 conditions = ~3 hours wall-clock with sequential runs, less with concurrency).

Cell A is already done — reuse existing post-fix S1 baseline. **Verify the source run is from Apr 22 or later** (post-segmenter-fix).

## Don'ts

- **Don't** add CoT-style reasoning to Ablation A. S1 is direct (no CoT); the merged ablation must also be direct, otherwise you're confounding "stage merge" with "added reasoning."
- **Don't** include severity priorities or correction edges in the Ablation A prompt. Strict parity with the structured classifier — and the dev benchmark doesn't score correction quality, so they wouldn't change the result anyway.
- **Don't** introduce semantic consistency or logprobs UQ for any ablation. UQ is a property of the full pipeline, evaluated separately.
- **Don't** run on S2. S1-only is the locked scope. If a reviewer asks about S2 generalization, note it as future work.
- **Don't** hide JSON parse failures by retrying more than once or by routing them to UNCLASSIFIED. Two attempts max, then `PARSE_FAILURE`. The failure rate is itself a result.
- **Don't** stretch the naive splitter to also do clause-level splitting on conjunctions. Sentence-level only — that's the contrast with the LLM segmenter.
- **Don't** add ecological-validity filters or per-node reweighting to ablation results. Report on the full dev set as-is, same as the existing baseline.
- **Don't** modify the structured pipeline to "be fair" to the ablations. The structured pipeline is the artifact being defended; the ablations bend around it.

## Reference files

- `safety/critic.py` — production critic; line references: META filter at :296, UNCLASSIFIED routing at :397-405, sanity check at :304-353
- `safety/classifier.py` — production classifier (S1); `CLINICAL_CODER_PROMPT` body to be reused in Ablation A
- `safety/graph_definitions.py` — `SEVERITY_PRIORITY` source of truth (also defined in `critic.py:33`)
- `experiments/run_benchmark.py` — existing benchmark harness; extend with new flags for ablation conditions
- `data/benchmarks/dev_dataset.json` — 480-case dev set
- `docs/planning/project_postfix_unsafe_miss_decomposition.md` — S1 vs S2 error-profile differences (justifies S1-only scope)
