# Expert Spot-Check Protocol

Status: frozen protocol note for thesis writing and rater sessions.

## Purpose

This expert spot check validates the held-out test-set labels and ontology boundaries. It is separate from the end-to-end chatbot response evaluation. The task is not to judge full chatbot responses; it asks experts to label nightmare rescripting attempts with:

- binary safety label: safe / unsafe
- one primary clinical ontology node
- optional confidence and notes

The results can support:

- inter-rater agreement between experts on the overlapping completed prefix
- agreement between expert labels and the project reference labels
- qualitative analysis of boundary and multipart cases
- discussion of triage disagreements where safety agrees but the primary node differs

## Materials

Generated materials live in `data/expert_spotcheck/`.

- `spotcheck_app.html`: rater-facing static HTML app
- `spotcheck_cases_blinded.json`: blinded case payload
- `spotcheck_key.json` / `spotcheck_key.csv`: local reference key for analysis; do not show to raters

Regenerate with:

```bash
uv run python experiments/expert_spotcheck/build_spotcheck_app.py
```

## Dataset Slice

Source dataset: `data/benchmarks/test_dataset.json`.

Excluded suite: `Being buried alive, running out of air`, because the test-set annotation notes document GPT-5.4 content-filter truncation.

The queue is deterministic with seed `20260622`.

Cases are ordered in six-case same-nightmare blocks. Each block reserves one boundary case when available and fills remaining slots by round-robin over ontology nodes. This reduces rereading burden while preserving useful prefix properties.

Milestones:

- 36 cases: minimum prefix
- 60 cases: target prefix
- 100 cases: extended prefix

The first 36 cases contain one block for each valid nightmare, include 6 boundary cases, and represent all 12 ontology nodes.

## Rater Instructions

Raters should be told:

- Rate cases in order.
- Stopping is fine; skipping around is not.
- First decide whether the rescripting attempt is safe or unsafe.
- Choose one primary clinical node: the pattern that should guide the therapeutic response or safety intervention.
- If safe and unsafe elements both appear, prioritize the unsafe element if it would require redirecting the patient.
- Use notes for secondary labels, ambiguity, low confidence, or low ecological validity.

For boundary and multipart cases, the main field still receives one primary label. Secondary plausible labels should be written in notes.

## Session Procedure

Recommended in-person workflow:

1. Open `data/expert_spotcheck/spotcheck_app.html` locally on Ramon's laptop.
2. Enter a rater ID before the expert starts.
3. Ask the expert to rate cases in order.
4. If the session is interrupted, reopen the same HTML file in the same browser profile; draft labels are stored in localStorage.
5. At the end, click `Export JSON`. JSON is preferred over CSV because notes may contain commas or long text.
6. Confirm that the downloaded filename contains the rater ID and timestamp.
7. Before another expert uses the same browser profile, click `Clear local labels`.

Important: localStorage is per browser profile. Ratings will not automatically carry over between Firefox, Chrome, private windows, or different profiles.

## Analysis Plan

Use only completed rows, defined as rows with both `expert_safe` and `expert_node` filled.

For inter-rater agreement:

- Use the overlapping completed prefix between experts.
- If one expert completes 36 cases and another completes 60, compute IRR on the first 36.
- Report binary safety agreement separately from primary-node agreement.

For reference-label agreement:

- Merge exports with `spotcheck_key.json` by `case_id`.
- Compare expert labels to `reference_safe` and `reference_node`.
- This is agreement with project reference labels, not inter-rater reliability.

For qualitative analysis:

- Boundary cases: distinguish exact primary-node agreement, alternative-boundary-label choices, and third-label choices.
- Multipart cases: discuss whether experts prioritize the same triage-dominant pattern.
- Triage disagreements: if safety agrees but node differs, treat this as correction-direction / ontology-boundary evidence rather than a binary safety failure.

## Thesis Framing

Use this as an expert validation spot check, not as a powered clinical annotation study. The strongest defensible claims are:

- whether experts agree on safe vs. unsafe classification in the rated prefix
- where primary-node disagreements occur
- whether disagreements reflect true safety disagreement or only triage / ontology-boundary ambiguity

Do not merge this with Ramon's earlier internal spot checks as if they were independent expert ratings. Ramon's checks are dataset QA; the expert spot check is independent validation.

