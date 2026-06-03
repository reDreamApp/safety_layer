#!/usr/bin/env python3
"""
Generate Figure 9: Worked End-to-End Pipeline Example.

Shows one concrete multi-part input flowing through all 5 stages of the
SafetyCritic pipeline, demonstrating what happens at each step:
1. Segmentation → 3 segments (META, ACTION-adaptive, ACTION-maladaptive)
2. META Filtering → META segment removed
3. Batch Classification → each segment classified to a graph node
4. Severity Triage → most critical risk selected
5. Constraint Synthesis → Validate + Correct message generated

Uses Graphviz to match existing thesis figure style.
"""

import subprocess
import os

DOT_SOURCE = r'''
digraph worked_example {
    graph [
        rankdir=TB
        fontname="Helvetica,sans-Serif"
        fontsize=12
        bgcolor="white"
        pad=0.4
        nodesep=0.4
        ranksep=0.55
        label=<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0">
            <TR><TD><B><FONT POINT-SIZE="15" COLOR="#1a1a1a">End-to-End Pipeline Example</FONT></B></TD></TR>
            <TR><TD><FONT POINT-SIZE="10" COLOR="#666666">A multi-part user input traced through all five stages of the Safety Critic</FONT></TD></TR>
        </TABLE>>
        labelloc=t
    ]
    node [fontname="Helvetica,sans-Serif" fontsize=9]
    edge [fontname="Helvetica,sans-Serif" fontsize=8]

    // ── Input ──
    input [
        shape=none margin=0
        label=<
        <TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="8"
               BGCOLOR="#E3F2FD" COLOR="#1565C0" STYLE="ROUNDED">
            <TR><TD COLSPAN="2" ALIGN="CENTER"><B><FONT COLOR="#1565C0" POINT-SIZE="10">User Input</FONT></B></TD></TR>
            <TR><TD COLSPAN="2" ALIGN="CENTER"><FONT POINT-SIZE="8" COLOR="#666666">Nightmare context: "Being chased by a shadowy figure through a dark forest"</FONT></TD></TR>
            <TR><TD COLSPAN="2" ALIGN="LEFT" BALIGN="LEFT" WIDTH="420">
                <FONT POINT-SIZE="9.5" COLOR="#1a1a1a">
                "This exercise is weird, but okay — I find a heavy branch on the ground<BR/>
                and pick it up. Then I just hide behind a tree and hope it goes away."
                </FONT>
            </TD></TR>
        </TABLE>>
    ]

    // ── Stage 1: Segmentation ──
    stage1_label [
        shape=none margin=0
        label=<
        <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4">
            <TR><TD BGCOLOR="#5C6BC0" WIDTH="130"><FONT COLOR="white" POINT-SIZE="9"><B>  Stage 1: Segment  </B></FONT></TD>
                <TD><FONT COLOR="#666666" POINT-SIZE="8">  Mistral Nemo (temp=0.1)</FONT></TD></TR>
        </TABLE>>
    ]

    segments [
        shape=none margin=0
        label=<
        <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6"
               COLOR="#9FA8DA" STYLE="ROUNDED">
            <TR>
                <TD BGCOLOR="#E8EAF6" ALIGN="CENTER"><FONT POINT-SIZE="8" COLOR="#666666"><B>Type</B></FONT></TD>
                <TD BGCOLOR="#E8EAF6" ALIGN="CENTER"><FONT POINT-SIZE="8" COLOR="#666666"><B>Text</B></FONT></TD>
                <TD BGCOLOR="#E8EAF6" ALIGN="CENTER"><FONT POINT-SIZE="8" COLOR="#666666"><B>Context</B></FONT></TD>
            </TR>
            <TR>
                <TD BGCOLOR="#FFF9C4"><FONT POINT-SIZE="9" COLOR="#F57F17"><B>META</B></FONT></TD>
                <TD ALIGN="LEFT"><FONT POINT-SIZE="9">"This exercise is weird, but okay"</FONT></TD>
                <TD><FONT POINT-SIZE="8" COLOR="#999999">null</FONT></TD>
            </TR>
            <TR>
                <TD BGCOLOR="#E8F5E9"><FONT POINT-SIZE="9" COLOR="#2E7D32"><B>ACTION</B></FONT></TD>
                <TD ALIGN="LEFT"><FONT POINT-SIZE="9">"I find a heavy branch and pick it up"</FONT></TD>
                <TD><FONT POINT-SIZE="8">"being chased in forest"</FONT></TD>
            </TR>
            <TR>
                <TD BGCOLOR="#FFEBEE"><FONT POINT-SIZE="9" COLOR="#C62828"><B>ACTION</B></FONT></TD>
                <TD ALIGN="LEFT"><FONT POINT-SIZE="9">"I just hide behind a tree and hope it goes away"</FONT></TD>
                <TD><FONT POINT-SIZE="8">"being chased in forest"</FONT></TD>
            </TR>
        </TABLE>>
    ]

    // ── Stage 2: META Filter ──
    stage2_label [
        shape=none margin=0
        label=<
        <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4">
            <TR><TD BGCOLOR="#7E57C2" WIDTH="130"><FONT COLOR="white" POINT-SIZE="9"><B>  Stage 2: Filter  </B></FONT></TD>
                <TD><FONT COLOR="#666666" POINT-SIZE="8">  Remove META segments</FONT></TD></TR>
        </TABLE>>
    ]

    filtered [
        shape=none margin=0
        label=<
        <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6"
               COLOR="#CE93D8" STYLE="ROUNDED">
            <TR>
                <TD BGCOLOR="#F3E5F5" ALIGN="CENTER"><FONT POINT-SIZE="8" COLOR="#666666"><B>Segment</B></FONT></TD>
                <TD BGCOLOR="#F3E5F5" ALIGN="CENTER"><FONT POINT-SIZE="8" COLOR="#666666"><B>Status</B></FONT></TD>
            </TR>
            <TR>
                <TD ALIGN="LEFT"><FONT POINT-SIZE="9" COLOR="#999999"><S>"This exercise is weird, but okay"</S></FONT></TD>
                <TD><FONT POINT-SIZE="8" COLOR="#F57F17">⊘ filtered (META)</FONT></TD>
            </TR>
            <TR>
                <TD ALIGN="LEFT"><FONT POINT-SIZE="9">"I find a heavy branch and pick it up"</FONT></TD>
                <TD><FONT POINT-SIZE="8" COLOR="#2E7D32">→ classify</FONT></TD>
            </TR>
            <TR>
                <TD ALIGN="LEFT"><FONT POINT-SIZE="9">"I just hide behind a tree and hope it goes away"</FONT></TD>
                <TD><FONT POINT-SIZE="8" COLOR="#2E7D32">→ classify</FONT></TD>
            </TR>
        </TABLE>>
    ]

    // ── Stage 3: Batch Classification ──
    stage3_label [
        shape=none margin=0
        label=<
        <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4">
            <TR><TD BGCOLOR="#0097A7" WIDTH="130"><FONT COLOR="white" POINT-SIZE="9"><B>  Stage 3: Classify  </B></FONT></TD>
                <TD><FONT COLOR="#666666" POINT-SIZE="8">  Entity Linker → Knowledge Graph</FONT></TD></TR>
        </TABLE>>
    ]

    classified [
        shape=none margin=0
        label=<
        <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6"
               COLOR="#80CBC4" STYLE="ROUNDED">
            <TR>
                <TD BGCOLOR="#E0F2F1" ALIGN="CENTER"><FONT POINT-SIZE="8" COLOR="#666666"><B>Segment</B></FONT></TD>
                <TD BGCOLOR="#E0F2F1" ALIGN="CENTER"><FONT POINT-SIZE="8" COLOR="#666666"><B>Code</B></FONT></TD>
                <TD BGCOLOR="#E0F2F1" ALIGN="CENTER"><FONT POINT-SIZE="8" COLOR="#666666"><B>Node</B></FONT></TD>
                <TD BGCOLOR="#E0F2F1" ALIGN="CENTER"><FONT POINT-SIZE="8" COLOR="#666666"><B>Type</B></FONT></TD>
                <TD BGCOLOR="#E0F2F1" ALIGN="CENTER"><FONT POINT-SIZE="8" COLOR="#666666"><B>Conf.</B></FONT></TD>
            </TR>
            <TR>
                <TD ALIGN="LEFT"><FONT POINT-SIZE="9">"find a heavy branch..."</FONT></TD>
                <TD><FONT POINT-SIZE="9"><B>CHANGE</B></FONT></TD>
                <TD><FONT POINT-SIZE="8">ENV_MASTERY</FONT></TD>
                <TD BGCOLOR="#E8F5E9"><FONT POINT-SIZE="8" COLOR="#2E7D32"><B>adaptive</B></FONT></TD>
                <TD><FONT POINT-SIZE="8">0.94</FONT></TD>
            </TR>
            <TR>
                <TD ALIGN="LEFT"><FONT POINT-SIZE="9">"hide behind a tree..."</FONT></TD>
                <TD><FONT POINT-SIZE="9"><B>HIDE</B></FONT></TD>
                <TD><FONT POINT-SIZE="8">AVOIDANCE</FONT></TD>
                <TD BGCOLOR="#FFEBEE"><FONT POINT-SIZE="8" COLOR="#C62828"><B>maladaptive</B></FONT></TD>
                <TD><FONT POINT-SIZE="8">0.91</FONT></TD>
            </TR>
        </TABLE>>
    ]

    // ── Stage 4: Severity Triage ──
    stage4_label [
        shape=none margin=0
        label=<
        <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4">
            <TR><TD BGCOLOR="#EF6C00" WIDTH="130"><FONT COLOR="white" POINT-SIZE="9"><B>  Stage 4: Triage  </B></FONT></TD>
                <TD><FONT COLOR="#666666" POINT-SIZE="8">  Select highest-severity risk</FONT></TD></TR>
        </TABLE>>
    ]

    triage [
        shape=none margin=0
        label=<
        <TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="8"
               BGCOLOR="#FFF3E0" COLOR="#E65100" STYLE="ROUNDED">
            <TR><TD ALIGN="CENTER">
                <FONT POINT-SIZE="9" COLOR="#E65100">
                <B>Primary risk:</B> AVOIDANCE (severity: HIGH)<BR/>
                <B>Also present:</B> ENV_MASTERY (adaptive) — will be validated
                </FONT>
            </TD></TR>
        </TABLE>>
    ]

    // ── Stage 5: Constraint Synthesis ──
    stage5_label [
        shape=none margin=0
        label=<
        <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4">
            <TR><TD BGCOLOR="#C62828" WIDTH="130"><FONT COLOR="white" POINT-SIZE="9"><B>  Stage 5: Constrain  </B></FONT></TD>
                <TD><FONT COLOR="#666666" POINT-SIZE="8">  Generate Validate + Correct message</FONT></TD></TR>
        </TABLE>>
    ]

    constraint [
        shape=none margin=0
        label=<
        <TABLE BORDER="2" CELLBORDER="0" CELLSPACING="0" CELLPADDING="8"
               BGCOLOR="#FBE9E7" COLOR="#C62828" STYLE="ROUNDED">
            <TR><TD ALIGN="CENTER"><B><FONT COLOR="#C62828" POINT-SIZE="10">Constraint Message → injected into LLM prompt</FONT></B></TD></TR>
            <TR><TD ALIGN="LEFT" BALIGN="LEFT" WIDTH="420">
                <FONT POINT-SIZE="9" COLOR="#1a1a1a">
                <B>VALIDATE:</B> The user showed adaptive behavior by finding a branch<BR/>
                to defend themselves (Environmental Mastery). Acknowledge this.<BR/>
                <BR/>
                <B>CORRECT:</B> However, the user then reverted to avoidance (hiding,<BR/>
                hoping the threat passes). This reinforces passivity.<BR/>
                <BR/>
                <B>REDIRECT:</B> Guide toward using the branch actively —<BR/>
                Behavioral Mastery (confronting the threat) or<BR/>
                Environmental Mastery (using the branch as a tool/barrier).
                </FONT>
            </TD></TR>
        </TABLE>>
    ]

    // ── Output indicator ──
    output [
        shape=none margin=0
        label=<
        <TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="6"
               BGCOLOR="#E8F5E9" COLOR="#2E7D32" STYLE="ROUNDED">
            <TR><TD ALIGN="CENTER">
                <FONT POINT-SIZE="9" COLOR="#2E7D32">
                <B>Result:</B> is_safe = False  |  Constraint injected into next LLM prompt  |  LLM generates corrected response
                </FONT>
            </TD></TR>
        </TABLE>>
    ]

    // ── Edges ──
    input -> stage1_label [arrowhead=none color="#455A64" penwidth=1.2]
    stage1_label -> segments [color="#455A64" penwidth=1.2]
    segments -> stage2_label [arrowhead=none color="#455A64" penwidth=1.2]
    stage2_label -> filtered [color="#455A64" penwidth=1.2]
    filtered -> stage3_label [arrowhead=none color="#455A64" penwidth=1.2]
    stage3_label -> classified [color="#455A64" penwidth=1.2]
    classified -> stage4_label [arrowhead=none color="#455A64" penwidth=1.2]
    stage4_label -> triage [color="#455A64" penwidth=1.2]
    triage -> stage5_label [arrowhead=none color="#455A64" penwidth=1.2]
    stage5_label -> constraint [color="#455A64" penwidth=1.2]
    constraint -> output [color="#2E7D32" penwidth=1.5 style=dashed]
}
'''

def generate_figure():
    """Generate the worked example figure."""
    output_dir = os.path.dirname(os.path.abspath(__file__))
    dot_path = os.path.join(output_dir, "worked_example.dot")

    with open(dot_path, 'w') as f:
        f.write(DOT_SOURCE)

    for fmt in ['png', 'svg', 'pdf']:
        output_path = os.path.join(output_dir, f"worked_example.{fmt}")
        dpi_flag = ['-Gdpi=200'] if fmt == 'png' else []

        result = subprocess.run(
            ['dot', '-T' + fmt] + dpi_flag + [dot_path, '-o', output_path],
            capture_output=True, text=True
        )

        if result.returncode == 0:
            print(f"✅ Generated: {output_path}")
        else:
            print(f"❌ Error generating {fmt}: {result.stderr}")


if __name__ == "__main__":
    generate_figure()
