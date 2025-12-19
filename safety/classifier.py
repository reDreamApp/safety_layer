"""
Block B: The Entity Linker (Clinical Classifier)

Uses an LLM to map user text to clinical graph node IDs.
The classifier acts as a "Clinical Coder" that identifies whether
user input represents adaptive or maladaptive dream behaviors.
"""

import os
import sys
from typing import Optional, Tuple
import logging
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AI.agent import Agent, ModelConfig, MODELS
from .graph_definitions import build_clinical_graph, get_all_node_ids, get_maladaptive_nodes, get_adaptive_nodes

logger = logging.getLogger(__name__)


# System prompt for the Clinical Coder
CLINICAL_CODER_PROMPT = """You are a Clinical Coder for Imagery Rehearsal Therapy (IRT). Your task is to classify dream actions/interventions into predefined clinical categories based on the MMS (Mastery Measurement Scale) and ZDPCS (Zurich Dream Process Coding System).

## Available Categories

### MALADAPTIVE (Risk) Categories - from ZDPCS:
1. **ZDPCS_SAFETY_PRINCIPLE** - Avoidance behaviors: hiding, freezing, looking away, becoming invisible, passive observation, doing nothing
2. **ZDPCS_INTERRUPT** - Dream escape: forcing oneself awake, waking up, dream ending abruptly, scene dissolving, refusing to continue
3. **ZDPCS_REGRESSIVE_AGGRESSION** - Extreme violence: killing everyone, excessive brutal violence, destroying the environment, uncontrolled rage, disproportionate violence

### ADAPTIVE (Goal) Categories - from MMS:
4. **BEHAVIORAL_MASTERY** - Active response: fighting back proportionately, running purposefully, confronting threats, taking control, winning over aggressor
5. **SOCIAL_MASTERY** - Social support: calling for help, allies appearing, working with others, receiving protection, adding helpful characters
6. **ENVIRONMENTAL_MASTERY** - Environment/Tools: finding weapons/tools, environment changing favorably, safe place appearing, spontaneous helpful events
7. **EMOTIONAL_MASTERY** - Self-regulation: calming down, accepting peacefully, transforming fear, staying present, changing emotional reactions
8. **MYTHICAL_MASTERY** - Supernatural: using magical powers, divine intervention, supernatural figure helping, gaining superpowers, miraculous events

### NEUTRAL Categories - Context without action:
9. **ZDPCS_NARRATIVE_SETTING** - Scene description: describing the environment, characters, or setting without active interaction or response
10. **ZDPCS_AFFECT_EXPRESSION** - Feeling statement: explicit expression of emotion (e.g., "I felt scared", "I was terrified") without accompanying action

## Instructions
- Analyze the user's proposed dream action/intervention
- Classify it into EXACTLY ONE of the 10 categories above
- Respond with ONLY the category code (e.g., "BEHAVIORAL_MASTERY")

### Negation Handling (CRITICAL)
- If the user mentions an action they AVOIDED doing (e.g., "I decided not to run", "I chose not to hide"), classify the DECISION itself, not the avoided action
- "I decided not to run away" = BEHAVIORAL_MASTERY (active choice to stay and engage)
- "I chose not to hide" = BEHAVIORAL_MASTERY (active choice to face the situation)
- "I refused to wake up" = EMOTIONAL_MASTERY (choice to stay in dream)

### Ambiguity Rule
- If the user describes ONLY the setting or their feelings WITHOUT taking any action, classify as NARRATIVE or AFFECT
- "There was a monster" = ZDPCS_NARRATIVE_SETTING
- "I felt scared" = ZDPCS_AFFECT_EXPRESSION  
- "I felt scared so I ran" = BEHAVIORAL_MASTERY (action present)

### Priority Rules
- If the input describes inaction or passive avoidance (doing nothing, hiding without choosing to), classify as ZDPCS_SAFETY_PRINCIPLE
- If the input describes waking up or ending the dream, classify as ZDPCS_INTERRUPT
- If the input describes extreme/chaotic violence (killing everyone, destroying everything), classify as ZDPCS_REGRESSIVE_AGGRESSION
- If the input describes using magic/supernatural powers, classify as MYTHICAL_MASTERY
- If the input describes finding tools or environment changing, classify as ENVIRONMENTAL_MASTERY

## Response Format
Respond with ONLY the category code. No explanations, no punctuation, no additional text.

Example inputs and outputs:
- "I hide under the bed" -> ZDPCS_SAFETY_PRINCIPLE
- "I do nothing" -> ZDPCS_SAFETY_PRINCIPLE
- "I wake myself up" -> ZDPCS_INTERRUPT
- "I kill everyone in the room" -> ZDPCS_REGRESSIVE_AGGRESSION
- "I punch the attacker" -> BEHAVIORAL_MASTERY
- "I fight back" -> BEHAVIORAL_MASTERY
- "I call for my friend to help" -> SOCIAL_MASTERY
- "I find a sword on the ground" -> ENVIRONMENTAL_MASTERY
- "I take a deep breath and stay calm" -> EMOTIONAL_MASTERY
- "I use my magical powers to fly away" -> MYTHICAL_MASTERY
- "An angel appears to protect me" -> MYTHICAL_MASTERY
- "There was a dark forest" -> ZDPCS_NARRATIVE_SETTING
- "I saw a monster" -> ZDPCS_NARRATIVE_SETTING
- "I felt terrified" -> ZDPCS_AFFECT_EXPRESSION
- "I decided not to run away" -> BEHAVIORAL_MASTERY
- "I chose to stay instead of hiding" -> BEHAVIORAL_MASTERY

### CRITICAL: Emotional Suppression vs Expression (Context-Dependent)
When nightmare context is provided, distinguish between:
- ACKNOWLEDGING emotion (therapeutic, neutral): "I felt scared", "I was terrified"  
- SUPPRESSING emotion about distressing content (avoidance, maladaptive): "I don't feel panic", "I'm fine with it"

If the nightmare contains distressing content (death, violence, threat) and the user claims to feel nothing or be "fine with it" WITHOUT transforming the scenario, classify as ZDPCS_SAFETY_PRINCIPLE (emotional avoidance).

Examples with context:
- Nightmare: "My dog was dead on the floor" + Response: "I don't feel any panic" -> ZDPCS_SAFETY_PRINCIPLE (emotional suppression)
- Nightmare: "My dog was dead on the floor" + Response: "I'm fine with the situation" -> ZDPCS_SAFETY_PRINCIPLE (emotional suppression)
- Nightmare: "My dog was dead on the floor" + Response: "I see my dog is actually alive and happy" -> ENVIRONMENTAL_MASTERY (transformation)
- Nightmare: "Being chased by monster" + Response: "I felt terrified" -> ZDPCS_AFFECT_EXPRESSION (acknowledging emotion)
"""


class ClinicalClassifier:
    """
    Classifies user dream interventions into clinical categories using an LLM.
    
    Uses the Agent class to send classification requests and validates
    that returned codes exist in the clinical knowledge graph.
    """
    
    def __init__(self, model_config: Optional[ModelConfig] = None):
        """
        Initialize the Clinical Classifier.
        
        Args:
            model_config: Optional model configuration. Defaults to MISTRAL_NEMO for speed.
        """
        # Use small Mistral model for classification
        self.model_config = model_config or MODELS["MISTRAL_NEMO"]
        
        # Initialize the agent with clinical coder prompt
        self.agent = Agent(
            model_config=self.model_config,
            system_prompt=CLINICAL_CODER_PROMPT,
            temperature=0.1  # Low temperature for consistent classification
        )
        
        # Load the graph to validate node IDs
        self.graph = build_clinical_graph()
        self.valid_node_ids = set(get_all_node_ids(self.graph))
        
        logger.info(f"ClinicalClassifier initialized with model: {self.model_config.name}")
        logger.info(f"Valid node IDs: {self.valid_node_ids}")
    
    async def classify_intent(self, user_text: str, context: Optional[str] = None) -> str:
        """
        Classify user dream intervention text into a clinical category.
        
        Args:
            user_text: The user's proposed dream action/intervention
            context: Optional context about the original nightmare for disambiguation
            
        Returns:
            The node ID (category code) that best matches the input
            
        Raises:
            ValueError: If the LLM returns an invalid node ID
        """
        try:
            # Build context-aware message if nightmare context is provided
            if context:
                classification_input = f"""[NIGHTMARE CONTEXT]
{context}

[USER'S REWRITING ATTEMPT]
{user_text}

Classify the rewriting attempt above. Remember: If the user claims to feel nothing or be "fine" with distressing content WITHOUT transforming the scenario, that is ZDPCS_SAFETY_PRINCIPLE (emotional avoidance)."""
            else:
                classification_input = user_text
            
            # Send classification request
            response, usage = await self.agent.generate(classification_input)
            
            # Clean the response (remove whitespace, convert to uppercase)
            node_id = response.strip().upper()
            
            # Remove any punctuation that might have been added
            node_id = ''.join(c for c in node_id if c.isalnum() or c == '_')
            
            logger.info(f"Classification result: '{user_text[:50]}...' -> {node_id}")
            logger.debug(f"Token usage: {usage}")
            
            # Validate the node ID exists in the graph
            if node_id not in self.valid_node_ids:
                logger.warning(f"Invalid node ID returned: {node_id}. Attempting fuzzy match...")
                node_id = self._fuzzy_match_node_id(node_id)
            
            return node_id
            
        except Exception as e:
            logger.error(f"Error classifying intent: {str(e)}")
            raise
    
    async def classify_with_confidence(self, user_text: str, context: Optional[str] = None) -> Tuple[str, dict]:
        """
        Classify user text and return additional metadata.
        
        Args:
            user_text: The user's proposed dream action/intervention
            context: Optional context about the original nightmare for disambiguation
            
        Returns:
            Tuple of (node_id, metadata_dict)
        """
        node_id = await self.classify_intent(user_text, context=context)
        
        # Get node attributes from graph
        node_attrs = dict(self.graph.nodes[node_id])
        
        metadata = {
            "node_id": node_id,
            "node_type": node_attrs.get("type"),
            "category": node_attrs.get("category"),
            "description": node_attrs.get("description"),
            "is_maladaptive": node_attrs.get("type") == "maladaptive",
            "input_text": user_text
        }
        
        return node_id, metadata
    
    def _fuzzy_match_node_id(self, invalid_id: str) -> str:
        """
        Attempt to match an invalid node ID to a valid one.
        
        Args:
            invalid_id: The invalid node ID returned by the LLM
            
        Returns:
            The best matching valid node ID
            
        Raises:
            ValueError: If no match can be found
        """
        # Try simple substring matching
        for valid_id in self.valid_node_ids:
            if invalid_id in valid_id or valid_id in invalid_id:
                logger.info(f"Fuzzy matched '{invalid_id}' to '{valid_id}'")
                return valid_id
        
        # Try matching keywords
        keyword_map = {
            "AVOID": "ZDPCS_SAFETY_PRINCIPLE",
            "HIDE": "ZDPCS_SAFETY_PRINCIPLE",
            "FREEZE": "ZDPCS_SAFETY_PRINCIPLE",
            "SAFE": "ZDPCS_SAFETY_PRINCIPLE",
            "WAKE": "ZDPCS_INTERRUPT",
            "INTERRUPT": "ZDPCS_INTERRUPT",
            "ESCAPE": "ZDPCS_INTERRUPT",
            "KILL": "ZDPCS_REGRESSIVE_AGGRESSION",
            "VIOLENCE": "ZDPCS_REGRESSIVE_AGGRESSION",
            "AGGRESSION": "ZDPCS_REGRESSIVE_AGGRESSION",
            "DESTROY": "ZDPCS_REGRESSIVE_AGGRESSION",
            "ACTION": "BEHAVIORAL_MASTERY",
            "FIGHT": "BEHAVIORAL_MASTERY",
            "BEHAV": "BEHAVIORAL_MASTERY",
            "HELP": "SOCIAL_MASTERY",
            "SOCIAL": "SOCIAL_MASTERY",
            "FRIEND": "SOCIAL_MASTERY",
            "TOOL": "ENVIRONMENTAL_MASTERY",
            "ENVIRON": "ENVIRONMENTAL_MASTERY",
            "CALM": "EMOTIONAL_MASTERY",
            "EMOTION": "EMOTIONAL_MASTERY",
            "SOOTH": "EMOTIONAL_MASTERY",
            "MYTHIC": "MYTHICAL_MASTERY",
            "MAGIC": "MYTHICAL_MASTERY",
            "SUPER": "MYTHICAL_MASTERY",
            "DIVINE": "MYTHICAL_MASTERY",
            "ANGEL": "MYTHICAL_MASTERY",
            "POWER": "MYTHICAL_MASTERY",
            # Neutral categories
            "NARRATIVE": "ZDPCS_NARRATIVE_SETTING",
            "SETTING": "ZDPCS_NARRATIVE_SETTING",
            "SCENE": "ZDPCS_NARRATIVE_SETTING",
            "AFFECT": "ZDPCS_AFFECT_EXPRESSION",
            "FEELING": "ZDPCS_AFFECT_EXPRESSION",
            "FELT": "ZDPCS_AFFECT_EXPRESSION",
        }
        
        for keyword, valid_id in keyword_map.items():
            if keyword in invalid_id:
                logger.info(f"Keyword matched '{invalid_id}' to '{valid_id}'")
                return valid_id
        
        # If no match found, raise an error
        raise ValueError(
            f"Could not match '{invalid_id}' to any valid node ID. "
            f"Valid IDs are: {self.valid_node_ids}"
        )
    
    def get_node_info(self, node_id: str) -> dict:
        """
        Get information about a specific node.
        
        Args:
            node_id: The node ID to look up
            
        Returns:
            Dictionary of node attributes
        """
        if node_id not in self.graph:
            raise ValueError(f"Node '{node_id}' not found in graph")
        
        return dict(self.graph.nodes[node_id])


# For testing
if __name__ == "__main__":
    import asyncio
    
    async def test_classifier():
        classifier = ClinicalClassifier()
        
        test_cases = [
            # Maladaptive
            "I hide under the bed",
            "I wake myself up to escape the nightmare",
            "I kill everyone in the room",
            "I do nothing and just watch",
            # Adaptive
            "I punch the attacker in the face",
            "I call for my friend to help me",
            "I find a magical sword",
            "I take a deep breath and stay calm",
            "I run away as fast as I can",
            # Neutral - Narrative
            "There was a dark forest",
            "I saw a monster in the corner",
            # Neutral - Affect
            "I felt terrified",
            "I was scared",
            # Negation handling
            "I decided not to run away",
            "I chose to stay instead of hiding",
        ]
        
        print("=" * 60)
        print("Clinical Classifier Test")
        print("=" * 60)
        
        for test in test_cases:
            try:
                node_id, metadata = await classifier.classify_with_confidence(test)
                node_type = metadata.get("node_type", "unknown")
                if node_type == "maladaptive":
                    status = "⚠️ MALADAPTIVE"
                elif node_type == "adaptive":
                    status = "✅ ADAPTIVE"
                else:
                    status = "🟡 NEUTRAL"
                print(f"\n{status}")
                print(f"  Input: '{test}'")
                print(f"  Classification: {node_id}")
                print(f"  Category: {metadata['category']}")
            except Exception as e:
                print(f"\n❌ ERROR for '{test}': {e}")
    
    asyncio.run(test_classifier())
