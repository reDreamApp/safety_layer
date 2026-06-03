# Thesis LaTeX and Writing Guide

Status: working reference for writing the ReDream AI master's thesis in LaTeX.

This guide merges the current `Thesis Structure.docx` and `Writing Guide V2.docx` into the repository so the LaTeX draft, argument structure, and writing constraints stay synchronized.

## Working Thesis

**Title:** ReDream AI: A Neuro-Symbolic Safety Layer for AI-Assisted Imagery Rehearsal Therapy

**Main research question:** Can a neuro-symbolic, knowledge-graph-augmented safety layer reduce clinically maladaptive content and improve IRT guideline adherence compared with an unconstrained baseline LLM?

**Framing constraint:** The thesis argues for a protocol-aware safety layer for IRT rescripting, not for a fully autonomous therapy system.

**Strongest claim:** The system provides protocol-aware detection, correction signals, uncertainty information, and auditability.

**Avoid claiming:** clinical efficacy, treatment effectiveness, standalone therapeutic readiness, or guaranteed safety.

## Source Files

The LaTeX project lives in `thesis/`.

| File | Purpose |
| --- | --- |
| `thesis/main.tex` | Document order and top-level front matter |
| `thesis/metadata.tex` | Title, author, university, supervisor, date |
| `thesis/preamble.tex` | Packages, bibliography style, layout settings |
| `thesis/chapters/*.tex` | Chapter prose |
| `thesis/references.bib` | BibLaTeX bibliography, currently seeded from the Chapter 3 draft |
| `thesis/figures/` | Thesis figures copied or generated for final use |
| `thesis/tables/` | Large table snippets, if separated from chapters |

Build command:

```bash
cd thesis
make pdf
```

The local machine currently needs a TeX toolchain installed before this can compile.

## Chapter Structure

### 1. Introduction

Goal: establish the clinical problem, the treatment gap, the AI opportunity, and the need for explicit safety.

Sections:

1.1 Nightmares and Nightmare Disorder as a Clinical Problem
- 1.1.1 Prevalence and Clinical Burden
- 1.1.2 Diagnostic Criteria of Nightmare Disorder
- 1.1.3 Clinical Relevance for PTSD and Mental Health

1.2 Imagery Rehearsal Therapy and the Treatment Gap
- 1.2.1 IRT as an Evidence-Based Treatment
- 1.2.2 Limited Awareness and Access
- 1.2.3 Motivation for Scalable Support

1.3 AI-Assisted Mental Health Interventions
- 1.3.1 Growing Use of AI for Mental Health Support
- 1.3.2 Existing AI Mental Health Approaches
- 1.3.3 Opportunity for AI-Assisted IRT

1.4 The Safety Challenge in AI-Mediated IRT
- 1.4.1 General Limitations of LLMs
- 1.4.2 Risks in Mental Health Contexts
- 1.4.3 Risks in IRT Rescripting
- 1.4.4 Need for an Explicit Clinical Safety Layer

1.5 Research Questions and Evaluation Strategy
- 1.5.1 Main Research Question
- 1.5.2 RQ1: Detection and Classification Reliability
- 1.5.3 RQ2: Classifier Design and Pipeline Components
- 1.5.4 RQ3: Uncertainty Quantification
- 1.5.5 RQ4: System-Level Safety and Guideline Adherence
- 1.5.6 Success Criteria

1.6 Contributions
- 1.6.1 Clinical Safety Ontology for IRT Rescripting
- 1.6.2 Benchmark Dataset for IRT Safety Classification
- 1.6.3 Neuro-Symbolic Safety Critic Pipeline
- 1.6.4 Methodological Contribution: Formalizing Protocol-Specific Clinical Safety

1.7 Thesis Outline

Figure 1.1: safety problem example in AI-assisted IRT.

### 2. Background and Related Work

Goal: provide enough clinical and technical context for the contribution.

Sections:

2.1 LLMs in Mental Health Applications
- 2.1.1 Existing Digital Mental Health Chatbots
- 2.1.2 LLM-Based Mental Health Support
- 2.1.3 Safety Limitations of Existing Approaches

2.2 Neuro-Symbolic Approaches to AI Safety
- 2.2.1 Definition and Basic Idea
- 2.2.2 Benefits for Safety-Critical Systems
- 2.2.3 Relevance for Clinical LLM Safety

2.3 Imagery Rehearsal Therapy as the Clinical Use Case
- 2.3.1 Treatment Rationale of IRT
- 2.3.2 Structure of the IRT Protocol
- 2.3.3 The Rescripting Stage as the Safety-Critical Point

2.4 Adaptive and Maladaptive Rescripting Patterns as Clinical Safety Categories
- 2.4.1 Adaptive Rescripting Patterns
- 2.4.2 Maladaptive Rescripting Patterns
- 2.4.3 From Clinical Patterns to Computational Categories

Figure 2.1: IRT protocol flow.
Table 2.1: adaptive and maladaptive rescripting patterns.
Figure 2.2: conceptual neuro-symbolic framing.

### 3. Neuro-Symbolic Safety Layer

Goal: present the main artifact.

Sections:

3.1 Clinical Safety Ontology for IRT Rescripting
- 3.1.1 Ontology Category Set
- 3.1.2 Category Attributes and Severity Levels
- 3.1.3 Corrective Mappings Between Maladaptive and Adaptive Categories
- 3.1.4 Graph Representation of Correction Relationships

3.2 Ontology Development and Clinical Validation
- 3.2.1 Literature-Based Construction
- 3.2.2 Clinical Rationale and Ontology Boundaries
- 3.2.3 Expert Review Process

3.3 System Overview and Integration Point
- 3.3.1 Baseline IRT Chatbot Flow
- 3.3.2 Safety Layer Placement in the Rescripting Stage
- 3.3.3 Safety Layer Inputs and Outputs
- 3.3.4 Constraint-Based Integration

3.4 LLM-Based Clinical Classification
- 3.4.1 Classification as Entity Linking to Ontology Categories
- 3.4.2 System 1: Direct Classification
- 3.4.3 System 2: Structured Clinical Reasoning
- 3.4.4 Prompt Rules, Labels, and Ambiguity Handling

3.5 Safety Critic Pipeline
- 3.5.1 Intelligent Segmentation
- 3.5.2 Meta-Statement Filtering
- 3.5.3 Segment-Level Classification
- 3.5.4 Finding Aggregation and Severity Triage
- 3.5.5 Constraint Synthesis
- 3.5.6 Worked End-to-End Example

3.6 Uncertainty Estimation and Risk Signaling
- 3.6.1 Token Log-Probability Confidence
- 3.6.2 Semantic Consistency
- 3.6.3 Uncertainty Signals and Severity-Based Risk Flags

3.7 Architectural Trade-Offs and Limitations
- 3.7.1 Clinical Ontology vs. Prompting Alone
- 3.7.2 Rationale for LLM-Based Classification
- 3.7.3 Pipeline Modularity and Preprocessing Trade-Offs
- 3.7.4 Limitations of the Implemented Design

Figures 3.1-3.5: ontology graph, system overview, optional S1/S2 classifier comparison, safety pipeline, worked example.

### 4. Evaluation

Goal: show classification reliability, uncertainty usefulness, component contributions, and system-level safety effects.

Sections:

4.1 Evaluation Design and Dataset Rationale
- 4.1.1 Evaluation Goals
- 4.1.2 Rationale for Synthetic Benchmarking
- 4.1.3 Dataset Construction
- 4.1.4 Scenario and Category Coverage
- 4.1.5 Human / Expert Annotation Material

4.2 Experimental Conditions and Metrics
- 4.2.1 Classifier Variants: System 1 and System 2
- 4.2.2 Pipeline Variants and Ablations
- 4.2.3 Uncertainty Methods: Log-Probabilities and Semantic Consistency
- 4.2.4 Evaluation Metrics
- 4.2.5 Reproducibility and Implementation Details

4.3 Component-Level Classification Results
- 4.3.1 Overall Safety Classification Performance
- 4.3.2 Node-Level Classification Performance
- 4.3.3 System 1 vs. System 2 Comparison
- 4.3.4 Effect of Semantic Consistency

4.4 Ablation and Pipeline Analysis
- 4.4.1 Contribution of Pipeline Components
- 4.4.2 Effect of Preprocessing and Input Structuring
- 4.4.3 Error Patterns Introduced or Resolved by Pipeline Variants

4.5 Failure Analysis and Edge Cases
- 4.5.1 Common Misclassification Patterns
- 4.5.2 Boundary Cases Between Adaptive and Maladaptive Categories
- 4.5.3 Clinically Relevant Failure Modes
- 4.5.4 Implications for System Safety

4.6 Uncertainty Quantification Results
- 4.6.1 Log-Probability as Error Signal
- 4.6.2 Semantic Consistency as Error Signal
- 4.6.3 Comparison of Uncertainty Methods

4.7 System-Level and Expert Evaluation
- 4.7.1 Baseline vs. Safety-Augmented Outputs
- 4.7.2 Expert Rating Protocol
- 4.7.3 Analysis of Expert Ratings and Qualitative Feedback
- 4.7.4 System-Level Findings and Limitations

Current headline results to incorporate carefully:

| Setting | Safety accuracy | Unsafe recall | Note |
| --- | ---: | ---: | --- |
| S1 baseline | 97.86% | 99.44% | Post-fix full dev benchmark |
| S1 consistency, N=5 | 97.86% | 99.44% | No overall gain |
| S2 baseline | 98.10% | 99.44% | Slight accuracy gain |
| S2 consistency, N=5 | 98.81% | 98.33% | Best accuracy, lower unsafe recall |

Interpretation rule: do not oversell. The best system improves overall accuracy but trades off some unsafe recall, and that trade-off needs explicit discussion.

### 5. Discussion

Goal: interpret the result, state limitations honestly, and identify responsible use.

Sections:

5.1 Summary and Interpretation of Findings
- 5.1.1 Answering the Main Research Question
- 5.1.2 Component-Level Findings
- 5.1.3 System-Level Findings
- 5.1.4 Interpretation of Uncertainty and Ablation Results

5.2 Relation to Existing Approaches
- 5.2.1 Compared with Generic LLM Safety Mechanisms
- 5.2.2 Compared with Existing Mental Health Chatbots
- 5.2.3 Contribution of Clinical Formalization

5.3 Limitations
- 5.3.1 Synthetic Dataset and Ecological Validity
- 5.3.2 Expert Validation and Annotation Scope
- 5.3.3 Model Dependence and Reproducibility
- 5.3.4 Integration Limitations of the Chatbot System
- 5.3.5 Scope of the Ontology and Clinical Coverage

5.4 Clinical and Ethical Implications
- 5.4.1 Role of Human Oversight
- 5.4.2 Risks of Over-Reliance on Automated Safety Layers
- 5.4.3 Privacy, Sensitive Content, and Deployment Constraints
- 5.4.4 Appropriate Use: Clinician-Supported Rather Than Standalone Therapy

5.5 Future Work
- 5.5.1 Evaluation with Real or Clinician-Curated IRT Material
- 5.5.2 Improved Integration into the Base Chatbot
- 5.5.3 Therapist-in-the-Loop Workflows and Review Interfaces
- 5.5.4 Human-in-the-Loop Review and Threshold Calibration
- 5.5.5 Refinement of the Ontology and Constraint Generation
- 5.5.6 Extension to Other Therapeutic Protocols
- 5.5.7 Longitudinal and Clinical Deployment Studies

### 6. Conclusion

Goal: give the final answer to the research question, summarize the ontology, benchmark/evaluation, and safety critic pipeline, and close with the broader significance of clinically grounded safety layers for protocol-aware AI systems.

## Writing Rules

### Top-down drafting

Write each section in this order:

1. Key claim in one sentence.
2. Three to five bullet points that support the claim.
3. Figure or table needed, if any.
4. Prose.

### Paragraph shape

Use this pattern:

1. Topic sentence.
2. Evidence or reasoning.
3. Transition to the next paragraph.

Avoid burying the point. If a paragraph only says "this is complex," replace it with the specific reason it matters.

### Tone

Use precise academic prose, but keep the argument readable. The thesis should sound clinically careful and technically concrete.

Prefer:

- "The safety layer constrains responses during the rescripting stage."
- "This result suggests a precision-recall trade-off."
- "The system is evaluated as a safety critic, not as an autonomous therapist."

Avoid:

- Marketing language.
- Claims of clinical efficacy.
- Claims that synthetic data proves real-world safety.
- Vague safety terms without tying them to the ontology.

### Terminology

Use these terms consistently:

| Preferred term | Avoid mixing with |
| --- | --- |
| Imagery Rehearsal Therapy | IRT therapy |
| rescripting | changing the dream, modifying the nightmare |
| rewriting action | response, behavior, coping strategy, user action |
| maladaptive pattern | unsafe node, bad response, harmful behavior |
| adaptive mastery | safe pattern, good response |
| safety layer | guardrail, filter, moderator |
| critic pipeline | classifier pipeline, detection system |
| entity linker | classifier, labeler, mapper |
| semantic consistency | self-consistency, voting, repeated sampling |

Use **rewriting action** for the unit that the safety layer evaluates: an action, reaction, or change that the client introduces while rewriting the nightmare. The safety layer is not judging whether the dream content is distressing; it is identifying and redirecting the client's proposed rewriting actions.

## Citation Workflow

Current bibliography status: Chapter 3 currently cites one source, `germain2004mastery`, which is now in `thesis/references.bib`.

For future Zotero imports:

1. In Zotero, create or select the thesis collection.
2. Export the collection as Better BibLaTeX if the Better BibTeX plugin is installed, otherwise export as BibLaTeX.
3. Save or overwrite `thesis/references.bib`.
4. In LaTeX, cite with `\textcite{key}` for narrative citations and `\parencite{key}` for parenthetical citations.

If the current draft is in Google Docs with Zotero citations:

1. Export the Google Doc as `.docx` or paste the section text.
2. Export the matching Zotero collection to `thesis/references.bib`.
3. Convert headings, paragraphs, figures, and citation placeholders into chapter `.tex` files.
4. Compile, fix missing citation keys, and normalize terminology.

Important: Google Docs Zotero citations do not always preserve citation keys in plain text. Exporting the matching Zotero collection is what lets us map prose citations to stable LaTeX keys.

## LaTeX Conventions

Use labels for anything referenced later:

```latex
\section{Safety Critic Pipeline}
\label{sec:safety-critic-pipeline}

\begin{figure}
  \centering
  \includegraphics[width=0.9\linewidth]{safety_pipeline_architecture}
  \caption{Overview of the critic pipeline.}
  \label{fig:safety-pipeline}
\end{figure}
```

Reference with:

```latex
\Cref{fig:safety-pipeline} shows ...
\Cref{sec:safety-critic-pipeline} explains ...
```

Use `\todo{...}` for placeholders. Before submission, search for:

```bash
rg "\\todo|TODO" thesis
```

## Current Open Decisions

1. Replace placeholder university, department, and supervisor in `thesis/metadata.tex`.
2. Decide whether the final thesis should use an official university LaTeX template.
3. Gather existing figure files into `thesis/figures/` and standardize filenames.
4. Replace figure and table placeholders with final generated assets.
5. Continue converting prose section by section from Google Docs or `.docx`.
