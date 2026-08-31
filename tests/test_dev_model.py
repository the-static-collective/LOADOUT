from dataclasses import FrozenInstanceError

import pytest

from loadout.dev.model import (
    AdapterBody,
    CapabilitySpec,
    EffectClass,
    EffectIntent,
    RefusalReason,
    parameter_map,
)


def test_adapter_body_binds_exact_sha_and_declared_effects():
    sha = "a" * 40
    body = AdapterBody(
        adapter_id="github-adapter",
        body_time_id=f"github-adapter@{sha}",
        source_sha=sha,
        capabilities=(CapabilitySpec("repo.inspect", EffectClass.OBSERVE),),
    )
    assert body.authority == "none"
    assert body.capabilities[0].effect == EffectClass.OBSERVE


def test_adapter_body_rejects_non_exact_sha():
    with pytest.raises(ValueError, match="40 lowercase hexadecimal"):
        AdapterBody(
            adapter_id="github-adapter",
            body_time_id="github-adapter@abc",
            source_sha="abc",
            capabilities=(),
        )


def test_adapter_body_rejects_body_time_mismatch():
    sha = "b" * 40
    with pytest.raises(ValueError, match="body_time_id"):
        AdapterBody(
            adapter_id="github-adapter",
            body_time_id=f"other@{sha}",
            source_sha=sha,
            capabilities=(),
        )


def test_adapter_body_rejects_authority_lauering():
    sha = "c" * 40
    with pytest.raises(ValueError, match="authority: none"):
        AdapterBody(
            adapter_id="gitbook-adapter",
            body_time_id=f"gitbook-adapter@{sha}",
            source_sha=sha,
            capabilities=(),
            authority="publish",
        )


def test_adapter_body_is_immutable():
    sha = "d" * 40
    body = AdapterBody(
        adapter_id="fixture",
        body_time_id=f"fixture@{sha}",
        source_sha=sha,
        capabilities=(),
    )
    with pytest.raises(FrozenInstanceError):
        body.authority = "merge"  # type: ignore[misc]


def test_refusal_reason_names_are_stable():
    assert RefusalReason.BODY_PIN_REQUIRED.value == "BODY_PIN_REQUIRED"
    assert RefusalReason.EFFECT_OUTSIDE_FENCE.value == "EFFECT_OUTSIDE_FENCE"
    assert RefusalReason.OWNER_GATE_STALE.value == "OWNER_GATE_STALE"


def _intent(*, parameters=()):
    return EffectIntent(
        "git.resolve_ref",
        EffectClass.OBSERVE,
        "repo:local",
        "local-git@body",
        "state:0",
        "sha256:" + "0" * 64,
        parameters=parameters,
    )


def test_existing_six_argument_effect_intent_construction_remains_compatible():
    intent = EffectIntent(
        "git.resolve_ref",
        EffectClass.OBSERVE,
        "repo:local",
        "local-git@body",
        "state:0",
        "sha256:" + "0" * 64,
    )
    assert intent.parameters == ()


def test_parameter_map_preserves_bounded_string_parameters():
    intent = _intent(parameters=(("ref", "main"), ("path", "README.md")))
    assert parameter_map(intent) == {"ref": "main", "path": "README.md"}


def test_parameter_map_refuses_duplicate_keys():
    intent = _intent(parameters=(("ref", "main"), ("ref", "HEAD")))
    with pytest.raises(ValueError, match="duplicate parameter key"):
        parameter_map(intent)


def test_parameter_map_refuses_non_string_pairs():
    intent = _intent(parameters=(("ref", 42),))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="parameter keys and values must be strings"):
        parameter_map(intent)
