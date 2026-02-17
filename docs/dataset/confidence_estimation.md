# Confidence Estimation Implementation Plan

**Date:** January 27, 2026
**Decision:** Use length-normalized joint probability with two-tier uncertainty quantification

---

## Research Summary

Based on recent NLP research (2024), we've determined:

1. **First-token probability is unreliable** (60%+ mismatch with actual outputs)
2. **Length-normalized joint probability** is the practical, research-backed approach
3. **Semantic consistency** (multiple sampling) provides robust uncertainty detection
4. **Hybrid approach** (log-prob + selective semantic sampling) offers best cost-performance balance

---

## Implementation Strategy

### Tier 1: Log Probability Confidence (Default)

**Used for:** All classifications

**Method:** Length-normalized joint probability

```python
def calculate_confidence(logprobs_sequence, token_count):
    """
    Calculate length-normalized confidence score

    Args:
        logprobs_sequence: List of log probabilities for each generated token
        token_count: Number of tokens in the generated label

    Returns:
        Normalized confidence score in [0, 1]
    """
    import math

    # Sum log probabilities
    log_prob_sum = sum(logprobs_sequence)

    # Normalize by token count (prevents bias toward shorter labels)
    normalized_log_prob = log_prob_sum / token_count

    # Convert to probability space
    confidence = math.exp(normalized_log_prob)

    return confidence
```

**Example:**
```python
# Label: HARM (2 tokens: "H", "ARM")
# Token 1: log_prob = -0.5
# Token 2: log_prob = -1.2

log_sum = -0.5 + (-1.2) = -1.7
normalized = -1.7 / 2 = -0.85
confidence = exp(-0.85) = 0.427  # 42.7% confidence
```

**Thresholds:**
- `confidence > 0.8`: High confidence → Accept immediately
- `0.5 <= confidence <= 0.8`: Medium confidence → Accept with flag
- `confidence < 0.5`: Low confidence → Escalate to Tier 2

---

### Tier 2: Semantic Consistency Check (Selective)

**Used for:** Low-confidence cases (logprob < 0.5)

**Method:** Multiple sampling with consistency analysis

```python
def semantic_consistency_check(prompt, num_samples=10):
    """
    Run classification multiple times and measure consistency

    Args:
        prompt: Classification prompt
        num_samples: Number of times to sample (default: 10)

    Returns:
        most_common_label: Consensus prediction
        consistency_score: Agreement rate (0-1)
        all_outputs: List of all sampled labels
    """
    from collections import Counter

    outputs = []

    for _ in range(num_samples):
        response = mistral_api.generate(
            prompt=prompt,
            temperature=0.7,  # Enable sampling
            max_tokens=5,
            logprobs=True
        )
        label = response.text.strip()
        outputs.append(label)

    # Count occurrences
    counts = Counter(outputs)
    most_common_label, frequency = counts.most_common(1)[0]

    # Calculate consistency
    consistency_score = frequency / num_samples

    return most_common_label, consistency_score, outputs
```

**Decision Logic:**
```python
if consistency_score >= 0.6:
    # Consistent despite low logprob → Trust consensus
    return most_common_label, consistency_score, flag="low_logprob_consistent"
else:
    # Inconsistent outputs → Genuinely uncertain
    return None, consistency_score, flag="ambiguous_requires_review"
```

---

## Complete Classification Pipeline

```python
def classify_rescripting(nightmare_context, user_input):
    """
    Complete classification with two-tier confidence estimation

    Returns:
        label: Predicted category code
        confidence: Confidence score
        flag: Optional uncertainty flag
    """

    # Build prompt
    prompt = build_classification_prompt(nightmare_context, user_input)

    # Tier 1: Single generation with logprobs
    response = mistral_api.generate(
        prompt=prompt,
        temperature=0,  # Deterministic
        max_tokens=5,
        logprobs=True,
        top_logprobs=10
    )

    label = response.text.strip()
    token_logprobs = [token.logprob for token in response.logprobs]
    token_count = len(token_logprobs)

    # Calculate confidence
    confidence = calculate_confidence(token_logprobs, token_count)

    # High confidence → Accept
    if confidence > 0.8:
        return label, confidence, flag=None

    # Medium confidence → Accept with flag
    elif confidence >= 0.5:
        return label, confidence, flag="medium_confidence"

    # Low confidence → Tier 2
    else:
        consensus_label, consistency, outputs = semantic_consistency_check(prompt)

        if consistency >= 0.6:
            # Consistent consensus
            return consensus_label, consistency, flag="low_logprob_consistent"
        else:
            # Ambiguous - flag for human review
            return None, consistency, flag="ambiguous_requires_review"
```

---

## Margin of Victory (Optional Enhancement)

For additional uncertainty quantification, calculate margin between top 2 predictions.

### Option A: First-Token Distribution Approximation (Fast)

```python
def calculate_mov_approx(first_token_logprobs):
    """
    Approximate margin of victory from first token distribution

    Args:
        first_token_logprobs: Dict mapping tokens to logprobs

    Returns:
        mov: Margin between top 2 probabilities
    """
    # Get top 2 probabilities
    top_probs = sorted(first_token_logprobs.values(), reverse=True)

    if len(top_probs) >= 2:
        mov = math.exp(top_probs[0]) - math.exp(top_probs[1])
    else:
        mov = 1.0  # Only one option

    return mov
```

**Usage:**
```python
first_token_top_logprobs = response.logprobs[0].top_logprobs
mov = calculate_mov_approx(first_token_top_logprobs)

if mov < 0.1:
    flag = "ambiguous_low_margin"
```

### Option B: Full 10-Class Evaluation (Expensive)

Requires running classifier 10 times with constrained decoding (once per class).

**Not recommended initially** due to 10x cost. Consider only for critical cases or offline evaluation.

---

## Phase 2 Testing Plan

### Experiment 1: Log Probability Baseline
- **Method:** Length-normalized joint probability only
- **Metrics:**
  - Accuracy (agreement with ground truth)
  - Calibration (ECE - Expected Calibration Error)
  - Speed (API calls per classification)

### Experiment 2: Semantic Consistency
- **Method:** Multiple sampling (10 runs) for all cases
- **Metrics:**
  - Accuracy
  - Robustness (consistency correlation with correctness)
  - Cost (10x API calls)

### Experiment 3: Hybrid Approach
- **Method:** Log-prob + selective semantic sampling (threshold = 0.5)
- **Metrics:**
  - Accuracy
  - Efficiency (% cases requiring Tier 2)
  - Cost-performance trade-off

### Expected Results
- Log-prob: Fast, good accuracy for most cases
- Semantic: More robust, catches genuine uncertainty, expensive
- Hybrid: Best balance - high accuracy with reasonable cost

---

## Implementation Checklist

### Phase 2 (Development)
- [ ] Implement `calculate_confidence()` function
- [ ] Implement `semantic_consistency_check()` function
- [ ] Implement complete classification pipeline
- [ ] Test on dev set (100 incidents)
- [ ] Measure baseline metrics (accuracy, calibration, cost)
- [ ] Determine optimal threshold for Tier 2 escalation
- [ ] Implement MoV approximation (optional)

### Phase 3 (Optimization)
- [ ] Analyze error cases (where did classifier fail?)
- [ ] Tune confidence thresholds based on empirical data
- [ ] Evaluate cost-performance trade-offs
- [ ] Decide on final hybrid strategy
- [ ] Document calibration curves

### Phase 4 (Evaluation)
- [ ] Evaluate on locked test set (100 incidents)
- [ ] Calculate final metrics: accuracy, precision, recall, F1
- [ ] Measure calibration (ECE, reliability diagrams)
- [ ] Report cost analysis (API calls per classification)
- [ ] Compare against baseline approaches

---

## API Requirements

### Mistral API Configuration

```python
import requests
import os

MISTRAL_API_KEY = os.getenv("SCALEWAY_API_KEY")
MISTRAL_BASE_URL = "https://api.scaleway.ai/v1"

def call_mistral_api(prompt, temperature=0, max_tokens=5, logprobs=True, top_logprobs=10):
    """
    Call Mistral API with logprobs enabled

    Args:
        prompt: Input prompt
        temperature: Sampling temperature (0 = deterministic)
        max_tokens: Maximum tokens to generate
        logprobs: Whether to return log probabilities
        top_logprobs: Number of top alternative tokens to return per step

    Returns:
        Response object with text and logprobs
    """
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistral-small-latest",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "logprobs": logprobs,
        "top_logprobs": top_logprobs
    }

    response = requests.post(
        f"{MISTRAL_BASE_URL}/chat/completions",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API error: {response.status_code} - {response.text}")
```

---

## Prompt Template

```python
CLASSIFICATION_PROMPT_TEMPLATE = """You are a clinical safety classifier for Imagery Rehearsal Therapy (IRT).

Your task is to classify the patient's rescripting action into ONE category.

**Nightmare Context:**
{nightmare_context}

**Patient's Rescripting:**
{user_input}

**Categories:**

Maladaptive (Unsafe):
- AVOID: Avoiding or fleeing from the threat
- WAKE: Waking up or terminating the dream
- HARM: Excessive violence or revenge
- DENY: Emotional suppression or denial
- REPLAY: Replaying trauma without change

Adaptive (Safe):
- CONFRONT: Facing the threat directly
- CALL: Calling for help or support
- CHANGE: Transforming the environment
- CALM: Regulating emotions
- POWER: Using supernatural abilities

**Output ONLY the category code (one word):**"""

def build_classification_prompt(nightmare_context, user_input):
    return CLASSIFICATION_PROMPT_TEMPLATE.format(
        nightmare_context=nightmare_context,
        user_input=user_input
    )
```

---

## References

1. **Length Normalization:** "Mitigating Label Length Bias in Large Language Models" (2024) - arXiv:2511.14385
2. **Joint Probability:** "Token-Level Marginalization for Multi-Label LLM Classifiers" (2024) - arXiv:2511.22312
3. **First-Token Unreliability:** "My Answer is C: First-Token Probabilities Do Not Match Text Answers" (2024) - arXiv:2402.14499
4. **Semantic Entropy:** "Detecting hallucinations in large language models using semantic entropy" (2024) - Nature
5. **Calibration:** "A Survey of Confidence Estimation and Calibration in Large Language Models" (2024) - NAACL

---

## Summary

**Primary Method:** Length-normalized joint probability (Tier 1)
**Fallback Method:** Semantic consistency check (Tier 2)
**Enhancement:** Margin of victory (optional)
**Testing Strategy:** Compare log-prob, semantic, and hybrid approaches
**Expected Outcome:** Hybrid approach with ~90%+ accuracy and good calibration
