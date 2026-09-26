"""Aegis firewall orchestration pipeline with executive-grade explainability."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from firewall import audit
from firewall.decode import decode_text
from firewall.ingest import merge_chunks
from firewall.models import ContentChunk, FirewallVerdict, GateDecision, ScanRequest
from firewall.provenance import tag_provenance
from firewall.risk import build_verdict
from firewall.static import run_static_detectors
from firewall.twin import run_behavioral_twin


def _classifier_only_score(findings: list) -> dict[str, Any]:
    """Simulate a naive keyword/LLM-classifier firewall (no twin, no provenance)."""
    if not findings:
        return {
            "decision": "allow",
            "risk_score": 0.05,
            "label": "Classifier-only",
            "rationale": "No high-confidence keyword hits — would likely ALLOW.",
        }
    top = max(findings, key=lambda f: f.confidence)
    risk = min(1.0, top.confidence * 0.7)
    if risk >= 0.75:
        decision = "block"
    elif risk >= 0.45:
        decision = "quarantine"
    else:
        decision = "allow"
    return {
        "decision": decision,
        "risk_score": round(risk, 3),
        "label": "Classifier-only",
        "rationale": (
            f"Top keyword hit: {top.attack_type.value} ({top.confidence:.2f}). "
            "No behavioral twin — indirect tool drift may be missed."
        ),
        "findings": [f.attack_type.value for f in findings],
    }


class AegisFirewall:
    def scan(
        self,
        session_id: str,
        user_message: str,
        attachments: Optional[list[dict[str, Any]]] = None,
    ) -> FirewallVerdict:
        trace: list[dict[str, Any]] = []

        chunks = merge_chunks(user_message, attachments)
        trace.append(
            {
                "stage": "ingest",
                "title": "Ingest & normalize",
                "status": "ok",
                "detail": f"{len(chunks)} chunk(s): "
                + ", ".join(f"{c.source.value}/{c.trust.value}" for c in chunks),
            }
        )

        decode_flags = False
        transforms: list[str] = []
        decoded_chunks: list[ContentChunk] = []
        for ch in chunks:
            result = decode_text(ch.text)
            decode_flags = decode_flags or result.suspicious
            transforms.extend(result.transformations)
            meta = dict(ch.metadata)
            meta["decode_transformations"] = result.transformations
            decoded_chunks.append(
                ContentChunk(
                    text=result.decoded,
                    source=ch.source,
                    trust=ch.trust,
                    metadata=meta,
                )
            )
        trace.append(
            {
                "stage": "decode",
                "title": "Decode / de-obfuscate",
                "status": "alert" if decode_flags else "ok",
                "detail": (
                    f"Transformations: {', '.join(transforms) or 'none'}"
                    + ("; encoded payload suspected" if decode_flags else "")
                ),
            }
        )

        doc = tag_provenance(decoded_chunks)
        trace.append(
            {
                "stage": "provenance",
                "title": "Provenance tagging",
                "status": "alert" if doc.has_untrusted else "ok",
                "detail": (
                    f"Untrusted spans={len(doc.untrusted_spans)}; "
                    "untrusted content stripped from instruction channel."
                    if doc.has_untrusted
                    else "No untrusted attachments."
                ),
            }
        )

        findings = run_static_detectors(doc, decode_suspicious=decode_flags)
        trace.append(
            {
                "stage": "static",
                "title": "Static detectors",
                "status": "alert" if findings else "ok",
                "detail": (
                    ", ".join(f"{f.attack_type.value} ({f.confidence:.2f})" for f in findings)
                    if findings
                    else "No static attack signatures."
                ),
            }
        )

        twin = run_behavioral_twin(doc.raw_text, doc.sanitized_text)
        trace.append(
            {
                "stage": "twin",
                "title": "Behavioral twin",
                "status": "alert" if twin.drift_score >= 0.45 else "ok",
                "detail": (
                    f"drift={twin.drift_score:.2f}; drifted={twin.drifted_tools or []}; "
                    f"trusted_tools={[t.name for t in twin.trusted_plan.tools]}; "
                    f"raw_tools={[t.name for t in twin.raw_plan.tools]}"
                ),
            }
        )

        verdict = build_verdict(
            session_id=session_id,
            findings=findings,
            twin=twin,
            raw_text=doc.raw_text,
            sanitized_text=doc.sanitized_text,
        )
        classifier = _classifier_only_score(findings)
        aegis_side = {
            "decision": verdict.decision.value,
            "risk_score": round(verdict.risk_score, 3),
            "label": "Aegis twin runtime",
            "rationale": verdict.explanation,
        }
        advantage = classifier["decision"] != verdict.decision.value or (
            twin.drift_score >= 0.5 and classifier["decision"] == "allow"
        )
        comparison = {
            "classifier_only": classifier,
            "aegis": aegis_side,
            "aegis_advantage": advantage,
            "headline": (
                "Aegis blocked behavioral drift that a classifier-only gate would miss."
                if advantage and verdict.decision != GateDecision.ALLOW
                else "Both paths agree on this sample."
                if classifier["decision"] == verdict.decision.value
                else "Decisions differ — review twin drift and static findings."
            ),
        }

        trace.append(
            {
                "stage": "risk",
                "title": "Risk engine",
                "status": "alert" if verdict.risk_score >= 0.45 else "ok",
                "detail": f"score={verdict.risk_score:.2f}; attacks="
                + ", ".join(a.value for a in verdict.attack_types if a.value != "None"),
            }
        )
        trace.append(
            {
                "stage": "gate",
                "title": "Gate decision",
                "status": "block"
                if verdict.decision == GateDecision.BLOCK
                else ("alert" if verdict.decision == GateDecision.QUARANTINE else "ok"),
                "detail": f"{verdict.decision.value.upper()} — tools "
                + ("execute trusted plan only" if verdict.decision == GateDecision.ALLOW else "halted"),
            }
        )

        verdict.pipeline_trace = trace
        verdict.comparison = comparison

        status = "pending" if verdict.decision == GateDecision.QUARANTINE else "final"
        event_id = audit.log_event(
            session_id=session_id,
            decision=verdict.decision.value,
            risk_score=verdict.risk_score,
            attack_types=[a.value for a in verdict.attack_types if a.value != "None"],
            explanation=verdict.explanation,
            raw_text=verdict.raw_text,
            sanitized_text=verdict.sanitized_text,
            twin=verdict.twin.model_dump() if verdict.twin else {},
            findings=[f.model_dump() for f in verdict.findings],
            status=status,
        )
        verdict.event_id = event_id
        return verdict

    def scan_request(self, req: ScanRequest) -> FirewallVerdict:
        return self.scan(req.session_id, req.user_message, req.attachments)

    @staticmethod
    def build_incident_report(verdict: FirewallVerdict, agent_out: dict[str, Any]) -> dict[str, Any]:
        return {
            "report_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "product": "Aegis Behavioral Twin Firewall",
            "claim": "F3/D2",
            "event_id": verdict.event_id,
            "session_id": verdict.session_id,
            "decision": verdict.decision.value,
            "risk_score": verdict.risk_score,
            "attack_types": [a.value for a in verdict.attack_types if a.value != "None"],
            "explanation": verdict.explanation,
            "pipeline_trace": verdict.pipeline_trace,
            "comparison": verdict.comparison,
            "twin": verdict.twin.model_dump() if verdict.twin else {},
            "findings": [f.model_dump() for f in verdict.findings],
            "agent": {
                "reply": agent_out.get("reply"),
                "tool_results": agent_out.get("tool_results") or [],
                "denied": agent_out.get("denied"),
            },
            "executive_summary": (
                f"Aegis issued {verdict.decision.value.upper()} "
                f"(risk {verdict.risk_score:.2f}). "
                + (
                    "High-risk tool trajectory drift was neutralized before execution."
                    if verdict.decision != GateDecision.ALLOW
                    else "Request allowed under current capability policy."
                )
            ),
        }
