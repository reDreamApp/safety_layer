## 1. Current Thesis Structure

Working structure:

1. Introduction
2. Background: IRT, maladaptive rescripting, adaptive mastery, AI safety / neuro-symbolic systems
3. Safety Layer: ontology, classifier, critic pipeline, integration
4. Evaluation: component benchmark, uncertainty analysis, integration/system-level evaluation, expert review
5. Discussion: interpretation, limitations, clinical implications, future work
6. Conclusion

## 3. Ontology And Expert Feedback

Current state:

- The ontology was reviewed/commented on by Dr. Annika Gieselmann.
- She did not complete the structured questionnaire.
- The ontology itself is still a core thesis artifact.

Question:

> Can I frame this as qualitative expert review / clinical feedback, while transparently stating that the structured questionnaire was not completed?

## 4. Component-Level Benchmark Results

Full post-fix dev benchmark:

| Metric          | S1 baseline | S1 consistency | S2 baseline | S2 consistency |
| --------------- | ----------: | -------------: | ----------: | -------------: |
| Safety accuracy |      97.86% |         97.86% |      98.10% |     **98.81%** |
| Unsafe recall   |  **99.44%** |     **99.44%** |  **99.44%** |         98.33% |
| Node accuracy   |      78.85% |         78.66% |      79.62% |     **80.58%** |

Interpretation:

- The safety critic performs strongly on the main safety task.
- S2 consistency has the best safety accuracy and node accuracy.
- S1/S2 baseline preserve the best unsafe recall.
- The S2 consistency result is a trade-off, not a simple win.

Question:

> Should the thesis prioritize unsafe recall as the main safety metric, even when another configuration has slightly better overall accuracy?

## 5. Uncertainty Analysis

Current finding:

- S1 logprob confidence is usable.
- S2 logprob confidence is weak because the final classification token is conditioned on the generated reasoning.
- Semantic consistency gives a more useful uncertainty signal for S2.
- However, no reliable operational threshold was established for an ensemble system.

Key numbers:

| Condition      | Uncertainty signal         | Safety AUROC | Node AUROC |
| -------------- | -------------------------- | -----------: | ---------: |
| S1 baseline    | Log-probability confidence |         0.77 |       0.85 |
| S1 consistency | Agreement ratio            |         0.62 |       0.66 |
| S2 baseline    | Log-probability confidence |         0.62 |       0.61 |
| S2 consistency | Agreement ratio            |         0.60 |       0.71 |

Threshold caveat:

- For S1, a 0.90 confidence threshold would flag 43 cases but catch only 1/9 safety errors.
- For S1, a 0.95 threshold would flag 71 cases and catch 4/9 safety errors.
- For S2, a 0.80 threshold would flag 160 cases while catching 5/8 safety errors.
- Conclusion: useful audit metadata, but not enough for a hard clarification/escalation cutoff yet.

## 6. Pipeline Ablations

S1 ablation results on scored development benchmark:

| Condition          | Safety acc. | Unsafe recall | Node acc. | False alarms / missed unsafe |
| ------------------ | ----------: | ------------: | --------: | ---------------------------: |
| Full S1 pipeline   |      97.86% |        99.44% |    78.10% |                        8 / 1 |
| Stage-merge        |      98.33% |        98.33% |    86.90% |                        4 / 3 |
| No segmentation    |      98.33% |        96.11% |    83.81% |                        0 / 7 |
| META filtering off |      95.48% |        99.44% |    75.71% |                       18 / 1 |
| Naive splitter     |      97.38% |        98.89% |    79.05% |                        9 / 2 |

Supplementary multi-maladaptive slice:

| Condition          | Primary-node acc. | Secondary-node recall | Any-maladaptive recall |
| ------------------ | ----------------: | --------------------: | ---------------------: |
| Full S1 pipeline   |           100.00% |                97.14% |                100.00% |
| Stage-merge        |           100.00% |               100.00% |                100.00% |
| No segmentation    |            71.43% |                17.14% |                 88.57% |
| META filtering off |           100.00% |                97.14% |                100.00% |
| Naive splitter     |            71.43% |                17.14% |                 88.57% |

Interpretation:

- META filtering mainly reduces false alarms from conversational/meta material.
- No segmentation can look good on aggregate accuracy, but misses more unsafe cases.
- Explicit segmentation matters most when multiple maladaptive patterns occur in one turn.
- Stage-merge is competitive and improves node accuracy, but loses unsafe recall on the main benchmark.
- Ablations support the full pipeline as a conservative default, not as the only possible architecture.

Question:

> Should the ablations be framed as evidence for the chosen pipeline, or mainly as diagnostic evidence about trade-offs and failure modes?

## 7. Segmentation Evaluation

Current framing:

- Segmentation is evaluated indirectly through the final critic verdict.
- I plan to discuss segmentation qualitatively, using observed error cases and pipeline behavior, but not as a systematic standalone segmentation evaluation.
- A separate segmentation annotation study was not performed.

Question:

> Is indirect evaluation through the final safety verdict acceptable, with segmentation discussed qualitatively as an internal dependency, error source, and limitation?

## 8. Integration / System-Level Findings

Pilot A/B constraint-redirect evaluation:

| Condition | Strong redirect | Partial redirect | Absent | Echoes maladaptive |
| --------- | --------------: | ---------------: | -----: | -----------------: |
| Control   |            4.0% |            96.0% |   0.0% |               0.0% |
| Treatment |           32.0% |            68.0% |   0.0% |               0.0% |

Supplementary multipart tier:

| Condition | Strong redirect | Partial redirect | Absent | Echoes maladaptive |
| --------- | --------------: | ---------------: | -----: | -----------------: |
| Control   |            0.0% |           100.0% |   0.0% |               0.0% |
| Treatment |           87.5% |            12.5% |   0.0% |               0.0% |

Interpretation:

- The safety constraint improves explicit redirect quality in some cases, especially AVOIDANCE and INTERRUPTION.
- Effects are uneven across nodes.
- VIOLENT_REVENGE is already partly covered by the base prompt, so the safety layer adds less and can reduce contextual specificity.
- The LLM-judge results are pilot results, not final expert ratings.

Question:

> Should these integration findings be treated as a main result, a pilot study, or mostly as limitations/future work?

## 9. Known Integration Limitations

Important findings:

- Redirect loop after repeated maladaptive proposals.
- Safety constraint can block stage transitions.
- Summary generation can become safe but unfaithful to the user's narrative.
- Correct classification does not guarantee good therapeutic dialogue.

## 10. Expert System Evaluation

Prepared:

- Expert rating app/export: `data/test_eval/system_eval_app.html`
- 86 rows total:
  - 43 control
  - 43 treatment
  - main unsafe, safe regression, robustness, multipart tiers
- Rating dimensions:
  - clinical acceptability
  - redirect quality
  - maladaptive endorsement
  - appropriate distress validation
  - free-text notes

Open issue:

- Two experts would allow stronger comparison.
- One expert may be the realistic fallback.

Question:

> If only one expert completes the evaluation, can this be presented as expert clinical review rather than inter-rater reliability?

## 11. Proposed Main Story For The Thesis

Possible final narrative:

> The safety layer is successful as an auditable clinical detection and correction component under controlled synthetic evaluation conditions. It performs strongly in component-level evaluation and provides clinically traceable verdicts. Its integration into a live IRT chatbot shows promising but uneven steering effects, and reveals that therapeutic flow requires additional dialogue-management mechanisms beyond classification. The main limitation is that the benchmark and system-level cases are synthetic, so performance on more ecologically valid IRT material remains an open question.

Question:

> Is this story balanced enough, or should the thesis argue more strongly for one contribution over the others?

## Decisions Needed

1. Is the structure alright?
2. Is the main contribution framed correctly?
3. Is indirect segmentation evaluation acceptable?
4. How should Annika's ontology feedback be described?
5. What is the minimum acceptable expert-eval fallback?
6. Should pilot integration results be central or supplementary?
7. Which findings belong in the main results chapter vs discussion/future work?
