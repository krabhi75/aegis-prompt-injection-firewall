"""Aegis shared models and enums."""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class TrustLevel(str, Enum):
    TRUSTED = "trusted"
    UNTRUSTED = "untrusted"


class AttackType(str, Enum):
    INSTRUCTION_OVERRIDE = "Instruction Override"
    ROLE_CHANGE = "Role Change"
    SECRET_EXTRACTION = "Secret Extraction"
    TOOL_ABUSE = "Tool Abuse"
    CREDENTIAL_THEFT = "Credential Theft"
    CONTEXT_POISONING = "Context Poisoning"
    MULTI_STEP_JAILBREAK = "Multi-Step Jailbreak"
    ENCODED_INSTRUCTIONS = "Encoded Instructions"
    INDIRECT_PROMPT_INJECTION = "Indirect Prompt Injection"
    NONE = "None"


class GateDecision(str, Enum):
    ALLOW = "allow"
    QUARANTINE = "quarantine"
    BLOCK = "block"


class InputSource(str, Enum):
    USER = "user"
    PDF = "pdf"
    HTML = "html"
    EMAIL = "email"
    MARKDOWN = "markdown"
    WORD = "word"
    API = "api"
    OCR = "ocr"
    IMAGE = "image"
    CODE = "code"
    TEXT = "text"


class ContentChunk(BaseModel):
    text: str
    source: InputSource
    trust: TrustLevel
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    rationale: str = ""


class AgentPlan(BaseModel):
    tools: list[ToolCall] = Field(default_factory=list)
    role_assumed: Optional[str] = None
    notes: str = ""


class StaticFinding(BaseModel):
    attack_type: AttackType
    confidence: float
    evidence: str
    span: str = ""


class TwinResult(BaseModel):
    trusted_plan: AgentPlan
    raw_plan: AgentPlan
    drift_score: float
    drifted_tools: list[str] = Field(default_factory=list)
    explanation: str = ""


class FirewallVerdict(BaseModel):
    decision: GateDecision
    risk_score: float
    attack_types: list[AttackType] = Field(default_factory=list)
    findings: list[StaticFinding] = Field(default_factory=list)
    twin: Optional[TwinResult] = None
    explanation: str = ""
    session_id: str = ""
    sanitized_text: str = ""
    raw_text: str = ""


class ScanRequest(BaseModel):
    session_id: str = "default"
    user_message: str = ""
    attachments: list[dict[str, Any]] = Field(default_factory=list)
    # attachments items: {source, content_b64 or text, filename}


class ScanResponse(BaseModel):
    verdict: FirewallVerdict
    agent_reply: Optional[str] = None
    tool_results: list[dict[str, Any]] = Field(default_factory=list)


class QuarantineAction(BaseModel):
    event_id: int
    action: str  # approve | deny
    analyst_note: str = ""
