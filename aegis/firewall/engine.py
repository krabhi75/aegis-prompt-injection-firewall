"""Aegis firewall orchestration pipeline."""

from __future__ import annotations

from typing import Any, Optional

from firewall import audit
from firewall.decode import decode_text
from firewall.ingest import merge_chunks
from firewall.models import ContentChunk, FirewallVerdict, GateDecision, ScanRequest
from firewall.provenance import tag_provenance
from firewall.risk import build_verdict
from firewall.static import run_static_detectors
from firewall.twin import run_behavioral_twin


class AegisFirewall:
    def scan(
        self,
        session_id: str,
        user_message: str,
        attachments: Optional[list[dict[str, Any]]] = None,
    ) -> FirewallVerdict:
        chunks = merge_chunks(user_message, attachments)
        # Decode each chunk text in place
        decode_flags = False
        decoded_chunks: list[ContentChunk] = []
        for ch in chunks:
            result = decode_text(ch.text)
            decode_flags = decode_flags or result.suspicious
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

        doc = tag_provenance(decoded_chunks)
        findings = run_static_detectors(doc, decode_suspicious=decode_flags)
        twin = run_behavioral_twin(doc.raw_text, doc.sanitized_text)
        verdict = build_verdict(
            session_id=session_id,
            findings=findings,
            twin=twin,
            raw_text=doc.raw_text,
            sanitized_text=doc.sanitized_text,
        )

        status = "pending" if verdict.decision == GateDecision.QUARANTINE else "final"
        audit.log_event(
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
        return verdict

    def scan_request(self, req: ScanRequest) -> FirewallVerdict:
        return self.scan(req.session_id, req.user_message, req.attachments)
