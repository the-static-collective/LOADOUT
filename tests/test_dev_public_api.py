import loadout.dev as dev


def test_public_api_exports_v0_surface():
    expected = {
        "AdapterBody", "CapabilityRequest", "CapabilitySpec", "CompileRequest", "CompileReceipt",
        "EffectClass", "EffectIntent", "EffectReceipt", "OwnerGate", "RefusalReason", "WorkflowEvent",
        "compile_world", "Adapter", "FakeAdapter", "invoke_effect",
        "DEV_IMPLEMENT", "DEV_DEBUG", "DEV_REVIEW", "DEV_LAND", "DEV_DOCS",
        "start_workflow", "transition",
    }
    assert expected <= set(dev.__all__)
    for name in expected:
        assert hasattr(dev, name)
