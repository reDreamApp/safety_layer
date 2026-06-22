#!/usr/bin/env python3
"""Generate Figure 4.2: component-level experimental design overview."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle


ROOT = Path(__file__).resolve().parents[1]
OUT_BASE = ROOT / "figures" / "experimental_design_overview"


def add_box(
    ax,
    x: float,
    y: float,
    w: float,
    h: float,
    text: str,
    face: str,
    edge: str,
    fontsize: float = 8.5,
    weight: str = "normal",
) -> None:
    ax.add_patch(Rectangle((x, y), w, h, facecolor=face, edgecolor=edge, linewidth=1.1))
    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        fontweight=weight,
        linespacing=1.18,
        color="#222222",
    )


def add_arrow(ax, x1: float, y1: float, x2: float, y2: float) -> None:
    ax.add_patch(
        FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=1.15,
            color="#3A3A3A",
            shrinkA=3,
            shrinkB=3,
        )
    )


def main() -> None:
    fig, ax = plt.subplots(figsize=(7.2, 2.05))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    blue = "#E8F1FA"
    blue_edge = "#4C78A8"
    amber = "#FFF3D7"
    amber_edge = "#C98712"
    green = "#EAF4E6"
    green_edge = "#59A14F"
    grey = "#F4F4F4"
    grey_edge = "#6B6B6B"

    add_box(
        ax,
        0.02,
        0.32,
        0.17,
        0.36,
        "Benchmark\ninputs\nsame labels",
        blue,
        blue_edge,
        fontsize=8.2,
        weight="bold",
    )

    add_box(
        ax,
        0.26,
        0.32,
        0.17,
        0.36,
        "Safety critic\npipeline",
        grey,
        grey_edge,
        fontsize=8.6,
        weight="bold",
    )

    add_box(
        ax,
        0.49,
        0.15,
        0.26,
        0.70,
        "Compared conditions\n\nS1 direct / S2 reasoned\n\nConsistency runs (N=5)\n\nPipeline ablations",
        amber,
        amber_edge,
        fontsize=7.5,
        weight="normal",
    )

    add_box(
        ax,
        0.82,
        0.25,
        0.17,
        0.50,
        "Case-level\nmetrics\n\nsafety acc.\nunsafe recall\nnode acc.\nagreement ratio",
        green,
        green_edge,
        fontsize=6.8,
        weight="normal",
    )

    add_arrow(ax, 0.19, 0.50, 0.26, 0.50)
    add_arrow(ax, 0.43, 0.50, 0.49, 0.50)
    add_arrow(ax, 0.75, 0.50, 0.82, 0.50)

    fig.savefig(f"{OUT_BASE}.png", dpi=260, bbox_inches="tight", pad_inches=0.02)
    fig.savefig(f"{OUT_BASE}.pdf", bbox_inches="tight", pad_inches=0.02)
    print(f"Wrote {OUT_BASE}.png and {OUT_BASE}.pdf")


if __name__ == "__main__":
    main()
