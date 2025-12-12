"""
Block C: The Critic Pipeline (SafetyCritic)

Orchestrates the safety check by combining:
- Block A: Knowledge Graph
- Block B: Clinical Classifier

Evaluates user dream interventions and returns safety verdicts
with constraint messages for the generator.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .graph_definitions import build_clinical_graph, get_correction_strategies
from .classifier import ClinicalClassifier

logger = logging.getLogger(__name__)


@dataclass
class SafetyResult:
    """
    Result of a safety evaluation.
    
    Attributes:
        is_safe: Whether the intervention is safe (adaptive) or not (maladaptive)
        node_id: The classified node ID
        node_type: 'adaptive' or 'maladaptive'
        category: The clinical category
        constraint: Constraint message for the generator (if unsafe)
        correction_strategies: List of suggested corrections (if unsafe)
        input_text: The original user input
        clinical_guideline: Clinical guidance for why this is problematic (if unsafe)
    """
    is_safe: bool
    node_id: str
    node_type: str
    category: str
    constraint: Optional[str] = None
    correction_strategies: Optional[List[Dict[str, Any]]] = None
    input_text: str = ""
    clinical_guideline: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "is_safe": self.is_safe,
            "node_id": self.node_id,
            "node_type": self.node_type,
            "category": self.category,
            "constraint": self.constraint,
            "correction_strategies": self.correction_strategies,
            "input_text": self.input_text,
            "clinical_guideline": self.clinical_guideline
        }


class SafetyCritic:
    """
    The main safety evaluation pipeline.
    
    Combines the knowledge graph and classifier to evaluate
    user dream interventions and generate safety constraints.
    """
    
    def __init__(self, classifier: Optional[ClinicalClassifier] = None):
        """
        Initialize the SafetyCritic.
        
        Args:
            classifier: Optional pre-initialized classifier. Creates one if not provided.
        """
        # Load the knowledge graph
        self.graph = build_clinical_graph()
        
        # Initialize or use provided classifier
        self.classifier = classifier or ClinicalClassifier()
        
        logger.info("SafetyCritic initialized")
    
    async def evaluate_intervention(self, user_input: str) -> SafetyResult:
        """
        Evaluate a user's proposed dream intervention for safety.
        
        This is the main entry point for the safety check.
        
        Args:
            user_input: The user's proposed action in the dream
            
        Returns:
            SafetyResult with verdict and any constraints
        """
        logger.info(f"Evaluating intervention: '{user_input[:50]}...'")
        
        try:
            # Step 1: Classify the input
            node_id = await self.classifier.classify_intent(user_input)
            
            # Step 2: Look up the node in the graph
            if node_id not in self.graph:
                logger.error(f"Node '{node_id}' not found in graph after classification")
                raise ValueError(f"Invalid node ID: {node_id}")
            
            node_attrs = dict(self.graph.nodes[node_id])
            node_type = node_attrs.get("type", "unknown")
            category = node_attrs.get("category", "unknown")
            
            # Step 3: Make decision based on node type
            if node_type == "adaptive":
                # Safe - return positive result
                result = SafetyResult(
                    is_safe=True,
                    node_id=node_id,
                    node_type=node_type,
                    category=category,
                    input_text=user_input
                )
                logger.info(f"SAFE: '{user_input[:30]}...' classified as {node_id} (adaptive)")
                
            else:  # maladaptive
                # Unsafe - get correction strategies and build constraint
                strategies = get_correction_strategies(self.graph, node_id)
                constraint = self._build_constraint_message(node_id, node_attrs, strategies)
                clinical_guideline = node_attrs.get("clinical_guideline", "")
                
                result = SafetyResult(
                    is_safe=False,
                    node_id=node_id,
                    node_type=node_type,
                    category=category,
                    constraint=constraint,
                    correction_strategies=strategies,
                    input_text=user_input,
                    clinical_guideline=clinical_guideline
                )
                logger.warning(f"UNSAFE: '{user_input[:30]}...' classified as {node_id} (maladaptive)")
            
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating intervention: {str(e)}")
            raise
    
    def _build_constraint_message(
        self, 
        node_id: str, 
        node_attrs: Dict[str, Any], 
        strategies: List[Dict[str, Any]]
    ) -> str:
        """
        Build a constraint message for the generator.
        
        Args:
            node_id: The maladaptive node ID
            node_attrs: The node's attributes
            strategies: List of correction strategies
            
        Returns:
            A constraint message string to inject into the prompt
        """
        # Get the risk description
        risk_description = node_attrs.get("description", node_id)
        clinical_guideline = node_attrs.get("clinical_guideline", "")
        
        # Build the correction suggestions
        suggestions = []
        for strategy in strategies:
            target = strategy["target_node"]
            direction = strategy.get("therapeutic_direction", "")
            suggestions.append(f"- {target}: {direction}")
        
        suggestions_text = "\n".join(suggestions) if suggestions else "Guide toward adaptive coping."
        
        # Construct the full constraint message
        constraint = f"""The user's proposed intervention "{node_id}" is MALADAPTIVE.

Risk Category: {node_attrs.get('category', 'unknown').upper()}
Description: {risk_description}

Clinical Guideline: {clinical_guideline}

REQUIRED: Do NOT validate or encourage this response. Instead, gently guide the user toward one of these ADAPTIVE alternatives:
{suggestions_text}

Use empathetic, supportive language while redirecting. Do not shame or criticize the user's suggestion."""

        return constraint
    
    async def evaluate_batch(self, inputs: List[str]) -> List[SafetyResult]:
        """
        Evaluate multiple interventions.
        
        Args:
            inputs: List of user inputs to evaluate
            
        Returns:
            List of SafetyResults
        """
        results = []
        for user_input in inputs:
            result = await self.evaluate_intervention(user_input)
            results.append(result)
        return results
    
    def get_graph_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the knowledge graph.
        
        Returns:
            Dictionary with graph statistics
        """
        maladaptive_count = sum(
            1 for _, attrs in self.graph.nodes(data=True) 
            if attrs.get("type") == "maladaptive"
        )
        adaptive_count = sum(
            1 for _, attrs in self.graph.nodes(data=True) 
            if attrs.get("type") == "adaptive"
        )
        
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "maladaptive_nodes": maladaptive_count,
            "adaptive_nodes": adaptive_count,
            "node_ids": list(self.graph.nodes())
        }


# For testing
if __name__ == "__main__":
    import asyncio
    
    async def test_critic():
        critic = SafetyCritic()
        
        print("=" * 70)
        print("SafetyCritic Test")
        print("=" * 70)
        
        # Print graph summary
        summary = critic.get_graph_summary()
        print(f"\nGraph Summary:")
        print(f"  Total nodes: {summary['total_nodes']}")
        print(f"  Maladaptive: {summary['maladaptive_nodes']}")
        print(f"  Adaptive: {summary['adaptive_nodes']}")
        print(f"  Total edges: {summary['total_edges']}")
        
        # Test cases from implementation plan
        test_cases = [
            "I wake up",                    # Should trigger ZDPCS_INTERRUPT -> Unsafe
            "I fight back",                 # Should trigger BEHAVIORAL_MASTERY -> Safe
            "I hide under the bed",         # Should trigger ZDPCS_SAFETY_PRINCIPLE -> Unsafe
            "I kill everyone",              # Should trigger ZDPCS_REGRESSIVE_AGGRESSION -> Unsafe
            "I call for help",              # Should trigger SOCIAL_MASTERY -> Safe
            "I find a magic wand",          # Should trigger ENVIRONMENTAL_MASTERY -> Safe
            "I take a deep breath",         # Should trigger EMOTIONAL_MASTERY -> Safe
            "I do nothing",                 # Should trigger ZDPCS_SAFETY_PRINCIPLE -> Unsafe
        ]
        
        print("\n" + "=" * 70)
        print("Test Results")
        print("=" * 70)
        
        for test in test_cases:
            result = await critic.evaluate_intervention(test)
            
            status = "✅ SAFE" if result.is_safe else "⚠️ UNSAFE"
            print(f"\n{status}: '{test}'")
            print(f"  → Classified as: {result.node_id} ({result.node_type})")
            
            if not result.is_safe:
                print(f"  → Category: {result.category}")
                print(f"  → Corrections available: {len(result.correction_strategies or [])}")
                if result.correction_strategies:
                    for s in result.correction_strategies:
                        print(f"     - {s['target_node']}")
    
    asyncio.run(test_critic())

