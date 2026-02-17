"""
Block C: The Critic Pipeline (SafetyCritic)

Upgraded to "Clinical Reasoning Engine" with:
- Intelligent Segmentation: Parses multi-part user inputs
- Batch Classification: Maps each segment to a Graph Node
- Triage Logic: Prioritizes the most critical risk for correction
- Constraint Synthesis: Generates "Validate + Correct" instructions

Orchestrates the safety check by combining:
- Block A: Knowledge Graph
- Block B: Clinical Classifier
"""

import logging
import json
import os
import sys
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .graph_definitions import build_clinical_graph, get_correction_strategies
from .classifier import ClinicalClassifier
from AI.agent import Agent, MODELS

logger = logging.getLogger(__name__)


# Severity levels for triage (lower number = higher priority)
SEVERITY_PRIORITY = {
    "VIOLENT_REVENGE": 1,               # CRITICAL - Violence
    "INTERRUPTION": 2,                  # HIGH - Waking Up/Escape
    "AVOIDANCE": 3,                     # MODERATE - Avoidance
}

# Segmenter system prompt
SEGMENTER_PROMPT = """You are a text segmenter for dream therapy responses. Your task is to parse user input into discrete segments, label each by type, AND extract the context/threat being responded to.

## Segment Types
- **ACTION**: The user describes doing something in the dream (e.g., "I fight the monster", "I run away")
- **THOUGHT**: The user describes a thought or decision (e.g., "I decide to stay", "I realize I can fly")
- **FEELING**: The user expresses an emotion (e.g., "I feel scared", "I'm terrified")
- **META**: Conversational/meta content not part of the dream narrative (e.g., "I hate this", "this is stupid", questions about therapy)

## Context Extraction
For each segment (especially ACTION/THOUGHT), identify the **Immediate Threat** or **Situation** the user is responding to.
- Use the provided Nightmare Context (if any) and the User Input.
- Example: If input is "I punch it", context might be "facing the monster".
- Example: If input is "I hide", context might be "being chased".
- If no clear context applies (e.g. for META), use null.

## Instructions
1. Split the input into discrete segments based on meaning
2. Label each segment with its type
3. Extract the "context" string for each segment
4. Return a JSON array of objects with "text", "type", and "context" keys
5. If the entire input is a single type, return a single-element array
6. Preserve the original text in each segment

## Response Format
Return ONLY valid JSON array. No explanations, no markdown, just JSON.

## Examples

Context: "Being chased by a dragon in a cave."
Input: "I hate this therapy, but I guess I turn and fight it."
Output: [{"text": "I hate this therapy", "type": "META", "context": null}, {"text": "but I guess I turn and fight it", "type": "ACTION", "context": "being chased by dragon"}]

Input: "I feel scared but I stand my ground"
Output: [{"text": "I feel scared", "type": "FEELING", "context": null}, {"text": "but I stand my ground", "type": "ACTION", "context": "facing the threat"}]

Input: "I run away as fast as I can"
Output: [{"text": "I run away as fast as I can", "type": "ACTION", "context": "escaping from danger"}]

Input: "This is dumb"
Output: [{"text": "This is dumb", "type": "META", "context": null}]

Input: "I'm terrified"
Output: [{"text": "I'm terrified", "type": "FEELING", "context": null}]

Input: "Why do I have to do this? Fine, I'll punch the monster I guess"
Output: [{"text": "Why do I have to do this?", "type": "META", "context": null}, {"text": "Fine, I'll punch the monster I guess", "type": "ACTION", "context": "confronting the monster"}]
"""


@dataclass
class SegmentResult:
    """Result of segmenting a single piece of text."""
    text: str
    segment_type: str  # ACTION, THOUGHT, FEELING, META
    context: Optional[str] = None  # Immediate threat/situation context for NLI classification
    node_id: Optional[str] = None
    node_type: Optional[str] = None  # adaptive, maladaptive, neutral
    category: Optional[str] = None
    confidence: Optional[float] = None  # Classification confidence from logprobs (0-1)
    mean_logprob: Optional[float] = None  # Mean log probability of classification tokens


@dataclass
class SafetyResult:
    """
    Result of a safety evaluation.
    
    Attributes:
        is_safe: Whether the intervention is safe (adaptive/neutral) or not (maladaptive)
        node_id: The primary classified node ID (most critical if unsafe)
        node_type: 'adaptive', 'maladaptive', or 'neutral'
        category: The clinical category
        constraint: Constraint message for the generator (if unsafe)
        correction_strategies: List of suggested corrections (if unsafe)
        input_text: The original user input
        clinical_guideline: Clinical guidance for why this is problematic (if unsafe)
        segments: List of all classified segments
        adaptive_segments: List of adaptive/neutral segments to validate
        severity: Severity level of the primary risk (if unsafe)
        confidence: Classification confidence for the primary node (0-1)
        mean_logprob: Mean log probability for the primary classification
    """
    is_safe: bool
    node_id: str
    node_type: str
    category: str
    constraint: Optional[str] = None
    correction_strategies: Optional[List[Dict[str, Any]]] = None
    input_text: str = ""
    clinical_guideline: str = ""
    segments: List[SegmentResult] = field(default_factory=list)
    adaptive_segments: List[SegmentResult] = field(default_factory=list)
    severity: Optional[str] = None
    confidence: Optional[float] = None
    mean_logprob: Optional[float] = None
    
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
            "clinical_guideline": self.clinical_guideline,
            "segments": [
                {
                    "text": s.text, 
                    "type": s.segment_type, 
                    "node_id": s.node_id, 
                    "node_type": s.node_type,
                    "confidence": s.confidence
                } 
                for s in self.segments
            ],
            "adaptive_segments": [{"text": s.text, "node_id": s.node_id} for s in self.adaptive_segments],
            "severity": self.severity,
            "confidence": self.confidence,
            "mean_logprob": self.mean_logprob
        }


class SafetyCritic:
    """
    The main safety evaluation pipeline - "Clinical Reasoning Engine".
    
    Implements the Segmented Analysis Pipeline:
    1. Intelligent Segmentation: Parse input into labeled segments
    2. Filtering: Discard META segments
    3. Batch Classification: Map each segment to a Graph Node
    4. Triage Logic: Select the most critical risk
    5. Constraint Synthesis: Generate Validate + Correct instructions
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
        
        # Initialize segmenter agent (small Mistral model for speed)
        self.segmenter = Agent(
            model_config=MODELS["MISTRAL_NEMO"],
            system_prompt=SEGMENTER_PROMPT,
            temperature=0.1
        )
        
        logger.info("SafetyCritic initialized with segmentation pipeline")
    
    async def segment_input(self, user_input: str, nightmare_context: Optional[str] = None) -> List[SegmentResult]:
        """
        Segment user input into discrete parts with type labels and context.
        
        Uses a lightweight LLM to parse complex, multi-part inputs.
        
        Args:
            user_input: The user's full response text
            nightmare_context: Optional context about the original nightmare
            
        Returns:
            List of SegmentResult objects with text, type, and context
        """
        try:
            # Build input with nightmare context if provided
            if nightmare_context:
                segmenter_input = f"Context: \"{nightmare_context}\"\nInput: \"{user_input}\""
            else:
                segmenter_input = f"Input: \"{user_input}\""
            
            response, _, _ = await self.segmenter.generate(segmenter_input)
            
            # Clean the response - remove any markdown code blocks if present
            cleaned = response.strip()
            if cleaned.startswith("```"):
                # Remove markdown code block wrapper
                lines = cleaned.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                cleaned = "\n".join(lines)
            
            # Extract JSON array - find the first [ and last ] to handle extra text
            start_idx = cleaned.find('[')
            end_idx = cleaned.rfind(']')
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                cleaned = cleaned[start_idx:end_idx + 1]
            
            # Parse JSON
            segments_data = json.loads(cleaned)
            
            segments = []
            for seg in segments_data:
                segments.append(SegmentResult(
                    text=seg.get("text", ""),
                    segment_type=seg.get("type", "ACTION").upper(),
                    context=seg.get("context")  # Extract context for NLI
                ))
            
            logger.info(f"Segmented input into {len(segments)} parts: {[(s.segment_type, s.context) for s in segments]}")
            return segments
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse segmenter response: {e}. Treating as single ACTION segment.")
            # Fallback: treat entire input as single ACTION segment
            return [SegmentResult(text=user_input, segment_type="ACTION", context=nightmare_context)]
        except Exception as e:
            logger.error(f"Segmentation error: {e}. Treating as single ACTION segment.")
            return [SegmentResult(text=user_input, segment_type="ACTION", context=nightmare_context)]
    
    async def evaluate_intervention(self, user_input: str, nightmare_context: Optional[str] = None) -> SafetyResult:
        """
        Evaluate a user's proposed dream intervention for safety.
        
        Implements the full Segmented Analysis Pipeline:
        1. Segment the input
        2. Filter META segments
        3. Classify remaining segments (with nightmare context for disambiguation)
        4. Triage by severity
        5. Build constraint message
        
        Args:
            user_input: The user's proposed action in the dream
            nightmare_context: Optional context about the original nightmare. 
                             Used to disambiguate emotional suppression from expression.
            
        Returns:
            SafetyResult with verdict and any constraints
        """
        context_info = f" (with nightmare context)" if nightmare_context else ""
        logger.info(f"Evaluating intervention{context_info}: '{user_input[:50]}...'")
        
        try:
            # Step 1: Segment the input (pass nightmare context for context extraction)
            segments = await self.segment_input(user_input, nightmare_context=nightmare_context)
            
            # Step 2: Filter out META segments
            dream_segments = [s for s in segments if s.segment_type != "META"]
            
            # If no dream segments remain, return safe/pass-through
            if not dream_segments:
                logger.info("No dream content found (all META). Passing through.")
                return SafetyResult(
                    is_safe=True,
                    node_id="META_ONLY",
                    node_type="meta",
                    category="conversational",
                    input_text=user_input,
                    segments=segments,
                    constraint="User input is conversational/meta content. Respond naturally without dream guidance."
                )
            
            # Step 3: Classify each dream segment
            maladaptive_segments = []
            adaptive_segments = []
            neutral_segments = []
            
            for segment in dream_segments:
                # Use segment-level context if available, otherwise fall back to nightmare context
                segment_context = segment.context or nightmare_context
                node_id, logprobs = await self.classifier.classify_intent(
                    segment.text, 
                    context=segment_context,
                    return_logprobs=True  # Always request logprobs for confidence
                )
                
                if node_id not in self.graph:
                    logger.warning(f"Node '{node_id}' not found in graph")
                    continue
                
                node_attrs = dict(self.graph.nodes[node_id])
                segment.node_id = node_id
                segment.node_type = node_attrs.get("type", "unknown")
                segment.category = node_attrs.get("category", "unknown")
                
                # Store confidence metrics from logprobs
                if logprobs:
                    segment.confidence = logprobs.confidence
                    segment.mean_logprob = logprobs.mean_logprob
                
                if segment.node_type == "maladaptive":
                    maladaptive_segments.append(segment)
                elif segment.node_type == "adaptive":
                    adaptive_segments.append(segment)
                else:  # neutral
                    neutral_segments.append(segment)
            
            # Step 4: Triage - if no maladaptive, return safe
            if not maladaptive_segments:
                # All safe - validate adaptive parts
                primary_segment = adaptive_segments[0] if adaptive_segments else (neutral_segments[0] if neutral_segments else dream_segments[0])
                
                result = SafetyResult(
                    is_safe=True,
                    node_id=primary_segment.node_id or "UNKNOWN",
                    node_type=primary_segment.node_type or "unknown",
                    category=primary_segment.category or "unknown",
                    input_text=user_input,
                    segments=segments,
                    adaptive_segments=adaptive_segments + neutral_segments,
                    constraint=self._build_validation_message(adaptive_segments + neutral_segments),
                    confidence=primary_segment.confidence,
                    mean_logprob=primary_segment.mean_logprob
                )
                logger.info(f"SAFE: All segments are adaptive/neutral")
                return result
            
            # Step 5: Sort maladaptive by severity and select top priority
            sorted_maladaptive = self._sort_by_severity(maladaptive_segments)
            primary_risk = sorted_maladaptive[0]
            
            # Get correction strategies
            strategies = get_correction_strategies(self.graph, primary_risk.node_id)
            node_attrs = dict(self.graph.nodes[primary_risk.node_id])
            
            # Build constraint with validate + correct structure
            constraint = self._build_constraint_message(
                primary_risk=primary_risk,
                node_attrs=node_attrs,
                strategies=strategies,
                adaptive_segments=adaptive_segments + neutral_segments
            )
            
            severity = self._get_severity_label(primary_risk.node_id)
            
            result = SafetyResult(
                is_safe=False,
                node_id=primary_risk.node_id,
                node_type=primary_risk.node_type,
                category=primary_risk.category,
                constraint=constraint,
                correction_strategies=strategies,
                input_text=user_input,
                clinical_guideline=node_attrs.get("clinical_guideline", ""),
                segments=segments,
                adaptive_segments=adaptive_segments + neutral_segments,
                severity=severity,
                confidence=primary_risk.confidence,
                mean_logprob=primary_risk.mean_logprob
            )
            
            logger.warning(f"UNSAFE: Primary risk is {primary_risk.node_id} ({severity})")
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating intervention: {str(e)}")
            raise
    
    def _sort_by_severity(self, segments: List[SegmentResult]) -> List[SegmentResult]:
        """
        Sort maladaptive segments by severity priority.
        
        Priority order:
        1. CRITICAL: VIOLENT_REVENGE (Violence)
        2. HIGH: INTERRUPTION (Waking Up)
        3. MODERATE: AVOIDANCE (Avoidance)
        
        Tie-breaker: First chronological occurrence (original order)
        
        Args:
            segments: List of maladaptive segments
            
        Returns:
            Sorted list with highest severity first
        """
        def get_priority(segment: SegmentResult) -> tuple:
            # Get severity priority (lower = more critical)
            severity = SEVERITY_PRIORITY.get(segment.node_id, 99)
            # Use original index for tie-breaking
            return severity
        
        return sorted(segments, key=get_priority)
    
    def _get_severity_label(self, node_id: str) -> str:
        """Get human-readable severity label for a node."""
        priority = SEVERITY_PRIORITY.get(node_id, 99)
        if priority == 1:
            return "CRITICAL"
        elif priority == 2:
            return "HIGH"
        elif priority == 3:
            return "MODERATE"
        return "UNKNOWN"
    
    def _build_validation_message(self, adaptive_segments: List[SegmentResult]) -> str:
        """Build a validation message for safe inputs."""
        if not adaptive_segments:
            return "User input is adaptive/neutral. Proceed with the dream narrative."
        
        validations = []
        for seg in adaptive_segments:
            if seg.node_id:
                validations.append(f"'{seg.text}' ({seg.node_id})")
        
        if validations:
            return f"VALIDATE: User demonstrated adaptive responses: {', '.join(validations)}. Proceed with encouragement."
        return "User input is adaptive/neutral. Proceed with the dream narrative."
    
    def _build_constraint_message(
        self, 
        primary_risk: SegmentResult,
        node_attrs: Dict[str, Any], 
        strategies: List[Dict[str, Any]],
        adaptive_segments: List[SegmentResult]
    ) -> str:
        """
        Build a constraint message for the generator with Validate + Correct structure.
        
        Args:
            primary_risk: The highest-priority maladaptive segment
            node_attrs: The node's attributes
            strategies: List of correction strategies
            adaptive_segments: Any adaptive/neutral segments to validate
            
        Returns:
            A constraint message string to inject into the prompt
        """
        severity = self._get_severity_label(primary_risk.node_id)
        risk_description = node_attrs.get("description", primary_risk.node_id)
        clinical_guideline = node_attrs.get("clinical_guideline", "")
        
        # Build VALIDATE section
        validate_section = ""
        if adaptive_segments:
            validations = []
            for seg in adaptive_segments:
                validations.append(f"'{seg.text}'")
            validate_section = f"""VALIDATE: The user showed positive elements: {', '.join(validations)}. 
Acknowledge these first (e.g., "Good job noticing..." or "I appreciate that you...")."""
        
        # Build CORRECT section
        primary_strategy = strategies[0] if strategies else None
        correction_direction = primary_strategy.get("therapeutic_direction", "Guide toward adaptive coping.") if primary_strategy else "Guide toward adaptive coping."
        
        # Build suggestions
        suggestions = []
        for strategy in strategies[:2]:  # Limit to top 2 suggestions
            target = strategy["target_node"]
            direction = strategy.get("therapeutic_direction", "")
            suggestions.append(f"- {target}: {direction}")
        suggestions_text = "\n".join(suggestions) if suggestions else "Guide toward adaptive coping."
        
        # Construct the full constraint message
        constraint = f"""[SAFETY SYSTEM - INTERVENTION REQUIRED]

{validate_section}

CORRECT: User demonstrated "{primary_risk.node_id}" - this is a {severity} risk.
Risk Description: {risk_description}
Clinical Guideline: {clinical_guideline}

INSTRUCTION: Gently redirect using this approach:
{correction_direction}

Alternative therapeutic directions:
{suggestions_text}

IMPORTANT: 
- Do NOT validate or encourage the maladaptive response ("{primary_risk.text}")
- Focus correction on THIS specific issue only - do not list other potential problems
- Use empathetic, supportive language while redirecting
- Do not shame or criticize the user's suggestion"""

        return constraint
    
    async def evaluate_batch(self, inputs: List[str], nightmare_context: Optional[str] = None) -> List[SafetyResult]:
        """
        Evaluate multiple interventions.
        
        Args:
            inputs: List of user inputs to evaluate
            nightmare_context: Optional context about the original nightmare
            
        Returns:
            List of SafetyResults
        """
        results = []
        for user_input in inputs:
            result = await self.evaluate_intervention(user_input, nightmare_context=nightmare_context)
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
        neutral_count = sum(
            1 for _, attrs in self.graph.nodes(data=True) 
            if attrs.get("type") == "neutral"
        )
        
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "maladaptive_nodes": maladaptive_count,
            "adaptive_nodes": adaptive_count,
            "neutral_nodes": neutral_count,
            "node_ids": list(self.graph.nodes())
        }


# For testing
if __name__ == "__main__":
    import asyncio
    
    async def test_critic():
        critic = SafetyCritic()
        
        print("=" * 70)
        print("SafetyCritic Test - Upgraded Pipeline")
        print("=" * 70)
        
        # Print graph summary
        summary = critic.get_graph_summary()
        print(f"\nGraph Summary:")
        print(f"  Total nodes: {summary['total_nodes']}")
        print(f"  Maladaptive: {summary['maladaptive_nodes']}")
        print(f"  Adaptive: {summary['adaptive_nodes']}")
        print(f"  Neutral: {summary['neutral_nodes']}")
        print(f"  Total edges: {summary['total_edges']}")
        
        # Test cases including complex multi-part inputs
        test_cases = [
            # Simple cases
            "I wake up",                    # Should trigger INTERRUPTION -> Unsafe
            "I fight back",                 # Should trigger BEHAVIORAL_MASTERY -> Safe
            "I hide under the bed",         # Should trigger AVOIDANCE -> Unsafe
            "I kill everyone",              # Should trigger VIOLENT_REVENGE -> Unsafe (CRITICAL)
            "I call for help",              # Should trigger SOCIAL_MASTERY -> Safe

            # Neutral cases
            "I felt scared",                # Should trigger AFFECT_EXPRESSION -> Safe (neutral)
            "There was a dark forest",      # Should trigger NARRATIVE_SETTING -> Safe (neutral)
            
            # Negation handling
            "I decided not to run away",    # Should trigger BEHAVIORAL_MASTERY -> Safe
            
            # Complex multi-part inputs
            "I hate this therapy, but I guess I fight the dragon.",  # META + ACTION -> Safe
            "I feel scared but I stand my ground",                    # FEELING + ACTION -> Safe
            "This is stupid. I wake up.",                            # META + INTERRUPT -> Unsafe
            "I felt terrified so I killed everyone in sight",        # FEELING + VIOLENCE -> Unsafe (CRITICAL)
        ]
        
        print("\n" + "=" * 70)
        print("Test Results")
        print("=" * 70)
        
        for test in test_cases:
            result = await critic.evaluate_intervention(test)
            
            if result.is_safe:
                status = "✅ SAFE"
            else:
                status = f"⚠️ UNSAFE ({result.severity})"
            
            print(f"\n{status}: '{test}'")
            print(f"  → Primary: {result.node_id} ({result.node_type})")
            
            if result.segments:
                print(f"  → Segments: {[(s.text[:20]+'...' if len(s.text) > 20 else s.text, s.segment_type, s.node_id) for s in result.segments]}")
            
            if result.adaptive_segments:
                print(f"  → Adaptive parts: {[s.node_id for s in result.adaptive_segments]}")
            
            if not result.is_safe:
                print(f"  → Category: {result.category}")
                print(f"  → Corrections available: {len(result.correction_strategies or [])}")
    
    asyncio.run(test_critic())
