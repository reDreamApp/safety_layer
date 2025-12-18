"""
Block B: The Entity Linker (Clinical Classifier)

NLI-Based Clinical Classifier using Cross-Encoder.

This module uses Natural Language Inference (NLI) to map user text to clinical 
graph node IDs. The Cross-Encoder approach provides more robust, logic-based 
classification than generative LLMs, specifically handling negation 
(e.g., "I decided not to run") and context more reliably.

Reference: Implementation Plan NLI Classifier (thesis methodology)
"""

import os
import sys
from typing import Optional, Tuple, Dict, List
import logging
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .graph_definitions import build_clinical_graph, get_all_node_ids, get_maladaptive_nodes, get_adaptive_nodes

logger = logging.getLogger(__name__)

# Confidence threshold for classification
CONFIDENCE_THRESHOLD = 0.5

# Default fallback node when confidence is too low
DEFAULT_NODE = "ZDPCS_NARRATIVE_SETTING"


class ClinicalClassifier:
    """
    NLI-Based Clinical Classifier using Cross-Encoder.
    
    Uses the cross-encoder/nli-deberta-v3-base model to classify dream 
    interventions into clinical categories by testing entailment between
    user input (premise) and clinical hypotheses.
    
    Key advantages over LLM-based classification:
    - Deterministic and reproducible results
    - Better handling of negation ("I decided not to run")
    - More robust context understanding
    - Faster inference (no generation needed)
    """
    
    def __init__(self, model_name: str = 'cross-encoder/nli-deberta-v3-base'):
        """
        Initialize the NLI Clinical Classifier.
        
        Args:
            model_name: The HuggingFace model name for the Cross-Encoder.
                       Defaults to 'cross-encoder/nli-deberta-v3-base'.
        """
        from sentence_transformers import CrossEncoder
        
        # Load the NLI model (downloads on first run)
        logger.info(f"Loading NLI model: {model_name}")
        self.model = CrossEncoder(model_name)
        self.model_name = model_name
        
        # Load the clinical knowledge graph
        self.graph = build_clinical_graph()
        self.valid_node_ids = set(get_all_node_ids(self.graph))
        
        # Pre-load hypotheses mapping: {node_id: hypothesis_string}
        self.node_hypotheses: Dict[str, str] = {}
        for node_id, data in self.graph.nodes(data=True):
            if 'nli_hypothesis' in data:
                self.node_hypotheses[node_id] = data['nli_hypothesis']
            else:
                logger.warning(f"Node {node_id} missing nli_hypothesis, using description")
                self.node_hypotheses[node_id] = data.get('description', node_id)
        
        # Determine the label mapping for the model
        # For nli-deberta-v3-base, labels are typically: [contradiction, neutral, entailment]
        # or [entailment, neutral, contradiction] depending on training
        self._setup_label_mapping()
        
        logger.info(f"ClinicalClassifier initialized with {len(self.node_hypotheses)} hypotheses")
        logger.info(f"Valid node IDs: {list(self.valid_node_ids)}")
    
    def _setup_label_mapping(self):
        """
        Set up the label mapping for extracting entailment scores.
        
        Different NLI models may have different label orderings.
        For cross-encoder/nli-deberta-v3-base:
        - Label 0: contradiction
        - Label 1: neutral  
        - Label 2: entailment
        """
        # Check if model has label2id mapping
        if hasattr(self.model.model, 'config') and hasattr(self.model.model.config, 'label2id'):
            label2id = self.model.model.config.label2id
            logger.info(f"Model label mapping: {label2id}")
            
            # Try to find entailment index
            if 'entailment' in label2id:
                self.entailment_idx = label2id['entailment']
            elif 'ENTAILMENT' in label2id:
                self.entailment_idx = label2id['ENTAILMENT']
            else:
                # Default for nli-deberta-v3-base: entailment is index 2
                self.entailment_idx = 2
                logger.warning(f"Could not find 'entailment' in label2id, using default index 2")
        else:
            # Default for most NLI models
            self.entailment_idx = 2
            logger.info(f"Using default entailment index: {self.entailment_idx}")
    
    async def classify_intent(self, user_text: str, context: Optional[str] = None) -> str:
        """
        Classify user dream intervention text into a clinical category using NLI.
        
        Algorithm:
        1. Construct premise from user text and context
        2. Create (premise, hypothesis) pairs for each node
        3. Run NLI inference
        4. Return node with highest entailment score (above threshold)
        
        Args:
            user_text: The user's proposed dream action/intervention
            context: Optional context (either segment context or nightmare context)
            
        Returns:
            The node ID (category code) that best matches the input
        """
        try:
            # 1. Prepare Premise
            premise = self._construct_premise(user_text, context)
            logger.debug(f"Constructed premise: {premise}")
            
            # 2. Prepare (Premise, Hypothesis) pairs
            node_ids = list(self.node_hypotheses.keys())
            pairs = [(premise, self.node_hypotheses[node]) for node in node_ids]
            
            # 3. Run NLI inference
            # The model returns logits for each class [contradiction, neutral, entailment]
            scores = self.model.predict(pairs, convert_to_numpy=True)
            
            # Handle different output shapes
            if len(scores.shape) == 1:
                # Model returns single score (some models do this)
                # Assume it's entailment probability
                entailment_scores = scores
            else:
                # Model returns logits for all classes
                # Extract entailment scores
                entailment_scores = scores[:, self.entailment_idx]
            
            # 4. Find best match
            best_idx = int(np.argmax(entailment_scores))
            best_score = float(entailment_scores[best_idx])
            best_node = node_ids[best_idx]
            
            logger.info(f"Classification: '{user_text[:50]}...' -> {best_node} (score: {best_score:.3f})")
            
            # Log top 3 for debugging
            top_indices = np.argsort(entailment_scores)[-3:][::-1]
            top_results = [(node_ids[i], float(entailment_scores[i])) for i in top_indices]
            logger.debug(f"Top 3 matches: {top_results}")
            
            # 5. Apply threshold
            if best_score < CONFIDENCE_THRESHOLD:
                logger.warning(f"Best score {best_score:.3f} below threshold {CONFIDENCE_THRESHOLD}, returning {DEFAULT_NODE}")
                return DEFAULT_NODE
            
            return best_node
            
        except Exception as e:
            logger.error(f"Error classifying intent: {str(e)}")
            raise
    
    def _construct_premise(self, user_text: str, context: Optional[str] = None) -> str:
        """
        Construct the premise for NLI inference.
        
        Args:
            user_text: The user's action/intervention text
            context: Optional context about the situation
            
        Returns:
            Formatted premise string
        """
        if context:
            return f"Context: {context} | Action: {user_text}"
        return user_text
    
    async def classify_with_confidence(self, user_text: str, context: Optional[str] = None) -> Tuple[str, dict]:
        """
        Classify user text and return additional metadata including confidence scores.
        
        Args:
            user_text: The user's proposed dream action/intervention
            context: Optional context about the situation
            
        Returns:
            Tuple of (node_id, metadata_dict) with confidence scores
        """
        try:
            # Prepare premise and pairs
            premise = self._construct_premise(user_text, context)
            node_ids = list(self.node_hypotheses.keys())
            pairs = [(premise, self.node_hypotheses[node]) for node in node_ids]
            
            # Run inference
            scores = self.model.predict(pairs, convert_to_numpy=True)
            
            # Handle output shape
            if len(scores.shape) == 1:
                entailment_scores = scores
            else:
                entailment_scores = scores[:, self.entailment_idx]
            
            # Get best match
            best_idx = int(np.argmax(entailment_scores))
            best_score = float(entailment_scores[best_idx])
            node_id = node_ids[best_idx]
            
            # Apply threshold
            if best_score < CONFIDENCE_THRESHOLD:
                node_id = DEFAULT_NODE
                # Find score for default node
                default_idx = node_ids.index(DEFAULT_NODE) if DEFAULT_NODE in node_ids else 0
                best_score = float(entailment_scores[default_idx])
            
            # Get node attributes
            node_attrs = dict(self.graph.nodes[node_id])
            
            # Build score ranking
            score_ranking = {
                node_ids[i]: float(entailment_scores[i]) 
                for i in np.argsort(entailment_scores)[-5:][::-1]
            }
            
            metadata = {
                "node_id": node_id,
                "node_type": node_attrs.get("type"),
                "category": node_attrs.get("category"),
                "description": node_attrs.get("description"),
                "is_maladaptive": node_attrs.get("type") == "maladaptive",
                "input_text": user_text,
                "context": context,
                "confidence_score": best_score,
                "score_ranking": score_ranking,
                "model_name": self.model_name
            }
            
            return node_id, metadata
            
        except Exception as e:
            logger.error(f"Error in classify_with_confidence: {str(e)}")
            raise
    
    def classify_intent_sync(self, user_text: str, context: Optional[str] = None) -> str:
        """
        Synchronous version of classify_intent for non-async contexts.
        
        Args:
            user_text: The user's proposed dream action/intervention
            context: Optional context about the situation
            
        Returns:
            The node ID (category code) that best matches the input
        """
        import asyncio
        return asyncio.get_event_loop().run_until_complete(
            self.classify_intent(user_text, context)
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
    
    def get_all_hypotheses(self) -> Dict[str, str]:
        """
        Get all node hypotheses for inspection/debugging.
        
        Returns:
            Dictionary mapping node IDs to their NLI hypotheses
        """
        return self.node_hypotheses.copy()


# For testing
if __name__ == "__main__":
    import asyncio
    
    async def test_classifier():
        print("=" * 70)
        print("NLI Clinical Classifier Test")
        print("=" * 70)
        
        classifier = ClinicalClassifier()
        
        # Print hypotheses
        print("\nLoaded NLI Hypotheses:")
        print("-" * 70)
        for node_id, hypothesis in classifier.get_all_hypotheses().items():
            print(f"  {node_id}: {hypothesis}")
        
        test_cases = [
            # Basic adaptive behaviors
            ("I punch the attacker in the face", None),
            ("I call for my friend to help me", None),
            ("I find a magical sword", None),
            ("I take a deep breath and stay calm", None),
            ("I use my magical powers to fly away", None),
            
            # Basic maladaptive behaviors
            ("I hide under the bed", None),
            ("I wake myself up to escape the nightmare", None),
            ("I kill everyone in the room", None),
            ("I do nothing and just watch", None),
            
            # Neutral
            ("There was a dark forest", None),
            ("I saw a monster in the corner", None),
            ("I felt terrified", None),
            
            # CRITICAL: Negation handling tests
            ("I decided not to run away", None),
            ("I chose to stay instead of hiding", None),
            ("I refuse to hide", None),
            
            # Context-aware tests
            ("I run", "being chased by a monster"),
            ("I hide", "tornado approaching"),
            ("I fight back", "facing an attacker"),
            
            # Complex sentences
            ("I felt scared but I stand my ground", None),
            ("Even though I was terrified, I confronted the monster", None),
        ]
        
        print("\n" + "=" * 70)
        print("Test Results")
        print("=" * 70)
        
        for test_input, context in test_cases:
            try:
                node_id, metadata = await classifier.classify_with_confidence(test_input, context=context)
                node_type = metadata.get("node_type", "unknown")
                score = metadata.get("confidence_score", 0)
                
                if node_type == "maladaptive":
                    status = "⚠️ MALADAPTIVE"
                elif node_type == "adaptive":
                    status = "✅ ADAPTIVE"
                else:
                    status = "🟡 NEUTRAL"
                
                context_str = f" [context: {context}]" if context else ""
                print(f"\n{status}")
                print(f"  Input: '{test_input}'{context_str}")
                print(f"  Classification: {node_id} (confidence: {score:.3f})")
                print(f"  Category: {metadata['category']}")
                
                # Show top scores
                top_scores = list(metadata['score_ranking'].items())[:3]
                print(f"  Top 3: {top_scores}")
                
            except Exception as e:
                print(f"\n❌ ERROR for '{test_input}': {e}")
    
    asyncio.run(test_classifier())
