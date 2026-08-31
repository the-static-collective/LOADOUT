from __future__ import annotations

import loadout.dev as dev


def test_merge_formation_public_api_exports_only_neutral_analyzer_names() -> None:
    assert callable(dev.analyze_merge_formation)
    assert issubclass(dev.MergeFormationInputError, ValueError)
    assert callable(dev.render_merge_formation_receipt)
    assert not hasattr(dev, "HumanEntropy")
    assert not hasattr(dev, "humanentropy")
