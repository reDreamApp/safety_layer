# **Master's Thesis Exposé V3 (Revised)**

**Title:** Formalizing Clinical Guidelines: A Knowledge-Graph Augmented Approach to Safety and Mastery in AI-Based Nightmare Therapy

**Author:** Ramon Zacharias **Supervisor:** Prof. Dr. Sebastian Musslick

## **1\. Problem Statement & Motivation**

Large Language Models (LLMs) have demonstrated significant capabilities in general psychotherapeutic interactions. This technological maturity presents a novel opportunity to automate accessible interventions like Imagery Rehearsal Therapy (IRT) for nightmare disorders—a treatment currently limited by a shortage of trained specialists and a pervasive lack of clinical dissemination, which prevents widespread patient access. However, a critical barrier to their deployment in clinical settings—and specifically in medical devices (MDR Class IIa)—is the lack of deterministic safety. Standard LLMs are probabilistic; they may occasionally suggest "maladaptive" coping strategies (e.g., avoidance, suppression, or violent revenge) that, while semantically plausible, directly contradict clinical guidelines and can reinforce trauma.

Current "black box" approaches rely on prompt engineering or fine-tuning, which cannot guarantee adherence to rigid medical protocols. To ensure patient safety, there is a need for **Neuro-Symbolic architectures** that combine the generative flexibility of LLMs with the rigid, rule-based logic of clinical manuals.

This thesis proposes a specific solution: A **Knowledge Graph-Augmented Retrieval (KG-RAG)** system that "supervises" the LLM. By formalizing established clinical coding systems—specifically the *Zürich Dream Process Coding System* (Moser & Hortig, 2019\) and the *Multidimensional Mastery Scale* (Germain et al., 2004)—into a computational graph, the system can deterministically detect and correct maladaptive suggestions before they reach the user.

## **2\. Central Research Questions**

**Core Question:** Can a Knowledge Graph-based constraint system significantly reduce the rate of clinically maladaptive suggestions in LLM-generated IRT interventions compared to a baseline LLM?

**Specific Questions:**

1. **Formalization:** How can the qualitative clinical rules of IRT (e.g., "Avoidance vs. Approach," "Behavioral Mastery") be translated into a machine-readable Knowledge Graph ontology?  
2. **Architecture:** How can this graph be integrated into an inference pipeline to act as a "Critic" that intercepts and corrects harmful outputs (e.g., transforming an "avoidance" suggestion into a "mastery" suggestion)?  
3. **Evaluation:** Does the KG-Augmented system achieve higher expert-rated scores on "Safety" and "Clinical Adherence" in a blind comparison against a standard GPT-4/Llama-3 baseline?

## **3\. Methodology**

The thesis follows a strict "Engineering & Validation" approach, avoiding the need for large-scale patient data collection by using synthetic "Critical Incident" testing.

### **Phase 1: Knowledge Engineering (The Graph)**

Instead of relying on subjective team knowledge, the Knowledge Graph (KG) will be constructed by digitizing two "Gold Standard" clinical frameworks:

* **Maladaptive Nodes (Avoidance):** Defined using the *Zürich Dream Process Coding System (ZDPCS)* (Moser & Hortig, 2019). The graph will encode concepts like "Flight," "Waking Up," and "Suppression" as `Safety_Risk: High`.  
* **Adaptive Nodes (Mastery):** Defined using the *Multidimensional Mastery Scale* (Germain et al., 2004). The graph will encode concepts like "Social Mastery" (seeking help) and "Behavioral Mastery" (fighting back) as `Goal_State`.

### **Phase 2: System Architecture (The "Critic")**

A Python-based pipeline will be developed (using LangChain/NetworkX):

1. **Input:** User describes a nightmare and a proposed change (e.g., "I run away").  
2. **Entity Linking:** The system maps the input to the KG (e.g., "Running away" $\\rightarrow$ `ZDPCS: Avoidance`).  
3. **Constraint Check:** The KG returns the rule: *Avoidance is maladaptive. Suggest Mastery.*  
4. **Generation:** The LLM is prompted with this specific constraint to generate the therapeutic response.

### **Phase 3: Critical Incident Simulation (The Experiment)**

To ensure reproducibility, the system will be tested on **100 Synthetic "Critical Incidents"**:

* Using GPT-4, I will generate 100 standardized patient inputs representing specific "Failure Modes" (e.g., 20 inputs of severe avoidance, 20 inputs of violent revenge, 20 inputs of hopelessness).  
* These inputs will be fed to both (A) The Baseline Model and (B) The Thesis KG-Model.

### **Phase 4: Comparative Evaluation**

* **Metric:** Blind expert rating (Inter-Rater Reliability) by clinical psychologists (e.g., team members Katharina Lüth / Dr. Gieselmann).  
* **Scoring:** Responses will be graded on a 1-5 Likert scale for *Safety*, *Empathy*, and *Adherence to IRT Guidelines*.  
* **Hypothesis:** The KG-Model will show a statistically significant reduction in "Safety Violations" (scores \< 3).

## **4\. Expected Outcomes**

1. **A "Safety Graph" Artifact:** A reusable `.json` or `.gml` file containing the formalized logic of Imagery Rehearsal Therapy.  
2. **A Validated Architecture:** A prototype pipeline that demonstrates how to restrict LLMs using clinical guidelines.  
3. **Scientific Evidence:** Quantitative data proving that symbolic constraints improve safety in mental health AI.

This work directly contributes to the "Explainability" and "Safety" modules required for the *reDreamAI* medical device certification.

