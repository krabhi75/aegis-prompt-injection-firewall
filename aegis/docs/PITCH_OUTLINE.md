# Aegis Pitch Deck Outline (ET AI Hackathon — Problem 2)

Use this outline for a 6–8 slide PDF/PPT. Keep visuals dark-teal (match console), not purple.

---

## Slide 1 — Title
**AEGIS**  
Behavioral Twin Prompt Injection Firewall  
ET AI Hackathon: Agentic Edition · Problem 2  
Solo · Claim **F3 / D2**

## Slide 2 — The real problem
- Tool-using agents read PDF / email / HTML / OCR
- Attackers hide instructions in those documents (**indirect prompt injection**)
- LLM “is this a jailbreak?” classifiers are evaded daily
- One successful injection → secret theft, tool abuse, data exfil

## Slide 3 — Insight (why we win)
Prompt injection is not a *text classification* problem.  
It is a **runtime security** problem: does untrusted content change what tools the agent would call?

## Slide 4 — Solution: Aegis
1. Provenance tag every chunk (trusted vs untrusted)
2. Decode obfuscation (base64/hex/rot13)
3. **Behavioral twin** — plan tools on sanitized vs raw
4. Capability tokens fail-closed
5. Human analyst for quarantine band

## Slide 5 — Architecture (diagram)
Paste pipeline from `ARCHITECTURE.md`.  
Call out twin drift visualization from the live demo.

## Slide 6 — Demo proof
| Scenario | Result |
|----------|--------|
| Benign PDF | ALLOW |
| Injected PDF | BLOCK + twin drift (`get_secret`, `send_email`) |
| Encoded HTML | BLOCK |
| Multi-step | QUARANTINE → human |

## Slide 7 — Evaluation claim
- **F3:** 9 attack types implemented, ≥7 in live demo  
- **D2:** corpus precision/recall (show metrics screenshot)  
- Responsible AI: audit log + analyst loop  
- Agentic: shadow agent plans; protected agent acts only on allow

## Slide 8 — Business impact & ask
*Enterprises cannot deploy agents on untrusted content without behavioral runtime controls.*  
Aegis is that control plane — ready for Accenture client agent platforms.

---

## Speaker notes (30s closer)
“Everyone else ships a classifier. We ship a twin. If the document tries to make your agent steal secrets, the plans diverge — and Aegis blocks before a single tool runs.”
