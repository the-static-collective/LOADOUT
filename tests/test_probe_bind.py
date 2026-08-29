from loadout.bind import evaluate_binding, validate_execution_attempt


def test_representation_only_lens_binds_without_effect_fence():
    capability = {
        "capability": "decoder",
        "operation": "transform-representation",
        "reachable_effects": [],
        "parameters": {"mode": "lens"},
    }
    result = evaluate_binding(capability, [])
    assert result["disposition"] == "BIND"
    assert result["reachable_effects"] == []
    assert result["unfenced_effects"] == []
    assert result["authority_delta"] == "none"


def test_unfenced_probe_refuses_before_effect():
    capability = {
        "capability": "decoder",
        "operation": "decode",
        "reachable_effects": ["target.state"],
        "parameters": {"mode": "probe"},
    }
    result = evaluate_binding(capability, [])
    assert result["disposition"] == "REFUSE"
    assert result["reason_code"] == "UNFENCED_REACHABLE_EFFECT"
    assert result["unfenced_effects"] == ["target.state"]


def test_fenced_probe_binds_but_does_not_expand_authority():
    capability = {
        "capability": "decoder",
        "operation": "intervene",
        "reachable_effects": ["target.state"],
        "parameters": {"mode": "probe", "input": "u0"},
    }
    result = evaluate_binding(capability, ["target.state"])
    assert result["disposition"] == "BIND"
    assert result["probe_receipt_required"] is True
    assert result["authority_delta"] == "none"
    assert "semantic_verdict" not in result


def test_unknown_reachable_effects_are_unresolved_not_assumed_safe():
    capability = {
        "capability": "opaque-tool",
        "operation": "inspect",
        "reachable_effects": None,
        "parameters": {},
    }
    result = evaluate_binding(capability, [])
    assert result["disposition"] == "UNRESOLVED"
    assert result["reason_code"] == "REACHABILITY_UNRESOLVED"


def test_parameter_drift_requires_recompile_before_execution():
    capability = {
        "capability": "probe",
        "operation": "intervene",
        "reachable_effects": ["target.state"],
        "parameters": {"input": "u0"},
    }
    binding = evaluate_binding(capability, ["target.state"])
    attempt = validate_execution_attempt(binding, {"input": "u1"})
    assert attempt == {
        "disposition": "REFUSE",
        "reason_code": "PARAMETER_DRIFT",
        "recompile_required": True,
    }
