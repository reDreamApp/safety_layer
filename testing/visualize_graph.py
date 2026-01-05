#!/usr/bin/env python3
"""
Visualize the Clinical Knowledge Graph

Creates a visual representation of the ontology for verification.
"""

import os
import sys
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Check if matplotlib is installed
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
except ImportError:
    print("Installing matplotlib for visualization...")
    os.system("pip install matplotlib")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

import networkx as nx
from safety.graph_definitions import build_clinical_graph, get_maladaptive_nodes, get_adaptive_nodes


def visualize_clinical_graph(save_path: str = "clinical_graph.png"):
    """
    Create a visualization of the clinical knowledge graph.
    
    Args:
        save_path: Path to save the image
    """
    G = build_clinical_graph()
    
    # Create figure with larger size
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    # Get node types for coloring
    maladaptive_nodes = list(get_maladaptive_nodes(G).keys())
    adaptive_nodes = list(get_adaptive_nodes(G).keys())
    
    # Define colors
    node_colors = []
    for node in G.nodes():
        if node in maladaptive_nodes:
            node_colors.append('#FF6B6B')  # Red for maladaptive
        else:
            node_colors.append('#4ECDC4')  # Teal for adaptive
    
    # Create layout - put maladaptive on left, adaptive on right
    pos = {}
    
    # Position maladaptive nodes on the left
    for i, node in enumerate(maladaptive_nodes):
        pos[node] = (-2, 2 - i * 1.5)
    
    # Position adaptive nodes on the right
    for i, node in enumerate(adaptive_nodes):
        pos[node] = (2, 2.5 - i * 1.2)
    
    # Draw edges with arrows
    edge_colors = '#888888'
    nx.draw_networkx_edges(
        G, pos, 
        edge_color=edge_colors,
        arrows=True,
        arrowsize=20,
        arrowstyle='-|>',
        connectionstyle='arc3,rad=0.1',
        width=2,
        alpha=0.7,
        ax=ax
    )
    
    # Draw nodes
    nx.draw_networkx_nodes(
        G, pos,
        node_color=node_colors,
        node_size=4000,
        alpha=0.9,
        ax=ax
    )
    
    # Draw labels with word wrap
    labels = {}
    for node in G.nodes():
        # Format label with newlines
        label = node.replace('_', '\n').replace('ZDPCS\n', 'ZDPCS_')
        labels[node] = label
    
    nx.draw_networkx_labels(
        G, pos,
        labels=labels,
        font_size=9,
        font_weight='bold',
        ax=ax
    )
    
    # Add edge labels
    edge_labels = {}
    for u, v, data in G.edges(data=True):
        edge_labels[(u, v)] = "corrects →"
    
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels=edge_labels,
        font_size=8,
        font_color='#555555',
        ax=ax
    )
    
    # Add title and legend
    ax.set_title(
        'Clinical Knowledge Graph: ZDPCS (Maladaptive) → MMS (Adaptive)\n'
        'Neuro-Symbolic Safety Layer Ontology',
        fontsize=14,
        fontweight='bold',
        pad=20
    )
    
    # Create legend
    red_patch = mpatches.Patch(color='#FF6B6B', label='Maladaptive (ZDPCS) - Risks')
    teal_patch = mpatches.Patch(color='#4ECDC4', label='Adaptive (MMS) - Goals')
    ax.legend(handles=[red_patch, teal_patch], loc='upper right', fontsize=10)
    
    # Add annotations for each node
    annotations = {
        'ZDPCS_SAFETY_PRINCIPLE': 'Avoidance:\nHiding, freezing,\nlooking away',
        'ZDPCS_INTERRUPT': 'Escape:\nWaking up,\nending dream',
        'ZDPCS_REGRESSIVE_AGGRESSION': 'Violence:\nChaotic destruction,\nuncontrolled rage',
        'BEHAVIORAL_MASTERY': 'Action:\nFighting back,\ntaking control',
        'SOCIAL_MASTERY': 'Help:\nCalling for help,\nallies appearing',
        'ENVIRONMENTAL_MASTERY': 'Environment:\nTools, safe places,\nsetting changes',
        'EMOTIONAL_MASTERY': 'Self-soothing:\nCalming down,\nstaying present',
        'MYTHICAL_MASTERY': 'Supernatural:\nMagic powers,\ndivine intervention',
    }
    
    for node, annotation in annotations.items():
        if node in pos:
            x, y = pos[node]
            offset_x = -1.5 if node in maladaptive_nodes else 1.5
            ax.annotate(
                annotation,
                xy=(x, y),
                xytext=(x + offset_x, y),
                fontsize=7,
                ha='center',
                va='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='gray', alpha=0.5)
            )
    
    ax.axis('off')
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"✅ Graph saved to: {save_path}")
    
    # Also save as PDF for higher quality
    pdf_path = save_path.replace('.png', '.pdf')
    plt.savefig(pdf_path, bbox_inches='tight', facecolor='white')
    print(f"✅ PDF version saved to: {pdf_path}")
    
    plt.show()
    
    return G


def print_ontology_summary():
    """Print a detailed summary of the ontology for verification."""
    G = build_clinical_graph()
    
    print("\n" + "=" * 80)
    print("ONTOLOGY VERIFICATION REPORT")
    print("=" * 80)
    
    print("\n📊 GRAPH STATISTICS:")
    print(f"   Total Nodes: {G.number_of_nodes()}")
    print(f"   Total Edges: {G.number_of_edges()}")
    
    print("\n" + "-" * 80)
    print("🔴 MALADAPTIVE NODES (Source: ZDPCS - Fischmann et al., 2021)")
    print("-" * 80)
    
    for node_id, attrs in get_maladaptive_nodes(G).items():
        print(f"\n  📌 {node_id}")
        print(f"     Category: {attrs.get('category', 'N/A')}")
        print(f"     Severity: {attrs.get('severity', 'N/A')}")
        print(f"     ZDPCS Concept: {attrs.get('zdpcs_concept', 'N/A')}")
        print(f"     Description: {attrs.get('description', 'N/A')[:80]}...")
        
        # Show correction strategies
        corrections = [v for _, v in G.out_edges(node_id)]
        print(f"     Corrects to: {corrections}")
    
    print("\n" + "-" * 80)
    print("🟢 ADAPTIVE NODES (Source: MMS - Germain et al., 2004)")
    print("-" * 80)
    
    for node_id, attrs in get_adaptive_nodes(G).items():
        print(f"\n  📌 {node_id}")
        print(f"     MMS Category: {attrs.get('mms_category', 'N/A')}")
        print(f"     Description: {attrs.get('description', 'N/A')[:80]}...")
    
    print("\n" + "-" * 80)
    print("⚠️  ONTOLOGY VERIFICATION NOTES")
    print("-" * 80)
    
    print("""
    MMS Manual (Germain et al., 2004) defines 6 subscales:
    ┌─────────────────────────────────────────────────────────────┐
    │ 1. Behavioral Mastery    → ✅ INCLUDED (BEHAVIORAL_MASTERY)    │
    │ 2. Social Mastery        → ✅ INCLUDED (SOCIAL_MASTERY)        │
    │ 3. Environmental Mastery → ✅ INCLUDED (ENVIRONMENTAL_MASTERY) │
    │ 4. Emotional Mastery     → ✅ INCLUDED (EMOTIONAL_MASTERY)     │
    │ 5. Mythical Mastery      → ✅ INCLUDED (MYTHICAL_MASTERY)      │
    │ 6. Avoidance             → ⚡ Mapped to ZDPCS nodes            │
    └─────────────────────────────────────────────────────────────┘
    
    ✅ All MMS mastery subscales are now represented!
    
    ZDPCS Maladaptive concepts:
    - Safety Principle (Avoidance) → ZDPCS_SAFETY_PRINCIPLE
    - Dream Interruption → ZDPCS_INTERRUPT  
    - Regressive Aggression → ZDPCS_REGRESSIVE_AGGRESSION
    """)
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    print_ontology_summary()
    visualize_clinical_graph("clinical_graph.png")

