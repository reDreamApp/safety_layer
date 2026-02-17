# Final Clinical Codes - Natural Multi-Token Labels

**Decision Date:** January 27, 2026

## Key Decision: Use Natural Multi-Token Labels

Based on recent NLP research (2024), we've decided to **abandon single-token optimization** in favor of natural, clinically accurate labels.

### Why This Decision?

**Research Findings:**
1. **First-token probability is unreliable** - 60%+ mismatch between first-token probs and actual outputs
2. **Length-normalized joint probability outperforms** first-token approaches
3. **Natural labels improve model performance** - LLMs generate clinically appropriate terms more reliably
4. **Multi-token handling is well-studied** - Length normalization effectively addresses token count bias

**Key Papers:**
- "My Answer is C: First-Token Probabilities Do Not Match Text Answers" (2024)
- "Token-Level Marginalization for Multi-Label LLM Classifiers" (2024)
- "A Survey of Confidence Estimation and Calibration in Large Language Models" (2024)

---

## Final Code Set - One Code Per Category

### Maladaptive Categories (Unsafe)

| # | Category | Code | Token Count | Rationale |
|---|----------|------|-------------|-----------|
| 1 | **Avoidance/Flight** | `AVOID` | ~2 tokens | Direct, clear avoidance behavior |
| 2 | **Interruption/Waking** | `WAKE` | ~1-2 tokens | Standard dream termination term |
| 3 | **Violent Revenge** | `HARM` | ~2 tokens | Clear violence without being gratuitous |
| 4 | **Suppression** | `DENY` | ~2 tokens | Direct emotional denial/suppression |
| 5 | **Trauma Replay** | `REPLAY` | ~2 tokens | Clinical term for repeating trauma |

### Adaptive Categories (Safe)

| # | Category | Code | Token Count | Rationale |
|---|----------|------|-------------|-----------|
| 6 | **Confrontational Mastery** | `CONFRONT` | ~2 tokens | Direct facing of threat |
| 7 | **Help-Seeking** | `CALL` | ~1 token | Calling for help/support |
| 8 | **Environmental Mastery** | `CHANGE` | ~1 token | Transforming environment |
| 9 | **Emotional Mastery** | `CALM` | ~2 tokens | Emotional regulation |
| 10 | **Mythical Mastery** | `POWER` | ~1 token | Supernatural empowerment |

---

## Code Characteristics

### Clinical Accuracy ✅
- All codes use natural therapeutic language
- Align with IRT clinical literature
- LLMs will naturally generate these terms

### Uniqueness ✅
- No duplicate codes across categories
- Each code is semantically distinct
- Clear one-to-one mapping: code → category

### Simplicity ✅
- Most codes are 1-2 tokens (manageable)
- Common English words
- Easy to understand and validate

---

## Confidence Estimation Method

### Primary Method: Length-Normalized Joint Probability

**Formula:**
```python
def calculate_confidence(logprobs_sequence, token_count):
    """
    Length-normalized confidence score

    Args:
        logprobs_sequence: List of log probabilities for each token
        token_count: Number of tokens in the label

    Returns:
        Normalized confidence score [0, 1]
    """
    log_prob_sum = sum(logprobs_sequence)
    normalized_log_prob = log_prob_sum / token_count
    confidence = exp(normalized_log_prob)
    return confidence
```

**Why This Works:**
- Prevents bias toward shorter labels
- Research-backed approach
- Works with Mistral API (just needs logprobs)
- Single forward pass (efficient)

---

## Uncertainty Quantification Strategy

### Two-Tier Approach

#### Tier 1: Log Probability (All Cases)
```python
response = classifier.generate(prompt, logprobs=True)
confidence = calculate_length_normalized_confidence(response.logprobs)

if confidence > 0.8:
    # High confidence - accept
    return response.label, confidence
elif confidence < 0.5:
    # Low confidence - escalate to Tier 2
    proceed_to_semantic_check()
else:
    # Medium confidence - accept with flag
    return response.label, confidence, flag="medium_confidence"
```

#### Tier 2: Semantic Consistency (Uncertain Cases)
```python
# Run classifier multiple times (5-10 runs)
outputs = []
for _ in range(10):
    response = classifier.generate(prompt, temperature=0.7, logprobs=True)
    outputs.append(response.label)

# Check consistency
from collections import Counter
counts = Counter(outputs)
most_common_label, frequency = counts.most_common(1)[0]
consistency_score = frequency / 10

if consistency_score < 0.6:
    # Inconsistent - flag for human review
    flag_for_review(outputs)
else:
    # Consistent despite low logprob - trust consensus
    return most_common_label, consistency_score
```

### Margin of Victory (Optional Enhancement)

For critical cases, calculate margin between top-2 predictions:

```python
# Option A: Approximate from first-token distribution
first_token_top_probs = response.logprobs[0].top_logprobs
sorted_probs = sorted(first_token_top_probs.values(), reverse=True)
mov_approx = sorted_probs[0] - sorted_probs[1]

# Option B: Full evaluation (expensive - 10 forward passes)
confidences = {}
for label in all_10_labels:
    response = classifier.generate_with_label(label)
    confidences[label] = calculate_confidence(response.logprobs)

sorted_labels = sorted(confidences.items(), key=lambda x: x[1], reverse=True)
top_conf = sorted_labels[0][1]
second_conf = sorted_labels[1][1]
mov_full = top_conf - second_conf

if mov_full < 0.1:
    flag_as_ambiguous()
```

---

## Phase 2 Testing Plan

### Experiment 1: Log Probability Baseline
- Use length-normalized joint probability
- Single generation per classification
- Measure: accuracy, calibration (ECE), speed

### Experiment 2: Semantic Consistency
- Run classification 10 times per instance
- Measure output consistency
- Measure: accuracy, robustness, cost

### Experiment 3: Hybrid Approach
- Use log prob by default
- Escalate to semantic sampling when log_prob < 0.5
- Measure: accuracy, efficiency, cost-performance trade-off

### Expected Findings
- Log prob: fast, good for most cases
- Semantic consistency: more robust but expensive
- Hybrid: best balance of speed and accuracy

### Metrics to Track
- **Accuracy:** Agreement with ground truth labels
- **Calibration:** ECE (Expected Calibration Error)
- **Coverage:** % of cases requiring Tier 2
- **Cost:** Average API calls per classification
- **Correlation:** Do low log-prob cases show low consistency?

---

## Implementation Notes

### Mistral API Requirements
```python
# Ensure API calls include logprobs
response = mistral_client.chat.complete(
    model="mistral-small-latest",
    messages=[{"role": "user", "content": prompt}],
    temperature=0,  # Deterministic for Tier 1
    max_tokens=5,
    logprobs=True,
    top_logprobs=10  # Get top 10 alternatives per token
)
```

### Prompt Template
```
You are a clinical safety classifier for Imagery Rehearsal Therapy.

Nightmare context: {nightmare_context}
User rescripting: {user_input}

Classify the rescripting action into ONE of these categories:

Maladaptive (Unsafe):
- AVOID: Avoiding/fleeing from threat
- WAKE: Waking up or terminating dream
- HARM: Excessive violence or revenge
- DENY: Emotional suppression or denial
- REPLAY: Replaying trauma without change

Adaptive (Safe):
- CONFRONT: Facing threat directly
- CALL: Calling for help/support
- CHANGE: Transforming environment
- CALM: Regulating emotions
- POWER: Using supernatural abilities

Output ONLY the category code:
```

---

## Alternative Approaches Considered

### ❌ Single-Token Optimization (Rejected)
- **Approach:** Find single-token codes for all categories
- **Why rejected:** Research shows first-token probabilities unreliable; forced unnatural codes (GET, MASK, BACK)
- **Conclusion:** Optimizing for wrong metric

### ❌ Marginal Probability (Not Feasible)
- **Approach:** Sum probabilities across all tokenization paths
- **Why not used:** Requires constrained decoding (10 forward passes), not supported by Mistral API
- **When useful:** Offline batch processing with local models

### ✅ Length-Normalized Joint Probability (Selected)
- **Approach:** Average token log-probs, normalize by length
- **Why selected:** Research-backed, API-compatible, single forward pass, handles multi-token naturally

---

## References

1. "My Answer is C: First-Token Probabilities Do Not Match Text Answers" (2024) - arXiv:2402.14499
2. "Token-Level Marginalization for Multi-Label LLM Classifiers" (2024) - arXiv:2511.22312
3. "A Survey of Confidence Estimation and Calibration in Large Language Models" (2024) - NAACL
4. "Detecting hallucinations in large language models using semantic entropy" (2024) - Nature
5. "Mitigating Label Length Bias in Large Language Models" (2024) - arXiv:2511.14385

---

## Summary

**Final Decision:** Use natural multi-token labels with length-normalized confidence estimation and two-tier uncertainty quantification (log-prob + semantic consistency).

**Key Insight:** Clinical accuracy and model naturalness are more important than single-token optimization, especially given that first-token probabilities are unreliable.

**Next Steps:** Update all generation scripts and documentation to reflect this approach.
