"""Provenance tagging: trusted vs untrusted spans."""

from __future__ import annotations

from dataclasses import dataclass, field

from firewall.models import ContentChunk, TrustLevel


@dataclass
class ProvenanceDocument:
    raw_text: str
    sanitized_text: str
    chunks: list[ContentChunk] = field(default_factory=list)
    untrusted_spans: list[str] = field(default_factory=list)

    @property
    def has_untrusted(self) -> bool:
        return any(c.trust == TrustLevel.UNTRUSTED and c.text.strip() for c in self.chunks)


def tag_provenance(chunks: list[ContentChunk]) -> ProvenanceDocument:
    raw_parts: list[str] = []
    trusted_parts: list[str] = []
    untrusted: list[str] = []

    for chunk in chunks:
        header = f"<<<{chunk.source.value}:{chunk.trust.value}>>>"
        block = f"{header}\n{chunk.text}\n<<<end>>>"
        raw_parts.append(block)
        if chunk.trust == TrustLevel.TRUSTED:
            trusted_parts.append(chunk.text)
        else:
            untrusted.append(chunk.text)
            # Sanitized view keeps only a neutral summary placeholder, not instructions
            preview = chunk.text.strip().replace("\n", " ")[:160]
            trusted_parts.append(
                f"[untrusted:{chunk.source.value} content omitted from instruction channel; "
                f"preview={preview!r}]"
            )

    return ProvenanceDocument(
        raw_text="\n\n".join(raw_parts),
        sanitized_text="\n\n".join(trusted_parts),
        chunks=chunks,
        untrusted_spans=untrusted,
    )
