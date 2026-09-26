"""Risk engine and allow / quarantine / block gate."""

from __future__ import annotations

from firewall import audit
from firewall.models import (
    AttackType,
    FirewallVerdict,
    GateDecision,
    StaticFinding,
    TwinResult,
)


BLOCK_THRESHOLD = 0.75
QUARANTINE_THRESHOLD = 0.45


def compute_risk(
    findings: list[StaticFinding],
    twin: TwinResult,
    session_id: str,
) -> tuple[float, list[AttackType], str]:
    score = 0.0
    attacks: list[AttackType] = []

    for f in findings:
        score = max(score, f.confidence * 0.85)
        if f.attack_type not in attacks:
            attacks.append(f.attack_type)

    if twin.drift_score >= 0.5:
        score = max(score, 0.55 + twin.drift_score * 0.4)
        if AttackType.TOOL_ABUSE not in attacks and twin.drifted_tools:
            attacks.append(AttackType.TOOL_ABUSE)
        if any(t in twin.drifted_tools for t in ("get_secret", "send_email")):
            if AttackType.SECRET_EXTRACTION not in attacks:
                attacks.append(AttackType.SECRET_EXTRACTION)
            if AttackType.INDIRECT_PROMPT_INJECTION not in attacks:
                # Often twin drift on docs == indirect injection
                attacks.append(AttackType.INDIRECT_PROMPT_INJECTION)

    session = audit.get_session_risk(session_id)
    session_risk = float(session["risk_score"])
    if session_risk >= 0.35 and score >= 0.35:
        score = min(1.0, score + 0.2)
        if AttackType.MULTI_STEP_JAILBREAK not in attacks:
            attacks.append(AttackType.MULTI_STEP_JAILBREAK)

    # Soft roleplay alone is medium
    if any(f.attack_type == AttackType.ROLE_CHANGE for f in findings) and twin.drift_score < 0.5:
        score = max(score, 0.5)

    explanation_parts = []
    if findings:
        explanation_parts.append(
            "Static: " + ", ".join(f"{f.attack_type.value} ({f.confidence:.2f})" for f in findings)
        )
    explanation_parts.append(twin.explanation)
    if session_risk:
        explanation_parts.append(f"Session risk carry={session_risk:.2f}")

    return min(1.0, score), attacks, " | ".join(explanation_parts)


def decide_gate(risk_score: float) -> GateDecision:
    if risk_score >= BLOCK_THRESHOLD:
        return GateDecision.BLOCK
    if risk_score >= QUARANTINE_THRESHOLD:
        return GateDecision.QUARANTINE
    return GateDecision.ALLOW


def build_verdict(
    session_id: str,
    findings: list[StaticFinding],
    twin: TwinResult,
    raw_text: str,
    sanitized_text: str,
) -> FirewallVerdict:
    risk, attacks, explanation = compute_risk(findings, twin, session_id)
    decision = decide_gate(risk)

    # Update session risk memory
    if decision == GateDecision.ALLOW:
        # Slight decay
        audit.bump_session_risk(session_id, -0.05, "allow_decay")
    elif decision == GateDecision.QUARANTINE:
        audit.bump_session_risk(session_id, 0.2, "quarantine")
    else:
        audit.bump_session_risk(session_id, 0.35, "block")

    return FirewallVerdict(
        decision=decision,
        risk_score=risk,
        attack_types=attacks or [AttackType.NONE],
        findings=findings,
        twin=twin,
        explanation=explanation,
        session_id=session_id,
        sanitized_text=sanitized_text,
        raw_text=raw_text,
    )
