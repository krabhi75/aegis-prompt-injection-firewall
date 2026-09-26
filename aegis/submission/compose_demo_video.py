"""Capture live demo screenshots and compose the 4-minute submission video."""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
ASSETS = Path(__file__).resolve().parent / "video_assets"
FRAMES = ASSETS / "frames"
OUT_VIDEO = Path(__file__).resolve().parent / "Aegis_Guard_Demo_4min.mp4"
AUDIO = ASSETS / "narration_naveen.mp3"
BASE = "https://aegis-prompt-injection-firewall.vercel.app"

# Brand
INK = (11, 31, 26)
ACCENT = (15, 118, 110)
BG = (244, 247, 246)
WHITE = (255, 255, 255)
MUTED = (91, 111, 104)


def _font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for c in candidates:
        p = Path(c)
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                continue
    return ImageFont.load_default()


def title_card(path: Path, title: str, subtitle: str = "", duration_hint: str = "") -> None:
    img = Image.new("RGB", (1920, 1080), INK)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 920, 1920, 1080], fill=ACCENT)
    d.text((96, 320), "AEGIS GUARD", font=_font(72, True), fill=WHITE)
    d.text((96, 420), title, font=_font(44, True), fill=(154, 230, 197))
    if subtitle:
        d.text((96, 500), subtitle, font=_font(28), fill=(197, 210, 204))
    if duration_hint:
        d.text((96, 960), duration_hint, font=_font(26, True), fill=WHITE)
    img.save(path, quality=95)


def end_card(path: Path) -> None:
    img = Image.new("RGB", (1920, 1080), INK)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 12, 1080], fill=ACCENT)
    d.text((96, 360), "Everyone else ships a classifier.", font=_font(40), fill=(197, 210, 204))
    d.text((96, 430), "We ship a twin.", font=_font(56, True), fill=WHITE)
    d.text((96, 560), "Live  ·  aegis-prompt-injection-firewall.vercel.app", font=_font(26), fill=(154, 230, 197))
    d.text((96, 620), "Claim  ·  F3 / D2", font=_font(26), fill=(154, 230, 197))
    d.text((96, 700), "Thank you.", font=_font(36, True), fill=WHITE)
    img.save(path, quality=95)


def make_section_card(path: Path, label: str, title: str) -> None:
    img = Image.new("RGB", (1920, 1080), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 1920, 8], fill=ACCENT)
    d.text((96, 400), label.upper(), font=_font(22, True), fill=ACCENT)
    d.text((96, 450), title, font=_font(48, True), fill=INK)
    img.save(path, quality=95)


def fit_screenshot(src: Path, dest: Path, caption: str = "") -> None:
    raw = Image.open(src).convert("RGB")
    canvas = Image.new("RGB", (1920, 1080), BG)
    # letterbox fit
    scale = min(1920 / raw.width, (1000 if caption else 1080) / raw.height)
    nw, nh = int(raw.width * scale), int(raw.height * scale)
    resized = raw.resize((nw, nh), Image.Resampling.LANCZOS)
    x, y = (1920 - nw) // 2, (1000 - nh) // 2 if caption else (1080 - nh) // 2
    canvas.paste(resized, (x, y))
    if caption:
        d = ImageDraw.Draw(canvas)
        d.rectangle([0, 1000, 1920, 1080], fill=INK)
        d.text((48, 1024), caption, font=_font(24, True), fill=WHITE)
    canvas.save(dest, quality=95)


def capture_via_api_and_browser() -> list[tuple[Path, float]]:
    """Return list of (frame_path, duration_seconds) synced roughly to narration."""
    FRAMES.mkdir(parents=True, exist_ok=True)
    frames: list[tuple[Path, float]] = []

    # Title cards (no browser required)
    t0 = FRAMES / "t00_title.png"
    title_card(t0, "Behavioral Twin Prompt Injection Firewall", "ET AI Hackathon · Problem 2 · Solo", "4-minute product demo")
    frames.append((t0, 8.0))

    t1 = FRAMES / "t01_problem.png"
    make_section_card(t1, "01  Problem", "Indirect injection in enterprise agents")
    frames.append((t1, 12.0))

    t2 = FRAMES / "t02_insight.png"
    make_section_card(t2, "02  Insight", "Not a classifier — a behavioral twin")
    frames.append((t2, 14.0))

    # Browser screenshots of live product
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        subprocess.run(
            [str(ROOT / ".venv/bin/pip"), "install", "-q", "playwright"],
            check=False,
        )
        subprocess.run([str(ROOT / ".venv/bin/python"), "-m", "playwright", "install", "chromium"], check=False)
        from playwright.sync_api import sync_playwright

    shots: list[tuple[str, str, float]] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(BASE, wait_until="networkidle", timeout=60000)
        time.sleep(1.2)
        hero = FRAMES / "s00_hero.png"
        page.screenshot(path=str(hero), full_page=False)
        shots.append((str(hero), "Live product — Aegis Guard on Vercel", 10.0))

        # Benign
        page.click('button[data-scenario="benign"]')
        page.wait_for_timeout(3500)
        b = FRAMES / "s01_benign.png"
        page.screenshot(path=str(b), full_page=False)
        shots.append((str(b), "Benign PDF → ALLOW", 12.0))

        # Inject
        page.click('button[data-scenario="inject"]')
        page.wait_for_timeout(4000)
        inj = FRAMES / "s02_inject.png"
        page.screenshot(path=str(inj), full_page=False)
        shots.append((str(inj), "Indirect injection → BLOCK + twin drift", 18.0))

        # Encoded
        page.click('button[data-scenario="encoded"]')
        page.wait_for_timeout(3500)
        enc = FRAMES / "s03_encoded.png"
        page.screenshot(path=str(enc), full_page=False)
        shots.append((str(enc), "Encoded HTML jailbreak → BLOCK", 12.0))

        # Multi-step
        page.click('button[data-scenario="multi1"]')
        page.wait_for_timeout(3000)
        page.click('button[data-scenario="multi2"]')
        page.wait_for_timeout(3500)
        multi = FRAMES / "s04_multi.png"
        page.screenshot(path=str(multi), full_page=False)
        shots.append((str(multi), "Multi-step jailbreak → session escalation", 14.0))

        # Command center
        page.click('.tab[data-view="command"]')
        page.wait_for_timeout(800)
        page.click("#refreshTelemetry")
        page.wait_for_timeout(4000)
        cmd = FRAMES / "s05_command.png"
        page.screenshot(path=str(cmd), full_page=False)
        shots.append((str(cmd), "Command Center — D2 corpus reliability", 14.0))

        # Frameworks
        page.click('.tab[data-view="frameworks"]')
        page.wait_for_timeout(2500)
        fw = FRAMES / "s06_frameworks.png"
        page.screenshot(path=str(fw), full_page=False)
        shots.append((str(fw), "OWASP LLM Top 10 · NIST AI RMF", 12.0))

        # Policy
        page.click('.tab[data-view="policy"]')
        page.wait_for_timeout(2000)
        pol = FRAMES / "s07_policy.png"
        page.screenshot(path=str(pol), full_page=False)
        shots.append((str(pol), "Capability policy — least privilege", 10.0))

        browser.close()

    for i, (src, caption, dur) in enumerate(shots):
        dest = FRAMES / f"f{i:02d}.png"
        fit_screenshot(Path(src), dest, caption)
        frames.append((dest, dur))

    claim = FRAMES / "t08_claim.png"
    make_section_card(claim, "09  Claim", "F3 / D2 — nine attacks · proven reliability")
    frames.append((claim, 10.0))

    end = FRAMES / "t09_end.png"
    end_card(end)
    frames.append((end, 12.0))

    return frames


def compose(frames: list[tuple[Path, float]]) -> Path:
    # Build concat demuxer with durations; loop last frame to match audio length
    audio_dur = float(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(AUDIO)],
            text=True,
        ).strip()
    )
    total = sum(d for _, d in frames)
    if total < audio_dur and frames:
        # extend final card
        last_path, last_d = frames[-1]
        frames[-1] = (last_path, last_d + (audio_dur - total) + 0.5)

    list_file = ASSETS / "frames.txt"
    lines = []
    for path, dur in frames:
        lines.append(f"file '{path.resolve()}'")
        lines.append(f"duration {dur:.3f}")
    # concat demuxer requires repeating last file without duration
    lines.append(f"file '{frames[-1][0].resolve()}'")
    list_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # First pass: slideshow video
    raw_video = ASSETS / "slideshow.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", str(list_file),
            "-vf", "fps=30,format=yuv420p",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            str(raw_video),
        ],
        check=True,
        capture_output=True,
    )

    # Mux with audio, trim/pad to audio length
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(raw_video),
            "-i", str(AUDIO),
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            str(OUT_VIDEO),
        ],
        check=True,
        capture_output=True,
    )
    return OUT_VIDEO


def main() -> None:
    if not AUDIO.exists():
        raise SystemExit(f"Missing audio: {AUDIO}")
    print("Capturing frames…")
    frames = capture_via_api_and_browser()
    print(f"{len(frames)} frames — composing video…")
    out = compose(frames)
    dur = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(out)],
        text=True,
    ).strip()
    print(f"OK {out} duration={dur}s size={out.stat().st_size}")


if __name__ == "__main__":
    main()
