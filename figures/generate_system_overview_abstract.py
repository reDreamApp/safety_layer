#!/usr/bin/env python3
"""
Generate abstract system overview figure.

High-level only: Patient, IRT Chatbot, Safety Layer, and the feedback loop.
No internals of any component. Replaces the overcrowded irt_chatbot_overview.

This figure answers: "What is the system and how do the parts relate?"
The detailed pipeline figure answers: "How does the safety layer work inside?"
"""

import subprocess
import os

DOT_SOURCE = r'''
digraph system_overview {
    graph [
        rankdir=LR
        fontname="Helvetica,sans-Serif"
        fontsize=12
        bgcolor="white"
        pad=0.4
        nodesep=0.6
        ranksep=1.2
        label=<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0">
            <TR><TD><B><FONT POINT-SIZE="15" COLOR="#1a1a1a">ReDream AI: System Overview</FONT></B></TD></TR>
            <TR><TD><FONT POINT-SIZE="10" COLOR="#666666">IRT Chatbot with Neuro-Symbolic Safety Layer</FONT></TD></TR>
        </TABLE>>
        labelloc=t
    ]
    node [fontname="Helvetica,sans-Serif" fontsize=10]
    edge [fontname="Helvetica,sans-Serif" fontsize=9]

    // ── Patient ──
    patient [
        shape=none margin=0
        label=<
        <TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="10"
               BGCOLOR="#E3F2FD" COLOR="#1565C0">
            <TR><TD ALIGN="CENTER"><B><FONT COLOR="#1565C0" POINT-SIZE="11">Patient</FONT></B></TD></TR>
            <TR><TD ALIGN="CENTER"><FONT POINT-SIZE="8" COLOR="#666666">Describes and<BR/>rescrips nightmare</FONT></TD></TR>
        </TABLE>>
    ]

    // ── IRT Chatbot ──
    chatbot [
        shape=none margin=0
        label=<
        <TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="10"
               BGCOLOR="#F5F5F5" COLOR="#455A64">
            <TR><TD ALIGN="CENTER"><B><FONT COLOR="#455A64" POINT-SIZE="11">IRT Chatbot</FONT></B></TD></TR>
            <TR><TD ALIGN="CENTER"><FONT POINT-SIZE="8" COLOR="#666666">LLM-powered<BR/>conversational agent</FONT></TD></TR>
            <TR><TD>
                <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4" COLOR="#BDBDBD">
                    <TR>
                        <TD BGCOLOR="#E8EAF6" ALIGN="CENTER"><FONT POINT-SIZE="7.5">1. Record</FONT></TD>
                        <TD BGCOLOR="#E8EAF6" ALIGN="CENTER"><FONT POINT-SIZE="7.5">2. Rescript</FONT></TD>
                        <TD BGCOLOR="#E8EAF6" ALIGN="CENTER"><FONT POINT-SIZE="7.5">3. Summary</FONT></TD>
                        <TD BGCOLOR="#E8EAF6" ALIGN="CENTER"><FONT POINT-SIZE="7.5">4. Closure</FONT></TD>
                    </TR>
                </TABLE>
            </TD></TR>
        </TABLE>>
    ]

    // ── Safety Layer ──
    safety [
        shape=none margin=0
        label=<
        <TABLE BORDER="2" CELLBORDER="0" CELLSPACING="0" CELLPADDING="10"
               BGCOLOR="#FBE9E7" COLOR="#C62828">
            <TR><TD ALIGN="CENTER"><B><FONT COLOR="#C62828" POINT-SIZE="11">Neuro-Symbolic<BR/>Safety Layer</FONT></B></TD></TR>
            <TR><TD ALIGN="CENTER"><FONT POINT-SIZE="8" COLOR="#666666">Detects maladaptive patterns<BR/>Generates corrective constraints</FONT></TD></TR>
            <TR><TD ALIGN="CENTER"><FONT POINT-SIZE="7" COLOR="#C62828"><I>Thesis contribution</I></FONT></TD></TR>
        </TABLE>>
    ]

    // ── Edges ──
    patient -> chatbot [
        label=<  <FONT POINT-SIZE="8" COLOR="#455A64">describes nightmare /<BR/>rescrips dream</FONT>  >
        color="#455A64" penwidth=1.3
    ]

    chatbot -> patient [
        label=<  <FONT POINT-SIZE="8" COLOR="#455A64">therapeutic<BR/>response</FONT>  >
        color="#455A64" penwidth=1.3
    ]

    chatbot -> safety [
        label=<  <FONT POINT-SIZE="8" COLOR="#C62828">patient input<BR/>(during rescripting)</FONT>  >
        color="#C62828" penwidth=1.3 style=dashed
    ]

    safety -> chatbot [
        label=<  <FONT POINT-SIZE="8" COLOR="#C62828">safe: proceed<BR/>unsafe: constraint message</FONT>  >
        color="#C62828" penwidth=1.3 style=dashed
    ]
}
'''

def generate_figure():
    output_dir = os.path.dirname(os.path.abspath(__file__))
    dot_path = os.path.join(output_dir, "system_overview_abstract.dot")

    with open(dot_path, 'w') as f:
        f.write(DOT_SOURCE)

    for fmt in ['png', 'svg', 'pdf']:
        output_path = os.path.join(output_dir, f"system_overview_abstract.{fmt}")
        dpi_flag = ['-Gdpi=200'] if fmt == 'png' else []
        result = subprocess.run(
            ['dot', '-T' + fmt] + dpi_flag + [dot_path, '-o', output_path],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"✅ {output_path}")
        else:
            print(f"❌ {fmt}: {result.stderr}")

if __name__ == "__main__":
    generate_figure()
