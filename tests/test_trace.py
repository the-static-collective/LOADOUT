from loadout.bind import evaluate_binding
from loadout.trace import trace_binding


def test_trace_binding_exposes_decision_path_without_semantic_verdict():
    receipt = evaluate_binding({
        "capability": "probe",
        "operation": "intervene",
        "reachable_effects": ["target.state"],
        "parameters": {"input": "u0"},
    }, [])
    trace = trace_binding(receipt)
    assert trace == [
        {"step": "REACH", "value": ["target.state"]},
        {"step": "FENCE", "value": ["target.state"]},
        {"step": "BIND", "value": "REFUSE"},
    ]
