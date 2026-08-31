import json
import subprocess
from pathlib import Path

from loadout.cli import main

ROOT = Path(__file__).parents[1]


def test_installed_cli_help_lists_reconstitute():
    result = subprocess.run(
        ["loadout", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "reconstitute" in result.stdout


def test_cli_bind_emits_machine_readable_receipt(tmp_path, capsys):
    capability = tmp_path / "capability.json"
    fence = tmp_path / "fence.json"
    capability.write_text(json.dumps({
        "capability": "probe",
        "operation": "intervene",
        "reachable_effects": ["target.state"],
        "parameters": {"input": "u0"},
    }))
    fence.write_text(json.dumps(["target.state"]))
    assert main(["bind", str(capability), "--fence", str(fence)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["disposition"] == "BIND"
    assert output["probe_receipt_required"] is True


def test_cli_reach_reports_missing_required_capability(tmp_path, capsys):
    compile_file = tmp_path / "compile.json"
    compile_file.write_text(json.dumps({
        "compile_trace": {"preserved_invariants": ["required-capability:repo.write"]},
        "capability_bindings": [{"capability": "repo.read", "status": "available"}],
    }))
    assert main(["reach", str(compile_file)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output == {"missing_capabilities": ["repo.write"], "reachable": False}


def test_cli_trace_emits_operator_path(tmp_path, capsys):
    receipt = tmp_path / "receipt.json"
    receipt.write_text(json.dumps({
        "disposition": "REFUSE",
        "reachable_effects": ["target.state"],
        "unfenced_effects": ["target.state"],
    }))
    assert main(["trace", str(receipt)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert [step["step"] for step in output] == ["REACH", "FENCE", "BIND"]


def test_cli_reconstitute_emits_threshold_and_world_birth(tmp_path, capsys):
    project0_fixture = ROOT / "fixtures/phaselift/project0-CROSSING-001.json"
    project0_provenance = ROOT / "fixtures/phaselift/project0-CROSSING-001.provenance.json"

    request_file = tmp_path / "request.json"
    request_file.write_text(json.dumps({
        "threshold_id": "threshold:B-cli",
        "receiving_constitution_ref": "constitution:loadout:B-cli",
        "continuity_requirements": {
            "identity": ["preserved", "transformed"],
            "protocol": ["preserved", "transformed", "reconstituted"],
            "purpose-meaning": ["preserved", "transformed"],
        },
        "missing_evidence_refs": [],
        "fatal_missing_refs": [],
        "protect_refs": ["artifact:odd-small-1"],
        "adopt_source_proposals": ["proposal:inspect-next"],
        "hold": False,
        "refuse_reason": None,
    }))

    compile_file = tmp_path / "compile.json"
    compile_file.write_text(json.dumps({
        "compile_id": "compile:B-cli",
        "parent_compile_id": None,
        "issued_at": "2026-08-30T06:00:00+00:00",
        "expires_at": "2026-08-30T07:00:00+00:00",
        "world_cut_ref": "world:B-cli",
        "context_pack_ref": "context:B-cli",
        "compile_trace": {
            "id": "trace:B-cli",
            "source_world_ref": "world:A",
            "operation": "reconstitute-from-crossing",
            "preserved_invariants": ["required-capability:repo.read"],
            "declared_loss": [],
            "producer": "loadout.kernel/v0",
            "freshness": "2026-08-30T06:00:00+00:00",
        },
        "capabilities": [
            {"capability": "repo.read", "operation": "inspect", "reachable_effects": [], "parameters": {}},
            {"capability": "repo.write", "operation": "intervene", "reachable_effects": ["repo.branch.write"], "parameters": {}},
        ],
        "effect_fence": ["repo.branch.write"],
        "effect_fence_ref": "fence:B-cli",
        "effect_authorizations": {},
        "owner_evidence_digest": "sha256:" + "d" * 64,
        "egress_policy_ref": "egress:B-cli",
    }))

    resolved_bodies_file = tmp_path / "resolved-bodies.json"
    resolved_bodies_file.write_text(json.dumps([
        {"logical_ref": "ALEX", "resolved_body": "alex:B1"},
        {"logical_ref": "Dogram", "resolved_body": "dogram:B1"},
    ]))

    assert main([
        "reconstitute",
        str(project0_fixture),
        str(project0_provenance),
        str(request_file),
        str(compile_file),
        "--world-id", "world:B-cli",
        "--occurred-at", "2026-08-30T06:00:01+00:00",
        "--resolved-bodies", str(resolved_bodies_file),
    ]) == 0

    output = json.loads(capsys.readouterr().out)
    assert output["threshold"]["disposition"] == "LIFT"
    assert output["birth_receipt"]["world_id"] == "world:B-cli"
    assert output["birth_receipt"]["source_handoff_digest"] == output["threshold"]["source_handoff_digest"]


def _live_manifest():
    return {
        "schema": "static-collective/current-organ/v0",
        "organ": "loadout",
        "owner": "the-static-collective/LOADOUT",
        "entrypoint": "skills/loadout/SKILL.md",
        "state": None,
        "allowed_roots": ["skills/loadout", "docs"],
        "resolution": "default-branch-head-then-pin",
        "fallback": "embedded-bootstrap",
    }


def test_cli_resolve_live_emits_pinned_receipt_and_bounded_documents(tmp_path, capsys):
    manifest = tmp_path / "manifest.json"
    evidence = tmp_path / "evidence.json"
    manifest_body = _live_manifest()
    manifest.write_text(json.dumps(manifest_body))
    evidence.write_text(json.dumps({
        "owner": manifest_body["owner"],
        "resolved_ref": "main",
        "resolved_sha": "0123456789abcdef0123456789abcdef01234567",
        "files": {
            ".live/current-organ.json": json.dumps(manifest_body, sort_keys=True),
            "skills/loadout/SKILL.md": "skill",
            "docs/needed.md": "needed",
            "docs/unrequested.md": "do not load",
        },
    }))

    assert main([
        "resolve-live",
        str(manifest),
        str(evidence),
        "--path",
        "docs/needed.md",
    ]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "RESOLVED"
    assert output["receipt"]["resolved_sha"] == "0123456789abcdef0123456789abcdef01234567"
    assert output["receipt"]["loaded"] == ["skills/loadout/SKILL.md", "docs/needed.md"]
    assert "docs/unrequested.md" not in output["documents"]


def test_cli_resolve_live_returns_two_for_unresolved_evidence(tmp_path, capsys):
    manifest = tmp_path / "manifest.json"
    evidence = tmp_path / "evidence.json"
    manifest_body = _live_manifest()
    manifest_body["allowed_roots"] = ["skills/loadout"]
    manifest.write_text(json.dumps(manifest_body))
    evidence.write_text(json.dumps({
        "owner": manifest_body["owner"],
        "resolved_ref": "main",
        "resolved_sha": "0123456789abcdef0123456789abcdef01234567",
        "files": {
            ".live/current-organ.json": json.dumps(manifest_body, sort_keys=True),
        },
    }))

    assert main(["resolve-live", str(manifest), str(evidence)]) == 2
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "UNRESOLVED"
    assert output["receipt"]["freshness"] == "UNRESOLVED"
