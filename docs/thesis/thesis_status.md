# Thesis Status

Status: handoff document for continuing the ReDream AI master's thesis in a new context.

## How to Continue in a New Context

Start by reading these files:

1. `docs/thesis/latex_writing_guide.md`
2. `docs/thesis/thesis_status.md`
3. `docs/thesis/expert_spotcheck_protocol.md` if working on expert validation or Chapter 4
4. `thesis/main.tex`
5. The chapter currently being edited, usually `thesis/chapters/03-safety-layer.tex`

Good startup prompt:

```text
Please continue helping me write my thesis. First read:
- docs/thesis/latex_writing_guide.md
- docs/thesis/thesis_status.md
- thesis/main.tex
- thesis/chapters/03-safety-layer.tex

Use the writing guide for style and structure. Keep the thesis readable and not overly technical. Before editing LaTeX, briefly explain proposed wording changes unless I ask you to edit directly.
```

Build command:

```bash
cd thesis
make pdf
```

The compiled PDF is saved to `thesis/build/main.pdf`.

## Current Writing Direction

The thesis should be readable for a broad academic audience, not only for engineers. Prefer clear, direct prose over dense technical justification.

Main framing:

- The thesis argues for a protocol-aware safety layer for AI-assisted Imagery Rehearsal Therapy (IRT).
- It does not claim clinical efficacy, treatment readiness, or autonomous therapy.
- The strongest claim is that the system provides protocol-specific detection, redirection signals, uncertainty information, and auditability.

Important terminology:

- Use `rewriting action` for an action, reaction, or change proposed by the client while rewriting the nightmare.
- Distinguish frightening dream content from unsafe rewriting actions.
- Neutral/context categories are not rewriting actions.
- The graph is a modelling and communication representation, not a computational necessity.

## Current Chapter State

The active chapter is `thesis/chapters/03-safety-layer.tex`.

Chapter 3 is now in full first-draft shape:

- `3.1 A Clinical Safety Ontology for IRT Rescripting`
- `3.1.1 Ontology Category Set`
- `3.1.2 Category Attributes and Severity Levels`
- `3.1.3 Corrective Mappings Between Maladaptive and Adaptive Categories`
- `3.1.4 Graph Representation of Correction Relationships`
- `3.2 Ontology Development and Expert Review`
- `3.3 System Overview and Integration Point`
- `3.4 LLM-Based Ontology Classification`
- `3.5 Safety Critic Pipeline`
- `3.6 Uncertainty Estimation and Risk Signaling`
- `3.7 Architectural Trade-Offs and Limitations`

The prose intentionally explains each concept in plain language before getting technical. It currently avoids over-justifying the graph representation and keeps the claims limited to protocol-aware detection, redirection, uncertainty information, and auditability.

Chapter 3 no longer contains `\todo{}` placeholders.

Recommended next writing step:

- Review Chapter 3 for flow, figure placement, and consistency with the current implementation.
- Then move to Chapter 4 evaluation writing, especially the benchmark setup, primary-node metric explanation, and S1/S2 results.

## Ontology Decisions

The ontology has:

- Five adaptive mastery categories:
  - `BEHAVIORAL_MASTERY`
  - `SOCIAL_MASTERY`
  - `ENVIRONMENTAL_MASTERY`
  - `EMOTIONAL_MASTERY`
  - `MYTHICAL_MASTERY`
- Five maladaptive rewriting-action categories:
  - `AVOIDANCE`
  - `INTERRUPTION`
  - `VIOLENT_REVENGE`
  - `SUPPRESSION`
  - `TRAUMA_REPLAY`
- Two neutral categories:
  - `NARRATIVE_SETTING`
  - `AFFECT_EXPRESSION`
- One operational fallback:
  - `UNCLASSIFIED`

Key distinction:

- `NARRATIVE_SETTING` and `AFFECT_EXPRESSION` are not rewriting actions.
- `UNCLASSIFIED` is not a clinical category; it is a fallback for clarification.

## Severity Decisions

Current implementation and thesis writing are aligned:

- `AVOIDANCE`: high
- `INTERRUPTION`: high
- `SUPPRESSION`: high
- `VIOLENT_REVENGE`: critical
- `TRAUMA_REPLAY`: critical

Severity is an internal triage/risk signal, not a diagnosis.

Important nuance:

- `AVOIDANCE` is high severity because it is a maladaptive rewriting action and should not be validated.
- It still has lower triage priority than interruption, suppression, violent revenge, and trauma replay when multiple maladaptive actions appear in one input.
- In implementation, triage ordering and severity label are related but not identical concepts. `SEVERITY_PRIORITY` decides which maladaptive finding becomes the primary correction; `_get_severity_label()` decides the label used in the constraint message.

Practical implication of changing avoidance from moderate back to high:

- Classifier results and safe/unsafe detection benchmarks are not affected.
- Correction mappings are not affected.
- End-to-end generated responses can be affected because pure avoidance inputs now receive the stricter `NO_VALIDATE` constraint.
- End-to-end evaluation should be regenerated after this change.

## Evaluation Metric Note

Important for Chapter 4:

- The benchmark datasets label each test case with `expected_safe` and, where applicable, one case-level `expected_node`.
- They do not contain gold segment boundaries or per-segment labels.
- Node accuracy in `experiments/run_benchmark.py` is therefore strict **primary-node accuracy** at the test-case level: it compares the critic's final `result.node_id` with the case's `expected_node`.
- For multipart cases, `expected_node` is the node that should dominate after triage, not a complete list of all nodes present in the input.
- Segment predictions are logged in `segments` / `segments_json` and can support qualitative error analysis, but current quantitative metrics do not measure whether every internal segment was segmented and labelled correctly.
- This is acceptable if described honestly as an end-to-end critic evaluation. Manual gold segmentation for all benchmark cases would be a separate, much larger annotation task and can be named as future work or a limitation.
- Neutral nodes were included in the benchmark (`AFFECT_EXPRESSION`, `NARRATIVE_SETTING`). They count as safe in the binary safety task, but strict node-level errors can occur when affect expression is classified as adaptive emotional mastery; that is usually a fine-grained category error rather than a safety error.
- Chapter 4 should more explicitly describe how data was generated from `experiments/generate_dataset.py`: scenario themes -> nightmare contexts -> category-targeted rewriting actions -> boundary cases -> multipart cases -> prompt revisions after QC findings.
- Boundary cases were planned deliberately, not discovered accidentally. They target six predefined clinical boundaries: `BEHAVIORAL_MASTERY` vs `VIOLENT_REVENGE`, `AVOIDANCE` vs `AFFECT_EXPRESSION`, `EMOTIONAL_MASTERY` vs `SUPPRESSION`, `NARRATIVE_SETTING` vs `TRAUMA_REPLAY`, `BEHAVIORAL_MASTERY` vs `AVOIDANCE`, and `BEHAVIORAL_MASTERY` vs `INTERRUPTION`.

## Dataset Quality Notes for Chapter 4

Development set quality control:

- The dev-set spot-check audit is `data/benchmarks/spot_check_log.json`.
- It sampled 36 labeled dev cases (3 per ontology node, seed 42; 36/420 labeled cases = 8.6%).
- Agreement with generated labels was 33/36 (91.7%).
- All three disagreements were `AFFECT_EXPRESSION` cases that Ramon judged better as unsafe `TRAUMA_REPLAY`.
- Thesis implication: dev-set `AFFECT_EXPRESSION` metrics should be interpreted cautiously. Some apparent false positives where the critic flags `TRAUMA_REPLAY` may reflect synthetic label noise rather than clinical classifier error.
- Do not silently relabel the dev benchmark unless creating a separate corrected-dev analysis. Instead, keep the original benchmark numbers and describe this as a known label-noise/ecological-validity limitation.

Held-out test set mitigation:

- The test-set annotation log is `data/benchmarks/test_annotation_log.json`.
- All valid `AFFECT_EXPRESSION` cases in the test set were manually reviewed by Ramon after excluding the buried-alive suite.
- In the test set, the remaining concern is mostly ecological validity and fine-grained safe-node overlap with `EMOTIONAL_MASTERY`, not a clear binary safety disagreement with `TRAUMA_REPLAY`.
- This supports using the test set and expert spot-check as the final validation layer rather than over-interpreting dev-set affect-expression errors.

`AFFECT_EXPRESSION` / `EMOTIONAL_MASTERY` sensitivity:

- Treat this honestly as an ontology/prompt-design limitation. The post-fix generation prompt for `AFFECT_EXPRESSION` requires emotional shift, which makes many generated examples read like `EMOTIONAL_MASTERY`.
- Best framing: `AFFECT_EXPRESSION` is useful as a neutral segment label, but weak as a standalone primary rescripting category. In real IRT, patients usually express feelings together with an adaptive or maladaptive action.
- If `AFFECT_EXPRESSION` and `EMOTIONAL_MASTERY` are collapsed for scoring:
  - S1 consistency dev node accuracy: 328/420 (78.1%) -> 345/420 (82.1%).
  - S2 consistency dev node accuracy: 336/420 (80.0%) -> 361/420 (86.0%).
  - Post-fix held-out test CSV node accuracy: 220/273 (80.6%) -> 230/273 (84.2%).
- This mainly affects strict primary-node accuracy and ontology granularity, not the binary safety conclusion.

Suggested Chapter 4 wording:

> A manual audit of the development set identified a systematic weakness in isolated `AFFECT_EXPRESSION` examples: some generated cases labeled as safe affect expression were better interpreted as `TRAUMA_REPLAY`, because they reproduced the original fear or helplessness state without a meaningful rescripting change. This label noise may cause a small number of clinically plausible unsafe classifications to appear as false positives in the development benchmark. The held-out test set mitigated this risk by manually reviewing all valid `AFFECT_EXPRESSION` cases; there, the remaining limitation was primarily ecological validity and overlap with `EMOTIONAL_MASTERY`, rather than binary safe/unsafe disagreement.

## Graph Figure

Current ontology graph files:

- `figures/generate_clinical_ontology_graph.py`
- `figures/clinical_ontology_graph.pdf`
- `figures/clinical_ontology_graph.png`
- `figures/clinical_ontology_graph.svg`

The figure is included in `3.1.4`.

Current graph design:

- Maladaptive rewriting actions are shown on the left.
- Adaptive mastery categories are shown on the right.
- Context and fallback categories are separated at the bottom.
- Primary, secondary, and tertiary correction links use different line styles.
- Severity is shown through color/border and legend, not repeated text inside the nodes.
- Adaptive nodes do not show MMS subscale numbers because the numbers did not add useful information in the figure.

Regenerate the graph with:

```bash
uv run python figures/generate_clinical_ontology_graph.py
```

Then rebuild the PDF with:

```bash
cd thesis
make pdf
```

## Current Verification

Recent focused tests passed after severity alignment:

```bash
uv run pytest tests/test_safety_module.py::test_knowledge_graph tests/test_constraint_synthesis.py::test_no_validate_block_when_empty_adaptive_high_or_critical
```

Known warning:

- `tests/test_safety_module.py::test_knowledge_graph` returns a bool and triggers a pytest warning. This is an old test style issue and not related to the thesis writing changes.

LaTeX build status:

- `make pdf` succeeds.
- Existing overfull hbox warnings occur in Chapter 3 because long `\texttt{...}` node names do not wrap easily. They are not caused by the ontology graph.

## Figures and Placeholders

Current completed or usable Chapter 3 figure:

- `fig:clinical-safety-ontology`: ontology graph in 3.1.4.

Remaining Chapter 3 figure placeholders:

- system overview and safety-layer feedback loop
- optional System 1 vs System 2 classifier comparison
- safety critic pipeline architecture
- worked end-to-end example

Existing generated figure assets under `figures/` may be useful, but some are stale and should be checked before insertion. In particular, older worked-example or safety-pipeline figures may still show avoidance as moderate.

## Writing Style Decisions

Preferred prose:

- readable, direct, and calm
- concept first, implementation second
- avoid overstating clinical or computational claims
- avoid defending choices that can simply be described as practical modelling decisions

Avoid:

- making the graph sound necessary for computation
- claiming that scary dream content itself is unsafe
- presenting severity labels as diagnosis
- overusing words like `directed` and `redirected` when plain phrasing works better

Good phrasing patterns:

- "The graph representation should be understood as a modelling and communication aid."
- "The relevant question is whether the client's proposed action supports mastery or encourages avoidance, suppression, repetition, or escalation."
- "Neutral categories describe context or affect, but do not trigger corrective redirection on their own."

## Source References to Consult

For clinical rationale and ontology development:

- `docs/clinical/Clinical_Ontology_Scientific_Rationale.md`
- `safety/graph_definitions.py`
- `docs/planning/integration_eval_notes.md`
- `docs/planning/System2_CoT_Findings.md`

For implementation behavior:

- `safety/graph_definitions.py`
- `safety/classifier.py`
- `safety/critic.py`
- `safety/stage_merge_critic.py`
- `tests/test_constraint_synthesis.py`
- `tests/test_safety_module.py`

For writing structure:

- `docs/thesis/latex_writing_guide.md`
- `thesis/main.tex`

## Open TODOs

- Draft Chapter 3.2 clinical development and validation sections.
- Add clinical rationale behind the corrective mappings in 3.2 rather than overloading 3.1.3.
- Replace remaining Chapter 3 figure placeholders with updated figures.
- Expand Chapter 4's dataset-generation methodology, including prompt-driven generation and deliberately planned boundary cases.
- Add Chapter 4 / discussion caveat on `AFFECT_EXPRESSION` as a weak standalone primary category, including the collapse sensitivity numbers above.
- Decide how to handle or explain stale pre-change end-to-end eval outputs that used `AVOIDANCE` as moderate.
- Regenerate the final end-to-end evaluation dataset after the current severity/constraint behavior is settled.
- Continue ensuring every generated figure matches the current implementation before inserting it into LaTeX.
