# Neuro-Symbolic Safety Layer for IRT Chatbot

A standalone Neuro-Symbolic "Critic" pipeline that intercepts user input, maps it to a Clinical Knowledge Graph (MMS/ZDPCS), and enforces safety constraints before generation.

## 🎯 Objective

Build a safety layer that uses a knowledge graph to identify maladaptive behaviors in user input and guide the chatbot toward adaptive therapeutic responses. This is part of a thesis project focusing on safety in Imagery Rehearsal Therapy (IRT) chatbots.

## 🏗️ Architecture

The system follows a 3-block neuro-symbolic architecture:

1. **Knowledge Graph (Block A)**: Clinical ontology based on ZDPCS (maladaptive behaviors) and MMS (adaptive goals)
2. **Entity Linker (Block B)**: LLM-based classifier that maps user text to graph nodes
3. **Critic Pipeline (Block C)**: Orchestrates safety checks and generates constraint messages

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

### Phase 2: The Safety Module (Neuro-Symbolic Logic) 🔄 **IN PROGRESS**

**Goal**: Implement the 3-block architecture

- **Block A**: Knowledge Graph (`safety/graph_definitions.py`)
  - Maladaptive nodes (Risks): AVOIDANCE, PASSIVITY, EXTREME_VIOLENCE, etc.
  - Adaptive nodes (Goals): BEHAVIORAL_MASTERY, SOCIAL_MASTERY, etc.
  - Correction edges connecting risks to goals

- **Block B**: Entity Linker (`safety/classifier.py`)
  - ClinicalClassifier class using Agent to map text to graph nodes
  - LLM-based classification with validation

- **Block C**: Critic Pipeline (`safety/critic.py`)
  - SafetyCritic class orchestrating safety checks
  - Returns safe/unsafe decisions with constraint messages

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
├── safety/                  # Safety module (Phase 2)
│   ├── graph_definitions.py  # Knowledge graph
│   ├── classifier.py         # Entity linker
│   └── critic.py              # Critic pipeline
├── experiments/             # Experiment scripts (Phase 4)
├── test_setup.py           # Setup verification script
├── implementation_plan.md  # Detailed implementation plan
└── README.md               # This file
```

## 🧪 Testing

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

## 📝 Current Status

**Phase 1: ✅ Complete**
- Repository initialized
- All core files migrated
- Dependencies installed
- Environment configured
- Server tested and working

**Phase 2: 🔄 Next Steps**
- Implement knowledge graph (Block A)
- Build entity linker (Block B)
- Create critic pipeline (Block C)

## 🔮 Future Work

- Graph abstraction layer for Neo4j migration
- Experiment data generation scripts
- Comprehensive test suite
- Performance optimization
- Production deployment configuration

## 📚 References

- **ZDPCS**: Moser et al. - Maladaptive behavior classification
- **MMS**: Germain et al. - Mastery measurement scale
- **IRT**: Imagery Rehearsal Therapy

## 📄 License

[Add your license here]

## 👤 Author

[Your name/institution]

---

**Note**: This is a thesis project. The safety layer is designed to ensure therapeutic safety in IRT chatbot interactions by identifying and redirecting maladaptive behaviors toward adaptive goals.

