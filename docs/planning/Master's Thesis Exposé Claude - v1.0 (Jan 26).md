# **Master's Thesis Exposé Claude**

**Title:** Formalizing Clinical Guidelines: A Knowledge-Graph Augmented Approach to Safety in AI-Based Nightmare Therapy

**Author:** Ramon Zacharias  
 **Supervisor:** Moritz Hartstang MSc., Prof. Dr. Sebastian Musslick  
 **Clinical Advisor:** Dr. Annika Gieselmann

## **1\. Problem Statement & Motivation**

Large Language Models (LLMs) offer a scalable solution for democratizing Imagery Rehearsal Therapy (IRT)—the gold-standard treatment for nightmare disorders. However, their deployment in mediy

cal devices (MDR Class IIa) is hindered by a lack of deterministic safety. Probabilistic models may suggest clinically maladaptive strategies (e.g., avoidance, suppression, or violent revenge) that, while semantically plausible, reinforce trauma and violate clinical guidelines.

To ensure patient safety, this thesis proposes a neuro-symbolic architecture combining the flexibility of LLMs with rigid clinical protocols. Specifically, a Knowledge Graph-Augmented Retrieval (KG-RAG) system will act as a deterministic "Critic," intercepting and correcting maladaptive suggestions via a formalized ontology of IRT clinical guidelines and the Multidimensional Mastery Scale (MMS). When unsafe content is detected, the system generates constraint messages that are incorporated into subsequent prompts to the base LLM to redirect the therapeutic conversation toward adaptive mastery strategies.

While practical deployment motivates this work, the scientific contribution lies in demonstrating that explicit formalization of clinical guidelines as knowledge graphs can provide measurable safety improvements and explainability over implicit learning in LLM-based therapeutic systems. This establishes a methodology for computational operationalization of evidence-based protocols applicable beyond IRT.

## **2\. Research Questions**

**Core Question:** Can a Knowledge Graph-Augmented constraint system significantly reduce the rate of clinically maladaptive suggestions in LLM-generated IRT interventions compared to a baseline LLM?

**Success Criteria:** This thesis will be considered successful if the KG-augmented system demonstrates statistically significant improvement (p \< 0.05) in expert safety ratings compared to baseline. Secondary success includes classifier accuracy \>85% and successful identification of a reliable uncertainty trigger (AUROC \> 0.70). Failure to achieve system-level improvement would indicate that while individual components perform adequately, integration challenges or constraint message design require fundamental revision.

**Specific Questions:**

1. **Reasoning Depth vs. Efficiency:** Does a "System 2" Generative approach (Explicit Grounding & Chain-of-Thought) significantly outperform a "System 1" Direct Classification approach (Implicit Processing) in mapping ambiguous user inputs to clinical safety labels?

2. **Pre-Processing Reliability:** Can a localized smaller-parameter model (12B range) achieve sufficient accuracy in Action Segmentation and Meta-Statement Filtering to serve as an autonomous gatekeeper?

3. **Uncertainty-Error Prediction:** Which uncertainty quantification method better predicts classifier errors and thus provides a more reliable trigger for requesting user clarification: Statistical Confidence (Token Log-Probabilities) or Semantic Consistency (Agreement across stochastic inference chains)?

4. **Clinical Efficacy:** Does the KG-Augmented system achieve significantly higher expert-rated scores on "Safety" and "Guideline Adherence" compared to a baseline IRT system without the critic module?

## **3\. Methodology**

The thesis employs an "Engineering & Validation" approach using synthetic "Critical Incident" stress testing.

### **Phase 1: Knowledge Engineering (The Graph)**

A Knowledge Graph (KG) will be constructed to serve as rigid semantic anchors, digitizing clinical IRT protocols:

* **Maladaptive Nodes (Risk):** Defined using IRT clinical guidelines (Krakow & Zadra, 2006), DSM-5 PTSD avoidance criteria, and empirical evidence from IRT research (Krakow et al., 2001). Specific patterns like "Avoidance," "Interruption/Waking," "Suppression," "Violent Revenge," and "Trauma Replay" are encoded with detailed clinical attributes.
* **Adaptive Nodes (Goal):** Defined using MMS (Germain et al., 2004). Patterns like "Social Mastery" (seeking help), "Behavioral Mastery" (active confrontation), "Environmental Mastery," "Emotional Mastery," and "Mythical Mastery" are encoded as therapeutic goal states.

The complete ontology will be validated by Dr. Annika Gieselmann to ensure clinical fidelity. While the graph maintains detailed node classifications for clinical precision in constraint message generation, **evaluation focuses on binary safety classification** (Safe/Unsafe) to provide clear, interpretable metrics for medical device validation.

**Phase 1 Summary:** This phase produces a clinically validated knowledge graph encoding IRT protocols, serving as the semantic foundation for the safety classifier and enabling explainable constraint generation.

### **Phase 2: System Architecture (The "Critic" Pipeline)**

A modular Python pipeline compares two "Neural Grounding Strategies" for mapping user text to safety classifications.

**1\. Input Processing (The Gatekeeper):** A smaller-parameter model (12B range) serves as the pre-processing unit, performing Action Segmentation (decomposing narratives into discrete actions) and Meta-Statement Filtering (removing non-dream commentary) to sanitize input.

**2\. The Safety Classifier (Comparative Architecture):** To isolate the impact of reasoning depth, two architectures are evaluated using lightweight models (20-30B parameter range). Both receive structured context comprising the Anchor (Original Nightmare) and Trajectory (Dialogue History).

**Classification Logic:** Actions within a turn are evaluated independently. Following IRT principles that discourage rehearsal of maladaptive patterns, any maladaptive action flags the entire turn as unsafe, even if followed by adaptive corrections. This conservative design choice prioritizes patient safety and will be validated by clinical experts during ontology review.

* **Approach A (System 1 \- Direct):** A lightweight LLM performs direct clinical classification via few-shot prompting, relying on implicit context processing.

* **Approach B (System 2 \- Reasoned):** A generative model utilizing Constrained Structured Generation (JSON Schema) to enforce explicit reasoning through three steps:

  1. Context Summary: Explicit grounding of scene facts
  2. Clinical Rationale: Chain-of-Thought derivation using IRT clinical guidelines and maladaptive pattern definitions
  3. Safety Classification: Binary safe/unsafe determination

**3\. Uncertainty Quantification:** Both architectures employ two uncertainty metrics:

* **Token Confidence:** Examining log-probabilities of generated tokens (low confidence indicates model uncertainty)  
* **Semantic Consistency:** Running 5 stochastic inference chains (temperature=0.7) and measuring agreement via percentage match across classifications. High consistency (≥80% agreement) indicates epistemic certainty; low consistency suggests the model is uncertain about the correct label.

These metrics are evaluated for their ability to predict classifier errors, identifying which better serves as a trigger for requesting user clarification when the system encounters ambiguous inputs.

**4\. Constraint Message Generation & Validation:** When unsafe content is detected, the system generates constraint messages following a standardized template: (1) Identified maladaptive pattern, (2) Clinical rationale for concern, (3) Specific adaptive alternative drawn from MMS categories.

A pilot evaluation (n=20, 4 per maladaptive category) validates that these messages successfully redirect the base LLM. Clinical experts rate redirected responses as Adaptive, Neutral, or Maladaptive. The template is iteratively refined until achieving ≥80% Adaptive or Neutral ratings (a threshold chosen to balance constraint effectiveness with practical iteration limits). If this threshold cannot be achieved after three iterations, constraint message design will be identified as a system limitation requiring future research.

**Phase 2 Summary:** This phase establishes the critic architecture, comparing reasoning approaches and validating that constraint messages effectively redirect the therapeutic LLM before full-scale evaluation.

### **Phase 3: Critical Incident Simulation & Validation**

The system is validated on 100 Synthetic "Critical Incidents" representing both specific failure modes and adaptive successes, generated using GPT-5.2 to ensure consistent clinical patterns. To enable robust error analysis and statistical power for subtype evaluation, the dataset is distributed as follows:

* **60 Maladaptive Incidents (Unsafe):** 20 cases each for **Avoidance**, **Violent Revenge**, and **Interruption**. This balanced distribution across your three core risk categories ensures that the safety classifier's performance is not skewed by a single failure mode.  
* **40 Adaptive Mastery Incidents (Safe):** 40 inputs representing various goal states (e.g., Behavioral, Social, or Emotional Mastery). These serve as a control group to measure the system's specificity and "False Positive" rate, ensuring the safety layer does not obstruct valid therapeutic progress.

All incidents are annotated by a clinical psychologist as Ground Truth. While real-world prevalence rates differ, this balanced design enables a rigorous assessment of the system's ability to discriminate between clinically harmful and helpful user inputs.

**Validation Approach:**

**Step 1 \- Segmentation Validation:** Validate the segmentation model's accuracy against expert annotations to establish preprocessing reliability.

**Step 2 \- Two-Stage Classifier Evaluation:**

* **Primary (Gold Segments):** Test both classifier architectures on expert-annotated segments to establish upper-bound classifier performance and isolate reasoning capabilities from preprocessing errors  
* **Secondary (Real Segmentation):** Test the best-performing classifier on the segmentation model's output to establish realistic performance with preprocessing errors. The performance gap quantifies segmentation's impact on classification accuracy.

**Step 3 \- Uncertainty-Error Analysis:** For each classification:

* Record both uncertainty metrics (token confidence, semantic consistency)  
* Record classification correctness (vs. expert ground truth)  
* Plot uncertainty vs. accuracy to assess whether high-uncertainty cases correlate with errors  
* For each metric, identify the threshold that maximizes correct error prediction  
* Compare metrics using AUROC: Which better predicts when the classifier will make mistakes?

The metric with higher AUROC for error prediction becomes the recommended clarification trigger. If metrics perform comparably (ΔAUROC \< 0.05), both will be recommended for ensemble-based triggering in future implementations.

**Statistical Considerations:** With n=100 and α=0.05, this design provides 80% power to detect medium-to-large effects (Cohen's d ≥ 0.5) in the primary comparison. Smaller effects will be acknowledged as preliminary evidence requiring replication with larger samples.

**Phase 3 Summary:** This phase validates three critical components—segmentation accuracy (Step 1), classifier performance under ideal and realistic conditions (Step 2), and uncertainty metrics for error prediction (Step 3)—establishing both upper-bound capabilities and real-world performance expectations.

### **Phase 4: System-Level Comparative Evaluation**

**Evaluation Design Philosophy:**

This thesis employs two complementary evaluation strategies:

1. **Component Analysis (Classifier):** Controlled evaluation on gold-standard segments establishes the safety classifier's intrinsic capabilities, comparing System 1 vs. System 2 architectures and characterizing uncertainty metrics.

2. **System-Level Comparison:** End-to-end evaluation compares the full KG-augmented system against baseline on expert safety ratings. This real-world assessment captures the combined effects of segmentation, classification, and constraint-based intervention, demonstrating whether formalized clinical knowledge improves therapeutic AI safety in practice.

While component metrics establish technical feasibility, system-level outcomes determine clinical utility. The gap between component performance and system outcomes represents the integration challenges inherent in multi-stage architectures—a limitation acknowledged for future detailed ablation studies.

**Primary Comparison:** KG-augmented system (best-performing classifier \+ constraint messages) vs. Baseline IRT system

**Baseline Definition:** The baseline consists of the same base LLM with standard IRT prompting but without the critic module. The KG-augmented system uses the identical base LLM and IRT prompt, enhanced with constraint messages generated by the critic when maladaptive content is detected.

**Evaluation Protocol:** Single-turn evaluation where experts assess system responses to critical incidents.

**Metrics:**

* **Component-Level (Classifier):** Binary classification accuracy (Safe/Unsafe) on both gold-standard and real segments, with precision, recall, and F1 scores; uncertainty metric comparison via AUROC  
* **System-Level:** One independent clinical psychologist and one researcher with IRT expertise rate full system outputs (baseline vs. KG-augmented) on Safety, Clinical Appropriateness, and IRT Guideline Adherence (1-5 Likert scale). Inter-rater reliability will be assessed to ensure rating consistency.  
* **Secondary:** Error analysis by maladaptive subtype to identify failure patterns

**Hypothesis:** The KG-augmented system will show statistically significant improvement in safety ratings compared to baseline, demonstrating that formalized clinical ontologies can enforce protocol adherence.

**Phase 4 Summary:** This phase provides the definitive comparison between baseline and KG-augmented systems, integrating component insights into a holistic assessment of whether knowledge graph formalization improves therapeutic AI safety in practice.

## **4\. Expected Outcomes**

1. **Clinical Artifact:** A validated, reusable knowledge graph encoding IRT clinical protocols (MMS and maladaptive pattern ontology) as a .json file, enabling transparent and explainable safety decisions  
2. **Benchmark Dataset:** 100 expert-annotated Critical Incidents serving as a gold standard for safety testing in therapeutic AI  
3. **Architectural Evidence:** Quantitative comparison identifying the superior safety classifier architecture ("System 1" vs. "System 2"), quantification of segmentation impact on classifier performance, and identification of the optimal uncertainty metric for human-in-the-loop triggers  
4. **Scientific Contribution:** Demonstrating that explicit formalization of therapeutic protocols as knowledge graphs improves safety and explainability in LLM-based mental health interventions compared to implicit learning approaches. This establishes a generalizable methodology for computational operationalization of evidence-based clinical guidelines, with applications extending beyond IRT to other protocol-driven therapeutic domains.

## **5\. Scope & Limitations**

**Thesis Focus:** This work establishes the feasibility of knowledge-graph augmented safety systems for therapeutic AI. The safety classifier component receives detailed controlled evaluation, while system-level assessment demonstrates practical utility through end-to-end comparison against baseline.

**Limitations:**

* Sample size of n=100 limits detectable effect sizes to medium-to-large effects (d ≥ 0.5)  
* Synthetic critical incidents may not capture full complexity of real patient responses  
* Binary safety classification prioritizes clear evaluation over nuanced trajectory analysis  
* Integration effects (interactions between segmentation, classification, and intervention) are assessed at system level but not fully disentangled through comprehensive ablation studies

**Future Work:** Detailed ablation studies to isolate individual component contributions, human-in-the-loop refinement mechanisms for continuous improvement, longitudinal evaluation with real patients, and generalization to other therapeutic domains (e.g., Exposure Therapy, CBT) include directions for future research beyond thesis scope.

