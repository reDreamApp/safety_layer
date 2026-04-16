# Thesis Skeleton — ReDream AI: Neuro-Symbolic Safety Layer for IRT Chatbot

**Status:** Working draft (2026-03-25). Structure agreed, figures planned, no prose yet.
**Writing approach:** Markdown drafts → LaTeX final. Figures in draw.io (conceptual) + matplotlib (data).

---

## 1. Introduction

### 1.1 Nightmares as a Clinical Problem
- Chronic nightmares affect 4–8% of the population
- Recognized clinical condition (DSM-5), not just "bad dreams"
- Strong comorbidity with PTSD, anxiety, depression
- Measurable quality-of-life impact
- **No figure.** Short scene-setting, 1–2 paragraphs.

### 1.2 The Treatment Gap
- IRT is the gold-standard evidence-based treatment (Krakow & Zadra 2006)
- Access is severely limited: specialist shortage, long waitlists, stigma
- Most people who need treatment don't get it
- **No figure.** Together with 1.1, about one page total.

### 1.3 AI-Assisted Mental Health Interventions
- LLM-based chatbots can scale therapeutic access
- Harvard Business survey: companionship/therapy is the most common real-world LLM use case — people already want this
- Brief landscape of existing approaches (Woebot, Wysa, etc.)
- Motivates using AI for IRT specifically
- **No figure.** Short.

### 1.4 The Safety Challenge
- LLMs in therapy are dangerous without guardrails
- They can suggest maladaptive coping strategies that *sound* plausible but reinforce trauma
- In nightmare rescripting, the failure modes are clinically defined (avoidance, suppression, violent revenge, etc.)
- The problem is subtle — maladaptive patterns often sound like natural, reasonable responses
- **📊 FIGURE 1: "The Problem Illustration"** — Chase nightmare example. Patient hides (avoidance), unconstrained LLM validates it (red), safety-layer-augmented LLM redirects to behavioral mastery (green). Detection strip at bottom hints at mechanism.
  - **Status:** Draft generated (Graphviz). Needs real LLM outputs plugged in.

### 1.5 Research Question
- Core: Can a KG-augmented neuro-symbolic safety layer reduce maladaptive suggestions in LLM-generated IRT interventions?
- Sub-questions (reframed to match actual work):
  1. Does explicit chain-of-thought reasoning (System 2) outperform direct classification (System 1) for ambiguous clinical inputs?
  2. Which uncertainty quantification method (token log-probs vs semantic consistency) better predicts classifier errors?
  3. Does the full safety-layer system produce safer outputs than the baseline LLM without the critic?
- **No figure.**

### 1.6 Contributions
- Clinically grounded ontology of IRT safety patterns (5 maladaptive, 5 adaptive, formalized as knowledge graph)
- Working neuro-symbolic critic pipeline with two classification strategies
- Benchmark evaluation on synthetic critical incidents + expert validation protocol
- **No figure.**

### 1.7 Thesis Outline
- One sentence per chapter summarizing what it covers
- **No figure** (or optional: mini chapter-flow diagram).

---

## 2. Background & Related Work

### 2.1 LLMs in Mental Health Applications
- Open with demand signal: Harvard Business survey on companionship/therapy as top LLM use case
- Survey of existing chatbot approaches (Woebot, Wysa, etc.)
- Current safety mechanisms are ad-hoc: content filters, RLHF guardrails, constitutional AI — not clinically grounded
- Gap: nobody is doing *formalized clinical protocol* safety
- **No figure.** ~1.5 pages.

### 2.2 Neuro-Symbolic Approaches to AI Safety
- Neuro-symbolic AI: combines neural flexibility (LLM) with symbolic guarantees (knowledge graph)
- Knowledge graphs provide structure, explainability, deterministic reasoning
- Brief overview of KG-RAG approaches in healthcare/safety contexts
- This is the methodological foundation for the thesis
- **📊 FIGURE 2: Neuro-symbolic concept diagram.** Abstract: "Neural (flexible, unpredictable)" + "Symbolic (rigid, explainable)" = combined approach. Helps clinical readers who don't know the term.
  - **Status:** Not yet created.

### 2.3 Nightmare Disorder & the IRT Protocol
- Clinical background: nightmare disorder (DSM-5 criteria), prevalence, impact
- IRT protocol steps: record nightmare → identify themes → rescript toward mastery → rehearse new version
- How rescripting works and why the rescripting stage is safety-critical
- **📊 FIGURE 3: IRT Protocol Overview.** Shows the IRT stages and where the safety-critical moment is.
  - **Status:** Existing figure (irt_chatbot_overview) could be adapted — may want a version that shows just the IRT protocol without system architecture details (save full system for Ch 3).

### 2.4 Maladaptive vs. Adaptive Rescripting Patterns
- Germain 2004 MMS: 5 mastery dimensions (Behavioral, Social, Environmental, Emotional, Mythical)
- IRT literature + DSM-5: 5 maladaptive failure modes (Avoidance, Interruption, Violent Revenge, Suppression, Trauma Replay)
- Introduces the clinical taxonomy that becomes the knowledge graph
- **📊 FIGURE 4: Table of clinical patterns.** Two columns — maladaptive patterns (left, with clinical source) and adaptive mastery dimensions (right, with MMS reference). No graph structure yet — just the raw clinical concepts from the literature.
  - **Status:** Not yet created. Could be a formatted table rather than a figure.

---

## 3. Neuro-Symbolic Safety Layer

### 3.1 Modeling Clinical Knowledge as a Graph
- Formalization of 2.4's clinical concepts into a computable knowledge graph
- Directly continues from the clinical patterns — reader just learned the taxonomy, now sees how it becomes a formal structure
- 12 nodes (5 maladaptive, 5 adaptive, 2 neutral), 15 correction edges, severity levels
- Design decisions: why these edges, why these severity tiers, node attributes
- This is the thesis contribution — synthesizing scattered clinical literature into one formal structure
- **📊 FIGURE 5: Clinical Ontology Graph.** The knowledge graph with all nodes, edges, color-coded by type/severity.
  - **Status:** ✅ Exists (clinical_ontology_graph). Strong figure, natural home is here.

### 3.2 Ontology Development & Validation Process
- Iterative design process: literature review → initial graph → validation document prepared for Dr. Gieselmann
- Clinical grounding documented for every node (references to Germain, Krakow, DSM-5)
- Validation protocol: what was sent, what feedback is expected, how changes would propagate through the pipeline
- Include expert feedback and resulting changes if received before submission
- **No figure** (unless ontology changed significantly through feedback — then before/after comparison).

### 3.3 System Overview & Integration Point
- Now that the reader understands the graph, zoom out to show the full system
- The safety layer sits between patient input and chatbot response during the rescripting stage
- Acts as a critic: intercept, evaluate, constrain if needed
- High-level: Patient → LLM → Safety Layer → (safe? pass / unsafe? constrain → re-prompt)
- **📊 FIGURE 6: Bird's-eye system view.** Simplified overview of the full system showing the chatbot, the safety layer, and the feedback loop. Reader now understands what the core component (the graph) is, so this overview makes more sense.
  - **Status:** Existing figure (irt_chatbot_overview) works here. Decide whether to use it here or in 2.3 — or use a simplified version here and the full one in 2.3. Avoid showing the same figure twice.

### 3.4 Classifying User Responses
- Entity linker: how user text maps to graph nodes
- Label engineering: 12 semantic single-token codes
- System 1 (Direct): LLM responds with one code, confidence via logprobs
- System 2 (Chain-of-Thought): structured reasoning (context summary → clinical rationale → classification), then code
- Comparability: identical code definitions, rules, examples — only the reasoning step differs
- Confidence estimation: logprobs (both systems) and semantic consistency (N=5, temp=0.7)
- Negation handling, ambiguity rules, context-aware suppression detection
- **📊 FIGURE 7: Classification component diagram.** Shows both System 1 and System 2 paths side by side. Same input → System 1 (direct code) vs System 2 (reasoning → code). Emphasizes that inputs/rules are identical.
  - **Status:** Not yet created.

### 3.5 The Critic Pipeline
- Full critic pipeline: segmentation → META filtering → batch classification → severity triage → constraint synthesis
- Each stage explained with its purpose and how it feeds the next
- Constraint message format: validate + correct (acknowledge → redirect)
- **📊 FIGURE 8: Safety Pipeline Architecture.** The detailed flowchart of all 5 stages.
  - **Status:** ✅ Exists (safety_pipeline_architecture). Strong, detailed figure.
- **📊 FIGURE 9: Worked end-to-end example.** One concrete maladaptive input flowing through all stages — showing what happens at segmentation, what META filtering catches, how classification works, triage result, final constraint output. Makes the abstract pipeline concrete.
  - **Status:** Not yet created. High priority — the "money figure."

### 3.6 Handling Uncertainty and Escalation
- What happens when the system isn't confident: clarification requests
- What happens with severe cases (trauma replay, self-harm indicators): escalation to therapist
- Two uncertainty approaches: logprobs vs semantic consistency — how each works, when each triggers
- **📊 FIGURE 10: Decision flowchart.** Confidence high + safe → pass, confidence high + unsafe → constrain, confidence low → clarify, severe → escalate.
  - **Status:** Not yet created.

### 3.7 Design Decisions & Trade-offs
- LLM-based classification vs rule-based (why LLM)
- Batch vs single classification (why batch)
- Confidence threshold analysis: analyzed, stays at 0.0 (rationale)
- What was tried and discarded
- **No figure** (or optional: small table of "approach → result → decision").

---

## 4. Evaluation

### 4.1 Dataset & Scenario Design
- Why synthetic: real nightmare rescripting transcripts don't exist as datasets, collecting real data requires ethics board approval + patient access (not feasible for master's thesis), sharing real data raises privacy/ethics concerns
- Secondary benefit: controlled coverage across all node types, reproducible, varying difficulty levels
- 480 synthetic critical incidents, generated with GPT-5.4, balanced across all 12 nodes
- Difficulty distribution: easy/medium/hard
- Generation methodology, quality control
- **📊 FIGURE 11: Dataset composition.** Bar chart or grid showing distribution per node, difficulty levels, maladaptive vs adaptive split.
  - **Status:** Not yet created. Generate with matplotlib from benchmark data.

### 4.2 Experimental Setup & Metrics
- Two evaluation levels:
  1. Component-level: classifier accuracy, System 1 vs System 2 comparison, uncertainty method comparison (2×2 design)
  2. System-level: full pipeline with safety layer vs baseline LLM without critic, on same scenarios
- Metrics: safety accuracy, unsafe recall, per-node precision/recall, confidence calibration
- Model, temperature, number of runs
- **📊 FIGURE 12: Experimental design matrix.** The 2×2 grid (System 1/2 × logprobs/semantic consistency) + system-level comparison design. Makes the evaluation structure visually obvious.
  - **Status:** Not yet created.

### 4.3 Quantitative Results
- Overall accuracy numbers (currently: 95.0% safety accuracy, 98.3% unsafe recall)
- Per-node breakdown: which categories are easy, which are hard
- System 1 vs System 2 comparison: where do they differ?
- Uncertainty method comparison: which predicts errors better?
- System-level: with vs without safety layer results
- **📊 FIGURE 13: Confusion matrix.** Heatmap, predicted vs actual.
  - **Status:** Not yet created. Generate with matplotlib.
- **📊 FIGURE 14: Per-node accuracy chart.** Bar chart of accuracy per category.
  - **Status:** Not yet created. Generate with matplotlib.
- **📊 FIGURE 15: System 1 vs System 2 comparison table/chart.** Side-by-side results.
  - **Status:** Not yet created. Depends on System 2 implementation.
- **📊 FIGURE 16: Uncertainty calibration.** Reliability diagram or ROC curve — how well do logprobs vs semantic consistency predict errors?
  - **Status:** Not yet created. Depends on evaluation runs.

### 4.4 Failure Analysis & Edge Cases
- Where does the system fail, and why?
- Categories of errors: ambiguous inputs, boundary cases between nodes, subtle patterns
- Shows critical thinking about limitations
- **📊 FIGURE 17: Failure case table.** 3–5 concrete examples with input, predicted label, correct label, and explanation of why it went wrong.
  - **Status:** Not yet created. Can pull from existing benchmark error analysis.

### 4.5 Expert Evaluation & Qualitative Feedback
- Evaluation design: what was sent to Dr. Gieselmann, evaluation protocol, what is being measured (agreement with classifications, qualitative assessment of constraint messages)
- Single-turn evaluation: LLM responses with vs without safety layer, rated by expert
- Results included if received before submission; methodology documented regardless
- **📊 FIGURE 18: Expert agreement summary** (if results available). Table or chart of agreement rates, notable disagreements.
  - **Status:** Depends on Dr. Gieselmann's response.

---

## 5. Discussion & Conclusion

### 5.1 Interpretation of Results
- What do the numbers mean?
- Where the system excels (clear-cut maladaptive patterns) vs struggles (ambiguous cases)
- What did System 1 vs System 2 reveal?
- What did the uncertainty comparison show?
- **No figure.** References back to Chapter 4 figures.

### 5.2 Comparison with Existing Approaches
- How this approach differs from existing LLM safety mechanisms (content filters, RLHF, constitutional AI)
- What's novel: clinical formalization via knowledge graphs, domain-specific ontology, explainable corrections
- Keep short — arguing the approach is different, not benchmarking against other systems
- **No figure.**

### 5.3 Limitations
- Synthetic dataset (not real patients)
- LLM dependency (model changes could affect results)
- Single-domain evaluation (only IRT)
- Ontology coverage gaps (what's not captured)
- Expert validation status
- **No figure.**

### 5.4 Clinical & Ethical Implications
- What this means for real deployment
- Risk of over-reliance on automated safety
- Role of human oversight
- Regulatory context (MDR Class IIa)
- **No figure.**

### 5.5 Future Work
- Integration with live IRT chatbot (Phase 3)
- Generalization to other therapeutic domains (CBT, exposure therapy, etc.)
- Larger-scale evaluation with real transcripts
- Human-in-the-loop learning from therapist corrections
- Threshold calibration with more data
- **No figure.**

---

## Figure Inventory

| # | Figure | Chapter | Status |
|---|--------|---------|--------|
| 1 | Problem Illustration (chase nightmare example) | 1.4 | Draft generated |
| 2 | Neuro-symbolic concept diagram | 2.2 | Not yet created |
| 3 | IRT Protocol Overview | 2.3 | Adapt from existing |
| 4 | Clinical patterns table (maladaptive + adaptive) | 2.4 | Not yet created |
| 5 | Clinical Ontology Graph | 3.1 | ✅ Exists |
| 6 | Bird's-eye system overview | 3.3 | Existing / adapt |
| 7 | Classification component (System 1 vs 2) | 3.4 | Not yet created |
| 8 | Safety Pipeline Architecture | 3.5 | ✅ Exists |
| 9 | Worked end-to-end example | 3.5 | Not yet created (HIGH PRIORITY) |
| 10 | Uncertainty decision flowchart | 3.6 | Not yet created |
| 11 | Dataset composition | 4.1 | Not yet created (matplotlib) |
| 12 | Experimental design matrix | 4.2 | Not yet created |
| 13 | Confusion matrix | 4.3 | Not yet created (matplotlib) |
| 14 | Per-node accuracy chart | 4.3 | Not yet created (matplotlib) |
| 15 | System 1 vs System 2 comparison | 4.3 | Depends on implementation |
| 16 | Uncertainty calibration (ROC/reliability) | 4.3 | Depends on evaluation |
| 17 | Failure case table | 4.4 | Not yet created |
| 18 | Expert agreement summary | 4.5 | Depends on Dr. Gieselmann |

**Summary:** 18 figures planned. 3 exist, 2 can be adapted, ~8 need creation, ~5 depend on pending work.
