"""Mutable runtime policy for capability tokens (demo console)."""

from __future__ import annotations

from copy import deepcopy
from threading import Lock
from typing import Any

from agent.capabilities import DEFAULT_CAPABILITIES, CapabilityToken, RESTRICTED_TOOLS
from agent.tools import TOOL_SCHEMAS

_lock = Lock()
_policy: dict[str, Any] = {
    "allowed_tools": sorted(DEFAULT_CAPABILITIES.allowed_tools),
    "allow_secrets": DEFAULT_CAPABILITIES.allow_secrets,
    "allow_external_email": DEFAULT_CAPABILITIES.allow_external_email,
    "allow_network": DEFAULT_CAPABILITIES.allow_network,
    "max_tool_calls": DEFAULT_CAPABILITIES.max_tool_calls,
    "notes": DEFAULT_CAPABILITIES.notes,
}


def get_policy() -> dict[str, Any]:
    with _lock:
        data = deepcopy(_policy)
    data["restricted_tools"] = sorted(RESTRICTED_TOOLS)
    data["available_tools"] = sorted(TOOL_SCHEMAS.keys())
    data["token_preview"] = describe_token(token_from_policy(data))
    return data


def update_policy(patch: dict[str, Any]) -> dict[str, Any]:
    with _lock:
        if "allowed_tools" in patch and isinstance(patch["allowed_tools"], list):
            _policy["allowed_tools"] = sorted({str(t) for t in patch["allowed_tools"]})
        for key in ("allow_secrets", "allow_external_email", "allow_network"):
            if key in patch:
                _policy[key] = bool(patch[key])
        if "max_tool_calls" in patch:
            _policy["max_tool_calls"] = max(1, min(20, int(patch["max_tool_calls"])))
        if "notes" in patch:
            _policy["notes"] = str(patch["notes"])[:240]
        snapshot = deepcopy(_policy)
    return get_policy() if snapshot else get_policy()


def reset_policy() -> dict[str, Any]:
    with _lock:
        _policy.clear()
        _policy.update(
            {
                "allowed_tools": sorted(DEFAULT_CAPABILITIES.allowed_tools),
                "allow_secrets": DEFAULT_CAPABILITIES.allow_secrets,
                "allow_external_email": DEFAULT_CAPABILITIES.allow_external_email,
                "allow_network": DEFAULT_CAPABILITIES.allow_network,
                "max_tool_calls": DEFAULT_CAPABILITIES.max_tool_calls,
                "notes": DEFAULT_CAPABILITIES.notes,
            }
        )
    return get_policy()


def token_from_policy(policy: dict[str, Any] | None = None) -> CapabilityToken:
    p = policy or get_policy()
    return CapabilityToken(
        allowed_tools=frozenset(p.get("allowed_tools") or []),
        allow_secrets=bool(p.get("allow_secrets")),
        allow_external_email=bool(p.get("allow_external_email")),
        allow_network=bool(p.get("allow_network")),
        max_tool_calls=int(p.get("max_tool_calls") or 5),
        notes=str(p.get("notes") or ""),
    )


def describe_token(token: CapabilityToken) -> dict[str, Any]:
    return {
        "allowed_tools": sorted(token.allowed_tools),
        "allow_secrets": token.allow_secrets,
        "allow_external_email": token.allow_external_email,
        "allow_network": token.allow_network,
        "max_tool_calls": token.max_tool_calls,
        "notes": token.notes,
        "fail_closed_restricted": sorted(RESTRICTED_TOOLS - token.allowed_tools),
    }
