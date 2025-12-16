# Neuro-Symbolic Safety Layer for IRT Chatbot

A standalone Neuro-Symbolic "Critic" pipeline that intercepts user input, maps it to a Clinical Knowledge Graph (MMS/ZDPCS), and enforces safety constraints before generation.

## 🎯 Objective

Build a safety layer that uses a knowledge graph to identify maladaptive behaviors in user input and guide the chatbot toward adaptive therapeutic responses. This is part of a thesis project focusing on safety in Imagery Rehearsal Therapy (IRT) chatbots.

## 🏗️ Architecture

The system follows a 3-block neuro-symbolic architecture with an upgraded "Clinical Reasoning Engine":

1. **Knowledge Graph (Block A)**: Clinical ontology based on ZDPCS (maladaptive behaviors), MMS (adaptive goals), and neutral categories
2. **Entity Linker (Block B)**: LLM-based classifier that maps user text to graph nodes with negation handling and ambiguity rules
3. **Critic Pipeline (Block C)**: "Clinical Reasoning Engine" with intelligent segmentation, batch classification, severity-based triage, and "Validate + Correct" constraint synthesis

### New Pipeline Flow

```
User Input → Intelligent Segmenter → Filter META → Batch Classify → Triage → Constraint Synthesis
                    ↓                      ↓              ↓           ↓              ↓
              [Segments with       [Dream content   [Map to      [Priority    [Validate adaptive +
               ACTION/THOUGHT/      only]           Graph        ranking]      Correct specific risk]
               FEELING/META]                        Nodes]
```

## 📋 Implementation Plan

### Phase 1: Repository Setup & Migration ✅ **COMPLETE**

- ✅ Git repository initialized
- ✅ Python virtual environment set up (using `uv`)
- ✅ Core files migrated from reDreamAI repository:
  - `AI/agent.py` - API wrapper for OpenAI/Groq
  - `AI/models.py` - Pydantic data structures
  - `AI/prompts.py` - Prompt templates (DE/EN)
  - `AI/logging_config.py` - Logging configuration
  - `AI/irt_app.py` - Main application logic
  - `AI/api.py` - FastAPI server
  - `AI/chat_client.py` - Terminal client
- ✅ Dependencies installed (NetworkX, Pandas, OpenAI, Groq, FastAPI, etc.)
- ✅ Environment configuration set up

### Phase 2: The Safety Module (Neuro-Symbolic Logic) ✅ **COMPLETE**

**Goal**: Implement the 3-block architecture with "Clinical Reasoning Engine"

- ✅ **Block A**: Knowledge Graph (`safety/graph_definitions.py`)
  - 10 nodes total:
    - 3 ZDPCS maladaptive (Safety Principle, Interrupt, Regressive Aggression)
    - 5 MMS adaptive (Behavioral, Social, Environmental, Emotional, Mythical Mastery)
    - 2 Neutral (Narrative Setting, Affect Expression)
  - 9 correction edges with clinical rationale and references
  - Full scientific documentation in `Documents/Clinical_Ontology_Scientific_Rationale.md`

- ✅ **Block B**: Entity Linker (`safety/classifier.py`)
  - ClinicalClassifier class using Agent to map text to graph nodes
  - LLM-based classification (Llama-3.1-8b-instant) with validation
  - **Negation handling**: Correctly classifies "I decided not to run" as mastery
  - **Ambiguity rules**: Distinguishes narrative/affect from action
  - **Context-aware classification**: Accepts nightmare context to disambiguate emotional suppression vs expression
  - Fuzzy matching for robustness

- ✅ **Block C**: Critic Pipeline (`safety/critic.py`) - **"Clinical Reasoning Engine"**
  - **Intelligent Segmentation**: Parses multi-part inputs (e.g., "I hate this, but I fight")
  - **META filtering**: Ignores conversational content, processes dream content
  - **Batch classification**: Maps each segment to Graph Nodes with nightmare context
  - **Context-aware emotional suppression detection**: Distinguishes "I feel scared" (acknowledging) from "I'm fine with it" (suppressing) based on nightmare content
  - **Severity-based triage**: Priority ranking (Critical → High → Moderate)
  - **"Validate + Correct" constraints**: Acknowledges positive elements before redirecting
  - SafetyResult includes segments, adaptive parts, and severity level

### Phase 3: Integration (Chatbot & Testing) 📅 **PLANNED**

- Hook SafetyCritic into `irt_app.py` for the rewriting stage
- Create verification script with test cases
- End-to-end testing

### Phase 4: Production Readiness & Future Migration 📅 **PLANNED**

- Abstraction layer for graph backend (NetworkX → Neo4j migration path)
- Experiment scripts for thesis data generation

## 🛠️ Tech Stack

- **Core**: Python 3.10+, OpenAI/Groq (via Agent class), Pydantic
- **Graph Engine**: NetworkX (Thesis MVP)
- **Future Target**: Neo4j (for production scalability)
- **Web Framework**: FastAPI
- **Environment Management**: `uv`

## 🚀 Setup

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd safety_layer
```

2. Create virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r AI/requirements.txt
```

3. Create `.env` file with your API keys:
```bash
cp .env.example .env
# Edit .env and add your keys:
# GROQ_API_KEY=your_key_here
# OPENAI_API_KEY=your_key_here
```

4. Verify setup:
```bash
python test_setup.py
```

## 🏃 Running the Server

Start the FastAPI server:

```bash
uvicorn AI.api:app --reload
```

Or using `uv`:

```bash
uv run uvicorn AI.api:app --reload
```

The server will be available at `http://127.0.0.1:8000`

### API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /chat` - Non-streaming chat endpoint
- `POST /chat/stream` - Streaming chat endpoint
- `GET /conversation/{session_id}` - Get conversation history
- `POST /chat/set_history` - Set conversation history

### Using the Chat Client

Terminal-based chat client:

```bash
# Streaming mode
python -m AI.chat_client --stream

# Regular mode
python -m AI.chat_client
```

## 📁 Project Structure

```
.
├── AI/                      # Core application code
│   ├── agent.py            # API wrapper (OpenAI/Groq)
│   ├── models.py           # Pydantic data models
│   ├── prompts.py          # Prompt templates
│   ├── irt_app.py          # Main application logic
│   ├── api.py              # FastAPI server
│   ├── chat_client.py      # Terminal client
│   └── logging_config.py  # Logging setup
├── safety/                  # Safety module (Phase 2) ✅
│   ├── graph_definitions.py  # Knowledge graph (10 nodes, 9 edges)
│   ├── classifier.py         # Entity linker with negation handling
│   └── critic.py              # Clinical Reasoning Engine (segmentation + triage)
├── Documents/               # Research papers & documentation
│   ├── Clinical_Ontology_Scientific_Rationale.md  # Scientific justification
│   ├── Multidimensional Mastery Scale (MMS) Scoring Manual.md
│   └── [Research papers: Germain, Fischmann, Moser, etc.]
├── experiments/             # Experiment scripts (Phase 4)
├── scenarios/               # Test scenarios for critic testing
│   ├── chase_nightmare.json    # Chase nightmare context
│   ├── chase_scenario_tests.json  # Chase nightmare test suite
│   ├── confrontation_nightmare.json  # Confrontation context
│   ├── confrontation_scenario_tests.json  # Confrontation test suite
│   ├── dog_dream_tests.json    # Dog loss nightmare test suite (emotional suppression)
│   └── batch_tests.json        # Batch test cases
├── test_setup.py           # Setup verification script
├── test_safety_module.py   # Phase 2 safety module tests
├── test_critic_interactive.py  # Interactive critic testing (Tier 1)
├── visualize_graph.py      # Graph visualization tool
├── clinical_graph.png/pdf  # Generated graph visualizations
├── implementation_plan.md  # Detailed implementation plan
└── README.md               # This file
```

## 🧪 Testing

### Setup Verification

Run the setup verification:

```bash
python test_setup.py
```

This will verify:
- All imports work correctly
- Models function properly
- Agent structure is correct
- Prompts are loaded
- Dependencies are installed
- Environment file exists

### Safety Module Tests

Run Phase 2 safety module tests:

```bash
python test_safety_module.py
```

This will verify:
- Knowledge graph structure (10 nodes: 3 maladaptive + 5 adaptive + 2 neutral, 9 edges)
- Clinical classifier accuracy with neutral categories and negation handling
- SafetyCritic pipeline functionality with segmentation and triage
- All correction strategies work correctly

### Interactive Critic Testing (Tier 1)

Test the SafetyCritic "Clinical Reasoning Engine" interactively:

```bash
# Interactive mode - type test inputs directly
python test_critic_interactive.py

# With nightmare context loaded
python test_critic_interactive.py --context scenarios/chase_nightmare.json

# Run scenario test suite (nightmare + test cases against that nightmare)
python test_critic_interactive.py --scenario scenarios/dog_dream_tests.json

# With verbose output showing constraint messages
python test_critic_interactive.py --scenario scenarios/chase_scenario_tests.json -v

# Run batch test cases (legacy - no nightmare context)
python test_critic_interactive.py --batch scenarios/batch_tests.json

# Live mode - chat through actual IRT session, test critic at rewriting stage
python test_critic_interactive.py --live
```

This shows detailed output for each test:
- **Segmentation**: How input was parsed (ACTION/THOUGHT/FEELING/META)
- **Classification**: Which graph node each segment mapped to (with nightmare context)
- **Triage**: Which risk was prioritized (for unsafe inputs)
- **Verdict**: SAFE or UNSAFE with severity level
- **Constraint**: The full message that would be injected into the generator

**Scenario Mode** (`--scenario`) is recommended as it provides nightmare context to each test, enabling accurate emotional suppression detection.

### Visualize the Knowledge Graph

Generate a visual representation of the ontology:

```bash
python visualize_graph.py
```

This creates `clinical_graph.png` and `clinical_graph.pdf` showing the complete ontology with all nodes and correction edges.

## 📝 Current Status

**Phase 1: ✅ Complete**
- Repository initialized
- All core files migrated
- Dependencies installed
- Environment configured
- Server tested and working

**Phase 2: ✅ Complete**
- Knowledge graph implemented (10 nodes: 3 ZDPCS maladaptive + 5 MMS adaptive + 2 Neutral)
- 9 correction edges with clinical rationale
- Clinical classifier with negation handling, ambiguity rules, and context-aware emotional suppression detection
- **Upgraded SafetyCritic "Clinical Reasoning Engine"**:
  - Intelligent segmentation for multi-part inputs
  - META content filtering
  - Context-aware batch classification (nightmare context piped through)
  - Emotional suppression detection: distinguishes acknowledgment vs avoidance
  - Severity-based triage (Critical/High/Moderate)
  - "Validate + Correct" constraint synthesis
- Comprehensive test scenarios with nightmare context
- Scientific documentation with direct quotes and references
- Graph visualizations generated
- All core tests passing

**Phase 3: 🔄 Next Steps**
- Hook SafetyCritic into `irt_app.py` for rewriting stage
- Create verification script with test cases
- End-to-end integration testing

## 🔮 Future Work

- Graph abstraction layer for Neo4j migration
- Experiment data generation scripts
- Comprehensive test suite
- Performance optimization
- Production deployment configuration

## 📚 References

### Primary Sources

1. **Germain, A., Krakow, B., Faucher, B., et al.** (2004). Increased Mastery Elements Associated With Imagery Rehearsal Treatment for Nightmares in Sexual Assault Survivors With PTSD. *Dreaming, 14*(4), 195-206.
   - Defines the Multidimensional Mastery Scale (MMS) - 6 mastery subscales

2. **Fischmann, T., Leuzinger-Bohleber, M., & Moser, U.** (2021). Dreams and Trauma: Changes in the Manifest Dreams in Psychoanalytic Treatments. *Frontiers in Psychology*.
   - Applies ZDPCS concepts to trauma dreams

3. **Moser, U., & Hortig, V.** (2019). *Microanalysis of Dreams: The Zurich Dream Process Coding System (ZDPCS)*. Springer.
   - Original ZDPCS methodology

4. **Rousseau, A., & Belleville, G.** (2018). The mechanisms of action underlying the efficacy of psychological nightmare treatments. *Sleep Medicine Reviews, 39*, 122-133.
   - Identifies "Prevention of Avoidance" as key mechanism

5. **Nielsen, T., & Levin, R.** (2007). Nightmares: A new neurocognitive model. *Sleep Medicine Reviews, 11*(4), 295-310.
   - AMPHAC model: nightmares = failed fear extinction

For detailed scientific rationale with direct quotes, see `Documents/Clinical_Ontology_Scientific_Rationale.md`.

## 📄 License

[Add your license here]

## 👤 Author

[Your name/institution]

---

**Note**: This is a thesis project. The safety layer is designed to ensure therapeutic safety in IRT chatbot interactions by identifying and redirecting maladaptive behaviors toward adaptive goals.

