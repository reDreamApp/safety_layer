Implementation Plan: Advanced Neuro-Symbolic Critic Pipeline

Objective: Upgrade the Safety Layer from a simple classifier to a "Clinical Reasoning Engine" that handles complex, multi-part user inputs deterministically.

1. Architectural Overview

We are moving from a "One-Input-One-Class" model to a Segmented Analysis Pipeline.

The New Flow:

Intelligent Segmentation: Pass full user input to a lightweight LLM. It extracts "Dream Units" and labels "Meta/Chat" content.

Filtering: Discard segments labeled as META. If no dream segments remain, return "Safe/Pass-through".

Batch Classification: Map each remaining dream unit to a Graph Node.

Triage Logic: Filter neutrals, identify risks, and select the single most critical error to correct.

Constraint Synthesis: Generate instructions to Validate adaptive parts and Correct the specific priority risk.

2. Knowledge Graph Updates (Block A)

File: safety/graph_definitions.py

Task: Add "Neutral Nodes" to handle narrative descriptions that are neither adaptive nor maladaptive.

New Nodes to Add:

ZDPCS_NARRATIVE_SETTING

Definition: Description of environment/characters without active interaction.

Type: Neutral.

System Action: Ignore/Validate context.

ZDPCS_AFFECT_EXPRESSION

Definition: Explicit statement of emotion (e.g., "I felt scared").

Type: Neutral.

System Action: Empathy validation.

3. Classifier Updates (Block B)

File: safety/classifier.py

Task: Update the CLINICAL_CODER_PROMPT to support the new granular approach.

Prompt Adjustments:

Add Neutral Categories: Include the two new nodes in the system prompt list.

Negation Handling: Add instruction: "If the user mentions an action they AVOIDED doing (e.g., 'I decided not to run'), classify the decision (Mastery), not the avoided action."

Ambiguity Rule: "If the user describes the setting or their feelings without taking action, classify as NARRATIVE or AFFECT."

4. Critic Pipeline Overhaul (Block C)

File: safety/critic.py

Task: Rewrite evaluate_intervention to implement the "Segmentation & Triage" logic.

4.1. The Intelligent Segmenter (Merged Router/Segmenter)

Input: User Text + Original Nightmare Summary (Context).

Logic: Use a lightweight LLM call (e.g., Groq 8b) to parse the text.

Prompt Strategy: "Identify discrete parts of the user's response. Label them as ACTION, THOUGHT, FEELING, or META (conversational/questions)."

Handling Mixed Input (Example):

Input: "I hate this therapy, but I guess I fight the dragon."

Output:

[
  {"text": "I hate this therapy", "type": "META"}, 
  {"text": "but I guess I fight the dragon", "type": "ACTION"}
]


4.2. The Triage Algorithm (Priority Logic)

If multiple maladaptive nodes are detected in the batch, apply this filter:

Filter: Ignore segments labeled META by the Segmenter. Then ignore Graph Nodes classified as Neutral (NARRATIVE, AFFECT).

Sort by Severity:

Priority 1 (CRITICAL): ZDPCS_REGRESSIVE_AGGRESSION (Violence).

Priority 2 (HIGH): ZDPCS_INTERRUPT (Waking Up).

Priority 3 (MODERATE): ZDPCS_SAFETY_PRINCIPLE (Avoidance).

Tie-Breaker: If severity is equal, pick the First Chronological occurrence.

Selection: Return ONLY the top-ranked maladaptive node for correction.

4.3. Constraint Synthesis

Construct the final prompt for the Chatbot:

IF SAFE: "User input is adaptive/neutral. VALIDATE: 

$$List Adaptive Actions$$

. Proceed."

IF UNSAFE:

"VALIDATE: 

$$List any Adaptive/Neutral parts found$$

 (e.g., 'Good job noticing the monster...')."

"CORRECT: User demonstrated 

$$Selected Maladaptive Node$$

. This is a 

$$Severity$$

 risk."

"INSTRUCTION: Gently redirect using 

$$Correction Strategy from Graph$$

. Do not list other errors."

5. Summary of Steps for Cursor

Modify safety/graph_definitions.py: Inject the 2 Neutral Nodes.

Modify safety/classifier.py: Update System Prompt with Neutrals and Negation rules.

Modify safety/critic.py:

Add segment_input() method with the META labeling logic.

Refactor evaluate_intervention() to process the list.

Implement the sort_by_severity() triage logic.

Update the _build_constraint_message to handle the "Validate + Correct" structure.