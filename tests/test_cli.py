import json
from pathlib import Path

from loadout.cli import main


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
