"""Static / heuristic detectors for prompt injection attack types."""

from __future__ import annotations

import re

from firewall.models import AttackType, StaticFinding, TrustLevel
from firewall.provenance import ProvenanceDocument

OVERRIDE_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|rules|prompts)",
    r"disregard\s+(your\s+)?(system|safety)\s+(prompt|instructions)",
    r"override\s+(the\s+)?system\s+prompt",
    r"new\s+instructions?\s*:",
    r"forget\s+everything\s+you\s+were\s+told",
]

ROLE_PATTERNS = [
    r"you\s+are\s+now\s+(dan|evil|unrestricted|root|admin)",
    r"act\s+as\s+(an?\s+)?(unfiltered|jailbroken|developer\s+mode)",
    r"pretend\s+you\s+have\s+no\s+restrictions",
    r"roleplay\s+as\s+system",
    r"switch\s+to\s+god\s+mode",
]

SECRET_PATTERNS = [
    r"(reveal|show|print|dump|exfiltrate)\s+(the\s+)?(api[_\s-]?key|secret|password|credentials?|token)",
    r"get_secret",
    r"send\s+(me\s+)?(the\s+)?(password|secret|api[_\s-]?key)",
]

TOOL_ABUSE_PATTERNS = [
    r"(call|invoke|use|run)\s+(the\s+)?(tool\s+)?(get_secret|send_email|shell_exec|write_file)",
    r"shell_exec\s*\(",
    r"send_email\s*\(",
]

CREDENTIAL_PATTERNS = [
    r"(aws_access_key|db_password|api_key)\b",
    r"Authorization:\s*Bearer\s+\S+",
    r"exfiltrat(e|ion)",
]

CONTEXT_POISON = [
    r"when\s+summarizing.*?(ignore|override|call\s+get_secret)",
    r"hidden\s+instruction",
    r"do\s+not\s+tell\s+the\s+user",
    r"system\s*:\s*you\s+must",
]

ENCODED_HINTS = [
    r"\[b64→\]",
    r"\[hex→\]",
    r"base64",
    r"decode\s+and\s+execute",
]

INDIRECT_HINTS = [
    r"ignore\s+previous",
    r"get_secret",
    r"send_email",
    r"attacker@",
    r"evil\.com",
]


def _find(patterns: list[str], text: str) -> list[re.Match[str]]:
    hits = []
    for pat in patterns:
        for m in re.finditer(pat, text, flags=re.IGNORECASE | re.DOTALL):
            hits.append(m)
    return hits


def run_static_detectors(doc: ProvenanceDocument, decode_suspicious: bool = False) -> list[StaticFinding]:
    findings: list[StaticFinding] = []
    full = doc.raw_text
    untrusted = "\n".join(doc.untrusted_spans)

    def add(attack: AttackType, conf: float, evidence: str, span: str = "") -> None:
        findings.append(StaticFinding(attack_type=attack, confidence=conf, evidence=evidence, span=span[:200]))

    for m in _find(OVERRIDE_PATTERNS, full):
        add(AttackType.INSTRUCTION_OVERRIDE, 0.9, "instruction override phrasing", m.group(0))

    for m in _find(ROLE_PATTERNS, full):
        add(AttackType.ROLE_CHANGE, 0.88, "role/persona swap attempt", m.group(0))

    for m in _find(SECRET_PATTERNS, full):
        add(AttackType.SECRET_EXTRACTION, 0.92, "secret extraction intent", m.group(0))

    for m in _find(TOOL_ABUSE_PATTERNS, full):
        add(AttackType.TOOL_ABUSE, 0.9, "high-risk tool invocation request", m.group(0))

    for m in _find(CREDENTIAL_PATTERNS, full):
        add(AttackType.CREDENTIAL_THEFT, 0.85, "credential identifiers / exfil language", m.group(0))

    for m in _find(CONTEXT_POISON, full):
        add(AttackType.CONTEXT_POISONING, 0.87, "poisoned context instruction", m.group(0))

    if decode_suspicious or _find(ENCODED_HINTS, full):
        add(AttackType.ENCODED_INSTRUCTIONS, 0.8, "encoded/obfuscated instruction channel", "decode layer")

    # Indirect: malicious instructions living in untrusted attachments
    if untrusted.strip() and _find(INDIRECT_HINTS, untrusted):
        add(
            AttackType.INDIRECT_PROMPT_INJECTION,
            0.93,
            "malicious instructions embedded in untrusted document/HTML/email/OCR",
            untrusted[:200],
        )

    # Deduplicate by attack type keeping max confidence
    best: dict[AttackType, StaticFinding] = {}
    for f in findings:
        if f.attack_type not in best or f.confidence > best[f.attack_type].confidence:
            best[f.attack_type] = f
    return list(best.values())
