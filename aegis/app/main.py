"""Aegis FastAPI application — executive demo APIs."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.policy import get_policy, reset_policy, token_from_policy, update_policy
from agent.protected import ProtectedAgent
from firewall import audit
from firewall.engine import AegisFirewall
from firewall.frameworks import ATTACK_PLAYBOOK, FRAMEWORKS
from firewall.models import (
    PolicyUpdate,
    QuarantineAction,
    ScanRequest,
    ScanResponse,
)

audit.init_db()

app = FastAPI(
    title="Aegis Prompt Injection Firewall",
    description="Behavioral twin firewall for ET AI Hackathon Problem 2 — executive edition",
    version="1.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

firewall = AegisFirewall()


class Health(BaseModel):
    status: str = "ok"
    product: str = "Aegis"
    claim: str = "F3/D2"
    edition: str = "executive"


def _agent() -> ProtectedAgent:
    return ProtectedAgent(token=token_from_policy())


def _run_scan(req: ScanRequest) -> ScanResponse:
    verdict = firewall.scan_request(req)
    agent_out = _agent().run(verdict, req.user_message)
    report = AegisFirewall.build_incident_report(verdict, agent_out)
    return ScanResponse(
        verdict=verdict,
        agent_reply=agent_out.get("reply"),
        tool_results=agent_out.get("tool_results") or [],
        incident_report=report,
    )


@app.get("/health", response_model=Health)
def health() -> Health:
    return Health()


@app.post("/scan", response_model=ScanResponse)
def scan(req: ScanRequest) -> ScanResponse:
    return _run_scan(req)


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
    return _run_scan(req)


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


@app.get("/telemetry")
def telemetry() -> dict[str, Any]:
    events = audit.list_events(100)
    counts = {"allow": 0, "quarantine": 0, "block": 0}
    attack_hist: dict[str, int] = {}
    for e in events:
        counts[e.get("decision", "allow")] = counts.get(e.get("decision", "allow"), 0) + 1
        for a in e.get("attack_types") or []:
            attack_hist[a] = attack_hist.get(a, 0) + 1
    try:
        from corpus.evaluate import evaluate_corpus

        corpus = evaluate_corpus()
        corpus_summary = {
            "n": corpus["n"],
            "precision": corpus["precision"],
            "recall": corpus["recall"],
            "f1": corpus["f1"],
            "accuracy": corpus["accuracy"],
            "by_attack": corpus.get("by_attack"),
        }
    except Exception as exc:  # noqa: BLE001
        corpus_summary = {"error": str(exc)}

    return {
        "claim": "F3/D2",
        "events_n": len(events),
        "decision_counts": counts,
        "attack_histogram": attack_hist,
        "recent": events[:12],
        "corpus": corpus_summary,
        "quarantine_pending": len(audit.list_quarantine()),
        "policy": get_policy(),
    }


@app.get("/frameworks")
def frameworks() -> dict[str, Any]:
    return FRAMEWORKS


@app.get("/playbooks")
def playbooks() -> list[dict[str, Any]]:
    return ATTACK_PLAYBOOK


@app.get("/policy")
def policy_get() -> dict[str, Any]:
    return get_policy()


@app.put("/policy")
def policy_put(update: PolicyUpdate) -> dict[str, Any]:
    patch = {k: v for k, v in update.model_dump().items() if v is not None}
    return update_policy(patch)


@app.post("/policy/reset")
def policy_reset() -> dict[str, Any]:
    return reset_policy()


@app.get("/incident/{event_id}")
def incident(event_id: int) -> dict[str, Any]:
    events = audit.list_events(500)
    for e in events:
        if e.get("id") == event_id:
            return {
                "report_version": "1.0",
                "product": "Aegis Behavioral Twin Firewall",
                "claim": "F3/D2",
                "event": e,
                "executive_summary": (
                    f"Event #{event_id}: decision={e.get('decision')} "
                    f"risk={e.get('risk_score')} attacks={e.get('attack_types')}"
                ),
            }
    return {"error": "not_found", "event_id": event_id}
