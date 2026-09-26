# Aegis 2-minute demo script

## Setup
```bash
make install
make api   # terminal 1
make ui    # terminal 2 → http://localhost:8501
```

## Shot list

| Time | Action | Expected |
|------|--------|----------|
| 0:00–0:20 | Open Aegis console, show hero + F3/D2 claim | Brand + claim visible |
| 0:20–0:40 | Demo Scenarios → **1 · Benign PDF summary** → Run | ALLOW, summarize tools only |
| 0:40–1:10 | Scenario **2 · Indirect injection in PDF** → Run | BLOCK; twin shows get_secret + send_email drift |
| 1:10–1:30 | Scenario **3 · Encoded HTML jailbreak** → Run | BLOCK; Encoded Instructions |
| 1:30–1:50 | **4a** soft roleplay then **4b** tool abuse | QUARANTINE / BLOCK; Multi-Step |
| 1:50–2:00 | Quarantine tab approve/deny + Audit log | Human-in-the-loop |

## Talking points
- Not an LLM classifier — behavioral twin compares tool trajectories
- Provenance: untrusted PDF/HTML never becomes instructions
- Capability tokens fail-closed on secrets/email
- Corpus metrics tab proves D2 reliability
