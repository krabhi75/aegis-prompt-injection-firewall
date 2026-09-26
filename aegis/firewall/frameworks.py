"""Enterprise framework mappings for executive demos (OWASP / NIST / Accenture narrative)."""

from __future__ import annotations

from typing import Any

FRAMEWORKS: dict[str, Any] = {
    "claim": "F3/D2",
    "product": "Aegis Behavioral Twin Firewall",
    "owasp_llm_top10": [
        {
            "id": "LLM01",
            "name": "Prompt Injection",
            "aegis_controls": [
                "Provenance tagging of untrusted content",
                "Behavioral twin trajectory comparison",
                "Decode layer for obfuscated instructions",
            ],
            "status": "covered",
        },
        {
            "id": "LLM02",
            "name": "Sensitive Information Disclosure",
            "aegis_controls": [
                "Capability tokens deny get_secret by default",
                "Credential sink monitoring on tool outputs",
            ],
            "status": "covered",
        },
        {
            "id": "LLM06",
            "name": "Excessive Agency",
            "aegis_controls": [
                "Least-privilege capability tokens",
                "Gate blocks drifted high-risk tools before execution",
            ],
            "status": "covered",
        },
        {
            "id": "LLM07",
            "name": "System Prompt Leakage",
            "aegis_controls": [
                "Instruction-override detectors",
                "Role-lock + twin persona drift detection",
            ],
            "status": "covered",
        },
        {
            "id": "LLM09",
            "name": "Misinformation",
            "aegis_controls": [
                "Human quarantine band for ambiguous cases",
                "Full audit trail for decisions",
            ],
            "status": "partial",
        },
    ],
    "nist_ai_rmf": [
        {
            "function": "Govern",
            "aegis": "Policy console + capability tokens as enforceable runtime policy",
        },
        {
            "function": "Map",
            "aegis": "Nine attack-type taxonomy mapped to detectors and twin signals",
        },
        {
            "function": "Measure",
            "aegis": "Corpus precision/recall + live telemetry dashboard",
        },
        {
            "function": "Manage",
            "aegis": "ALLOW / QUARANTINE / BLOCK with analyst human-in-the-loop",
        },
    ],
    "enterprise_controls": [
        {
            "name": "Zero-trust content",
            "detail": "External PDF/HTML/email/OCR never enters the instruction channel",
        },
        {
            "name": "Behavioral containment",
            "detail": "Shadow agent plans compared before any tool runs",
        },
        {
            "name": "Least privilege",
            "detail": "Capability tokens fail closed on secrets, shell, external email",
        },
        {
            "name": "Human oversight",
            "detail": "Quarantine queue with approve/deny and analyst notes",
        },
        {
            "name": "Auditability",
            "detail": "Immutable decision log with twin plans and findings",
        },
    ],
    "talking_points": [
        "Classifiers answer 'does this look like a jailbreak?' — Aegis answers 'would this change what tools the agent calls?'",
        "Indirect injection in documents is the enterprise-critical failure mode for tool-using agents.",
        "Accenture clients deploying agents on email and PDFs need a runtime control plane, not a chatbot filter.",
    ],
}


ATTACK_PLAYBOOK: list[dict[str, Any]] = [
    {
        "id": "instruction_override",
        "name": "Instruction Override",
        "severity": "Attacker replaces system intent with new directives.",
        "enterprise_impact": "Policy bypass, unsafe tool use, brand/legal exposure.",
        "aegis_defense": "Static override patterns + twin conflict with trusted goals.",
        "demo": "inject",
    },
    {
        "id": "role_change",
        "name": "Role Change",
        "severity": "Forces unrestricted / DAN / admin personas.",
        "enterprise_impact": "Safety policy collapse across a session.",
        "aegis_defense": "Role-lock detectors + twin role_assumed drift.",
        "demo": "multi1",
    },
    {
        "id": "secret_extraction",
        "name": "Secret Extraction",
        "severity": "Coerces vault or credential disclosure.",
        "enterprise_impact": "API key / password theft.",
        "aegis_defense": "Twin get_secret drift + capability deny + sink monitor.",
        "demo": "inject",
    },
    {
        "id": "tool_abuse",
        "name": "Tool Abuse",
        "severity": "Triggers shell, write, or external email tools.",
        "enterprise_impact": "RCE-class impact or data exfiltration.",
        "aegis_defense": "Capability tokens + drifted-tool detection.",
        "demo": "multi2",
    },
    {
        "id": "credential_theft",
        "name": "Credential Theft",
        "severity": "Targets named secrets and exfil channels.",
        "enterprise_impact": "Cloud account compromise.",
        "aegis_defense": "Credential pattern detectors + email sink alerts.",
        "demo": "inject",
    },
    {
        "id": "context_poisoning",
        "name": "Context Poisoning",
        "severity": "Hides instructions inside retrieved/API context.",
        "enterprise_impact": "Silent policy override via RAG/tools.",
        "aegis_defense": "Provenance quarantine of untrusted spans.",
        "demo": "encoded",
    },
    {
        "id": "multi_step",
        "name": "Multi-Step Jailbreak",
        "severity": "Softens policy over turns, then weaponizes.",
        "enterprise_impact": "Bypasses single-turn filters.",
        "aegis_defense": "Session risk memory across turns.",
        "demo": "multi2",
    },
    {
        "id": "encoded",
        "name": "Encoded Instructions",
        "severity": "Obfuscates payloads (base64/hex/rot13).",
        "enterprise_impact": "Evades keyword classifiers.",
        "aegis_defense": "Decode layer before twin/static analysis.",
        "demo": "encoded",
    },
    {
        "id": "indirect",
        "name": "Indirect Prompt Injection",
        "severity": "Malicious instructions live in documents attackers control.",
        "enterprise_impact": "The #1 agent deployment risk for enterprises.",
        "aegis_defense": "Untrusted-doc twin: raw plan diverges from trusted plan.",
        "demo": "inject",
    },
]
