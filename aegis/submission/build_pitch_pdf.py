"""Export a PDF twin of the pitch deck (Unstop accepts PDF or PPT)."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

OUT = Path(__file__).resolve().parent / "Aegis_Guard_ET_AI_Hackathon_Problem2.pdf"
INK = HexColor("#0B1F1A")
ACCENT = HexColor("#0F766E")
MUTED = HexColor("#5B6F68")
BG = HexColor("#F4F7F6")


def build() -> Path:
    page = landscape(A4)
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=page,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.5 * inch,
    )
    title = ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=28, textColor=INK, spaceAfter=10)
    h = ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=18, textColor=INK, spaceAfter=8)
    body = ParagraphStyle("b", fontName="Helvetica", fontSize=12, textColor=INK, leading=16, spaceAfter=4)
    muted = ParagraphStyle("m", fontName="Helvetica", fontSize=11, textColor=MUTED, leading=15, spaceAfter=3)

    story = []
    story.append(Paragraph("AEGIS GUARD", title))
    story.append(Paragraph("Behavioral Twin Prompt Injection Firewall", h))
    story.append(Paragraph("ET AI Hackathon: Agentic Edition · Problem 2 · Solo · <b>Claim F3 / D2</b>", muted))
    story.append(Paragraph("Live: https://aegis-prompt-injection-firewall.vercel.app", muted))
    story.append(Paragraph("GitHub: https://github.com/krabhi75/aegis-prompt-injection-firewall", muted))
    story.append(Spacer(1, 14))

    story.append(Paragraph("1. The enterprise risk", h))
    story.append(Paragraph(
        "Tool-using agents read PDFs, email, HTML, and APIs. Attackers hide instructions inside those documents "
        "(indirect prompt injection) to trigger secret theft and tool abuse. Keyword classifiers are not enough.",
        body,
    ))

    story.append(Paragraph("2. Insight", h))
    story.append(Paragraph(
        "Prompt injection is a <b>runtime security</b> problem: would untrusted content change the agent’s tool calls? "
        "Aegis runs a behavioral twin (trusted plan vs raw plan) and blocks on high-risk drift.",
        body,
    ))

    story.append(Paragraph("3. Control plane", h))
    story.append(Paragraph(
        "Ingest → Decode → Provenance → Static (9 attack types) → Behavioral Twin → Risk → Gate "
        "(ALLOW / QUARANTINE / BLOCK) → Protected agent with capability tokens · Human analyst quarantine.",
        body,
    ))

    story.append(Paragraph("4. Demo proof", h))
    data = [
        ["Scenario", "Result"],
        ["Benign product PDF", "ALLOW"],
        ["Indirect injection in PDF", "BLOCK — twin drift get_secret + send_email"],
        ["Encoded HTML jailbreak", "BLOCK — decode layer"],
        ["Multi-step roleplay → tools", "QUARANTINE / BLOCK — session risk"],
        ["Analyst queue", "HITL approve/deny + audit"],
    ]
    t = Table(data, colWidths=[3.8 * inch, 5.2 * inch])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
                ("TEXTCOLOR", (0, 0), (-1, 0), white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BACKGROUND", (0, 1), (-1, -1), BG),
                ("TEXTCOLOR", (0, 1), (-1, -1), INK),
                ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#D9E2DE")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 12))

    story.append(Paragraph("5. Declared 9-blocker: F3 / D2", h))
    story.append(Paragraph(
        "<b>F3:</b> All 9 official attack types implemented; demo shows ≥7. "
        "<b>D2:</b> Structured/textual multimodal inputs with high reliability "
        "(corpus n=55, precision/recall/F1≈1.0, pytest 11/11). "
        "<b>Not claiming D3</b> (Word/image OCR not fully demonstrated).",
        body,
    ))

    story.append(Paragraph("6. Business impact", h))
    story.append(Paragraph(
        "Risk reduction for Accenture clients shipping agents · Auditability (incident JSON) · "
        "OWASP LLM Top 10 / NIST AI RMF mapped · Humans in the loop.",
        body,
    ))

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<b>Closer:</b> Everyone else ships a classifier. We ship a twin. "
        "If the document tries to make your agent steal secrets, the plans diverge — "
        "and Aegis blocks before a single tool runs.",
        body,
    ))

    doc.build(story)
    return OUT


if __name__ == "__main__":
    print(build())
