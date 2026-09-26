"""Decode / de-obfuscation layer for encoded prompt injections."""

from __future__ import annotations

import base64
import binascii
import re
import urllib.parse
from dataclasses import dataclass

HOMOGLYPH_MAP = str.maketrans(
    {
        "а": "a",  # cyrillic
        "е": "e",
        "о": "o",
        "р": "p",
        "с": "c",
        "у": "y",
        "х": "x",
        "і": "i",
        "Ⅰ": "I",
        "ⅼ": "l",
    }
)

B64_RE = re.compile(r"(?<![A-Za-z0-9+/=])([A-Za-z0-9+/]{16,}={0,2})(?![A-Za-z0-9+/=])")
HEX_RE = re.compile(r"(?:\\x[0-9a-fA-F]{2}){4,}|(?:[0-9a-fA-F]{2}\s*){8,}")
URL_RE = re.compile(r"(?:%[0-9a-fA-F]{2}){4,}")
ROT_HINT = re.compile(r"rot13|rot-13", re.I)


@dataclass
class DecodeResult:
    original: str
    decoded: str
    transformations: list[str]
    suspicious: bool


def _try_b64(s: str) -> tuple[str, bool]:
    try:
        pad = "=" * ((4 - len(s) % 4) % 4)
        raw = base64.b64decode(s + pad, validate=False)
        text = raw.decode("utf-8", errors="strict")
        if any(c.isalpha() for c in text) and text.isprintable():
            return text, True
    except Exception:  # noqa: BLE001
        pass
    return s, False


def _try_hex(s: str) -> tuple[str, bool]:
    cleaned = re.sub(r"\\x|\s+", "", s)
    if len(cleaned) % 2:
        return s, False
    try:
        raw = binascii.unhexlify(cleaned)
        text = raw.decode("utf-8", errors="strict")
        if text.isprintable():
            return text, True
    except Exception:  # noqa: BLE001
        pass
    return s, False


def _rot13(s: str) -> str:
    out = []
    for ch in s:
        if "a" <= ch <= "z":
            out.append(chr((ord(ch) - 97 + 13) % 26 + 97))
        elif "A" <= ch <= "Z":
            out.append(chr((ord(ch) - 65 + 13) % 26 + 65))
        else:
            out.append(ch)
    return "".join(out)


def decode_text(text: str) -> DecodeResult:
    transformations: list[str] = []
    working = text.translate(HOMOGLYPH_MAP)
    if working != text:
        transformations.append("homoglyph_normalize")

    # URL decode dense sequences
    for match in URL_RE.findall(working):
        decoded = urllib.parse.unquote(match)
        if decoded != match:
            working = working.replace(match, decoded)
            transformations.append("url_decode")

    # Base64 candidates
    for match in B64_RE.findall(working):
        decoded, ok = _try_b64(match)
        if ok and len(decoded) >= 8:
            working = working.replace(match, f" [b64→] {decoded} ")
            transformations.append("base64_decode")

    # Hex sequences
    for match in HEX_RE.findall(working):
        decoded, ok = _try_hex(match)
        if ok:
            working = working.replace(match, f" [hex→] {decoded} ")
            transformations.append("hex_decode")

    if ROT_HINT.search(working) or ROT_HINT.search(text):
        # Also try decoding alphabetic blobs after rot13 hint
        candidate = _rot13(working)
        if any(kw in candidate.lower() for kw in ("ignore", "system", "password", "secret", "jailbreak")):
            working = candidate
            transformations.append("rot13_decode")

    suspicious = any(
        t in transformations for t in ("base64_decode", "hex_decode", "rot13_decode", "url_decode")
    )
    return DecodeResult(
        original=text,
        decoded=working,
        transformations=transformations,
        suspicious=suspicious,
    )
