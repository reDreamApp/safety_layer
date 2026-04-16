# ReDream AI — Thesis Structure (Draft v1)
## Neuro-Symbolic Safety Layer for AI-Assisted Imagery Rehearsal Therapy

*Ramon Zacharias — February 2026*

---

## 1. Introduction
- 1.1 Problem & Motivation
- 1.2 Research Questions & Objectives
- 1.3 Contributions
- 1.4 Thesis Outline

**Key figure:** System overview — full IRT chatbot with safety layer highlighted. This is the "map" figure that readers refer back to throughout the thesis.

---

## 2. Background & Related Work
- 2.1 Nightmare Disorder & IRT Protocol
- 2.2 Maladaptive vs. Adaptive Rescripting Patterns (Germain 2004, MMS)
- 2.3 LLMs in Mental Health Applications
- 2.4 Neuro-Symbolic Approaches to AI Safety

**Key figures:**
- Clinical ontology graph (5 maladaptive → correction edges → 5 adaptive nodes). Probably the single most important figure in the thesis.
- Timeline/overview of IRT protocol steps

---

## 3. Neuro-Symbolic Safety Layer *(Core Contribution)*
- 3.1 IRT Chatbot Architecture & Integration Point
- 3.2 Clinical Knowledge Graph (Block A) — ontology design, node/edge rationale
- 3.3 Ontology Validation — process with Dr. Gieselmann, iterations, outcome
- 3.4 LLM-Based Entity Linker (Block B) — classification, confidence estimation, negation handling
- 3.5 Critic Pipeline (Block C) — segmentation → META filtering → batch classification → severity triage → constraint synthesis
- 3.6 Uncertainty Handling & User Clarification — when confidence is below threshold, the system asks the user to clarify intent rather than acting autonomously; severe cases (e.g., trauma replay, self-harm indicators) escalate directly to therapist/emergency services
- 3.7 Design Decisions & Trade-offs

**Key figures:**
- Flowchart: user message → safety check → response (Moritz specifically requested this)
- One architecture diagram per block (A, B, C)
- End-to-end pipeline diagram showing all three blocks connected
- Worked example: a maladaptive input flowing through all three blocks step by step
- Decision flowchart: confidence threshold → clarify with user vs. proceed vs. escalate to therapist/emergency

---

## 4. Evaluation
- 4.1 Dataset & Scenario Design
- 4.2 Benchmark Protocol
- 4.3 Quantitative Results (classifier accuracy, confidence calibration, system-level)
- 4.4 Expert Evaluation & Qualitative Feedback (ratings, notable opinions, disagreements)
- 4.5 Failure Analysis & Edge Cases

**Key figures:**
- Confusion matrix / classification results
- Confidence distribution plots
- Table of example classifications (correct, interesting failures, edge cases)
- Expert rating summary

---

## 5. Discussion
- 5.1 Interpretation of Results
- 5.2 Limitations
- 5.3 Clinical & Ethical Implications
- 5.4 Relation to Existing Work

---

## 6. Conclusion & Future Work
- 6.1 Summary
- 6.2 Generalizability — Applying the Methodology to Other Domains (e.g., CBT-I, exposure therapy, other therapeutic AI applications: how the 3-block pattern transfers when the knowledge graph and classification targets change)
- 6.3 Future Work — including: using user corrections from clarification dialogues as training signal to improve the classifier over time (human-in-the-loop learning), threshold calibration experiments

---

## Notes

**Moritz's guidance:** 80% of the thesis should be understandable through figures alone. Start visual early — structure thoughts, process, and results graphically. Text comes last.

**Sebastian's tips:** Work top-down (headings → key statements → arguments → prose). Each paragraph: topic sentence → arguments → transition. Don't bury the lede. Consistency in terminology. Minimize cognitive load. Cut ruthlessly.

**Next step:** For each sub-section, formulate 2-3 key statements (bullet points) before writing any prose.
