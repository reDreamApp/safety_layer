Implementation Plan: Neuro-Symbolic Safety Layer (Thesis MVP)

Objective: Build a standalone Neuro-Symbolic "Critic" pipeline that intercepts user input, maps it to a Clinical Knowledge Graph (MMS/ZDPCS), and enforces safety constraints before generation.

Tech Stack: * Core: Python 3.10+, OpenAI/Groq (via existing Agent class), Pydantic.

Graph Engine: NetworkX (Chosen for Thesis MVP due to artifact portability and speed).

Future Production Target: Neo4j (For multi-user scalability and complex traversals).

Phase 1: Repository Setup & Migration

Goal: Initialize a clean environment and migrate the "Organs" (core logic) from the existing chatbot to this new experiment body.

1.1. Project Initialization

Initialize a new git repository (thesis-safety-layer).

Set up a fresh Python virtual environment.

1.2. File Migration

Copy the following files from the reDreamAI repository to your new root.

AI/agent.py (The API wrapper)

AI/models.py (The data structures)

AI/prompts.py (Required by agent.py)

AI/logging_config.py

AI/requirements.txt

.env (Configuration keys)

For Interactive Chatting (Optional but Recommended):

AI/irt_app.py (The main application logic)

AI/api.py (The FastAPI server)

AI/chat_client.py (The terminal client)

1.3. Dependency Management

Update requirements.txt to include networkx (for the graph) and pandas (for the experiment data).

Install all requirements.

Phase 2: The Safety Module (Neuro-Symbolic Logic)

Goal: Implement the 3-block architecture: Knowledge (Graph), Perception (Classifier), Reasoning (Critic).

2.1. Block A: The Knowledge Graph

File: safety/graph_definitions.py

Task: Create a function build_clinical_graph() that returns a directed graph (nx.DiGraph) representing the clinical ontology.

Requirements:

Maladaptive Nodes (Risks): Define nodes based on the ZDPCS (Moser et al.).

Examples: AVOIDANCE (High Risk), PASSIVITY (Medium Risk), EXTREME_VIOLENCE (Critical Risk).

Attributes: Each node must have a type="maladaptive", severity, and a clinical_guideline string explaining why it is harmful.

Adaptive Nodes (Goals): Define nodes based on the MMS (Germain et al.).

Examples: BEHAVIORAL_MASTERY, SOCIAL_MASTERY, ENVIRONMENTAL_MASTERY, EMOTIONAL_MASTERY.

Attributes: Each node must have a type="adaptive" and a description.

Correction Edges: Define directed edges from Risks to Goals.

Logic: If the user exhibits AVOIDANCE, the edge points to the solution BEHAVIORAL_MASTERY.

Edge Attribute: relation="correction_strategy".

2.2. Block B: The Entity Linker

File: safety/classifier.py

Task: Create a class ClinicalClassifier that uses the existing Agent to map user text to Graph Node IDs.

Requirements:

Configuration: Initialize a specific Agent instance (using a fast model like GPT-4o-mini or Llama-3-8b).

System Prompt: Write a prompt acting as a "Clinical Coder." It must list the available codes defined in Block A and instruct the LLM to output only the code (e.g., "AVOIDANCE") for a given input.

Method: Implement classify_intent(user_text) -> str which sends the prompt and returns the cleaned Node ID.

Validation: Ensure the returned ID actually exists in the graph.

2.3. Block C: The Critic Pipeline

File: safety/critic.py

Task: Create a class SafetyCritic that orchestrates the safety check.

Requirements:

Initialization: Load the Graph (Block A) and the Classifier (Block B).

Method: Implement evaluate_intervention(user_input) -> dict.

Logic Flow:

Classify: Pass input to the Classifier to get the Node ID.

Check: Look up the Node in the Graph.

Decision:

If node.type == "adaptive": Return Safe.

If node.type == "maladaptive":

Traverse the graph to find neighbors connected via correction_strategy edges.

Construct a Constraint Message for the generator: "User proposed

$$Risk$$

. This is maladaptive. Suggest

$$Connected Goal$$

instead."

Return Unsafe + Constraint Message.

Phase 3: Integration (Chatbot & Testing)

Goal: Integrate the Critic into the actual Chatbot Logic.

3.1. Hook into irt_app.py

Task: Modify irt_app.py to use the SafetyCritic before generating a response.

Logic to Add (Pseudo-code):

# In process_chat_message...
if stage == "rewriting":
    critic = SafetyCritic()
    safety_result = await critic.evaluate_intervention(chat_input.message)
    
    if not safety_result['is_safe']:
        # INJECT THE CONSTRAINT
        # Append safety_result['constraint'] to the system prompt
        full_prompt += f"\n\n[SYSTEM WARNING]: {safety_result['constraint']}"



3.2. Verification Script

File: test_pipeline.py

Task: Create an async script to run the SafetyCritic against a list of hardcoded test cases to verify the logic outside the chat.

Test Cases:

"I wake up" -> Should trigger AVOIDANCE -> Result: Unsafe.

"I fight back" -> Should trigger BEHAVIORAL_MASTERY -> Result: Safe.

Phase 4: Production Readiness & Future Migration

Goal: Prepare the architecture for scaling beyond the thesis.

4.1. Abstraction Layer (For Neo4j Support)

Task: Ensure SafetyCritic does not interact with NetworkX directly.

Create a GraphProvider abstract base class.

Implement NetworkXProvider (for Thesis).

Future: Implement Neo4jProvider (for Product).

This ensures you can switch the backend later by changing one line of code.

4.2. Experiment Scripts

experiments/generate_incidents.py: A script using Agent to generate 100 synthetic patient inputs (20 per category).

experiments/run_study.py: A script to process that CSV through the SafetyCritic and save results for blind rating.