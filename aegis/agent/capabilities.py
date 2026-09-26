"""Capability tokens for protected agent tools."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet


@dataclass(frozen=True)
class CapabilityToken:
    """Scoped permission grant for a single agent turn."""

    allowed_tools: FrozenSet[str]
    allow_secrets: bool = False
    allow_external_email: bool = False
    allow_network: bool = False
    max_tool_calls: int = 5
    notes: str = ""


DEFAULT_CAPABILITIES = CapabilityToken(
    allowed_tools=frozenset(
        {"search_docs", "read_file", "summarize", "call_api"}
    ),
    allow_secrets=False,
    allow_external_email=False,
    allow_network=True,
    max_tool_calls=5,
    notes="default enterprise agent policy",
)

# High-risk tools never granted by default
RESTRICTED_TOOLS = frozenset({"get_secret", "send_email", "write_file", "shell_exec"})


def can_invoke(token: CapabilityToken, tool_name: str, arguments: dict | None = None) -> tuple[bool, str]:
    arguments = arguments or {}
    if tool_name in RESTRICTED_TOOLS and tool_name not in token.allowed_tools:
        return False, f"capability deny: {tool_name} is restricted"
    if tool_name not in token.allowed_tools:
        return False, f"capability deny: {tool_name} not in token"
    if tool_name == "get_secret" and not token.allow_secrets:
        return False, "capability deny: secrets not permitted"
    if tool_name == "send_email" and not token.allow_external_email:
        to = str(arguments.get("to", ""))
        if to and not to.endswith("@corp.example"):
            return False, "capability deny: external email blocked"
    return True, "ok"
