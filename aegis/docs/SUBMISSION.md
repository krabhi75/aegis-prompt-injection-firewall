# Submission checklist — Aegis (Problem 2)

## Required Unstop artifacts

- [x] Working prototype (this repo)
- [ ] Pitch deck PDF/PPT — build from [`docs/PITCH_OUTLINE.md`](../docs/PITCH_OUTLINE.md)
- [ ] 2-minute demo video — follow [`demos/SCRIPT.md`](../demos/SCRIPT.md)
- [x] Architecture write-up — [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md)

## Declared 9-blocker position

**F3 / D2** (do not claim D3 unless OCR+tesseract is in the recorded video)

Justification:
- F3: 9 attack types in static/twin/decode; live demo shows ≥7
- D2: corpus n=55, precision/recall/f1 = 1.0 on current suite; pytest green

## Run before recording

```bash
make install && make test && make corpus
make api   # term 1
make ui    # term 2
```
