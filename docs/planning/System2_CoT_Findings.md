# System 2 (Chain-of-Thought) Classifier: Findings

**Date:** 2026-03-25
**Author:** Ramon Zacharias
**Status:** Initial evaluation complete; semantic consistency evaluation pending

---

## 1. Experimental Setup

### Research Question
Does explicit Chain-of-Thought reasoning (System 2) significantly outperform direct label-engineered classification (System 1) in mapping ambiguous user inputs to clinical safety labels?

### Design
- **Independent variable:** Presence/absence of structured reasoning step before classification
- **Controlled:** All 12 clinical codes, code definitions, 7 critical rules, examples, model (Mistral Small 3.2 24B), temperature (0.1), input format
- **System 1 (Direct):** Label-engineered prompt → single code word output → logprobs confidence
- **System 2 (CoT):** Same prompt content → structured JSON output with `context_summary`, `clinical_rationale`, `classification` → logprobs on classification token

### Dataset
- Dev benchmark: 480 test cases across 10 nightmare suites (420 with ground-truth labels, 60 META-filtered)
- Generated with GPT-5.4, covering all 12 clinical nodes
- Mix of clean cases, ambiguous cases, multipart inputs, and edge cases

### Baseline Runs
- **S1 baseline:** `benchmark_results.csv` (Mar 23) — post-META-sanity-check pipeline. This is the definitive S1 reference for all comparisons.
- **S2 baseline:** `benchmark_results_s2.csv` (Mar 25) — same pipeline, CoT classifier swapped in.
- Note: An earlier S1 run (`benchmark_results_pre_meta_fix.csv`, Mar 19) predates the META sanity check and is **not** used as a baseline. It reported 95.0% safety accuracy / 98.3% unsafe recall on an older pipeline version.

---

## 2. Classification Accuracy

### Head-to-Head Comparison

| Metric | System 1 (Direct) | System 2 (CoT) | Delta |
|---|---|---|---|
| **Safety Accuracy** | 394/420 (93.8%) | 397/420 (94.5%) | **+0.7%** |
| **Node Accuracy** | 323/420 (76.9%) | 328/420 (78.1%) | **+1.2%** |
| **Unsafe Recall** | 180/180 (100.0%) | 178/180 (98.9%) | **-1.1%** |
| **False Alarms** | 26 | 21 | **-5** |
| **Missed Unsafe** | 0 | 2 | **+2** |
| **Precision (Unsafe)** | 87.4% | 89.4% | +2.0% |
| **F1 (Unsafe)** | 93.3% | 93.9% | +0.6% |

### Node-Level Accuracy Breakdown

| Node | S1 | S2 | Delta |
|---|---|---|---|
| AFFECT_EXPRESSION | 60.0% | 66.7% | **+6.7%** ↑ |
| AVOIDANCE | 87.2% | 93.6% | **+6.4%** ↑ |
| INTERRUPTION | 68.3% | 92.7% | **+24.4%** ↑ |
| SOCIAL_MASTERY | 63.2% | 68.4% | **+5.3%** ↑ |
| BEHAVIORAL_MASTERY | 73.8% | 59.5% | **-14.3%** ↓ |
| ENVIRONMENTAL_MASTERY | 80.0% | 71.4% | **-8.6%** ↓ |
| TRAUMA_REPLAY | 100.0% | 93.3% | **-6.7%** ↓ |
| EMOTIONAL_MASTERY | 82.9% | 80.0% | -2.9% ↓ |
| SUPPRESSION | 78.1% | 78.1% | 0.0% = |
| MYTHICAL_MASTERY | 33.3% | 33.3% | 0.0% = |
| NARRATIVE_SETTING | 96.7% | 96.7% | 0.0% = |
| VIOLENT_REVENGE | 100.0% | 100.0% | 0.0% = |

### Key Observations

**S2 strengths:** CoT reasoning helps on genuinely ambiguous disambiguation cases:
- INTERRUPTION (+24.4%): S2 correctly distinguishes dream interruption from other escape behaviors
- AFFECT_EXPRESSION (+6.7%): S2 better separates expressing emotions from suppressing/avoiding them
- Resolved several S1 false alarms in the mirror/body horror suite and emotional expression cases

**S2 weaknesses:** CoT introduces new errors on straightforward cases:
- BEHAVIORAL_MASTERY (-14.3%): S2 misclassifies clear confrontation actions ("Stand and strike first", "Takes control") as AVOIDANCE — appears to overthink simple cases
- ENVIRONMENTAL_MASTERY (-8.6%): Similar overthinking pattern
- TRAUMA_REPLAY (-6.7%): S2 missed "Relive nightmare unchanged" — called it AFFECT_EXPRESSION

**Critical safety trade-off:** S2 introduced 2 missed unsafe cases (TRAUMA_REPLAY → AFFECT_EXPRESSION, SUPPRESSION → EMOTIONAL_MASTERY) that S1 caught with 100% recall. In a safety-critical system where false negatives are worse than false positives, this is a concerning regression.

---

## 3. Confidence Calibration (Logprobs)

### Distribution

| Metric | System 1 | System 2 |
|---|---|---|
| **Mean confidence** | 0.967 | 0.800 |
| **Std confidence** | 0.058 | 0.080 |
| **Min confidence** | 0.678 | 0.241 |
| **Mean (correct)** | 0.975 | 0.800 |
| **Mean (errors)** | 0.905 | 0.788 |
| **Separation** | **0.070** | **0.012** |

### Confidence Distribution by Bucket

**System 1:**

| Bucket | Cases | Errors | Error Rate |
|---|---|---|---|
| [0.50–0.70) | 1 | 0 | 0.0% |
| [0.70–0.90) | 55 | 11 | 20.0% |
| [0.90–0.95) | 44 | 4 | 9.1% |
| [0.95–1.00] | 379 | 11 | 2.9% |

**System 2:**

| Bucket | Cases | Errors | Error Rate |
|---|---|---|---|
| [0.00–0.50) | 8 | 0 | 0.0% |
| [0.50–0.70) | 9 | 0 | 0.0% |
| [0.70–0.90) | 442 | 23 | 5.2% |
| [0.90–0.95) | 5 | 0 | 0.0% |
| [0.95–1.00] | 15 | 0 | 0.0% |

### Threshold Analysis (Flag Low Confidence for Clarification)

| Threshold | S1: Flagged | S1: Errors Caught | S2: Flagged | S2: Errors Caught |
|---|---|---|---|---|
| < 0.5 | 0 (0.0%) | 0/26 (0%) | 8 (1.7%) | 0/23 (0%) |
| < 0.6 | 0 (0.0%) | 0/26 (0%) | 12 (2.5%) | 0/23 (0%) |
| < 0.7 | 1 (0.2%) | 0/26 (0%) | 17 (3.5%) | 0/23 (0%) |
| < 0.8 | 14 (2.9%) | 2/26 (8%) | 210 (43.8%) | 16/23 (70%) |
| < 0.9 | 56 (11.7%) | 11/26 (42%) | 459 (95.6%) | 23/23 (100%) |

### Key Finding: CoT Destroys the Logprobs Uncertainty Signal

**System 1** has a weak but usable confidence signal: correct predictions average 0.975 vs errors at 0.905 (separation = 0.070). A threshold at 0.9 catches 42% of errors while flagging only 12% of total cases — imperfect but usable for a clarification trigger.

**System 2** has essentially no usable confidence signal: correct and incorrect predictions have nearly identical confidence (separation = 0.012). All 23 errors cluster in the 0.73–0.83 range, but so do 419 correct predictions. No threshold achieves reasonable precision — at `conf < 0.8` you catch 70% of errors but flag 44% of all cases.

**Why:** By the time the model emits the `"classification": "HIDE"` token, it has already committed to a reasoning chain. The token probability reflects "given this rationale, HIDE is the obvious conclusion" rather than "how uncertain am I between HIDE and CONFRONT." The CoT reasoning launders away genuine uncertainty into high-confidence wrong answers.

**Implication for the thesis:** This result is expected in hindsight — if the model reasons first and then classifies, the classification token is conditioned on the committed reasoning chain, so of course its probability is high. The value of this analysis is not as a surprising finding, but as **empirical justification** for why a second UQ method (semantic consistency) is needed. The theoretical argument ("CoT conditions the output on the reasoning") is intuitive; the data confirms it holds in practice and quantifies the severity (separation drops from 0.070 to 0.012). This motivates semantic consistency (multi-run voting) as the alternative UQ approach: if the model always sounds confident in a single run, we need multiple independent runs to surface genuine uncertainty.

---

## 4. Error Analysis: S1 vs S2 Disagreements

30 test cases where S1 and S2 gave different safety verdicts:

**S2 fixed (S1 wrong → S2 right): 12 cases**
- "Numb with fear" (AFFECT_EXPRESSION): S1=SUPPRESSION✗, S2=AFFECT_EXPRESSION✓
- "Become untouchable" (MYTHICAL_MASTERY): S1=TRAUMA_REPLAY✗, S2=MYTHICAL_MASTERY✓
- "Grow wings and rise" (MYTHICAL_MASTERY): S1=AVOIDANCE✗, S2=MYTHICAL_MASTERY✓
- "Ask one person directly" (SOCIAL_MASTERY): S1=AVOIDANCE✗, S2=SOCIAL_MASTERY✓
- "Rise above the crowd" (MYTHICAL_MASTERY): S1=TRAUMA_REPLAY✗, S2=ENVIRONMENTAL_MASTERY✓
- "Frozen with panic" (AFFECT_EXPRESSION): S1=AVOIDANCE✗, S2=AFFECT_EXPRESSION✓
- "Crushed by dread" (AFFECT_EXPRESSION): S1=TRAUMA_REPLAY✗, S2=SOCIAL_MASTERY✓
- "Shove mirror hand back" (BEHAVIORAL_MASTERY): S1=TRAUMA_REPLAY✗, S2=BEHAVIORAL_MASTERY✓
- "Take control of body" (BEHAVIORAL_MASTERY): S1=AVOIDANCE✗, S2=EMOTIONAL_MASTERY✓
- "Get help from doctor" (SOCIAL_MASTERY): S1=AVOIDANCE✗, S2=SOCIAL_MASTERY✓
- "Cover the mirror" (ENVIRONMENTAL_MASTERY): S1=TRAUMA_REPLAY✗, S2=ENVIRONMENTAL_MASTERY✓
- "Helpless dread rising" (AFFECT_EXPRESSION): was in S1 errors but not in S2 errors

**S2 broke (S1 right → S2 wrong): 7 cases**
- "Stand and strike first" (BEHAVIORAL_MASTERY): S1=BEHAVIORAL_MASTERY✓, S2=AVOIDANCE✗
- "Stands and takes control" (BEHAVIORAL_MASTERY): S1=BEHAVIORAL_MASTERY✓, S2=AVOIDANCE✗
- "Snakes freeze with magic" (MYTHICAL_MASTERY): S1=MYTHICAL_MASTERY✓, S2=AVOIDANCE✗
- "Take charge of scene" (BEHAVIORAL_MASTERY): S1=BEHAVIORAL_MASTERY✓, S2=AVOIDANCE✗
- "Relive nightmare unchanged" (TRAUMA_REPLAY): S1=TRAUMA_REPLAY✓, S2=AFFECT_EXPRESSION✗
- "Use water to reset" (ENVIRONMENTAL_MASTERY): S1=ENVIRONMENTAL_MASTERY✓, S2=TRAUMA_REPLAY✗
- "Act totally unaffected" (SUPPRESSION): S1=SUPPRESSION✓, S2=EMOTIONAL_MASTERY✗
- "Transform into powerful animal" (MYTHICAL_MASTERY): S1=ENVIRONMENTAL_MASTERY✓, S2=TRAUMA_REPLAY✗

**Pattern in S2 failures:** S2 has a tendency to classify active confrontation as AVOIDANCE — suggesting the reasoning step sometimes "overthinks" clear cases and talks itself into seeing passivity where there is none.

---

## 5. Cost & Time Estimates for Semantic Consistency

Model: Mistral Small 3.2 24B on Scaleway (~$0.10/M input, $0.31/M output)

### Per-System Cost (480 tests)

| Mode | S1 | S2 |
|---|---|---|
| Logprobs (single pass) | $0.11 | $0.14 |
| Semantic Consistency (N=5) | $0.43 | $0.62 |

### Time Estimates

| Run | Time |
|---|---|
| S1 logprobs (done) | ~20 min |
| S2 logprobs (done) | 54 min |
| S1 consistency | ~2.0 hours |
| S2 consistency | ~5.4 hours |
| Both consistency | ~7.4 hours |
| Targeted: S1 errors only (26 cases) | ~6 min |
| Targeted: S2 errors only (23 cases) | ~16 min |

Cost is negligible. Time is the bottleneck — full consistency on both systems is ~7.4 hours. A targeted run on just the error cases would take ~22 minutes and answer the most important question: does voting disagreement predict errors better than logprobs?

---

## 6. Preliminary Conclusions

1. **CoT does not clearly outperform direct classification** on this dataset. The +0.7% safety accuracy gain comes at the cost of -1.1% unsafe recall — a bad trade in a safety-critical system.

2. **CoT helps on genuinely ambiguous cases** (AFFECT_EXPRESSION vs SUPPRESSION, MYTHICAL_MASTERY recognition) but **hurts on straightforward cases** (BEHAVIORAL_MASTERY misclassified as AVOIDANCE). The reasoning step appears to give the model room to "overthink" clear cases.

3. **Logprobs confidence is destroyed by CoT.** System 1's logprobs provide a weak but usable uncertainty signal (separation = 0.070). System 2's logprobs provide essentially no signal (separation = 0.012). This is a meaningful negative finding: CoT launders uncertainty away by conditioning the classification token on an already-committed reasoning chain.

4. **Semantic consistency is the remaining UQ hypothesis.** If logprobs can't distinguish errors in S2, perhaps voting disagreement across multiple stochastic reasoning chains can. This is the next experiment to run.

5. **The optimal strategy may be an ensemble:** Use S1 as the primary classifier (100% unsafe recall), use S2 as a second opinion on low-confidence S1 predictions, and use semantic consistency to quantify uncertainty on the S2 opinion. This would preserve S1's safety guarantee while leveraging S2's disambiguation ability on hard cases.

---

## 7. Ablation: Context-Aware Few-Shot Examples

**Date:** 2026-03-25

### Motivation

Both the S1 and S2 prompts contain 12 decontextualized one-liner examples (e.g., `"I hide under the bed" -> HIDE`), but at inference time the classifier receives a structured `[NIGHTMARE CONTEXT]` / `[USER'S REWRITING ATTEMPT]` input. This format mismatch between few-shot examples and actual input means the model must learn on its own that nightmare context should inform classification. We tested whether adding context-aware examples improves accuracy.

### Design

Three clinically grounded examples were added to both prompts identically (keeping the S1-vs-S2 comparison controlled). Each demonstrates that the same surface action can classify differently depending on nightmare context:

1. Aimless fleeing from a chaser → HIDE (avoidance without agency)
2. Purposeful running toward exit from same chaser → CONFRONT (active mastery)
3. "I'm fine" after a traumatic scene → DENY (suppression in distressing context)

Implementation: `CONTEXT_AWARE_EXAMPLES` block in `classifier.py` (imported by `classifier_cot.py`), toggled via `use_context_examples=True` constructor flag. Benchmark flag: `--context-examples`.

### Results (2×2 Comparison)

Baseline S1 = post-META-sanity-check run (`benchmark_results.csv`, Mar 23).

| Metric | S1 | S1+ctx | S2 | S2+ctx |
|---|---|---|---|---|
| **Safety Accuracy** | 394/420 (93.8%) | 387/420 (92.1%, ↓1.7%) | 397/420 (94.5%) | 400/420 (95.2%, ↑0.7%) |
| **Unsafe Recall** | 180/180 (100.0%) | 180/180 (100.0%, =) | 178/180 (98.9%) | 177/180 (98.3%, ↓0.6%) |
| **Node Accuracy** | 323/420 (76.9%) | 311/420 (74.0%, ↓2.9%) | 328/420 (78.1%) | 332/420 (79.0%, ↑0.9%) |
| **False Alarms** (safe→unsafe) | 26 | 33 (↑7) | 21 | 17 (↓4) |
| **Missed Unsafe** | 0 | 0 (=) | 2 | 3 (↑1) |

### Analysis

**Context examples hurt S1.** Safety accuracy dropped from 93.8% to 92.1%, node accuracy dropped from 76.9% to 74.0%, and false alarms increased from 26 to 33. The model appears to be overcorrecting: the explanatory rationales in the examples (e.g., "fleeing without agency is avoidance, not purposeful action") condition the direct classifier to second-guess adaptive actions. For a single-token-output classifier, the reasoning in the examples acts as noise rather than guidance. Unsafe recall remained at 100% but only because the conservative bias labels more things as unsafe overall.

**Context examples had marginal effect on S2.** Safety accuracy improved slightly (94.5%→95.2%) and false alarms dropped (21→17), but unsafe recall regressed (98.9%→98.3%) with one additional missed unsafe case. Node accuracy improved slightly (78.1%→79.0%). The CoT classifier benefits modestly from the reasoning in the examples because it is already in a reasoning mode — the parenthetical explanations align with its output format. However, the gains are not significant enough to justify the added prompt complexity, especially with the recall regression.

### Confidence Calibration (2×2)

| Metric | S1 | S1+ctx | S2 | S2+ctx |
|---|---|---|---|---|
| **Mean confidence** | 0.970 | 0.963 | 0.799 | 0.787 |
| **Mean (correct)** | 0.975 | 0.971 | 0.800 | 0.788 |
| **Mean (errors)** | 0.905 | 0.877 | 0.788 | 0.770 |
| **Separation** | **0.070** | **0.093** | **0.012** | **0.018** |

Context examples improved confidence calibration in both classifiers despite not improving accuracy. S1+ctx separation rose from 0.070 to 0.093; S2+ctx from 0.012 to 0.018.

**Threshold efficiency at conf < 0.9:**

| Run | Flagged | Errors caught |
|---|---|---|
| S1 | 41 (9.8%) | 11/26 (42%) |
| S1+ctx | 54 (12.9%) | 17/33 (52%) |
| S2 | 401 (95.5%) | 23/23 (100%) |
| S2+ctx | 399 (95.0%) | 20/20 (100%) |

S2's confidence remains useless for thresholding regardless of examples (must flag 95%+ of all cases to catch errors). S1+ctx catches a higher fraction of its errors (52% vs 42% at the same threshold) but has more errors to catch.

### Error Pattern Analysis

S1+ctx introduced 15 new safety errors while fixing 8 old ones (net -7). The new errors show a systematic pattern:

**What adaptive nodes get misclassified as (15 new errors):**
- TRAUMA_REPLAY: 9 cases (60%)
- SUPPRESSION: 4 cases (27%)
- AVOIDANCE: 2 cases (13%)

**Which ground truth nodes are affected:**
- MYTHICAL_MASTERY: 4, BEHAVIORAL_MASTERY: 3, EMOTIONAL_MASTERY: 3, ENVIRONMENTAL_MASTERY: 2, SOCIAL_MASTERY: 2, AFFECT_EXPRESSION: 1

The context examples taught two principles: "aimless fleeing = avoidance" and "I'm fine = suppression." The model over-generalized: adaptive actions that could be loosely interpreted as passive (calming down, using tools, seeking help) get pulled toward maladaptive labels. The TRAUMA_REPLAY over-classification is particularly telling — the chase example (nightmare context + ambiguous action) appears to bias the model toward interpreting more inputs as "reliving the nightmare without change."

Notably, the model's *confidence* on these new errors is lower (mean 0.826) than on its correct predictions (0.971), meaning the model partially "knows" it is guessing. This is consistent with the improved separation: the context examples make the model less accurate but better calibrated.

### Conclusion

**Revert to original prompts for both classifiers.** The context-aware examples degrade S1 accuracy (93.8%→92.1%) by inducing systematic over-classification of adaptive actions as maladaptive. S2 gains are negligible (+0.7% safety accuracy) and come with a recall regression. The original decontextualized examples are sufficient; the model generalizes across the format gap between examples and inference input.

**Secondary finding:** Context examples improve confidence calibration (S1 separation: 0.070→0.093) even while hurting accuracy, suggesting that few-shot examples influence the model's uncertainty estimation independently of classification quality. This is a minor but potentially interesting observation for future prompt engineering research.

This ablation is documented as a negative result in the thesis. The `use_context_examples` flag is retained in the codebase for reproducibility but defaults to `False`.

---

## 8. Next Steps

- [x] Run semantic consistency on error cases (targeted, ~22 min) to check if voting predicts errors — **DONE 2026-04-14.** Results: `consistency_errors_20260414_151034.csv`. Consistency fixed 17/26 S1 errors (65%) and 19/23 S2 errors (83%), zero cases broken in the error+control slice. Agreement separation S2: 0.012 (logprobs) → 0.255 (voting) — voting is the usable UQ signal for CoT. Agreement separation S1: 0.070 → 0.086, plus direct error correction via majority vote.
- [ ] **Run full semantic consistency benchmark on the full 480-case dev set (S1 and S2).** The targeted results are promising, but the "zero broken cases" property has only been confirmed on a 25-case correct-control slice per system. A full-set run is needed to rule out regressions on previously-correct predictions before declaring semantic consistency the recommended UQ method. Est. ~2h for S1, ~5.4h for S2 (per §5 cost estimates). Blocks: writeup of the UQ chapter / `Semantic_Consistency_Findings.md`.
- [ ] Analyze whether the 2 S2 missed unsafe cases would have been caught by consistency voting (fold into full-set consistency writeup)

### Scoped out (documented as limitations / future work)

- **S2 BEHAVIORAL_MASTERY → AVOIDANCE failure pattern — not investigated further.** Decision (2026-04-20): document in the thesis as a negative finding, not as an engineering puzzle. Rationale: (a) the proposed ensemble uses S1 as primary and only consults S2 on low-confidence S1 predictions — BEHAVIORAL_MASTERY cases are almost always high-confidence in S1, so they rarely reach S2 and a fix would not move end-to-end metrics; (b) prompt iteration is a rabbit hole requiring repeated benchmark re-runs; (c) the pattern already carries its weight as a negative result that complements the logprobs-separation collapse (§3) — both illustrate that CoT does not uniformly dominate and launders its own uncertainty. Will be documented in thesis §4.4 (Failure Analysis) with the concrete examples from §4 above. Revisit only if the full-set consistency run surfaces previously-correct BEHAVIORAL_MASTERY cases breaking at scale.
- **Ensemble approach (S1 primary + S2 second-opinion + semantic-consistency UQ on S2) — not implemented for the thesis.** Proposed in §6 point 5; listed as future work in thesis §5.5. Implementation would require an integration layer, threshold calibration, and a separate end-to-end eval — out of scope given timeline constraints.

---

## 9. Files

| File | Purpose |
|---|---|
| `safety/classifier_cot.py` | System 2 (CoT) classifier implementation |
| `safety/semantic_consistency.py` | Semantic consistency UQ module |
| `experiments/run_comparison.py` | Side-by-side comparison script |
| `experiments/run_benchmark.py` | Benchmark script (`--classifier s1/s2`, `--context-examples`) |
| `experiments/run_consistency_errors.py` | Targeted consistency run on error cases |
| `tests/test_classifier_cot.py` | Unit + integration tests |
| `tests/test_cot_sanity.py` | 10-case sanity check script |
| `data/benchmarks/benchmark_results.csv` | **S1 baseline** (post-META-fix, Mar 23) |
| `data/benchmarks/benchmark_results_s2.csv` | **S2 baseline** (Mar 25) |
| `data/benchmarks/benchmark_results_pre_meta_fix.csv` | S1 pre-META-fix (Mar 19, superseded) |
| `data/benchmarks/benchmark_results_s1_ctx.csv` | S1 + context examples results |
| `data/benchmarks/benchmark_results_s2_ctx.csv` | S2 + context examples results |
