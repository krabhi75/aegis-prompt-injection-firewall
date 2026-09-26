"""Export a professional multi-page PDF twin of the Aegis Guard pitch deck."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

OUT = Path(__file__).resolve().parent / "Aegis_Guard_ET_AI_Hackathon_Problem2.pdf"
INK = HexColor("#0B1F1A")
ACCENT = HexColor("#0F766E")
ACCENT2 = HexColor("#115E59")
MUTED = HexColor("#5B6F68")
BG = HexColor("#F4F7F6")
LINE = HexColor("#D9E2DE")
ALLOW = HexColor("#047857")
BLOCK = HexColor("#B91C1C")
MINT = HexColor("#9AE6C5")
SOFT = HexColor("#C5D2CC")

PAGE = landscape(A4)
W, H = PAGE


def _footer(c: canvas.Canvas, page: str) -> None:
    c.setStrokeColor(ACCENT)
    c.setLineWidth(3)
    c.line(0, H - 6, W, H - 6)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 9)
    c.drawString(0.6 * inch, 0.35 * inch, f"Aegis Guard  ·  ET AI Hackathon Problem 2  ·  Claim F3 / D2  ·  {page}")
    c.drawRightString(W - 0.55 * inch, 0.35 * inch, page)


def _card(c: canvas.Canvas, x, y, w, h, title: str, body: str, accent=ACCENT) -> None:
    c.setFillColor(white)
    c.setStrokeColor(LINE)
    c.setLineWidth(1)
    c.roundRect(x, y, w, h, 8, fill=1, stroke=1)
    c.setFillColor(accent)
    c.rect(x, y, 6, h, fill=1, stroke=0)
    c.setFillColor(ACCENT2)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x + 16, y + h - 22, title)
    style = ParagraphStyle(
        "card",
        fontName="Helvetica",
        fontSize=10,
        textColor=MUTED,
        leading=14,
    )
    p = Paragraph(body.replace("\n", "<br/>"), style)
    pw, ph = p.wrap(w - 28, h - 40)
    p.drawOn(c, x + 16, y + h - 36 - ph)


def _bg(c: canvas.Canvas, color=BG) -> None:
    c.setFillColor(color)
    c.rect(0, 0, W, H, fill=1, stroke=0)


def slide_title(c: canvas.Canvas) -> None:
    _bg(c, INK)
    c.setFillColor(ACCENT2)
    c.rect(0, 0, W, 1.45 * inch, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 42)
    c.drawString(0.8 * inch, H - 2.4 * inch, "AEGIS GUARD")
    c.setFillColor(MINT)
    c.setFont("Helvetica", 20)
    c.drawString(0.8 * inch, H - 3.15 * inch, "Behavioral Twin Prompt Injection Firewall")
    c.setFillColor(SOFT)
    c.setFont("Helvetica", 13)
    c.drawString(0.8 * inch, H - 3.55 * inch, "ET AI Hackathon: Agentic Edition  ·  Problem 2  ·  Solo")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(0.8 * inch, 0.85 * inch, "Self-estimated 9-blocker:  F3  /  D2")
    c.setFont("Helvetica", 11)
    c.drawString(0.8 * inch, 0.5 * inch, "Live  ·  aegis-prompt-injection-firewall.vercel.app")
    c.showPage()


def slide_problem(c: canvas.Canvas) -> None:
    _bg(c)
    _footer(c, "02")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(0.7 * inch, H - 0.95 * inch, "The enterprise risk")
    cards = [
        (0.7, "Agents touch untrusted content", "PDF, email, HTML, OCR, and APIs now feed tool-using agents. Attackers hide instructions inside those documents."),
        (4.0, "Indirect prompt injection", "A single poisoned attachment can trigger get_secret, send_email, or shell tools — without the user noticing."),
        (7.3, "Classifiers are not enough", "Keyword / LLM jailbreak detectors ask: “Does this look bad?” Attackers evade that every day."),
    ]
    accents = [ACCENT, ACCENT, BLOCK]
    for (x, t, b), a in zip(cards, accents):
        _card(c, x * inch, H - 4.2 * inch, 3.1 * inch, 2.5 * inch, t, b, a)
    c.setFillColor(INK)
    c.setFont("Helvetica", 12)
    c.drawString(0.7 * inch, 1.6 * inch, "Accenture clients are shipping copilots and agents into production workflows.")
    c.drawString(0.7 * inch, 1.25 * inch, "Without a runtime control plane, every document becomes an attack surface.")
    c.showPage()


def slide_insight(c: canvas.Canvas) -> None:
    _bg(c)
    _footer(c, "03")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(0.7 * inch, H - 0.95 * inch, "The insight: runtime, not classification")
    lines = [
        "Prompt injection is not a text-classification problem.",
        "It is a runtime security problem:",
        "    Does untrusted content change what tools the agent would call?",
        "",
        "Aegis Guard runs a behavioral twin:",
        "    • Trusted plan — instructions with untrusted content stripped",
        "    • Raw plan — instructions as attackers hope the agent will see them",
        "    • If plans diverge on high-risk tools → BLOCK or QUARANTINE",
        "",
        "Everyone else ships a classifier. We ship a twin.",
    ]
    y = H - 1.55 * inch
    for line in lines:
        c.setFont("Helvetica-Bold" if line.startswith("Everyone") else "Helvetica", 13)
        c.setFillColor(INK if not line.startswith("    ") else MUTED)
        c.drawString(0.7 * inch, y, line)
        y -= 0.38 * inch
    c.showPage()


def slide_control(c: canvas.Canvas) -> None:
    _bg(c)
    _footer(c, "04")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(0.7 * inch, H - 0.95 * inch, "Aegis Guard control plane")
    steps = [
        ("01 Ingest", "Normalize PDF, HTML, email, OCR, API"),
        ("02 Decode", "Unwrap base64 / hex / rot13 / homoglyphs"),
        ("03 Provenance", "Tag trusted vs untrusted spans"),
        ("04 Static", "Detect 9 attack families"),
        ("05 Twin", "Dual tool-plan comparison"),
        ("06 Risk + Gate", "ALLOW · QUARANTINE · BLOCK"),
    ]
    for i, (t, b) in enumerate(steps):
        col = i % 3
        row = i // 3
        x = 0.7 + col * 3.5
        y = H - (3.5 + row * 2.45) * inch
        _card(c, x * inch, y, 3.3 * inch, 2.15 * inch, t, b)
    c.showPage()


def slide_architecture(c: canvas.Canvas) -> None:
    _bg(c)
    _footer(c, "05")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(0.7 * inch, H - 0.95 * inch, "Architecture — evidence for claims")
    c.setFillColor(white)
    c.setStrokeColor(LINE)
    c.roundRect(0.7 * inch, H - 2.5 * inch, W - 1.4 * inch, 1.15 * inch, 8, fill=1, stroke=1)
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(W / 2, H - 1.85 * inch, "Ingest → Decode → Provenance → Static → Behavioral Twin → Risk → Gate")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    c.drawCentredString(W / 2, H - 2.2 * inch, "Protected Agent (capability tokens)  ·  Analyst Quarantine (HITL)")
    bullets = [
        "Capability tokens fail-closed on secrets, shell, external email",
        "SQLite audit trail + incident JSON export",
        "Session risk memory for multi-step jailbreaks",
        "Optional OpenAI-compatible LLM planner (offline twin by default)",
        "Stack: Python · FastAPI · Streamlit (local) · Vercel production UI",
        "Repo: github.com/krabhi75/aegis-prompt-injection-firewall",
    ]
    y = H - 3.1 * inch
    for b in bullets:
        c.setFillColor(INK)
        c.setFont("Helvetica", 12)
        c.drawString(0.9 * inch, y, f"•  {b}")
        y -= 0.42 * inch
    c.showPage()


def slide_demo(c: canvas.Canvas) -> None:
    _bg(c)
    _footer(c, "06")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(0.7 * inch, H - 0.95 * inch, "Demo proof")
    rows = [
        ("Benign product PDF", "ALLOW", "Trusted summarize path", ALLOW),
        ("Indirect injection in PDF", "BLOCK", "Twin drift: get_secret + send_email", BLOCK),
        ("Encoded HTML jailbreak", "BLOCK", "Decode layer + override", BLOCK),
        ("Multi-step roleplay → tools", "QUARANTINE / BLOCK", "Session risk escalation", ACCENT),
        ("Human analyst queue", "HITL", "Approve / deny with audit note", ACCENT),
    ]
    y = H - 1.85 * inch
    for name, decision, detail, color in rows:
        c.setFillColor(white)
        c.setStrokeColor(LINE)
        c.roundRect(0.7 * inch, y - 0.15 * inch, W - 1.4 * inch, 0.72 * inch, 6, fill=1, stroke=1)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(0.95 * inch, y + 0.15 * inch, name)
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(5.4 * inch, y + 0.15 * inch, decision)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 10)
        c.drawString(8.0 * inch, y + 0.15 * inch, detail)
        y -= 0.85 * inch
    c.showPage()


def slide_claim(c: canvas.Canvas) -> None:
    _bg(c)
    _footer(c, "07")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(0.7 * inch, H - 0.95 * inch, "9-blocker claim — F3 / D2")
    f3 = (
        "All 9 official attack types implemented and covered in corpus:<br/><br/>"
        "1 Instruction Override<br/>2 Role Change<br/>3 Secret Extraction<br/>"
        "4 Tool Abuse<br/>5 Credential Theft<br/>6 Context Poisoning<br/>"
        "7 Multi-Step Jailbreak<br/>8 Encoded Instructions<br/>9 Indirect Prompt Injection<br/><br/>"
        "Live demo demonstrates ≥7 clearly."
    )
    d2 = (
        "Mostly structured/textual multimodal inputs "
        "(user, PDF text, HTML, email, API, OCR text) "
        "with demonstrable reliability:<br/><br/>"
        "• Corpus n = 55<br/>"
        "• Precision / Recall / F1 ≈ 1.0 on suite<br/>"
        "• Pytest: 11/11 passed<br/>"
        "• Command Center metrics in live UI<br/><br/>"
        "Not claiming D3: Word/image OCR not fully shown in production demo."
    )
    _card(c, 0.7 * inch, 0.9 * inch, 5.5 * inch, 5.0 * inch, "F3 — Features (≥7 attack types)", f3)
    _card(c, 6.5 * inch, 0.9 * inch, 5.3 * inch, 5.0 * inch, "D2 — Depth (high reliability)", d2)
    c.showPage()


def slide_close(c: canvas.Canvas) -> None:
    _bg(c)
    _footer(c, "08")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(0.7 * inch, H - 0.95 * inch, "Business impact & ask")
    lines = [
        "Measurable outcomes for enterprises deploying agents:",
        "  • Risk reduction — block secret theft and tool abuse before execution",
        "  • Auditability — incident JSON + decision trail for security teams",
        "  • Governance — OWASP LLM Top 10 & NIST AI RMF mapped controls",
        "  • Human oversight — quarantine band keeps humans in the loop",
        "",
        "Live: https://aegis-prompt-injection-firewall.vercel.app",
        "Code: https://github.com/krabhi75/aegis-prompt-injection-firewall",
        "",
        "Closer: Everyone else ships a classifier. We ship a twin.",
        "If the document tries to make your agent steal secrets,",
        "the plans diverge — and Aegis blocks before a single tool runs.",
    ]
    y = H - 1.55 * inch
    for line in lines:
        bold = line.startswith("Closer") or line.startswith("Live") or line.startswith("Code")
        c.setFont("Helvetica-Bold" if bold else "Helvetica", 12)
        c.setFillColor(INK if not line.startswith("  ") else MUTED)
        c.drawString(0.7 * inch, y, line)
        y -= 0.38 * inch
    c.showPage()


def build() -> Path:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=PAGE)
    c.setTitle("Aegis Guard — ET AI Hackathon Problem 2")
    c.setAuthor("Aegis Guard")
    slide_title(c)
    slide_problem(c)
    slide_insight(c)
    slide_control(c)
    slide_architecture(c)
    slide_demo(c)
    slide_claim(c)
    slide_close(c)
    c.save()
    return OUT


if __name__ == "__main__":
    path = build()
    print(path)
