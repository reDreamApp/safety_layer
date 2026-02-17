# Thesis Progress Report

**Title:** Formalizing Clinical Guidelines: A Knowledge-Graph Augmented Approach to Safety and Mastery in AI-Based Nightmare Therapy

**Author:** Ramon Zacharias  
**Supervisor:** Prof. Dr. Sebastian Musslick  
**Date:** December 2024

---

## 1. Project Overview

### Problem
LLM-based chatbots for Imagery Rehearsal Therapy (IRT) can suggest maladaptive coping strategies (avoidance, violence, waking up) that contradict clinical guidelines and may reinforce trauma.

### Solution
A **Neuro-Symbolic Safety Layer** that combines:
- **Symbolic reasoning**: A clinical knowledge graph encoding therapeutic guidelines
- **Neural processing**: LLMs for understanding user intent

The system intercepts user inputs during dream rewriting and ensures responses align with clinical best practices.

### Core Research Question
> Can a Knowledge Graph-based constraint system significantly reduce clinically maladaptive suggestions in LLM-generated IRT interventions?

---

## 2. Clinical Foundation

The safety layer formalizes two established clinical frameworks:

| Framework | Source | Role |
|-----------|--------|------|
| **ZDPCS** (Zürich Dream Process Coding System) | Moser & Hortig, 2019 | Defines maladaptive behaviors |
| **MMS** (Multidimensional Mastery Scale) | Germain et al., 2004 | Defines adaptive coping goals |

---

## 3. Current Implementation State

### ✅ Completed: Three-Block Architecture

```
User Input → [Segmenter] → [Classifier] → [Knowledge Graph] → Constraint → Chatbot
```

#### Block A: Knowledge Graph
- **10 nodes** implemented in NetworkX:
  - 3 maladaptive (avoidance, escape, violence) with severity levels
  - 5 adaptive (behavioral, social, environmental, emotional, mythical mastery)
  - 2 neutral (narrative setting, affect expression)
- **9 correction edges** with clinical rationale and therapeutic directions

#### Block B: Clinical Classifier
- LLM-based entity linker (Llama-3.1-8B via Groq)
- Maps free-text to graph nodes
- Handles negation ("I decided NOT to run" → adaptive)
- Distinguishes actions from feelings

#### Block C: SafetyCritic Pipeline ("Clinical Reasoning Engine")
- **Intelligent Segmentation**: Parses multi-part inputs  
  - Example: "I hate this, but I fight back" → [META, ACTION]
- **META Filtering**: Ignores conversational resistance
- **Severity-Based Triage**: Prioritizes most critical risk
  - CRITICAL: Violence
  - HIGH: Waking up
  - MODERATE: Avoidance
- **Constraint Synthesis**: Generates "Validate + Correct" instructions

### ✅ Completed: Testing Infrastructure
- Scenario-based test suites (nightmare + multiple rewriting attempts)
- 100% pass rate on current test cases
- Detailed output: segmentation, classification, triage, constraint messages

### 📁 Files
```
safety/
├── graph_definitions.py   # Knowledge Graph (Block A)
├── classifier.py          # Entity Linker (Block B)
└── critic.py              # SafetyCritic Pipeline (Block C)
```

---

## 4. Example: System in Action

**User Input:** `"I'm so angry that I kill everyone in the room"`

**Pipeline Result:**
```
Segmentation:
  [FEELING] "I'm so angry" → ZDPCS_AFFECT_EXPRESSION (neutral)
  [ACTION] "that I kill everyone" → ZDPCS_REGRESSIVE_AGGRESSION (maladaptive)

Triage: CRITICAL severity (violence)

Constraint Injected:
  VALIDATE: User showed positive elements: "I'm so angry"
  CORRECT: This is CRITICAL risk - violence doesn't resolve the threat
  INSTRUCTION: Guide toward controlled, purposeful action instead
```

---

## 5. Next Steps

| Phase | Task | Status |
|-------|------|--------|
| Integration | Hook SafetyCritic into IRT chatbot | Planned |
| Experiment | Generate 100 synthetic critical incidents | Planned |
| Evaluation | Blind expert rating (Safety, Empathy, Adherence) | Planned |

---

## 6. Key Deliverables (Thesis Outputs)

1. **Safety Graph Artifact**: Reusable clinical ontology (`.json`/NetworkX)
2. **Validated Architecture**: Prototype demonstrating KG-constrained LLMs
3. **Scientific Evidence**: Quantitative safety improvement data
