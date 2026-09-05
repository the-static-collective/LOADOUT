from __future__ import annotations

from importlib import import_module

from loadout.dev.adapters import Adapter, FakeAdapter
from loadout.dev.compiler import compile_world
from loadout.dev.live_git import resolve_current_organ_from_git
from loadout.dev.local_git import LocalGitReadAdapter
from loadout.dev.membrane import invoke_effect
from loadout.dev.model import (
    AdapterBody,
    CapabilityRequest,
    CapabilitySpec,
    CompileReceipt,
    CompileRequest,
    EffectClass,
    EffectIntent,
    EffectReceipt,
    OwnerGate,
    RefusalReason,
    WorkflowEvent,
    parameter_map,
)
from loadout.dev.openmanus import OpenManusJsonStdioAdapter, OpenManusProviderReceipt
from loadout.dev.workflow import (
    DEV_DEBUG,
    DEV_DOCS,
    DEV_IMPLEMENT,
    DEV_LAND,
    DEV_REVIEW,
    start_workflow,
    transition,
)

_MERGE_FORMATION_EXPORTS = {
    "MergeFormationInputError",
    "analyze_merge_formation",
    "render_merge_formation_receipt",
}


def __getattr__(name: str):
    if name in _MERGE_FORMATION_EXPORTS:
        module = import_module("loadout.dev.merge_formation")
        value = getattr(module, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "Adapter", "AdapterBody", "CapabilityRequest", "CapabilitySpec", "CompileReceipt", "CompileRequest",
    "DEV_DEBUG", "DEV_DOCS", "DEV_IMPLEMENT", "DEV_LAND", "DEV_REVIEW",
    "EffectClass", "EffectIntent", "EffectReceipt", "FakeAdapter", "LocalGitReadAdapter", "OwnerGate",
    "OpenManusJsonStdioAdapter", "OpenManusProviderReceipt",
    "RefusalReason", "WorkflowEvent", "compile_world", "invoke_effect", "parameter_map",
    "resolve_current_organ_from_git", "start_workflow", "transition",
    "MergeFormationInputError", "analyze_merge_formation", "render_merge_formation_receipt",
]
