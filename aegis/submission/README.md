# Submission package — upload these to Unstop

## Files (ready)

| File | Purpose |
|------|---------|
| [`Aegis_Guard_ET_AI_Hackathon_Problem2.pptx`](Aegis_Guard_ET_AI_Hackathon_Problem2.pptx) | Professional pitch deck (brand-matched) |
| [`Aegis_Guard_ET_AI_Hackathon_Problem2.pdf`](Aegis_Guard_ET_AI_Hackathon_Problem2.pdf) | PDF version of the deck |
| [`Aegis_Guard_Demo_4min.mp4`](Aegis_Guard_Demo_4min.mp4) | ~4:30 demo video with Indian-English Deepgram narration |

## Links

- **Live demo:** https://aegis-prompt-injection-firewall.vercel.app
- **GitHub:** https://github.com/krabhi75/aegis-prompt-injection-firewall
- **Claim:** F3 / D2

## Voice

- Deepgram Flux TTS: `flux-naveen-en` (Indian English, adult, professional)
- Script: `NARRATION_SCRIPT.md`
- Audio: `video_assets/narration_naveen.mp3`

## Regenerate (optional)

```bash
# from repo root, with DEEPGRAM_API_KEY in .env (never commit .env)
.venv/bin/python aegis/submission/build_pitch_deck.py
.venv/bin/python aegis/submission/build_pitch_pdf.py
.venv/bin/python aegis/submission/generate_voiceover.py
.venv/bin/python aegis/submission/compose_demo_video.py
```

## Security

Rotate your Deepgram API key after the hackathon — it was pasted in chat.
Never commit `.env`.
