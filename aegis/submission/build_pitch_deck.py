"""Generate professional Aegis Guard pitch deck (PPTX) matching product brand."""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

OUT = Path(__file__).resolve().parent.parent / "submission" / "Aegis_Guard_ET_AI_Hackathon_Problem2.pptx"

# Brand (from public/index.html)
INK = RGBColor(0x0B, 0x1F, 0x1A)
ACCENT = RGBColor(0x0F, 0x76, 0x6E)
ACCENT2 = RGBColor(0x11, 0x5E, 0x59)
MUTED = RGBColor(0x5B, 0x6F, 0x68)
BG = RGBColor(0xF4, 0xF7, 0xF6)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LINE = RGBColor(0xD9, 0xE2, 0xDE)
ALLOW = RGBColor(0x04, 0x78, 0x57)
BLOCK = RGBColor(0xB9, 0x1C, 0x1C)


def _set_run(run, text, size=18, bold=False, color=INK, font="Arial"):
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font


def _add_bg(slide, color=BG):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    # send to back
    spTree = slide.shapes._spTree
    sp = shape._element
    spTree.remove(sp)
    spTree.insert(2, sp)


def _bar(slide, y=0):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, y, Inches(13.333), Inches(0.08))
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT
    bar.line.fill.background()


def _footer(slide, page: str):
    box = slide.shapes.add_textbox(Inches(0.6), Inches(7.05), Inches(10), Inches(0.3))
    p = box.text_frame.paragraphs[0]
    run = p.add_run()
    _set_run(run, f"Aegis Guard  ·  ET AI Hackathon Problem 2  ·  Claim F3 / D2  ·  {page}", 10, False, MUTED)
    box2 = slide.shapes.add_textbox(Inches(11.2), Inches(7.05), Inches(1.5), Inches(0.3))
    p2 = box2.text_frame.paragraphs[0]
    p2.alignment = PP_ALIGN.RIGHT
    r2 = p2.add_run()
    _set_run(r2, page, 10, False, MUTED)


def _title(slide, text, top=0.45, size=32):
    box = slide.shapes.add_textbox(Inches(0.7), Inches(top), Inches(12), Inches(0.7))
    p = box.text_frame.paragraphs[0]
    run = p.add_run()
    _set_run(run, text, size, True, INK)


def _body(slide, lines, top=1.4, size=16, width=12):
    box = slide.shapes.add_textbox(Inches(0.7), Inches(top), Inches(width), Inches(5.2))
    tf = box.text_frame
    tf.word_wrap = True
    first = True
    for line in lines:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.space_after = Pt(8)
        run = p.add_run()
        _set_run(run, line, size, False, INK if not line.startswith("  ") else MUTED)


def _card(slide, left, top, w, h, title, body, accent=ACCENT):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = WHITE
    shape.line.color.rgb = LINE
    tip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(0.08), Inches(h))
    tip.fill.solid()
    tip.fill.fore_color.rgb = accent
    tip.line.fill.background()
    t = slide.shapes.add_textbox(Inches(left + 0.25), Inches(top + 0.2), Inches(w - 0.4), Inches(0.4))
    r = t.text_frame.paragraphs[0].add_run()
    _set_run(r, title, 14, True, ACCENT2)
    b = slide.shapes.add_textbox(Inches(left + 0.25), Inches(top + 0.65), Inches(w - 0.4), Inches(h - 0.85))
    b.text_frame.word_wrap = True
    rb = b.text_frame.paragraphs[0].add_run()
    _set_run(rb, body, 12, False, MUTED)


def build() -> Path:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # 01 Title + team
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _add_bg(s, INK)
    accent_band = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(5.9), Inches(13.333), Inches(1.6))
    accent_band.fill.solid()
    accent_band.fill.fore_color.rgb = ACCENT2
    accent_band.line.fill.background()
    box = s.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.5), Inches(1))
    r = box.text_frame.paragraphs[0].add_run()
    _set_run(r, "AEGIS GUARD", 48, True, WHITE)
    box2 = s.shapes.add_textbox(Inches(0.8), Inches(2.3), Inches(11.5), Inches(1.4))
    tf = box2.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    _set_run(r, "Behavioral Twin Prompt Injection Firewall", 24, False, RGBColor(0x9A, 0xE6, 0xC5))
    p2 = tf.add_paragraph()
    r2 = p2.add_run()
    _set_run(r2, "Agentic Cybersecurity  ·  Solo build  ·  Python", 16, False, RGBColor(0xC5, 0xD2, 0xCC))
    p3 = tf.add_paragraph()
    r3 = p3.add_run()
    _set_run(r3, "Team: Abhishek — Product · Architecture · Full-stack implementation", 15, False, RGBColor(0xE6, 0xF5, 0xF2))
    box3 = s.shapes.add_textbox(Inches(0.8), Inches(6.15), Inches(11.5), Inches(0.9))
    tf3 = box3.text_frame
    r = tf3.paragraphs[0].add_run()
    _set_run(r, "Live demo  ·  aegis-prompt-injection-firewall.vercel.app", 16, True, WHITE)
    p = tf3.add_paragraph()
    r = p.add_run()
    _set_run(r, "GitHub  ·  github.com/krabhi75/aegis-prompt-injection-firewall", 14, False, RGBColor(0xE6, 0xF5, 0xF2))

    # 02 Problem
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _add_bg(s)
    _bar(s)
    _title(s, "Problem statement")
    _card(s, 0.7, 1.4, 3.9, 2.4, "Agents touch untrusted content", "PDF, email, HTML, OCR, and APIs now feed tool-using agents. Attackers hide instructions inside those documents.")
    _card(s, 4.8, 1.4, 3.9, 2.4, "Indirect prompt injection", "A single poisoned attachment can trigger get_secret, send_email, or shell tools — without the user noticing.")
    _card(s, 8.9, 1.4, 3.7, 2.4, "Classifiers are not enough", "Keyword / LLM jailbreak detectors ask: “Does this look bad?” Attackers evade that every day.", BLOCK)
    _body(s, [
        "Enterprises are shipping copilots and agents into production workflows.",
        "Without a runtime control plane, every document becomes an attack surface.",
    ], top=4.2, size=15)
    _footer(s, "02")

    # 03 Solution insight
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _add_bg(s)
    _bar(s)
    _title(s, "Proposed solution — runtime twin, not classification")
    _body(s, [
        "Prompt injection is a runtime security problem:",
        "    Does untrusted content change what tools the agent would call?",
        "",
        "Aegis Guard runs a behavioral twin:",
        "    • Trusted plan  — instructions with untrusted content stripped",
        "    • Raw plan      — instructions as attackers hope the agent will see them",
        "    • If plans diverge on high-risk tools → BLOCK or QUARANTINE",
        "",
        "Everyone else ships a classifier. We ship a twin.",
    ], top=1.35, size=17)
    _footer(s, "03")

    # 04 Control plane
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _add_bg(s)
    _bar(s)
    _title(s, "Aegis Guard control plane")
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
        _card(s, 0.7 + col * 4.15, 1.35 + row * 2.35, 3.95, 2.15, t, b)
    _footer(s, "04")

    # 05 Architecture
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _add_bg(s)
    _bar(s)
    _title(s, "Architecture")
    _body(s, [
        "Input → Ingest → Decode → Provenance → Static → Behavioral Twin → Risk → Gate",
        "                                                              ↓",
        "                                        Protected Agent (caps)  |  Analyst Quarantine",
        "",
        "Supporting controls:",
        "  • Capability tokens fail-closed on secrets, shell, external email",
        "  • SQLite audit trail + incident JSON export",
        "  • Session risk memory for multi-step jailbreaks",
        "  • Optional OpenAI-compatible LLM planner enrichment (offline twin by default)",
        "",
        "Repo: github.com/krabhi75/aegis-prompt-injection-firewall",
    ], top=1.3, size=15)
    _footer(s, "05")

    # 06 AI models & tech
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _add_bg(s)
    _bar(s)
    _title(s, "AI models & technologies")
    _card(s, 0.7, 1.35, 6.0, 4.8, "Agentic AI in the product",
          "• Dual planner (trusted vs raw tool trajectories)\n"
          "• Deterministic offline planner by default — reproducible demos\n"
          "• Optional OpenAI-compatible / Ollama LLM planner enrichment\n"
          "• Protected agent executes only on ALLOW with capability tokens\n"
          "• Session memory for multi-step jailbreak escalation")
    _card(s, 6.95, 1.35, 5.6, 4.8, "Engineering stack",
          "• Python 3.11 · FastAPI · Pydantic v2\n"
          "• Streamlit analyst console (local)\n"
          "• Vercel Executive Console (production)\n"
          "• pypdf · BeautifulSoup · Pillow (+ optional Tesseract OCR)\n"
          "• SQLite audit · pytest · 55-sample corpus")
    _footer(s, "06")

    # 07 Demo proof
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _add_bg(s)
    _bar(s)
    _title(s, "Product demo — proof points")
    rows = [
        ("Benign product PDF", "ALLOW", "Trusted summarize path"),
        ("Indirect injection in PDF", "BLOCK", "Twin drift: get_secret + send_email"),
        ("Encoded HTML jailbreak", "BLOCK", "Decode layer + override"),
        ("Multi-step roleplay → tools", "QUARANTINE / BLOCK", "Session risk escalation"),
        ("Human analyst queue", "HITL", "Approve / deny with audit note"),
    ]
    y = 1.35
    for name, decision, detail in rows:
        shape = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(y), Inches(11.9), Inches(0.85))
        shape.fill.solid()
        shape.fill.fore_color.rgb = WHITE
        shape.line.color.rgb = LINE
        t = s.shapes.add_textbox(Inches(0.95), Inches(y + 0.18), Inches(5.5), Inches(0.5))
        _set_run(t.text_frame.paragraphs[0].add_run(), name, 14, True, INK)
        d = s.shapes.add_textbox(Inches(6.6), Inches(y + 0.18), Inches(2.2), Inches(0.5))
        color = ALLOW if decision == "ALLOW" else (BLOCK if "BLOCK" in decision else ACCENT)
        _set_run(d.text_frame.paragraphs[0].add_run(), decision, 13, True, color)
        det = s.shapes.add_textbox(Inches(8.8), Inches(y + 0.18), Inches(3.5), Inches(0.5))
        _set_run(det.text_frame.paragraphs[0].add_run(), detail, 12, False, MUTED)
        y += 0.95
    _footer(s, "07")

    # 08 Business impact
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _add_bg(s)
    _bar(s)
    _title(s, "Business impact")
    _card(s, 0.7, 1.35, 3.9, 4.6, "Risk reduction", "Block secret theft and tool abuse before execution — agents stay useful on benign documents.")
    _card(s, 4.8, 1.35, 3.9, 4.6, "Audit & governance", "Incident JSON, decision trails, OWASP LLM Top 10 & NIST AI RMF mapped controls for security teams.")
    _card(s, 8.9, 1.35, 3.7, 4.6, "Human oversight", "Quarantine band keeps analysts in the loop for ambiguous cases — fail-closed on high risk.")
    _footer(s, "08")

    # 09 Scalability
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _add_bg(s)
    _bar(s)
    _title(s, "Scalability")
    _body(s, [
        "Designed as a side-car control plane in front of any tool-using agent:",
        "  • Stateless scan API — horizontal scale behind a load balancer",
        "  • Offline twin by default — predictable latency without LLM round-trips",
        "  • Optional LLM planner only where enrichment adds value",
        "  • SQLite today → Postgres / object storage for multi-tenant audit at scale",
        "  • Capability tokens enforce least privilege per tenant / agent role",
        "  • Corpus + pytest gate regressions as detectors grow",
        "",
        "Same pattern works for email triage, ticket agents, and document copilots.",
    ], top=1.3, size=16)
    _footer(s, "09")

    # 10 Roadmap
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _add_bg(s)
    _bar(s)
    _title(s, "Future roadmap")
    _card(s, 0.7, 1.35, 3.9, 4.6, "Near term", "Deeper OCR / Word paths · richer policy packs · SIEM / webhook exporters · stronger multi-tenant audit.")
    _card(s, 4.8, 1.35, 3.9, 4.6, "Mid term", "Native SDK embeds · streaming scan for long docs · adaptive thresholds per agent role · red-team corpus growth.")
    _card(s, 8.9, 1.35, 3.7, 4.6, "North star", "Default runtime firewall for enterprise agents — twin + provenance + caps as industry pattern.")
    _footer(s, "10")

    # 11 Closer
    s = prs.slides.add_slide(prs.slide_layouts[6])
    _add_bg(s, INK)
    band = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.12), Inches(7.5))
    band.fill.solid()
    band.fill.fore_color.rgb = ACCENT
    band.line.fill.background()
    box = s.shapes.add_textbox(Inches(0.9), Inches(2.2), Inches(11.5), Inches(3.5))
    tf = box.text_frame
    tf.word_wrap = True
    r = tf.paragraphs[0].add_run()
    _set_run(r, "Everyone else ships a classifier.", 28, False, RGBColor(0xC5, 0xD2, 0xCC))
    p = tf.add_paragraph()
    r = p.add_run()
    _set_run(r, "We ship a twin.", 40, True, WHITE)
    p = tf.add_paragraph()
    r = p.add_run()
    _set_run(r, "", 14, False, WHITE)
    p = tf.add_paragraph()
    r = p.add_run()
    _set_run(r, "If the document tries to make your agent steal secrets,", 18, False, RGBColor(0xE6, 0xF5, 0xF2))
    p = tf.add_paragraph()
    r = p.add_run()
    _set_run(r, "the plans diverge — and Aegis blocks before a single tool runs.", 18, False, RGBColor(0xE6, 0xF5, 0xF2))
    box2 = s.shapes.add_textbox(Inches(0.9), Inches(6.2), Inches(11.5), Inches(0.7))
    r = box2.text_frame.paragraphs[0].add_run()
    _set_run(r, "Live  ·  aegis-prompt-injection-firewall.vercel.app     ·     Thank you", 16, True, RGBColor(0x9A, 0xE6, 0xC5))

    prs.save(OUT)
    return OUT


if __name__ == "__main__":
    path = build()
    print(path)
