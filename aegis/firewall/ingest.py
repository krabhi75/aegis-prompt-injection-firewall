"""Ingest & normalize multimodal inputs into ContentChunks."""

from __future__ import annotations

import base64
import io
import re
from email import message_from_string
from typing import Any, Optional

from bs4 import BeautifulSoup
from pypdf import PdfReader

from firewall.models import ContentChunk, InputSource, TrustLevel

# Sources that are never trusted as instructions
UNTRUSTED_SOURCES = {
    InputSource.PDF,
    InputSource.HTML,
    InputSource.EMAIL,
    InputSource.OCR,
    InputSource.IMAGE,
    InputSource.API,
    InputSource.WORD,
    InputSource.MARKDOWN,
    InputSource.CODE,
}


def ingest_text(text: str, source: InputSource = InputSource.USER) -> ContentChunk:
    trust = TrustLevel.TRUSTED if source == InputSource.USER else TrustLevel.UNTRUSTED
    # User message can still contain attacks, but provenance starts trusted;
    # static/twin layers still inspect it.
    if source in UNTRUSTED_SOURCES:
        trust = TrustLevel.UNTRUSTED
    return ContentChunk(text=text or "", source=source, trust=trust)


def ingest_pdf_bytes(data: bytes, filename: str = "doc.pdf") -> ContentChunk:
    reader = PdfReader(io.BytesIO(data))
    pages = []
    for i, page in enumerate(reader.pages):
        pages.append(f"[page {i + 1}]\n{(page.extract_text() or '')}")
    text = "\n".join(pages)
    return ContentChunk(
        text=text,
        source=InputSource.PDF,
        trust=TrustLevel.UNTRUSTED,
        metadata={"filename": filename, "pages": len(reader.pages)},
    )


def ingest_html(html: str, filename: str = "page.html") -> ContentChunk:
    from bs4 import Comment

    soup = BeautifulSoup(html, "html.parser")
    comment_texts = [str(c) for c in soup.find_all(string=lambda t: isinstance(t, Comment))]
    hidden: list[str] = []
    for tag in soup.find_all(attrs={"style": re.compile(r"display\s*:\s*none", re.I)}):
        hidden.append(tag.get_text(" ", strip=True))
    for tag in soup.find_all(["script", "meta"]):
        content = tag.get("content") or tag.string or ""
        if content:
            hidden.append(str(content))

    visible = soup.get_text("\n", strip=True)
    extras = "\n".join([*comment_texts, *hidden])
    text = visible
    if extras.strip():
        text = f"{visible}\n\n[hidden_channels]\n{extras}"
    return ContentChunk(
        text=text,
        source=InputSource.HTML,
        trust=TrustLevel.UNTRUSTED,
        metadata={"filename": filename, "hidden_channels": bool(extras.strip())},
    )


def ingest_email(raw: str, filename: str = "mail.eml") -> ContentChunk:
    msg = message_from_string(raw)
    parts = [
        f"From: {msg.get('From', '')}",
        f"Subject: {msg.get('Subject', '')}",
    ]
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain":
                payload = part.get_payload(decode=True)
                if isinstance(payload, bytes):
                    body += payload.decode("utf-8", errors="ignore")
                else:
                    body += str(payload or "")
            elif ctype == "text/html":
                payload = part.get_payload(decode=True)
                html = payload.decode("utf-8", errors="ignore") if isinstance(payload, bytes) else str(payload or "")
                body += "\n" + ingest_html(html).text
    else:
        payload = msg.get_payload(decode=True)
        if isinstance(payload, bytes):
            body = payload.decode("utf-8", errors="ignore")
        else:
            body = str(msg.get_payload() or "")
    parts.append(body)
    return ContentChunk(
        text="\n".join(parts),
        source=InputSource.EMAIL,
        trust=TrustLevel.UNTRUSTED,
        metadata={"filename": filename},
    )


def ingest_ocr_image(data: bytes, filename: str = "scan.png") -> ContentChunk:
    """Best-effort OCR; falls back to placeholder if tesseract unavailable."""
    text = ""
    try:
        from PIL import Image
        import shutil
        import subprocess

        img = Image.open(io.BytesIO(data))
        if shutil.which("tesseract"):
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            proc = subprocess.run(
                ["tesseract", "stdin", "stdout"],
                input=buf.getvalue(),
                capture_output=True,
                check=False,
            )
            text = proc.stdout.decode("utf-8", errors="ignore")
        else:
            # Offline-safe demo path: store note that OCR engine missing
            text = (
                "[ocr_unavailable] Image received. Install tesseract for live OCR. "
                "Demo corpus uses pre-extracted OCR text attachments instead."
            )
    except Exception as exc:  # noqa: BLE001
        text = f"[ocr_error] {exc}"
    return ContentChunk(
        text=text,
        source=InputSource.OCR,
        trust=TrustLevel.UNTRUSTED,
        metadata={"filename": filename},
    )


def ingest_api_json(payload: Any, filename: str = "api.json") -> ContentChunk:
    import json

    if isinstance(payload, (dict, list)):
        text = json.dumps(payload, indent=2)
    else:
        text = str(payload)
    return ContentChunk(
        text=text,
        source=InputSource.API,
        trust=TrustLevel.UNTRUSTED,
        metadata={"filename": filename},
    )


def ingest_attachment(item: dict[str, Any]) -> ContentChunk:
    source_str = str(item.get("source", "text")).lower()
    try:
        source = InputSource(source_str)
    except ValueError:
        source = InputSource.TEXT

    if item.get("text"):
        if source == InputSource.HTML:
            return ingest_html(item["text"], item.get("filename", "page.html"))
        if source == InputSource.EMAIL:
            return ingest_email(item["text"], item.get("filename", "mail.eml"))
        if source == InputSource.API:
            return ingest_api_json(item["text"], item.get("filename", "api.json"))
        return ingest_text(item["text"], source if source != InputSource.TEXT else InputSource.USER)

    b64 = item.get("content_b64") or item.get("content")
    if not b64:
        return ingest_text("", source)
    data = base64.b64decode(b64)
    filename = item.get("filename", "attachment")

    if source == InputSource.PDF or filename.lower().endswith(".pdf"):
        return ingest_pdf_bytes(data, filename)
    if source in {InputSource.IMAGE, InputSource.OCR} or filename.lower().endswith(
        (".png", ".jpg", ".jpeg", ".webp")
    ):
        return ingest_ocr_image(data, filename)
    if source == InputSource.HTML or filename.lower().endswith((".html", ".htm")):
        return ingest_html(data.decode("utf-8", errors="ignore"), filename)
    if source == InputSource.EMAIL or filename.lower().endswith(".eml"):
        return ingest_email(data.decode("utf-8", errors="ignore"), filename)

    return ingest_text(data.decode("utf-8", errors="ignore"), source)


def merge_chunks(user_message: str, attachments: Optional[list[dict[str, Any]]] = None) -> list[ContentChunk]:
    chunks = [ingest_text(user_message, InputSource.USER)]
    for item in attachments or []:
        chunks.append(ingest_attachment(item))
    return chunks
