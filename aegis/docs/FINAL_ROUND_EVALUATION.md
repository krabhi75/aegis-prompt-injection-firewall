# Final Round Evaluation — Aegis Guard (Problem 2)

**Product:** Aegis Guard — Behavioral Twin Prompt Injection Firewall  
**Live:** https://aegis-prompt-injection-firewall.vercel.app  
**GitHub:** https://github.com/krabhi75/aegis-prompt-injection-firewall  
**Declared 9-blocker: F3 / D2** (do **not** claim D3)

This document maps the official ET × Accenture brief to the current project and lists exactly what you must still submit to Unstop.

---

## 1. Official submission requirements (read 3×)

### From Unstop Phase 2 (Build Sprint)

You must upload **all three**:

| # | Artifact | Status | Action |
|---|----------|--------|--------|
| 1 | **Working prototype** — GitHub repository URL | DONE | Submit repo URL |
| 2 | **Pitch deck** — PDF or PowerPoint | **MISSING** | Build from `docs/PITCH_OUTLINE.md` → export PDF |
| 3 | **Demo video** — ~2–5 minutes of the solution working | **MISSING** | Record using live Vercel + script below |

### From problem PDF (“Expectations from final submission”)

| # | Artifact | Status | Action |
|---|----------|--------|--------|
| 1 | **Working demo** covering all claimed areas | DONE | Live site + local; video must show claimed attacks |
| 2 | **Detailed structural architecture** (process flow, decisions, model usage, features ↔ claims) | PARTIAL | `docs/ARCHITECTURE.md` exists — export/polish into deck appendix or separate PDF and **explicitly justify F3/D2** |

### Critical rule (penalties)

> Teams must declare their self-estimated position in the 9-blocker and clearly justify it. **Penalties for overestimation and underestimation.**

**Safe claim: F3 / D2.**  
D3 needs highly heterogeneous multimodal input **plus** high reliability demonstrated (real Word + image OCR in the recorded demo). You have OCR path code but not a solid D3 demo — **do not claim D3**.

---

## 2. Problem 2 — Feature / Depth scorecard

### Features (F-axis) — attack types detected

| Attack type (official list) | In code | In live demo scenarios | Evidence |
|----------------------------|---------|------------------------|----------|
| 1 Instruction Override | Yes | Injected PDF / encoded | static + twin |
| 2 Role Change | Yes | 4a soft roleplay | static |
| 3 Secret Extraction | Yes | Injected PDF | twin `get_secret` |
| 4 Tool Abuse | Yes | Inject / 4b | twin + caps |
| 5 Credential Theft | Yes | corpus + sink | static + sinks |
| 6 Context Poisoning | Yes | API/corpus | provenance |
| 7 Multi-Step Jailbreaks | Yes | 4a → 4b | session risk |
| 8 Encoded Instructions | Yes | Encoded HTML | decode layer |
| 9 Indirect Prompt Injection | Yes | Injected PDF | untrusted twin |

**F3 requires ≥7.** You implement **9**. → **F3 justified** if the video shows at least 7 clearly.

### Depth (D-axis)

| Level | Meaning | Your position |
|-------|---------|----------------|
| D1 | Structured/textual, mostly acceptable | Surpassed |
| **D2** | Structured/textual, **high demonstrable reliability** | **CLAIM THIS** — corpus n=55, P/R/F1≈1.0, 11 pytest |
| D3 | Heterogeneous multimodal + high reliability | **Do not claim** — Word weak; image OCR needs tesseract in video |

**Input sources coverage**

| Source | Status | Notes |
|--------|--------|-------|
| User messages | Strong | Live scan |
| PDFs | Strong | Text + real PDF fixtures in `demos/` |
| HTML | Strong | Comments / hidden channels |
| Emails | Strong | `.eml` path |
| Markdown | OK | via text |
| API responses | Strong | JSON ingest |
| OCR text | OK | paste OCR text |
| Images via OCR | Weak for demo | Code exists; tesseract optional |
| Source code | Partial | as text |
| Word documents | Weak | No real `.docx` parser — **don’t highlight** |

---

## 3. Evaluation framework — win / risk scoring

Judges use these 8 parameters + the 9-blocker.

| # | Criterion | Score (1–5) | Verdict | How to maximize in deck/video |
|---|-----------|-------------|---------|-------------------------------|
| 1 | Significance & relevance | **5** | Strong | Open with “agents + PDF/email = enterprise breach path” |
| 2 | Innovation & originality | **5** | Strong | Repeat: **not a classifier — behavioral twin** |
| 3 | Effective use of AI | **3.5** | Risk | Twin planner is agentic; optional LLM exists. Say: “deterministic twin for reliability (D2); LLM enrichment optional.” Don’t pretend a giant LLM is the firewall. |
| 4 | Technical complexity & execution | **4.5** | Strong | Show architecture + pipeline trace + GitHub quality |
| 5 | Agentic / autonomous capability | **4.5** | Strong | Shadow planner + protected agent + tools + quarantine |
| 6 | Business / user impact | **4.5** | Strong | Risk reduction for Accenture clients shipping agents |
| 7 | Prototype quality & usability | **4.5** | Strong | Live Vercel URL — zero setup for judges |
| 8 | Scalability, Responsible AI & robustness | **4.5** | Strong | HITL quarantine, audit, capability tokens, OWASP/NIST map |

**Overall prototype strength: Top-tier for Problem 2 — if submission artifacts are complete.**  
**Current blocker to winning Phase 2 shortlist: missing pitch deck + demo video.**

---

## 4. What is already competition-ready

- Live production demo (Vercel) with executive console  
- GitHub public repo + README + architecture  
- F3 attack coverage (9 types) with corpus proof for D2  
- Differentiator: behavioral twin + classifier-vs-Aegis comparison  
- Agentic path: plan → gate → tools / quarantine  
- Responsible AI: policy console, audit, HITL  
- Frameworks tab (OWASP / NIST) for Accenture language  
- Tests green; corpus metrics reproducible  

---

## 5. What YOU must still do (non-negotiable)

### A. Pitch deck (PDF or PPT) — build today

Use `docs/PITCH_OUTLINE.md`. **Required slides:**

1. Title — Aegis Guard · Problem 2 · **Claim F3 / D2**  
2. Problem — indirect injection in enterprise agents  
3. Insight — runtime twin, not text classifier  
4. Solution — 5 layers (provenance → decode → static → twin → gate)  
5. Architecture diagram (from ARCHITECTURE.md)  
6. Demo proof table + **live URL**  
7. 9-blocker justification (F3 evidence + D2 corpus screenshot)  
8. Business impact + Accenture fit + closer line  

Export as **PDF**. Filename suggestion: `Aegis_Guard_ET_AI_Hackathon_Problem2.pdf`

### B. Demo video (2–5 min) — record today

**Use the live site** (not only Streamlit):  
https://aegis-prompt-injection-firewall.vercel.app

| Time | Shot | Must show |
|------|------|-----------|
| 0:00–0:25 | Hero + F3/D2 claim + live URL | Brand |
| 0:25–0:45 | Benign path | **ALLOW** |
| 0:45–1:25 | Indirect injection | **BLOCK** + twin drift + classifier-vs-Aegis advantage |
| 1:25–1:45 | Encoded HTML | **BLOCK** + decode |
| 1:45–2:15 | 4a → 4b multi-step | Session escalation |
| 2:15–2:40 | Pipeline trace + Incident JSON download | Explainability |
| 2:40–3:10 | Command Center metrics | D2 proof (precision/recall) |
| 3:10–3:40 | Frameworks (OWASP/NIST) + Quarantine approve/deny | Responsible AI |
| 3:40–4:00 | Closer | “Everyone ships a classifier. We ship a twin.” |

Upload to YouTube/Drive **unlisted** if Unstop asks for a link; otherwise upload the file.

### C. Architecture justification (include in deck or separate PDF)

One page that states:

> **Self-estimated position: F3 / D2**  
> F3: 9/9 attack types implemented; video demonstrates ≥7.  
> D2: textual/structured multimodal text paths; corpus n=55, precision=recall=F1=1.0 on suite; pytest 11/11.  
> Not claiming D3: image OCR / Word not fully demonstrated in production demo.

### D. Unstop form fields (double-check)

- Problem statement selected: **Problem 2 — Prompt Injection Firewall**  
- GitHub: `https://github.com/krabhi75/aegis-prompt-injection-firewall`  
- Live demo (if asked): `https://aegis-prompt-injection-firewall.vercel.app`  
- Declared grid: **F3 / D2**  
- Team: Solo  

---

## 6. Optional upgrades (only if time — not blockers)

| Upgrade | Why | Priority |
|---------|-----|----------|
| Real `.pdf` upload in video (`demos/injected_product.pdf`) | Stronger multimodal proof | High if easy |
| 30s of optional LLM twin with API key | Softens “Effective use of AI” risk | Medium |
| One-page architecture PDF export | Cleaner than markdown for judges | Medium |
| `.docx` ingest | Only if chasing D3 — **not recommended now** | Skip |

---

## 7. Win strategy (Phase 2 → Top 10 → Finale)

1. **Phase 2 shortlist:** Complete deck + video + clear F3/D2 claim. Incomplete submissions lose to weaker but complete ones.  
2. **Differentiation line (memorize):**  
   *“Classifiers ask if text looks like a jailbreak. Aegis asks whether untrusted content would change the agent’s tool calls — and blocks before any tool runs.”*  
3. **Finale (if Top 10):** Live demo on Vercel; open with twin advantage; show Command Center + HITL; end with Accenture client agent deployment risk.  
4. **Never overclaim D3** — overestimation is explicitly penalized.

---

## 8. Final go / no-go

| Gate | Status |
|------|--------|
| Prototype works | GO |
| Innovation clear | GO |
| F3 / D2 defensible | GO |
| Pitch deck uploaded | **NO-GO until you build it** |
| Demo video uploaded | **NO-GO until you record it** |
| Architecture claim justified in submission | **NO-GO until in deck/PDF** |

**Bottom line:** The product is strong enough to compete for 1st. The submission package is not complete until **deck + video + explicit F3/D2 justification** are uploaded to Unstop.
