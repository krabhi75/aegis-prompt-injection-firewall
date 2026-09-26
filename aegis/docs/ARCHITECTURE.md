# Aegis Architecture — ET AI Hackathon Problem 2

## Product

**Aegis** is a behavioral twin Prompt Injection Firewall. It intercepts user messages and multimodal content (PDF, HTML, email, OCR, API) before they influence a tool-using agent.

**Self-estimated 9-blocker position: F3 / D2**

| Axis | Claim | Evidence |
|------|-------|----------|
| F3 | ≥7 attack types | All 9 types implemented; demo covers ≥7 |
| D2 | Structured/textual + high reliability | 55-sample corpus + pytest; metrics in UI |

D3 stretch: OCR/image ingest path exists (`firewall/ingest.py::ingest_ocr_image`). Claim D3 only if tesseract is shown in the recorded demo.

---

## Pipeline

```
Input → Ingest/Normalize → Decode → Provenance → Static Detectors
                                                  ↓
                                            Behavioral Twin
                                                  ↓
                                             Risk Engine
                                                  ↓
                                      ALLOW | QUARANTINE | BLOCK
                                          ↓         ↓
                                   Protected Agent  Analyst Console
```

### Module map

| Stage | Path | Responsibility |
|-------|------|----------------|
| Ingest | `firewall/ingest.py` | PDF/HTML/email/OCR/API → `ContentChunk` |
| Decode | `firewall/decode.py` | base64 / hex / URL / rot13 / homoglyph |
| Provenance | `firewall/provenance.py` | trusted vs untrusted spans |
| Static | `firewall/static.py` | rule detectors for 9 attack types |
| Twin | `firewall/twin.py` + `agent/planner.py` | dual plan + drift score |
| Risk/Gate | `firewall/risk.py` | thresholds + session memory |
| Engine | `firewall/engine.py` | orchestration + audit |
| Caps | `agent/capabilities.py` | capability tokens |
| Tools | `agent/tools.py` | sandboxed tools + sink monitor |
| Agent | `agent/protected.py` | execute only on ALLOW |
| API | `app/main.py` | FastAPI |
| UI | `ui/console.py` | Streamlit analyst console |
| Corpus | `corpus/` | D2 precision/recall proof |

---

## Attack coverage (F3)

| Attack | Primary detector | Demo moment |
|--------|------------------|-------------|
| Instruction Override | static + twin | Scenario 2 / encoded |
| Role Change | static + role lock | Scenario 4a |
| Secret Extraction | twin drift + caps | Scenario 2 |
| Tool Abuse | twin new-tool + caps | Scenario 2 / 4b |
| Credential Theft | sink + static | corpus m09 / m20 |
| Context Poisoning | provenance + static | API poison cases |
| Multi-Step Jailbreak | session risk | Scenario 4a→4b |
| Encoded Instructions | decode layer | Scenario 3 |
| Indirect Prompt Injection | untrusted twin | Scenario 2 PDF |

---

## Behavioral twin (differentiator)

1. Build `raw_text` (all chunks) and `sanitized_text` (untrusted omitted from instruction channel).
2. Plan tools twice: `plan_trusted` vs `plan_raw`.
3. Drift if raw plan adds high-risk tools (`get_secret`, `send_email`, `shell_exec`, `write_file`) or external email destinations.
4. Risk engine merges static confidence + drift + session history → gate.

Keyword classifiers miss indirect injection buried in PDFs. Twin does not: the *behavior* changes.

---

## Responsible AI / human-in-the-loop

- Quarantine band (risk 0.45–0.75) requires analyst approve/deny.
- Full SQLite audit trail (`firewall/audit.py`).
- Secrets never leave the fake vault under default capabilities.
- Fail-closed on restricted tools.

---

## Business impact (Accenture judges)

Enterprises deploying tool-using agents on email, web, and PDF cannot rely on prompt classifiers alone. Aegis provides a **runtime control plane**: provenance, behavioral containment, capability tokens, and human oversight — the same pattern Accenture uses for enterprise security architectures.

---

## How to reproduce metrics

```bash
make install
make test
make corpus
```

Open Streamlit → **Corpus Metrics** → Evaluate corpus.
