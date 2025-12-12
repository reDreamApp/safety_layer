# **Thesis Reading List & Ontology Resources**

**Project:** Formalizing Clinical Guidelines (Neuro-Symbolic AI for Nightmare Therapy) **Author:** Ramon Zacharias

## **🟢 Part 1: Defining the "Good" Nodes (Adaptive Mastery)**

*Use these papers to populate the "Goal State" nodes in your Knowledge Graph. These define what the AI should steer the user TOWARD.*

### **1\. The Definitions of Mastery**

* **Paper:** Germain, A., Krakow, B., et al. (2004). *"Increased Mastery Elements Associated With Imagery Rehearsal Treatment for Nightmares in Sexual Assault Survivors With PTSD."* Dreaming, 14(4).  
* **Why read this?** This is your **primary source** for the Knowledge Graph. It contains the "Multidimensional Mastery Scale."  
* **Your Action:** Go to the "Measures" or "Method" section. Extract the exact definitions for:  
  * **Behavioral Mastery** (Physical action).  
  * **Social Mastery** (Seeking help).  
  * **Emotional Mastery** (Calming self).

### **2\. The Proof of Mastery**

* **Paper:** Kunze, A. E., et al. (2019). *"Mediators of Change in Imagery Rescripting and Imaginal Exposure for Nightmares."* Behavior Therapy.  
* **Why read this?** It proves that "Mastery" is the specific mechanism that makes IRT work (unlike just exposure).  
* **Your Motivation:** You need this for your Introduction. It validates why your AI focuses on *rescripting* outcomes rather than just *listening* to the nightmare.

## **🔴 Part 2: Defining the "Bad" Nodes (Maladaptive Coping)**

*Use these papers to populate the "Safety Risk" nodes. These define what the AI must DETECT and CORRECT.*

### **3\. The Logic of Avoidance vs. Approach**

* **Paper:** Fischmann, T., Leuzinger-Bohleber, M., & Moser, U. (2021). *"Dreams and Trauma: Changes in the Manifest Dreams..."* Frontiers in Psychology.  
* **Why read this?** It summarizes the **Zürich Dream Process Coding System (ZDPCS)** in English.  
* **Your Action:** Look for the logic describing "Position Field" (passive) vs. "Loco-Time Motion" (active). Use this to define "Passivity" and "Avoidance" in your graph.

### **4\. The Mechanism of Maladaptive Coping**

* **Paper:** Rousseau, A., & Belleville, G. (2018). *"The mechanisms of action underlying the efficacy of psychological nightmare treatments."* Sleep Medicine Reviews.  
* **Why read this?** It explicitly lists "Prevention of Avoidance" as a key mechanism.  
* **Your Motivation:** Use this to define *why* suggestions like "I'll just wake up" or "I'll try not to think about it" are clinically harmful.

### **5\. The Fear Extinction Model**

* **Paper:** Nielsen, T., & Levin, R. (2007). *"Nightmares: A new neurocognitive model."* Sleep Medicine Reviews.  
* **Why read this?** It explains the "AMPHAC" model.  
* **Your Motivation:** It provides the neuroscience backing: Nightmares are a failure of fear extinction. Avoidance prevents extinction. Therefore, your AI *must* block avoidance to allow extinction to happen.

## **🗺️ Part 3: The "Why" (Clinical Justification)**

*Use these papers to write your Introduction and Problem Statement. They explain why we need AI for this in the first place.*

### **6\. The "Gold Standard"**

* **Paper:** Aurora, R. N., et al. (2010). *"Best practice guide for the treatment of nightmare disorder in adults."* Journal of Clinical Sleep Medicine.  
* **Why read this?** It establishes IRT as a **Level A** recommendation.  
* **Your Motivation:** This is your shield. If anyone asks "Is this therapy real?", you cite this.

### **7\. The Dissemination Gap**

* **Paper:** Pietrowsky, R., & Thünker, J. (2014). *"Nightmares: Knowledge and attitudes in health care providers..."*  
* **Why read this?** It shows that most doctors don't know about IRT.  
* **Your Motivation:** This justifies the **AI aspect** of your thesis. You are automating the therapy because human experts are scarce and knowledge is not disseminating fast enough.

## **⚙️ Part 4: The "How" (Technical Architecture)**

*Use these references to design your Python pipeline.*

### **8\. Neuro-Symbolic AI**

* **Review:** Sarkas, G., et al. (2023) (or similar recent survey). *"Neuro-symbolic AI: A Survey."*  
* **Why read this?** You need to understand the concept of a "Critic" or "Guardrail."  
* **Your Motivation:** It gives you the vocabulary to describe your system: "A neural generator (LLM) supervised by a symbolic critic (Knowledge Graph)."

## **⚡ Quick Reference: Mapping Papers to Thesis Sections**

| Thesis Section | Key Papers to Cite |
| ----- | ----- |
| **Introduction** | Aurora et al. (2010), Pietrowsky & Thünker (2014) |
| **Methodology (Ontology)** | Germain et al. (2004), Fischmann/Moser (2021) |
| **Methodology (AI)** | Sarkas et al. (2023) |
| **Discussion (Mechanisms)** | Kunze et al. (2019), Nielsen & Levin (2007) |

Code Repos

- Dreamy for annotation and anonymization  
  [https://github.com/lorenzoscottb/DReAMy](https://github.com/lorenzoscottb/DReAMy)  
- Dreambank for dream reports  
- https://dreambank.net/