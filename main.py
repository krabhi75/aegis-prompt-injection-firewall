"""Vercel / local FastAPI entrypoint for Aegis.

Vercel detects FastAPI apps via a root `main.py` exporting `app`.
Streamlit is local-only; this entry serves the web demo UI from /public.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AEGIS = ROOT / "aegis"
if str(AEGIS) not in sys.path:
    sys.path.insert(0, str(AEGIS))

from fastapi.responses import FileResponse, RedirectResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

from app.main import app  # noqa: E402  # aegis/app/main.py

PUBLIC = ROOT / "public"


@app.get("/", include_in_schema=False)
def demo_ui() -> FileResponse:
    return FileResponse(PUBLIC / "index.html")


@app.get("/favicon.ico", include_in_schema=False)
def favicon_ico() -> RedirectResponse:
    return RedirectResponse(url="/static/favicon.svg", status_code=307)


@app.get("/favicon.svg", include_in_schema=False)
def favicon_svg() -> FileResponse:
    return FileResponse(PUBLIC / "favicon.svg", media_type="image/svg+xml")


@app.get("/apple-touch-icon.png", include_in_schema=False)
@app.get("/apple-touch-icon.svg", include_in_schema=False)
def apple_touch() -> FileResponse:
    return FileResponse(PUBLIC / "apple-touch-icon.svg", media_type="image/svg+xml")


if PUBLIC.exists():
    app.mount("/static", StaticFiles(directory=str(PUBLIC)), name="static")
