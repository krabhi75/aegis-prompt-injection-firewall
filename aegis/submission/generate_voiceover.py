"""Generate Deepgram Flux TTS narration for the 4-minute demo video.

Voice: flux-naveen-en (Indian English, adult, professional).
API key loaded from project .env — never commit the key.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT / ".env"
SCRIPT_PATH = Path(__file__).resolve().parent / "NARRATION_SCRIPT.md"
OUT_DIR = Path(__file__).resolve().parent / "video_assets"
OUT_AUDIO = OUT_DIR / "narration_naveen.mp3"

# Indian English adult professional (Deepgram Flux)
MODEL = os.getenv("AEGIS_TTS_MODEL", "flux-naveen-en")
# Fallback if Flux early-access unavailable
FALLBACK_MODEL = "aura-2-odysseus-en"


def load_env() -> None:
    if not ENV_PATH.exists():
        return
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def extract_script(md: str) -> str:
    # Drop markdown headers / timing comments; keep narration body after ---
    if "---" in md:
        md = md.split("---", 2)[-1]
    lines = []
    for line in md.splitlines():
        s = line.strip()
        if not s:
            lines.append("")
            continue
        if s.startswith("#"):
            continue
        lines.append(s)
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def synthesize(text: str, model: str, api_key: str) -> bytes:
    # Flux batch REST
    url = f"https://api.deepgram.com/v2/speak?model={model}&encoding=mp3&bit_rate=48000"
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json",
    }
    with httpx.Client(timeout=180.0) as client:
        resp = client.post(url, headers=headers, json={"text": text})
        if resp.status_code >= 400:
            # Try classic Aura v1 endpoint as fallback
            aura_url = (
                f"https://api.deepgram.com/v1/speak?model={FALLBACK_MODEL}"
                f"&encoding=mp3&bit_rate=48000"
            )
            resp2 = client.post(aura_url, headers=headers, json={"text": text})
            if resp2.status_code >= 400:
                raise RuntimeError(
                    f"Deepgram TTS failed.\nFlux: {resp.status_code} {resp.text[:500]}\n"
                    f"Aura: {resp2.status_code} {resp2.text[:500]}"
                )
            print(f"WARN: Flux model unavailable; used fallback {FALLBACK_MODEL}", file=sys.stderr)
            return resp2.content
        return resp.content


def main() -> None:
    load_env()
    api_key = os.getenv("DEEPGRAM_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("DEEPGRAM_API_KEY missing in .env")

    text = extract_script(SCRIPT_PATH.read_text(encoding="utf-8"))
    words = len(re.findall(r"\w+", text))
    print(f"Script words≈{words}  model={MODEL}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Chunk under Deepgram Flux 2000-char hard limit
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    # Prefer sentence packing
    sentences: list[str] = []
    for p in paragraphs:
        sentences.extend([s.strip() for s in re.split(r"(?<=[.!?])\s+", p) if s.strip()])
    chunks: list[str] = []
    buf = ""
    for s in sentences:
        if len(buf) + len(s) + 1 > 1700 and buf:
            chunks.append(buf.strip())
            buf = s
        else:
            buf = f"{buf} {s}".strip() if buf else s
    if buf.strip():
        chunks.append(buf.strip())

    print(f"TTS chunks: {len(chunks)}")
    part_files: list[Path] = []
    for i, chunk in enumerate(chunks, 1):
        audio = synthesize(chunk, MODEL, api_key)
        part = OUT_DIR / f"narration_part{i:02d}.mp3"
        part.write_bytes(audio)
        part_files.append(part)
        print(f"  wrote {part.name} ({len(audio)} bytes)")

    if len(part_files) == 1:
        OUT_AUDIO.write_bytes(part_files[0].read_bytes())
    else:
        # Concat demuxer
        list_file = OUT_DIR / "concat.txt"
        list_file.write_text(
            "\n".join(f"file '{p.resolve()}'" for p in part_files) + "\n",
            encoding="utf-8",
        )
        import subprocess

        subprocess.run(
            [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", str(list_file), "-c", "copy", str(OUT_AUDIO),
            ],
            check=True,
            capture_output=True,
        )
    print(f"OK {OUT_AUDIO}")


if __name__ == "__main__":
    main()
