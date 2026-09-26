"""Protected agent that only runs when firewall allows."""

from __future__ import annotations

from typing import Any, Optional

from agent.capabilities import DEFAULT_CAPABILITIES, CapabilityToken
from agent.planner import plan_from_text
from agent.tools import ToolRuntime
from firewall.models import FirewallVerdict, GateDecision


class ProtectedAgent:
    def __init__(self, token: CapabilityToken | None = None) -> None:
        self.token = token or DEFAULT_CAPABILITIES

    def run(self, verdict: FirewallVerdict, user_message: str) -> dict[str, Any]:
        if verdict.decision == GateDecision.BLOCK:
            return {
                "reply": "Blocked by Aegis firewall. Malicious instructions were neutralized.",
                "tool_results": [],
                "denied": True,
            }
        if verdict.decision == GateDecision.QUARANTINE:
            return {
                "reply": "Held in quarantine for human analyst review. No tools executed.",
                "tool_results": [],
                "denied": True,
            }

        # Execute only the trusted plan
        plan = (
            verdict.twin.trusted_plan
            if verdict.twin
            else plan_from_text(verdict.sanitized_text, mode="trusted")
        )
        runtime = ToolRuntime(token=self.token)
        results = []
        for call in plan.tools[: self.token.max_tool_calls]:
            # Prefer sanitized content for summarize
            args = dict(call.arguments)
            if call.name == "summarize" and verdict.sanitized_text:
                args["text"] = user_message + "\n" + verdict.sanitized_text[:1500]
            tr = runtime.invoke(call.name, args)
            results.append(
                {
                    "name": tr.name,
                    "ok": tr.ok,
                    "denied": tr.denied,
                    "deny_reason": tr.deny_reason,
                    "output": tr.output,
                    "sink_alert": tr.sink_alert,
                }
            )

        if runtime.sink_events:
            return {
                "reply": "Execution halted: credential/exfil sink detected post-gate.",
                "tool_results": results,
                "denied": True,
                "sink_events": runtime.sink_events,
            }

        summaries = [str(r["output"]) for r in results if r["ok"] and r["name"] == "summarize"]
        if summaries:
            reply = summaries[0]
        elif results:
            reply = "Agent completed allowed tools:\n" + "\n".join(
                f"- {r['name']}: {r['output']}" for r in results if r["ok"]
            )
        else:
            reply = "Request allowed. No tool calls required."

        return {"reply": reply, "tool_results": results, "denied": False}
