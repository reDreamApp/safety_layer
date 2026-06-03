# Thesis Status

Status: handoff document for continuing the ReDream AI master's thesis in a new context.

## How to Continue in a New Context

Start by reading these files:

1. `docs/thesis/latex_writing_guide.md`
2. `docs/thesis/thesis_status.md`
3. `thesis/main.tex`
4. The chapter currently being edited, usually `thesis/chapters/03-safety-layer.tex`

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

Section 3.1 is in good draft shape:

- `3.1 A Clinical Safety Ontology for IRT Rescripting`
- `3.1.1 Ontology Category Set`
- `3.1.2 Category Attributes and Severity Levels`
- `3.1.3 Corrective Mappings Between Maladaptive and Adaptive Categories`
- `3.1.4 Graph Representation of Correction Relationships`

The prose in 3.1 intentionally explains the concept in plain language before getting technical. It currently avoids over-justifying the graph representation.

Section 3.2 onward is mostly placeholders and should be drafted next.

Recommended next writing step:

- Draft `3.2 Ontology Development and Clinical Validation`, starting with `3.2.1 Literature-Based Construction`.
- Then write `3.2.2 Clinical Rationale and Ontology Boundaries`, where the clinical rationale behind severity levels and corrective mappings can be explained more fully.
- Then write `3.2.3 Expert Review Process`, including Dr. Annika Gieselmann's ontology validation.

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
- Decide how to handle or explain stale pre-change end-to-end eval outputs that used `AVOIDANCE` as moderate.
- Regenerate the final end-to-end evaluation dataset after the current severity/constraint behavior is settled.
- Continue ensuring every generated figure matches the current implementation before inserting it into LaTeX.
