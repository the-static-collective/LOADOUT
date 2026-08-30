from __future__ import annotations

from loadout.canonical import sha256_json


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def parse_project0_handoff(bundle: dict, provenance: dict) -> dict:
    _require(isinstance(bundle, dict), "project0 fixture must be an object")
    _require(bundle.get("schema") == "phaselift.source-fixture/v0", "unsupported source fixture")

    envelope = bundle.get("envelope")
    continuity = bundle.get("continuityClaim")
    hints = bundle.get("sourceHints", {})

    _require(isinstance(envelope, dict), "project0 envelope required")
    _require(envelope.get("protocolVersion") == "p0.exchange/0.1", "unsupported encounter protocol")
    _require(isinstance(continuity, dict), "continuity claim required")
    _require(continuity.get("schema") == "p0.continuity/0.1", "unsupported continuity protocol")
    _require(isinstance(provenance, dict), "source provenance required")

    source_authority_refs = sorted(envelope.get("sourceAuthorityRefs", []))
    producer_refs = sorted(
        ref
        for ref in envelope.get("sourceProvenanceRefs", [])
        if isinstance(ref, str) and ref.startswith("producer:")
    )
    protected_requests = sorted(hints.get("protectedRefs", []))
    source_open_proposals = list(hints.get("openProposals", []))

    handoff_payload = {
        "source_fixture": {
            "repo": provenance["source_repo"],
            "commit": provenance["source_commit"],
            "path": provenance["source_path"],
            "sha256": provenance["source_sha256"],
        },
        "source_encounter": envelope,
        "continuity_claim": continuity,
        "source_authority_refs": source_authority_refs,
        "historical_producer_refs": producer_refs,
        "protected_requests": protected_requests,
        "source_open_proposals": source_open_proposals,
    }

    return {
        "schema": "loadout.project0-handoff/v0",
        **handoff_payload,
        "handoff_digest": sha256_json(handoff_payload),
    }
