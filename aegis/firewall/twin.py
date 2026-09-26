"""Behavioral twin: compare trusted vs raw agent plans."""

from __future__ import annotations

from agent.planner import plan_from_text
from firewall.models import TwinResult


HIGH_RISK_TOOLS = {"get_secret", "send_email", "shell_exec", "write_file"}


def run_behavioral_twin(raw_text: str, sanitized_text: str) -> TwinResult:
    trusted_plan = plan_from_text(sanitized_text, mode="trusted")
    raw_plan = plan_from_text(raw_text, mode="raw")

    trusted_names = {t.name for t in trusted_plan.tools}
    raw_names = {t.name for t in raw_plan.tools}
    drifted = sorted(raw_names - trusted_names)

    # Argument / destination drift for shared tools
    trust_args = {(t.name, tuple(sorted(t.arguments.items()))) for t in trusted_plan.tools}
    raw_args = {(t.name, tuple(sorted(t.arguments.items()))) for t in raw_plan.tools}
    arg_drift = len(raw_args - trust_args)

    drift = 0.0
    if drifted:
        drift += 0.45
        if any(t in HIGH_RISK_TOOLS for t in drifted):
            drift += 0.35
    if arg_drift:
        drift += min(0.2, 0.05 * arg_drift)
    if raw_plan.role_assumed and raw_plan.role_assumed != trusted_plan.role_assumed:
        drift += 0.25
    # External email destination is always drift
    for t in raw_plan.tools:
        if t.name == "send_email":
            to = str(t.arguments.get("to", ""))
            if to and not to.endswith("@corp.example"):
                drift = max(drift, 0.9)
                if "send_email" not in drifted:
                    drifted.append("send_email")

    drift = min(1.0, drift)
    if drift >= 0.5:
        explanation = (
            f"Behavioral twin detected plan drift. "
            f"Trusted tools={sorted(trusted_names)}; raw tools={sorted(raw_names)}; "
            f"drifted={drifted}."
        )
    elif drift > 0:
        explanation = f"Minor twin divergence (score={drift:.2f}). drifted={drifted}"
    else:
        explanation = "Trusted and raw plans align; no behavioral drift."

    return TwinResult(
        trusted_plan=trusted_plan,
        raw_plan=raw_plan,
        drift_score=drift,
        drifted_tools=drifted,
        explanation=explanation,
    )
