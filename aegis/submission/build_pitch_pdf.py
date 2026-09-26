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
    c.drawString(0.6 * inch, 0.35 * inch, f"Aegis Guard  ·  Prompt Injection Firewall  ·  {page}")
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
    style = ParagraphStyle("card", fontName="Helvetica", fontSize=10, textColor=MUTED, leading=14)
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
    c.drawString(0.8 * inch, H - 2.2 * inch, "AEGIS GUARD")
    c.setFillColor(MINT)
    c.setFont("Helvetica", 18)
    c.drawString(0.8 * inch, H - 2.85 * inch, "Behavioral Twin Prompt Injection Firewall")
    c.setFillColor(SOFT)
    c.setFont("Helvetica", 12)
    c.drawString(0.8 * inch, H - 3.25 * inch, "Agentic Cybersecurity  ·  Solo build  ·  Python")
    c.setFillColor(HexColor("#E6F5F2"))
    c.setFont("Helvetica", 12)
    c.drawString(0.8 * inch, H - 3.7 * inch, "Team: Abhishek — Product · Architecture · Full-stack implementation")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(0.8 * inch, 0.85 * inch, "Live  ·  aegis-prompt-injection-firewall.vercel.app")
    c.setFont("Helvetica", 11)
    c.drawString(0.8 * inch, 0.5 * inch, "GitHub  ·  github.com/krabhi75/aegis-prompt-injection-firewall")
    c.showPage()


def slide_problem(c: canvas.Canvas) -> None:
    _bg(c)
    _footer(c, "02")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(0.7 * inch, H - 0.95 * inch, "Problem statement")
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
    c.drawString(0.7 * inch, 1.6 * inch, "Enterprises are shipping copilots and agents into production workflows.")
    c.drawString(0.7 * inch, 1.25 * inch, "Without a runtime control plane, every document becomes an attack surface.")
    c.showPage()


def slide_solution(c: canvas.Canvas) -> None:
    _bg(c)
    _footer(c, "03")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(0.7 * inch, H - 0.95 * inch, "Proposed solution — runtime twin, not classification")
    lines = [
        "Prompt injection is a runtime security problem:",
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
    c.drawString(0.7 * inch, H - 0.95 * inch, "Architecture")
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
        "Repo: github.com/krabhi75/aegis-prompt-injection-firewall",
    ]
    y = H - 3.1 * inch
    for b in bullets:
        c.setFillColor(INK)
        c.setFont("Helvetica", 12)
        c.drawString(0.9 * inch, y, f"•  {b}")
        y -= 0.42 * inch
    c.showPage()


def slide_tech(c: canvas.Canvas) -> None:
    _bg(c)
    _footer(c, "06")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(0.7 * inch, H - 0.95 * inch, "AI models & technologies")
    _card(
        c, 0.7 * inch, 0.9 * inch, 5.5 * inch, 5.0 * inch, "Agentic AI in the product",
        "• Dual planner (trusted vs raw tool trajectories)<br/>"
        "• Deterministic offline planner by default<br/>"
        "• Optional OpenAI-compatible / Ollama enrichment<br/>"
        "• Protected agent executes only on ALLOW<br/>"
        "• Session memory for multi-step jailbreaks",
    )
    _card(
        c, 6.5 * inch, 0.9 * inch, 5.3 * inch, 5.0 * inch, "Engineering stack",
        "• Python 3.11 · FastAPI · Pydantic v2<br/>"
        "• Streamlit analyst console (local)<br/>"
        "• Vercel Executive Console (production)<br/>"
        "• pypdf · BeautifulSoup · Pillow (+ OCR)<br/>"
        "• SQLite audit · pytest · 55-sample corpus",
    )
    c.showPage()


def slide_demo(c: canvas.Canvas) -> None:
    _bg(c)
    _footer(c, "07")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(0.7 * inch, H - 0.95 * inch, "Product demo — proof points")
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


def slide_business(c: canvas.Canvas) -> None:
    _bg(c)
    _footer(c, "08")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(0.7 * inch, H - 0.95 * inch, "Business impact")
    _card(c, 0.7 * inch, 1.0 * inch, 3.3 * inch, 4.6 * inch, "Risk reduction",
          "Block secret theft and tool abuse before execution — agents stay useful on benign documents.")
    _card(c, 4.2 * inch, 1.0 * inch, 3.3 * inch, 4.6 * inch, "Audit & governance",
          "Incident JSON, decision trails, OWASP LLM Top 10 & NIST AI RMF mapped controls.")
    _card(c, 7.7 * inch, 1.0 * inch, 3.3 * inch, 4.6 * inch, "Human oversight",
          "Quarantine band keeps analysts in the loop — fail-closed on high risk.")
    c.showPage()


def slide_scale(c: canvas.Canvas) -> None:
    _bg(c)
    _footer(c, "09")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(0.7 * inch, H - 0.95 * inch, "Scalability")
    lines = [
        "Designed as a side-car control plane in front of any tool-using agent:",
        "  • Stateless scan API — horizontal scale behind a load balancer",
        "  • Offline twin by default — predictable latency without LLM round-trips",
        "  • Optional LLM planner only where enrichment adds value",
        "  • SQLite today → Postgres / object storage for multi-tenant audit",
        "  • Capability tokens enforce least privilege per tenant / agent role",
        "  • Corpus + pytest gate regressions as detectors grow",
        "",
        "Same pattern works for email triage, ticket agents, and document copilots.",
    ]
    y = H - 1.55 * inch
    for line in lines:
        c.setFont("Helvetica", 13)
        c.setFillColor(INK if not line.startswith("  ") else MUTED)
        c.drawString(0.7 * inch, y, line)
        y -= 0.4 * inch
    c.showPage()


def slide_roadmap(c: canvas.Canvas) -> None:
    _bg(c)
    _footer(c, "10")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(0.7 * inch, H - 0.95 * inch, "Future roadmap")
    _card(c, 0.7 * inch, 1.0 * inch, 3.3 * inch, 4.6 * inch, "Near term",
          "Deeper OCR / Word paths · richer policy packs · SIEM / webhook exporters · stronger multi-tenant audit.")
    _card(c, 4.2 * inch, 1.0 * inch, 3.3 * inch, 4.6 * inch, "Mid term",
          "Native SDK embeds · streaming scan for long docs · adaptive thresholds per agent role · red-team corpus growth.")
    _card(c, 7.7 * inch, 1.0 * inch, 3.3 * inch, 4.6 * inch, "North star",
          "Default runtime firewall for enterprise agents — twin + provenance + caps as industry pattern.")
    c.showPage()


def slide_close(c: canvas.Canvas) -> None:
    _bg(c, INK)
    c.setFillColor(ACCENT)
    c.rect(0, 0, 10, H, fill=1, stroke=0)
    c.setFillColor(SOFT)
    c.setFont("Helvetica", 22)
    c.drawString(0.9 * inch, H - 2.6 * inch, "Everyone else ships a classifier.")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 34)
    c.drawString(0.9 * inch, H - 3.3 * inch, "We ship a twin.")
    c.setFillColor(HexColor("#E6F5F2"))
    c.setFont("Helvetica", 14)
    c.drawString(0.9 * inch, H - 4.1 * inch, "If the document tries to make your agent steal secrets,")
    c.drawString(0.9 * inch, H - 4.45 * inch, "the plans diverge — and Aegis blocks before a single tool runs.")
    c.setFillColor(MINT)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(0.9 * inch, 1.0 * inch, "Live  ·  aegis-prompt-injection-firewall.vercel.app     ·     Thank you")
    c.showPage()


def build() -> Path:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=PAGE)
    c.setTitle("Aegis Guard — Pitch Deck")
    c.setAuthor("Aegis Guard")
    slide_title(c)
    slide_problem(c)
    slide_solution(c)
    slide_control(c)
    slide_architecture(c)
    slide_tech(c)
    slide_demo(c)
    slide_business(c)
    slide_scale(c)
    slide_roadmap(c)
    slide_close(c)
    c.save()
    return OUT


if __name__ == "__main__":
    path = build()
    print(path)
