"""Aegis FastAPI application."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent.protected import ProtectedAgent
from firewall import audit
from firewall.engine import AegisFirewall
from firewall.models import GateDecision, QuarantineAction, ScanRequest, ScanResponse

audit.init_db()

app = FastAPI(
    title="Aegis Prompt Injection Firewall",
    description="Behavioral twin firewall for ET AI Hackathon Problem 2",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

firewall = AegisFirewall()
agent = ProtectedAgent()


class Health(BaseModel):
    status: str = "ok"
    product: str = "Aegis"
    claim: str = "F3/D2"


@app.get("/health", response_model=Health)
def health() -> Health:
    return Health()


@app.post("/scan", response_model=ScanResponse)
def scan(req: ScanRequest) -> ScanResponse:
    verdict = firewall.scan_request(req)
    agent_out: dict[str, Any] = {"reply": None, "tool_results": []}
    if verdict.decision == GateDecision.ALLOW:
        agent_out = agent.run(verdict, req.user_message)
    elif verdict.decision == GateDecision.QUARANTINE:
        agent_out = agent.run(verdict, req.user_message)
    else:
        agent_out = agent.run(verdict, req.user_message)
    return ScanResponse(
        verdict=verdict,
        agent_reply=agent_out.get("reply"),
        tool_results=agent_out.get("tool_results") or [],
    )


@app.post("/scan/upload")
async def scan_upload(
    session_id: str = Form("default"),
    user_message: str = Form(""),
    source: str = Form("pdf"),
    file: UploadFile = File(...),
) -> ScanResponse:
    import base64

    data = await file.read()
    b64 = base64.b64encode(data).decode("ascii")
    req = ScanRequest(
        session_id=session_id,
        user_message=user_message,
        attachments=[{"source": source, "content_b64": b64, "filename": file.filename or "upload"}],
    )
    return scan(req)


@app.get("/audit")
def get_audit(limit: int = 50) -> list[dict[str, Any]]:
    return audit.list_events(limit)


@app.get("/quarantine")
def get_quarantine() -> list[dict[str, Any]]:
    return audit.list_quarantine()


@app.post("/quarantine/resolve")
def resolve(action: QuarantineAction) -> dict[str, Any]:
    ok = audit.resolve_quarantine(action.event_id, action.action, action.analyst_note)
    return {"ok": ok, "event_id": action.event_id, "action": action.action}


@app.get("/session/{session_id}")
def session_status(session_id: str) -> dict[str, Any]:
    return audit.get_session_risk(session_id)


@app.get("/metrics/corpus")
def corpus_metrics() -> dict[str, Any]:
    from corpus.evaluate import evaluate_corpus

    return evaluate_corpus()
