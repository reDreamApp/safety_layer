**Topic:** Formalizing Clinical Guidelines (Neuro-Symbolic AI for Safety) **Author:** Ramon Zacharias

## **Phase 0: START RIGHT NOW (Week 0\)**

Before you write a single line of code, download and skim these 4 documents. They are the "Source of Truth" for your Knowledge Graph.

### **1\. The Clinical "Ground Truth" (Psychology)**

**Paper 1 (The Mastery Scale)**

* **Citation:** Germain, A., Krakow, B., et al. (2004). "Increased Mastery Elements Associated With Imagery Rehearsal Treatment..."  
* **Your Task:** Go to the "Measures" section. Copy the definitions of **Behavioral**, **Social**, and **Emotional Mastery** into a text file. These are your "Good" nodes.

**Paper 2 (The Coding System)**

* **Citation:** Fischmann, T., Leuzinger-Bohleber, M., & Moser, U. (2021). "Dreams and Trauma: Changes in the Manifest Dreams..." (Frontiers in Psychology).  
* **Your Task:** Look for the "Zurich Dream Process Coding System (ZDPCS)" section. Find the logic for **"Avoidance"** vs. **"Approach."** These are your "Bad" vs. "Good" nodes.

**Paper 3 (The Guideline)**

* **Citation:** Aurora, R. N., et al. (2010). "Best practice guide for the treatment of nightmare disorder in adults." (AASM).  
* **Your Task:** Read the abstract and the specific recommendation for IRT. This is your "Why" for the introduction.

### **2\. The Technical Architecture (AI)**

**Paper 4 (Neuro-Symbolic Concept)**

* **Citation:** Sarkas et al. (2023) or similar recent surveys on "Neuro-symbolic AI" or "Constrained Text Generation".  
* **Your Task:** Understand the concept of a "Critic" or "Guardrail" in LLMs. You don't need to replicate their code, just understand the architecture.

## **Phase 1: Knowledge Engineering (Dec/Jan)**

**Goal:** Convert PDF text into a structured JSON file. **No complex coding yet.**

* **Weeks 1-2: Ontology Definition**  
  * Create a spreadsheet.  
  * Column A: "Concept" (e.g., Running Away).  
  * Column B: "Category" (e.g., Avoidance).  
  * Column C: "Safety Risk" (High).  
  * Review this list with Katharina/Dr. Gieselmann. Get them to "sign off" on it.  
* **Weeks 3-4: Graph Construction**  
  * Convert the spreadsheet into a JSON or NetworkX format.  
  * Write a simple Python script to load this file and search for keywords (e.g., `search_graph("I want to wake up")` \-\> Returns `Avoidance`).

## **Phase 2: The "Critic" Pipeline (Feb)**

**Goal:** Build the Python backend (Startup Synergy: This becomes your App's safety layer).

* **Weeks 5-6: The "Entity Linker"**  
  * Use a lightweight LLM (or simple string matching) to map User Input \-\> Graph Nodes.  
  * *Milestone:* Your script can take a sentence and output the "Clinical Code."  
* **Weeks 7-8: The RAG Pipeline**  
  * Set up LangChain.  
  * Create the "System Prompt" that takes the Graph Output and instructs the LLM.  
  * *Draft Prompt:* "The clinical guideline for this input is \[AVOIDANCE\]. You must suggest a \[MASTERY\] alternative."

## **Phase 3: Simulation & Data Gen (Mar)**

**Goal:** Create the dataset for your experiment.

* **Weeks 9-10: The "Patient Simulator"**  
  * Write a script using GPT-4 API.  
  * Prompt it to generate **100 Critical Incidents** (20 Avoidance, 20 Violence, 20 Hopelessness, 20 Magic, 20 Success).  
  * Save this as `test_dataset.csv`.  
* **Weeks 11-12: The Dry Run**  
  * Run the 100 inputs through your "Thesis Model."  
  * Debug. If the AI still suggests violence, tweak your System Prompt.

## **Phase 4: The Experiment (Apr)**

**Goal:** Gather the scientific data.

* **Weeks 13-14: Final Execution**  
  * Run `test_dataset.csv` through **Model A (Baseline Llama)**.  
  * Run `test_dataset.csv` through **Model B (Thesis KG-Model)**.  
  * Output: A spreadsheet with 200 pairs of (Input \-\> Response).  
* **Weeks 15-16: Blind Rating**  
  * Anonymize the spreadsheet (hide which model wrote which).  
  * Send it to Katharina. Ask her to rate "Safety" and "Appropriateness" (1-5).  
  * *This effectively ends the "Work" phase.*

## **Phase 5: Writing \- Methods & Results (May)**

**Goal:** Write the "Meat" of the thesis.

* **Weeks 17-18: Methods Section**  
  * Describe the Graph construction (cite Moser/Germain).  
  * Describe the Pipeline.  
* **Weeks 19-20: Results Section**  
  * Calculate the score difference (e.g., "KG Model scored 4.8 vs Baseline 3.5").  
  * Calculate Inter-Rater Reliability (Cohen's Kappa).  
  * Make 3 cool charts: "Safety Violation Rate," "Mastery Suggestion Rate."

## **Phase 6: Intro, Discussion & Polish (Jun)**

**Goal:** Finish and Submit.

* **Weeks 21-22: Introduction & Discussion**  
  * Write the Intro (Problem: AI is unsafe. Solution: Graphs).  
  * Write Discussion (Implications for Medical Device Regulation).  
* **Weeks 23-24: Formatting & Submission**  
  * Final proofread.  
  * Submit.

