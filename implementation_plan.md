Implementation Plan: Neuro-Symbolic Safety Layer (Thesis MVP)

Objective: Build a standalone Neuro-Symbolic "Critic" pipeline that intercepts user input, maps it to a Clinical Knowledge Graph (MMS/ZDPCS), and enforces safety constraints before generation.

Tech Stack:

Core: Python 3.10+, OpenAI/Groq (via existing Agent class), Pydantic.

Graph Engine: NetworkX (Chosen for Thesis MVP due to artifact portability and speed).

Future Production Target: Neo4j (For multi-user scalability and complex traversals).

---

## Phase 1: Repository Setup & Migration ✅ COMPLETE

Goal: Initialize a clean environment and migrate the "Organs" (core logic) from the existing chatbot to this new experiment body.

### 1.1. Project Initialization

- ✅ Initialize a new git repository (thesis-safety-layer).
- ✅ Set up a fresh Python virtual environment.

### 1.2. File Migration

Copied the following files from the reDreamAI repository:

- AI/agent.py (The API wrapper)
- AI/models.py (The data structures)
- AI/prompts.py (Required by agent.py)
- AI/logging_config.py
- AI/requirements.txt
- .env (Configuration keys)
- AI/irt_app.py (The main application logic)
- AI/api.py (The FastAPI server)
- AI/chat_client.py (The terminal client)

### 1.3. Dependency Management

- ✅ Updated requirements.txt to include networkx and pandas.
- ✅ Installed all requirements.

---

## Phase 2: The Safety Module (Neuro-Symbolic Logic) ✅ COMPLETE

Goal: Implement the 3-block architecture: Knowledge (Graph), Perception (Classifier), Reasoning (Critic).

### 2.1. Block A: The Knowledge Graph ✅

File: `safety/graph_definitions.py`

Task: Create a function `build_clinical_graph()` that returns a directed graph (nx.DiGraph) representing the clinical ontology.

**Implemented Nodes (10 total):**

**Maladaptive Nodes (Risks) - Source: ZDPCS:**
- `ZDPCS_SAFETY_PRINCIPLE` (Avoidance): Hiding, freezing, doing nothing, passive observation
- `ZDPCS_INTERRUPT` (Escape): Waking up, dream ending, refusing to continue
- `ZDPCS_REGRESSIVE_AGGRESSION` (Violence): Killing everyone, excessive violence, destroying environment

**Adaptive Nodes (Goals) - Source: MMS:**
- `BEHAVIORAL_MASTERY` (Action): Fighting back, confronting, taking control
- `SOCIAL_MASTERY` (Help): Calling for help, allies appearing, receiving protection
- `ENVIRONMENTAL_MASTERY` (Tools): Finding weapons, environment changing favorably
- `EMOTIONAL_MASTERY` (Self-soothing): Calming down, staying present, transforming fear
- `MYTHICAL_MASTERY` (Supernatural): Using magical powers, divine intervention

**Neutral Nodes (Context) - New:**
- `ZDPCS_NARRATIVE_SETTING`: Scene description without action
- `ZDPCS_AFFECT_EXPRESSION`: Feeling statements without action

**Correction Edges (9 total):**
- Directed edges from Risk → Goal with relation="correction_strategy"
- Each edge includes priority (primary/secondary/tertiary), rationale, clinical reference, and therapeutic direction

### 2.2. Block B: The Entity Linker ✅

File: `safety/classifier.py`

Task: Create a class `ClinicalClassifier` that maps user text to Graph Node IDs.

**Implemented Features:**
- System Prompt acting as "Clinical Coder" with all 10 categories
- **Negation Handling**: "I decided not to run" → BEHAVIORAL_MASTERY (not avoidance)
- **Ambiguity Rules**: "I felt scared" → ZDPCS_AFFECT_EXPRESSION (not action)
- Method: `classify_intent(user_text) -> str`
- Validation ensures returned ID exists in graph
- Fuzzy matching for robustness

### 2.3. Block C: The Critic Pipeline - "Clinical Reasoning Engine" ✅

File: `safety/critic.py`

Task: Create a class `SafetyCritic` that orchestrates the safety check with intelligent segmentation and triage.

**Upgraded Pipeline Architecture:**

```
User Input → Intelligent Segmenter → Filter META → Batch Classify → Triage → Constraint Synthesis
```

**2.3.1. Intelligent Segmenter**

Input: User text
Output: List of segments with labels (ACTION, THOUGHT, FEELING, META)

Example:
- Input: "I hate this therapy, but I guess I fight the dragon."
- Output: [{"text": "I hate this therapy", "type": "META"}, {"text": "but I guess I fight the dragon", "type": "ACTION"}]

**2.3.2. META Filtering**

- Discard segments labeled META (conversational content)
- If no dream segments remain, return "Safe/Pass-through"

**2.3.3. Batch Classification**

- Map each remaining dream segment to a Graph Node
- Track adaptive, maladaptive, and neutral segments separately

**2.3.4. Triage Algorithm (Severity-Based)**

Priority Ranking:
1. **CRITICAL**: ZDPCS_REGRESSIVE_AGGRESSION (Violence)
2. **HIGH**: ZDPCS_INTERRUPT (Waking Up)
3. **MODERATE**: ZDPCS_SAFETY_PRINCIPLE (Avoidance)

Tie-Breaker: First chronological occurrence

Selection: Return ONLY the top-ranked maladaptive node for correction

**2.3.5. Constraint Synthesis ("Validate + Correct")**

IF SAFE:
```
VALIDATE: User demonstrated adaptive responses: [List]. Proceed with encouragement.
```

IF UNSAFE:
```
VALIDATE: [List any Adaptive/Neutral parts found]
CORRECT: User demonstrated [Selected Maladaptive Node]. This is a [Severity] risk.
INSTRUCTION: Gently redirect using [Correction Strategy from Graph]. Do not list other errors.
```

---

## Phase 3: Integration (Chatbot & Testing) 📅 PLANNED

Goal: Integrate the Critic into the actual Chatbot Logic.

### 3.1. Hook into irt_app.py

Task: Modify irt_app.py to use the SafetyCritic before generating a response.

Logic to Add (Pseudo-code):

```python
# In process_chat_message...
if stage == "rewriting":
    critic = SafetyCritic()
    safety_result = await critic.evaluate_intervention(chat_input.message)
    
    if not safety_result['is_safe']:
        # INJECT THE CONSTRAINT
        # Append safety_result['constraint'] to the system prompt
        full_prompt += f"\n\n{safety_result['constraint']}"
```

### 3.2. Verification Script

File: `test_pipeline.py`

Task: Create an async script to run the SafetyCritic against test cases.

Test Cases should include:
- Simple inputs (single action)
- Complex multi-part inputs (META + ACTION)
- Negation handling ("I decided not to...")
- Neutral inputs (feelings/narrative)
- Mixed severity inputs (multiple maladaptive in one message)

---

## Phase 4: Production Readiness & Future Migration 📅 PLANNED

Goal: Prepare the architecture for scaling beyond the thesis.

### 4.1. Abstraction Layer (For Neo4j Support)

Task: Ensure SafetyCritic does not interact with NetworkX directly.

- Create a GraphProvider abstract base class.
- Implement NetworkXProvider (for Thesis).
- Future: Implement Neo4jProvider (for Product).

This ensures you can switch the backend later by changing one line of code.

### 4.2. Experiment Scripts

- `experiments/generate_incidents.py`: Script using Agent to generate synthetic patient inputs
- `experiments/run_study.py`: Script to process inputs through SafetyCritic and save results for analysis

---

## Summary of Completed Work

### Files Modified/Created:

1. **safety/graph_definitions.py**
   - Added 2 Neutral nodes (ZDPCS_NARRATIVE_SETTING, ZDPCS_AFFECT_EXPRESSION)
   - Added `get_neutral_nodes()` helper function
   - Updated test output to include neutral nodes

2. **safety/classifier.py**
   - Added Neutral categories to system prompt
   - Added Negation Handling rules
   - Added Ambiguity Rules for settings/feelings
   - Updated fuzzy matching keywords
   - Updated test cases

3. **safety/critic.py** - Major Overhaul
   - Added `SEGMENTER_PROMPT` for intelligent segmentation
   - Added `SEVERITY_PRIORITY` mapping
   - Added `SegmentResult` dataclass
   - Updated `SafetyResult` with segments, adaptive_segments, severity
   - Implemented `segment_input()` method
   - Implemented `_sort_by_severity()` triage method
   - Updated `evaluate_intervention()` with full pipeline
   - Updated `_build_constraint_message()` with Validate + Correct structure
   - Added `_build_validation_message()` for safe inputs
   - Updated test cases for new features

### Node Count: 10 total
- 3 Maladaptive (ZDPCS)
- 5 Adaptive (MMS)
- 2 Neutral (Context)

### Edge Count: 9 correction strategies
