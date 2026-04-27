"""Structural smoke test for SafetyCritic._build_constraint_message.

Constraint synthesis is pure string formatting from graph attributes (no LLM
calls). These tests are a regression guard for future refactors of
`graph_definitions.py` or the constraint template: they assert the returned
string has the expected sections, cites the node's clinical description and
at least one correction-edge target, and contains no unresolved `{...}`
placeholders.

Run with: uv run pytest tests/test_constraint_synthesis.py -v
"""

import re
import pytest
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from safety.critic import SafetyCritic, SegmentResult
from safety.graph_definitions import build_clinical_graph, get_correction_strategies


UNSAFE_NODES = ["AVOIDANCE", "INTERRUPTION", "VIOLENT_REVENGE", "SUPPRESSION", "TRAUMA_REPLAY"]


@pytest.fixture(scope="module")
def critic():
    return SafetyCritic()


@pytest.fixture(scope="module")
def graph():
    return build_clinical_graph()


@pytest.mark.parametrize("node_id", UNSAFE_NODES)
def test_constraint_synthesis_structure(critic, graph, node_id):
    """For each unsafe node, _build_constraint_message returns a constraint with
    the expected header, sections, clinical description, and a correction target."""
    segment = SegmentResult(
        text=f"<fake segment text for {node_id}>",
        segment_type="ACTION",
        node_id=node_id,
        node_type="maladaptive",
        category=graph.nodes[node_id].get("category", "unknown"),
        confidence=0.9,
    )
    # Include a synthetic adaptive segment so the VALIDATE section is exercised
    # (the constraint template omits VALIDATE when adaptive_segments is empty).
    adaptive_segment = SegmentResult(
        text="<fake adaptive segment>",
        segment_type="ACTION",
        node_id="BEHAVIORAL_MASTERY",
        node_type="adaptive",
        category="mastery",
        confidence=0.9,
    )
    node_attrs = dict(graph.nodes[node_id])
    strategies = get_correction_strategies(graph, node_id)

    constraint = critic._build_constraint_message(
        primary_risk=segment,
        node_attrs=node_attrs,
        strategies=strategies,
        adaptive_segments=[adaptive_segment],
        unclassified_segments=None,
    )

    # Header
    assert constraint.startswith("[SAFETY SYSTEM - INTERVENTION REQUIRED]"), \
        f"{node_id}: missing safety-system header"

    # Clinical description of the node (first 40 chars should be unique enough)
    description = node_attrs.get("description", "")
    assert description, f"{node_id}: node has no description to cite"
    assert description[:40] in constraint, \
        f"{node_id}: clinical description not present in constraint"

    # At least one correction-edge target node name present
    assert strategies, f"{node_id}: no correction strategies defined in graph"
    assert any(s["target_node"] in constraint for s in strategies), \
        f"{node_id}: no correction-edge target node cited in constraint"

    # Section markers
    for marker in ("VALIDATE", "CORRECT", "INSTRUCTION", "IMPORTANT"):
        assert marker in constraint, f"{node_id}: missing '{marker}' section marker"

    # No unresolved template placeholders like {foo}
    unresolved = re.findall(r"\{[A-Za-z_][A-Za-z0-9_]*\}", constraint)
    assert not unresolved, f"{node_id}: unresolved placeholders {unresolved}"
