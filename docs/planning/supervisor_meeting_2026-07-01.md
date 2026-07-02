# Supervisor Meeting Notes - 2026-07-01

Purpose: give a compact state-of-thesis overview, check whether the current thesis structure and emphasis are still good, and clarify the remaining methodological details before final writing. The thesis proposal itself is already validated; the meeting is about whether the changed details are integrated coherently.

## One-Minute Status

The thesis implementation is largely complete. The clinically grounded safety layer has:

- a validated ontology / knowledge graph for maladaptive and adaptive IRT rescripting patterns,
- an LLM-based entity linker / classifier,
- a critic pipeline that segments user input, classifies segments, triages risk, and synthesizes corrective constraints,
- integration into the IRT chatbot,
- component-level benchmark results on the full dev set,
- pilot system-level A/B results,
- an expert rating app/export prepared for Phase 4 evaluation.

The remaining thesis work is mainly evaluation framing, expert annotation, figure polishing, and writing.

## Main Results To Present

### 1. Component-Level Safety Classification Is Strong

Post-fix full dev benchmark: 480 rows total, 420 safety-evaluable rows.

| Metric | S1 baseline | S1 consistency | S2 baseline | S2 consistency |
|---|---:|---:|---:|---:|
| Safety accuracy | 97.86% (411/420) | 97.86% (411/420) | 98.10% (412/420) | **98.81% (415/420)** |
| Unsafe recall | **99.44% (179/180)** | **99.44% (179/180)** | **99.44% (179/180)** | 98.33% (177/180) |
| Node accuracy | 78.85% | 78.66% | 79.62% | **80.58%** |
| Error rows | 0 | 0 | 0 | 0 |

Interpretation:

- All configurations are strong on the main safety task.
- S2 consistency gives the best safety accuracy and node accuracy.
- S2 consistency costs one additional unsafe miss compared with S1/S2 baseline (3 misses instead of 1), so this is a precision/recall trade-off.
- In a safety-critical framing, S1 baseline / S1 consistency remain attractive because unsafe recall is the key metric.

Suggested verbal framing:

> The safety layer reaches high component-level performance. The most safety-conservative configuration keeps unsafe recall at 99.44%, while the best overall accuracy comes from S2 with semantic consistency. The remaining decision is how to frame that trade-off in the thesis.

Source: `docs/planning/System2_CoT_Findings.md` section 11.2.

### 2. Semantic Consistency Is Useful Mainly For S2 / CoT Uncertainty

Earlier analysis showed that logprob confidence is weak for the S2 chain-of-thought classifier because the classification token is conditioned on the already-written reasoning chain.

Key point:

- For S2, semantic consistency recovers a useful uncertainty signal.
- For S1, logprob confidence is already adequate and cheaper.
- This motivates, but does not validate, an ensemble-style future-work design: S1 as primary safety gate, S2 consistency as a possible second opinion. A good operational threshold was not established, so this should stay future work rather than a thesis result.

Suggested verbal framing:

> The UQ contribution is not "consistency always improves accuracy." The more precise finding is that consistency is especially useful when token logprobs stop being meaningful, as in the CoT classifier.

### 3. Segmenter Stability Was A Real Bottleneck, Now Mostly Controlled

Earlier full-set consistency runs showed regressions caused by upstream segmentation drift, not by vote aggregation. The root cause was heterogeneous OpenRouter backend routing. Switching the segmenter to Scaleway-direct `MISTRAL_NEMO` with `temperature=0` stabilized the previously problematic cases.

Important for the meeting:

- This is the main argument for not evaluating segmentation as a separate thesis target.
- Segmentation is still documented as a critical internal dependency and limitation.
- The thesis can honestly say segmentation instability was diagnosed and mitigated.

Suggested verbal framing:

> I am evaluating the safety critic end-to-end rather than treating segmentation as an independently annotated task. Segmentation errors matter, and I document them, but the thesis claim is about the critic's final clinical verdict and corrective signal.

### 4. Integration Testing Found Useful But Uneven System-Level Effects

Pilot A/B constraint-redirect evaluation:

- 33 maladaptive scenarios.
- Control: base chatbot response.
- Treatment: chatbot response with safety constraint injected.
- Judged with LLM-as-judge rubric as a pilot before expert evaluation.

Main-tier v2 headline:

| Condition | Strong redirect | Partial redirect | Absent | Echoes maladaptive |
|---|---:|---:|---:|---:|
| Control | 4.0% | 96.0% | 0.0% | 0.0% |
| Treatment | 32.0% | 68.0% | 0.0% | 0.0% |
| Delta | +28.0 pp | -28.0 pp | +0.0 pp | +0.0 pp |

Multipart supplementary tier:

| Condition | Strong redirect | Partial redirect | Absent | Echoes maladaptive |
|---|---:|---:|---:|---:|
| Control | 0.0% | 100.0% | 0.0% | 0.0% |
| Treatment | 87.5% | 12.5% | 0.0% | 0.0% |
| Delta | +87.5 pp | -87.5 pp | +0.0 pp | +0.0 pp |

Important caveat:

- These are pilot LLM-judge results, not final expert ratings.
- The effect is asymmetric: strongest lift for AVOIDANCE and INTERRUPTION, weaker or negative for nodes already covered by the base prompt, especially VIOLENT_REVENGE.

Suggested verbal framing:

> The integration result is not a simple "safety layer always improves the chatbot" story. It improves explicit redirects especially where the base prompt is weak, but it can also reduce contextual richness where the base prompt already handles the failure mode.

Sources: `data/integration_eval/integration_eval_summary_v2.md`, `docs/planning/integration_eval_notes.md`.

### 5. Integration Limitations Are Thesis Findings, Not Just Bugs

End-to-end integration exposed issues that are important to document:

- Redirect loop: repeated maladaptive user proposals can cause repeated similar redirects.
- Stage-transition blocking: safety constraints can interfere with moving from rewriting to summary.
- Summary sanitization vs user agency: safe summaries may become too unfaithful to the user's narrative.
- Classification accuracy does not automatically imply good therapeutic flow.

Suggested verbal framing:

> One contribution is showing the gap between an accurate safety classifier and a therapeutically smooth integrated chatbot. Most safety-layer evaluations stop at classification; this thesis can document what breaks at integration time.

## Current Expert Evaluation State

Ontology validation:

- Dr. Annika Gieselmann reviewed/commented on the ontology document, but did not fill out the structured questionnaire.
- Need to clarify how to frame this in the thesis: probably as qualitative expert feedback / ontology review rather than a completed questionnaire-based validation.
- Ask whether her document comments are sufficient evidence for saying the ontology was clinically reviewed, and how explicitly the missing questionnaire should be disclosed.

Prepared:

- Expert system-eval app/export exists: `data/test_eval/system_eval_app.html`.
- Current export has 86 rows:
  - 43 control,
  - 43 treatment,
  - tiers: main unsafe, safe regression, robustness, multipart.
- Rating rubric covers clinical acceptability, redirect quality, maladaptive endorsement, appropriate distress validation, and free-text notes.

Still needed:

- External expert ratings from Dr. Annika Gieselmann and/or Katharina Lueth.
- Decide what is acceptable if only one expert has time.

Suggested fallback language if only one expert completes it:

> With one expert, the thesis should frame the evaluation as expert clinical review / external plausibility validation, not as robust inter-rater reliability.

## Graphics To Show In LaTeX Draft

Open the LaTeX draft (`thesis/main.pdf`) for graphics rather than duplicating them here. Ask for feedback on whether these are the right core figures:

- Architecture / 3-block pipeline: graph, classifier, critic.
- Ontology diagram: maladaptive nodes, adaptive MMS nodes, correction edges.
- Benchmark results table or bar chart.
- UQ comparison: logprob vs semantic consistency.
- Integration A/B results by condition and node.
- Example case walkthrough: user input -> segmenting -> node classification -> safety verdict -> corrective constraint.
- Limitation figure: component-level accuracy vs conversation-flow failure modes.

Practical question:

> Are these figures enough to carry the argument, or should I reduce/expand the planned figure set?

## Proposed Thesis Narrative

Suggested central claim:

> This thesis presents a clinically grounded neuro-symbolic safety layer for IRT nightmare rescripting. The layer produces auditable clinical verdicts and corrective directions for maladaptive rescripting content. Component-level benchmarks show high safety accuracy and unsafe recall, while integration experiments reveal both the promise and the limits of constraint-based steering in a live therapeutic chatbot.

Important nuance:

- Do not overclaim that the integrated chatbot is solved.
- Do claim that the safety layer provides a clinically traceable detection and correction signal.
- Treat integration friction as evidence that safety classification and therapeutic dialogue management are separate challenges.

## Questions For Supervisor

### Evaluation Scope

1. Is it acceptable that I evaluate segmentation indirectly through the final safety verdict, rather than running a separate segmentation annotation study?
2. Should segmentation be framed as an internal implementation step, a limitation, or a separate subcomponent with light qualitative analysis?
3. Is the component-level benchmark plus pilot integration evaluation enough, assuming expert ratings are limited?

### Expert Annotation

4. How should I frame Annika's ontology feedback, given that she commented on the ontology document but did not complete the structured questionnaire?
5. Is it acceptable to describe the ontology as clinically reviewed / expert-reviewed, as long as I am transparent about the format of the feedback?
6. If only one external expert completes the rating sheet, can I present it as expert validation rather than IRR?
7. What minimum expert-eval sample size would be acceptable for the thesis?
8. Should the expert evaluation focus on all 86 prepared rows, or would a smaller high-value subset be methodologically cleaner?

### Results Framing

9. Should I present the rough benchmark and pilot integration results now, explicitly marked as preliminary where appropriate?
10. How should I frame the S2 consistency trade-off: best safety accuracy, but slightly lower unsafe recall?
11. Is it acceptable to mention S1-primary + S2-consistency as a future-work direction, while explicitly saying that no reliable operational threshold was found?

### Integration Findings

12. Should the integration issues be presented as limitations only, or as a positive contribution because they show the classification-to-dialogue gap?
13. Is it methodologically sound not to fix the base chatbot flow, because changing it would confound the safety-vs-baseline comparison?
14. Should the thesis include the small constraint tweak pilot, or keep it as supplementary / future work?

### Writing And Scope

15. Which chapters/results are essential for a defensible master's thesis, and which can move to future work?
16. Are the current planned figures sufficient, or should I reduce them to fewer stronger figures?
17. What is the strongest thesis contribution from his perspective: ontology, safety critic accuracy, uncertainty analysis, or integration findings?

## Meeting Goal

The main decision needed from this meeting:

> Is the current thesis structure and argument emphasis still right, given the updated results and evaluation constraints?

Secondary decision:

> Which changed details should be integrated into the main thesis argument, and which should be treated as limitations, supplementary material, or future work?
