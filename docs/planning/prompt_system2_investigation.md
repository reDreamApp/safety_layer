# Prompt: Investigate & Implement System 2 (Chain-of-Thought) Classifier Variant

## Context

This is a master's thesis project: a neuro-symbolic safety layer for an IRT (Imagery Rehearsal Therapy) chatbot. The safety layer classifies dream rescripting actions as adaptive or maladaptive using a clinical knowledge graph.

**The current classifier (System 1 / "Direct")** lives in `safety/classifier.py`. It uses "Label Engineering" — an LLM prompt that describes 12 clinical codes and asks the model to respond with ONE code word only (e.g., `HIDE`, `CONFRONT`, `REPLAY`). Confidence is measured via length-normalized joint log-probabilities of the output tokens. This approach currently achieves **95.0% safety accuracy and 98.3% unsafe recall** on a 480-test benchmark.

**The goal** is to implement a **System 2 / "Reasoned" variant** that uses explicit Chain-of-Thought (CoT) reasoning before classifying. The exposé describes this as:

> A generative model utilizing Constrained Structured Generation (JSON Schema) to enforce explicit reasoning through three steps:
> 1. Context Summary: Explicit grounding of scene facts
> 2. Clinical Rationale: Chain-of-Thought derivation using IRT clinical guidelines and maladaptive pattern definitions
> 3. Safety Classification: Binary safe/unsafe determination with category label

The research question is: **Does explicit reasoning (System 2) significantly outperform direct classification (System 1) in mapping ambiguous user inputs to clinical safety labels?**

## Key Files to Read First

1. `safety/classifier.py` — Current System 1 classifier. Understand the full implementation: `ClinicalClassifier` class, `CLINICAL_CODER_PROMPT`, `CODE_MAP`, `ClassificationResult` dataclass, and especially how `classify()` works with logprobs.
2. `safety/critic.py` — The critic pipeline that calls the classifier. Understand how `ClassificationResult` is consumed (especially in `_classify_segments()` and `_triage_classifications()`).
3. `safety/graph_definitions.py` — The clinical knowledge graph with all node definitions, correction edges, and clinical descriptions. The System 2 prompt should ground its reasoning in this clinical knowledge.
4. `AI/agent.py` — The `Agent` class and `ModelConfig`. Understand how the LLM is called, especially `generate_with_logprobs()` and any structured output / JSON mode capabilities.
5. `experiments/run_benchmark.py` — How benchmarks are run, so you know how to evaluate System 2.
6. `data/benchmarks/` — Look at the benchmark dataset structure.
7. `CLAUDE.md` — Project conventions and current state.

## Design Constraints

### Comparability (CRITICAL)

The goal is a controlled comparison. The **only independent variable** should be the reasoning step. Everything else must be held constant:

- **Must stay identical across System 1 and System 2:** The 12 codes, all code definitions, all critical rules (violence threshold, feeling vs avoidance, emotional regulation vs suppression, etc.), the examples, the model, the temperature, the input format.
- **The only difference:** System 1 says "respond with ONE CODE only, no explanations." System 2 says "first reason through these three steps, then give your code."
- **Do NOT add extra classification hints, disambiguation rules, or additional examples to the System 2 prompt that System 1 doesn't also get.** The performance difference should come from the reasoning *process*, not from extra information in the prompt.
- **Litmus test:** If you removed the CoT requirement from the System 2 prompt and just said "now give the code," it should produce the same classifications as System 1.

### Interface & Architecture

1. **System 2 must produce the same `ClassificationResult` interface** so it plugs into the critic pipeline without changes to `critic.py`.
2. **Keep it as a separate class or mode** — e.g., `ClinicalClassifierCoT` or a `reasoning_mode="cot"` parameter on the existing class. Don't replace System 1; we need both for comparison.
3. **The System 2 prompt should leverage the clinical knowledge from the graph.** The CoT reasoning should explicitly reference IRT clinical guidelines, maladaptive pattern definitions, and the distinction rules — but only the same rules already present in the System 1 prompt.

### Uncertainty Quantification (implement BOTH methods)

The exposé proposes comparing two uncertainty quantification approaches. Implement both so we can evaluate them:

1. **Token Log-Probabilities:** Extract logprobs on the classification token(s). For System 1 this already exists (length-normalized joint probability). For System 2, extract logprobs on the final classification code within the structured output. Both systems should produce a comparable logprobs-based confidence score.

2. **Semantic Consistency:** Run N stochastic inference chains (exposé suggests N=5, temperature=0.7) and measure agreement via percentage match across classifications. High consistency (≥80% agreement) = confident; low consistency = uncertain. Implement this for BOTH System 1 and System 2 so the comparison is fair. This should be an optional mode (it's 5x the API calls) that can be toggled on for evaluation runs.

The research question is: which method better predicts classifier errors and thus provides a more reliable trigger for requesting user clarification?

### Structured Output Format

Suggestion (adapt as needed):
   ```json
   {
     "context_summary": "Brief grounding of scene facts and what the user is doing",
     "clinical_rationale": "Step-by-step reasoning applying IRT guidelines to this action",
     "classification": "HIDE",
     "safety": "UNSAFE"
   }
   ```

## Tasks

1. **Read and understand** all key files listed above before writing any code.
2. **Design the System 2 prompt.** It must use the exact same code definitions, rules, and examples as System 1. The only addition is the structured reasoning requirement. Consider how to phrase the CoT steps so the model genuinely reasons rather than just adding boilerplate before the same snap judgment.
3. **Implement the System 2 classifier** as a new class or mode in `safety/classifier.py` (or a new file like `safety/classifier_cot.py` if cleaner).
4. **Implement BOTH uncertainty quantification methods:**
   - Token log-probs confidence (for both System 1 and System 2, comparable scores)
   - Semantic consistency mode (N=5, temp=0.7, percentage agreement) — as an optional mode for both classifiers. This can be a wrapper or utility function that takes any classifier and runs it N times.
5. **Make it runnable on the existing benchmark.** Either adapt `run_benchmark.py` to accept a classifier mode flag, or create a small comparison script that can run: System 1 + logprobs, System 2 + logprobs, System 1 + semantic consistency, System 2 + semantic consistency.
6. **Write tests** for the new classifier variant and the semantic consistency mode.
7. **Do a quick sanity test** — run ~10 examples manually (mix of easy and hard cases) to verify it works before committing to a full benchmark run. Pick some known edge cases from the data.

## What NOT to Do

- Don't modify the existing System 1 classifier behavior or prompt.
- Don't modify `critic.py` — System 2 must produce compatible `ClassificationResult` objects.
- Don't run the full 480-test benchmark yet (that's expensive and slow). Just get it working and sanity-tested.
- Don't change the knowledge graph or node definitions.

## Useful Context

- The project uses `uv` for all Python (venv, deps, running).
- Model is configurable via `ModelConfig` / `MODELS` dict in `AI/agent.py`. Current default is GPT-5.4.
- The benchmark dataset is in `data/benchmarks/` as JSON files.
- Conventional commits for any git changes.
