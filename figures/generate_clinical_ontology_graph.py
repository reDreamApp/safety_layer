#!/usr/bin/env python3
"""
Generate the clinical safety ontology figure for the thesis.

The figure is intentionally explanatory rather than algorithmic: it shows how
maladaptive rewriting actions map to adaptive mastery categories, with neutral
and unclassified categories separated from the correction structure.
"""

from __future__ import annotations

import textwrap
from pathlib import Path
import sys

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from safety.graph_definitions import build_clinical_graph  # noqa: E402


OUTPUT_DIR = Path(__file__).resolve().parent

MALADAPTIVE_ORDER = [
    "AVOIDANCE",
    "INTERRUPTION",
    "VIOLENT_REVENGE",
    "SUPPRESSION",
    "TRAUMA_REPLAY",
]

ADAPTIVE_ORDER = [
    "BEHAVIORAL_MASTERY",
    "EMOTIONAL_MASTERY",
    "SOCIAL_MASTERY",
    "ENVIRONMENTAL_MASTERY",
    "MYTHICAL_MASTERY",
]

NEUTRAL_ORDER = [
    "NARRATIVE_SETTING",
    "AFFECT_EXPRESSION",
    "UNCLASSIFIED",
]

DISPLAY_NAMES = {
    "AVOIDANCE": "Avoidance",
    "INTERRUPTION": "Interruption",
    "VIOLENT_REVENGE": "Violent revenge",
    "SUPPRESSION": "Suppression",
    "TRAUMA_REPLAY": "Trauma replay",
    "BEHAVIORAL_MASTERY": "Behavioral mastery",
    "SOCIAL_MASTERY": "Social mastery",
    "ENVIRONMENTAL_MASTERY": "Environmental mastery",
    "EMOTIONAL_MASTERY": "Emotional mastery",
    "MYTHICAL_MASTERY": "Mythical mastery",
    "NARRATIVE_SETTING": "Narrative setting",
    "AFFECT_EXPRESSION": "Affect expression",
    "UNCLASSIFIED": "Unclassified",
}

PALETTE = {
    "adaptive_fill": "#E8F5E9",
    "adaptive_edge": "#2E7D32",
    "high_fill": "#FFF4E6",
    "high_edge": "#E65100",
    "critical_fill": "#FDECEC",
    "critical_edge": "#C62828",
    "neutral_fill": "#EEF2F7",
    "neutral_edge": "#607D8B",
    "unclassified_fill": "#F5F5F5",
    "unclassified_edge": "#757575",
    "primary_edge": "#1F3A5F",
    "secondary_edge": "#78909C",
    "tertiary_edge": "#B0BEC5",
    "text": "#1F2933",
    "muted": "#667085",
}


def wrap_label(text: str, width: int = 22) -> str:
    return "\n".join(textwrap.wrap(text, width=width))


def draw_node(
    ax,
    xy: tuple[float, float],
    width: float,
    height: float,
    title: str,
    subtitle: str,
    fill: str,
    edge: str,
    linewidth: float = 1.8,
):
    x, y = xy
    left = x - width / 2
    bottom = y - height / 2

    patch = FancyBboxPatch(
        (left, bottom),
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        facecolor=fill,
        edgecolor=edge,
        linewidth=linewidth,
        zorder=3,
    )
    ax.add_patch(patch)

    ax.text(
        x,
        y + (height * 0.13 if subtitle else 0),
        wrap_label(title, 20),
        ha="center",
        va="center",
        fontsize=10,
        fontweight="bold",
        color=PALETTE["text"],
        zorder=4,
    )
    if subtitle:
        ax.text(
            x,
            y - height * 0.24,
            wrap_label(subtitle, 28),
            ha="center",
            va="center",
            fontsize=7.5,
            color=PALETTE["muted"],
            zorder=4,
        )


def node_style(node_id: str, attrs: dict) -> tuple[str, str, float]:
    node_type = attrs.get("type")
    if node_type == "adaptive":
        return PALETTE["adaptive_fill"], PALETTE["adaptive_edge"], 1.8
    if node_type == "neutral":
        return PALETTE["neutral_fill"], PALETTE["neutral_edge"], 1.6
    if node_type == "unclassified":
        return PALETTE["unclassified_fill"], PALETTE["unclassified_edge"], 1.6
    if attrs.get("severity") == "critical":
        return PALETTE["critical_fill"], PALETTE["critical_edge"], 2.4
    return PALETTE["high_fill"], PALETTE["high_edge"], 1.8


def node_subtitle(node_id: str, attrs: dict) -> str:
    node_type = attrs.get("type")
    if node_type == "adaptive":
        return ""
    if node_type == "neutral":
        return "not a rewriting action"
    if node_type == "unclassified":
        return "seek clarification"
    return ""


def edge_style(priority: str) -> tuple[str, float, str, float]:
    if priority == "primary":
        return PALETTE["primary_edge"], 2.4, "solid", 0.95
    if priority == "secondary":
        return PALETTE["secondary_edge"], 1.35, "solid", 0.70
    return PALETTE["tertiary_edge"], 1.2, "dashed", 0.65


def draw_edge(
    ax,
    source: tuple[float, float],
    target: tuple[float, float],
    priority: str,
    rad: float,
):
    color, linewidth, linestyle, alpha = edge_style(priority)
    arrow = FancyArrowPatch(
        source,
        target,
        arrowstyle="-|>",
        mutation_scale=13,
        linewidth=linewidth,
        linestyle=linestyle,
        color=color,
        alpha=alpha,
        connectionstyle=f"arc3,rad={rad}",
        shrinkA=18,
        shrinkB=18,
        zorder=2,
    )
    ax.add_patch(arrow)


def generate_figure():
    graph = build_clinical_graph()

    fig, ax = plt.subplots(figsize=(11.5, 8.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.27,
        0.965,
        "Maladaptive rewriting actions",
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        color=PALETTE["text"],
    )
    ax.text(
        0.73,
        0.965,
        "Adaptive mastery categories",
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        color=PALETTE["text"],
    )

    mal_y = [0.84, 0.68, 0.52, 0.36, 0.20]
    adaptive_y = [0.84, 0.68, 0.52, 0.36, 0.20]
    positions = {}

    for node_id, y in zip(MALADAPTIVE_ORDER, mal_y):
        attrs = graph.nodes[node_id]
        positions[node_id] = (0.23, y)
        fill, edge, linewidth = node_style(node_id, attrs)
        draw_node(
            ax,
            positions[node_id],
            width=0.28,
            height=0.095,
            title=DISPLAY_NAMES[node_id],
            subtitle=node_subtitle(node_id, attrs),
            fill=fill,
            edge=edge,
            linewidth=linewidth,
        )

    for node_id, y in zip(ADAPTIVE_ORDER, adaptive_y):
        attrs = graph.nodes[node_id]
        positions[node_id] = (0.77, y)
        fill, edge, linewidth = node_style(node_id, attrs)
        draw_node(
            ax,
            positions[node_id],
            width=0.28,
            height=0.095,
            title=DISPLAY_NAMES[node_id],
            subtitle=node_subtitle(node_id, attrs),
            fill=fill,
            edge=edge,
            linewidth=linewidth,
        )

    # Edge curvature keeps overlapping correction links readable.
    for source, target, attrs in graph.edges(data=True):
        if attrs.get("relation") != "correction_strategy":
            continue
        s_y = positions[source][1]
        t_y = positions[target][1]
        y_delta = t_y - s_y
        priority = attrs.get("priority", "tertiary")
        if priority == "primary":
            rad = 0.02 if abs(y_delta) < 0.02 else 0.12
        elif priority == "secondary":
            rad = 0.20 if y_delta >= 0 else -0.20
        else:
            rad = 0.30 if y_delta >= 0 else -0.30
        draw_edge(ax, positions[source], positions[target], priority, rad)

    ax.text(
        0.5,
        0.115,
        "Context and fallback categories",
        ha="center",
        va="center",
        fontsize=10,
        fontweight="bold",
        color=PALETTE["text"],
    )

    neutral_x = [0.18, 0.50, 0.82]
    for node_id, x in zip(NEUTRAL_ORDER, neutral_x):
        attrs = graph.nodes[node_id]
        positions[node_id] = (x, 0.045)
        fill, edge, linewidth = node_style(node_id, attrs)
        draw_node(
            ax,
            positions[node_id],
            width=0.20,
            height=0.065,
            title=DISPLAY_NAMES[node_id],
            subtitle=node_subtitle(node_id, attrs),
            fill=fill,
            edge=edge,
            linewidth=linewidth,
        )

    legend_handles = [
        Line2D([0], [0], color=PALETTE["primary_edge"], lw=2.4, label="Primary correction"),
        Line2D([0], [0], color=PALETTE["secondary_edge"], lw=1.5, label="Secondary correction"),
        Line2D([0], [0], color=PALETTE["tertiary_edge"], lw=1.4, linestyle="--", label="Tertiary correction"),
        Line2D([0], [0], color=PALETTE["high_edge"], lw=2.0, label="High severity"),
        Line2D([0], [0], color=PALETTE["critical_edge"], lw=2.6, label="Critical severity"),
    ]
    ax.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.02),
        ncol=5,
        frameon=False,
        fontsize=8.5,
        handlelength=2.4,
        columnspacing=1.2,
    )

    fig.tight_layout(pad=0.8)
    for extension in ("pdf", "png", "svg"):
        output_path = OUTPUT_DIR / f"clinical_ontology_graph.{extension}"
        fig.savefig(output_path, dpi=240, bbox_inches="tight", facecolor="white")
        print(output_path)


if __name__ == "__main__":
    generate_figure()
