"""
Block B: Maladaptive-First NLI Clinical Classifier

Prioritizes correctly classifying maladaptive behaviors over adaptive ones.
In clinical settings, it's more important to catch harmful behaviors
(hiding, escaping dream, excessive violence) than to perfectly categorize
helpful behaviors.

Strategy:
1. First check against maladaptive hypotheses
2. If any maladaptive score exceeds threshold, classify as maladaptive
3. Only if no maladaptive match, classify among all nodes
"""

import os
import sys
from typing import Optional, Tuple, Dict, List
import logging
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .graph_definitions import build_clinical_graph, get_all_node_ids

logger = logging.getLogger(__name__)


def softmax(x):
    """Convert scores to probability distribution."""
    exp_x = np.exp(x - np.max(x))
    return exp_x / exp_x.sum()


# Maladaptive hypotheses - tuned for high recall but more specific
MALADAPTIVE_HYPOTHESES = {
    "ZDPCS_SAFETY_PRINCIPLE": "The dreamer hides, freezes, does nothing, or avoids taking action.",
    "ZDPCS_INTERRUPT": "The dreamer wakes up or forces themselves out of the dream.",
    "ZDPCS_REGRESSIVE_AGGRESSION": "The dreamer kills everyone, slaughters, massacres, or destroys everything.",
}

# All node hypotheses for fallback classification
ALL_NODE_HYPOTHESES = {
    # Adaptive
    "BEHAVIORAL_MASTERY": "The dreamer directly confronts, fights, or physically resists the threat.",
    "SOCIAL_MASTERY": "The dreamer asks another person for help or receives assistance from someone else.",
    "ENVIRONMENTAL_MASTERY": "The dreamer finds a useful object like a weapon or tool, or the surroundings change to become safe.",
    "EMOTIONAL_MASTERY": "The dreamer manages their emotions by calming down, breathing deeply, or staying present despite fear.",
    "MYTHICAL_MASTERY": "The dreamer gains supernatural abilities, uses magic or superpowers, flies, or receives help from a divine being.",
    # Maladaptive (same as above)
    "ZDPCS_SAFETY_PRINCIPLE": "The dreamer hides, freezes, avoids, does nothing, or stays passive.",
    "ZDPCS_INTERRUPT": "The dreamer wakes up, ends the dream, or escapes from the dream.",
    "ZDPCS_REGRESSIVE_AGGRESSION": "The dreamer kills, murders, slaughters, massacres, or destroys everything.",
    # Neutral
    "ZDPCS_NARRATIVE_SETTING": "The dreamer sees or observes something without doing anything about it.",
    "ZDPCS_AFFECT_EXPRESSION": "The dreamer expresses fear, sadness, or other emotions without doing anything else.",
}

# Threshold for maladaptive detection on RAW entailment score (not softmax)
# Raw scores range roughly from -5 to +5, with >0 indicating entailment
# Higher = more precise (fewer false positives), Lower = more recall
MALADAPTIVE_RAW_THRESHOLD = 2.5


class MaladaptiveFirstClassifier:
    """
    NLI Classifier that prioritizes maladaptive detection.
    
    Trade-off: Higher recall for maladaptive behaviors at the cost of
    some false positives (adaptive behaviors classified as maladaptive).
    
    This is clinically appropriate because:
    - Missing a maladaptive behavior is more harmful than over-flagging
    - The safety layer can then prompt for correction/redirection
    - Better to guide unnecessarily than miss harmful patterns
    """
    
    def __init__(self, model_name: str = 'cross-encoder/nli-deberta-v3-base'):
        from sentence_transformers import CrossEncoder
        
        logger.info(f"Loading NLI model: {model_name}")
        self.model = CrossEncoder(model_name)
        self.model_name = model_name
        
        self.graph = build_clinical_graph()
        self.valid_node_ids = set(get_all_node_ids(self.graph))
        
        self.maladaptive_hypotheses = MALADAPTIVE_HYPOTHESES
        self.all_hypotheses = ALL_NODE_HYPOTHESES
        
        self._setup_label_mapping()
        
        logger.info(f"MaladaptiveFirstClassifier initialized")
        logger.info(f"Maladaptive raw threshold: {MALADAPTIVE_RAW_THRESHOLD}")
    
    def _setup_label_mapping(self):
        if hasattr(self.model.model, 'config') and hasattr(self.model.model.config, 'label2id'):
            label2id = self.model.model.config.label2id
            if 'entailment' in label2id:
                self.entailment_idx = label2id['entailment']
            elif 'ENTAILMENT' in label2id:
                self.entailment_idx = label2id['ENTAILMENT']
            else:
                self.entailment_idx = 2
        else:
            self.entailment_idx = 2
    
    def _get_scores(self, premise: str, hypotheses: Dict[str, str]) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Get raw and softmax scores for hypotheses."""
        labels = list(hypotheses.keys())
        pairs = [(premise, hypotheses[label]) for label in labels]
        
        scores = self.model.predict(pairs, convert_to_numpy=True)
        
        if len(scores.shape) == 1:
            raw_scores = scores
        else:
            raw_scores = scores[:, self.entailment_idx]
        
        probs = softmax(raw_scores)
        
        raw_dict = {labels[i]: float(raw_scores[i]) for i in range(len(labels))}
        prob_dict = {labels[i]: float(probs[i]) for i in range(len(labels))}
        
        return raw_dict, prob_dict
    
    def _construct_premise(self, user_text: str, context: Optional[str] = None) -> str:
        if context:
            return f"Context: {context} | Action: {user_text}"
        return user_text
    
    async def classify_intent(self, user_text: str, context: Optional[str] = None) -> str:
        """
        Maladaptive-first classification.
        
        1. Check maladaptive hypotheses first using RAW entailment scores
        2. If best maladaptive raw score exceeds threshold, return that
        3. Otherwise, classify among all nodes
        """
        premise = self._construct_premise(user_text, context)
        
        # Step 1: Check maladaptive hypotheses FIRST using RAW scores
        mal_raw, mal_probs = self._get_scores(premise, self.maladaptive_hypotheses)
        best_mal = max(mal_raw, key=mal_raw.get)
        best_mal_raw = mal_raw[best_mal]
        
        logger.debug(f"Maladaptive check: {best_mal} (raw={best_mal_raw:.2f})")
        
        # If maladaptive RAW score exceeds threshold, classify as maladaptive
        if best_mal_raw >= MALADAPTIVE_RAW_THRESHOLD:
            logger.info(f"Maladaptive detected: '{user_text[:30]}...' -> {best_mal} (raw={best_mal_raw:.2f})")
            return best_mal
        
        # Step 2: No strong maladaptive signal, classify among all nodes
        all_raw, all_probs = self._get_scores(premise, self.all_hypotheses)
        best_node = max(all_probs, key=all_probs.get)
        
        logger.info(f"Classification: '{user_text[:30]}...' -> {best_node} ({all_probs[best_node]:.2f})")
        return best_node
    
    async def classify_with_confidence(self, user_text: str, context: Optional[str] = None) -> Tuple[str, dict]:
        """
        Maladaptive-first classification with detailed metadata.
        """
        premise = self._construct_premise(user_text, context)
        
        # Step 1: Check maladaptive first using RAW scores
        mal_raw, mal_probs = self._get_scores(premise, self.maladaptive_hypotheses)
        best_mal = max(mal_raw, key=mal_raw.get)
        best_mal_raw = mal_raw[best_mal]
        
        maladaptive_triggered = best_mal_raw >= MALADAPTIVE_RAW_THRESHOLD
        
        if maladaptive_triggered:
            final_node = best_mal
            all_probs = mal_probs
            confidence = mal_probs[best_mal]
        else:
            # Step 2: Full classification
            all_raw, all_probs = self._get_scores(premise, self.all_hypotheses)
            final_node = max(all_probs, key=all_probs.get)
            confidence = all_probs[final_node]
        
        node_attrs = dict(self.graph.nodes[final_node])
        
        metadata = {
            "node_id": final_node,
            "node_type": node_attrs.get("type"),
            "category": node_attrs.get("category"),
            "description": node_attrs.get("description"),
            "is_maladaptive": node_attrs.get("type") == "maladaptive",
            "input_text": user_text,
            "context": context,
            # Maladaptive check info
            "maladaptive_triggered": maladaptive_triggered,
            "maladaptive_raw_scores": mal_raw,
            "maladaptive_probs": mal_probs,
            "maladaptive_threshold": MALADAPTIVE_RAW_THRESHOLD,
            # Full scores (if computed)
            "all_scores": all_probs,
            "confidence": confidence,
            "model_name": self.model_name
        }
        
        return final_node, metadata
    
    def get_node_info(self, node_id: str) -> dict:
        if node_id not in self.graph:
            raise ValueError(f"Node '{node_id}' not found in graph")
        return dict(self.graph.nodes[node_id])


# For testing
if __name__ == "__main__":
    import asyncio
    
    async def test_maladaptive_first():
        print("=" * 70)
        print("Maladaptive-First NLI Classifier Test")
        print("=" * 70)
        
        classifier = MaladaptiveFirstClassifier()
        
        test_cases = [
            # Should detect as MALADAPTIVE
            ("I hide under the bed", "monster in room"),
            ("I freeze in place", "predator approaching"),
            ("I do nothing", "danger around"),
            ("I wake myself up", "nightmare too intense"),
            ("I force the dream to end", "being overwhelmed"),
            ("I kill everyone", "surrounded by enemies"),
            ("I destroy everything", "trapped"),
            ("I massacre them all", "enemies everywhere"),
            ("I slaughter everyone I see", "being chased"),
            
            # Should be ADAPTIVE (not triggered by maladaptive check)
            ("I fight back", "being attacked"),
            ("I punch the monster", "confronting threat"),
            ("I call for help", "facing danger"),
            ("I calm myself down", "feeling scared"),
            ("I use my powers to fly", "escaping"),
            
            # Should be NEUTRAL
            ("I see a dark forest", "entering dream"),
            ("I feel terrified", "facing monster"),
        ]
        
        print(f"\nMaladaptive threshold: {MALADAPTIVE_THRESHOLD}")
        print("\nResults:")
        print("-" * 70)
        
        maladaptive_correct = 0
        maladaptive_total = 9  # First 9 cases
        
        for i, (action, context) in enumerate(test_cases):
            node_id, meta = await classifier.classify_with_confidence(action, context)
            
            type_emoji = {"adaptive": "✅", "maladaptive": "⚠️", "neutral": "🟡"}.get(meta["node_type"], "❓")
            triggered = " [MAL CHECK]" if meta["maladaptive_triggered"] else ""
            
            print(f"\n{type_emoji} \"{action}\"{triggered}")
            print(f"   Result: {node_id} ({meta['confidence']*100:.1f}%)")
            print(f"   Maladaptive scores: {', '.join([f'{k}:{v*100:.0f}%' for k,v in sorted(meta['maladaptive_scores'].items(), key=lambda x:-x[1])])}")
            
            # Count maladaptive detection
            if i < 9 and meta["node_type"] == "maladaptive":
                maladaptive_correct += 1
        
        print("\n" + "=" * 70)
        print(f"Maladaptive Detection: {maladaptive_correct}/{maladaptive_total} ({maladaptive_correct/maladaptive_total*100:.0f}%)")
        print("=" * 70)
    
    asyncio.run(test_maladaptive_first())
