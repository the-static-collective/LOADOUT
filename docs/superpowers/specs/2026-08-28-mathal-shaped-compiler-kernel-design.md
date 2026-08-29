# LOADOUT Mathal-Shaped Compiler Kernel — Design

**Date:** 2026-08-28
**Status:** APPROVED FOR IMPLEMENTATION
**Repository:** `the-static-collective/LOADOUT`

## Decision

Implement LOADOUT as a small deterministic bounded-world compiler shaped around pure operators that can later lower onto Dogram without depending on Dogram at runtime.

Core pipeline:

```text
TASK -> CUT -> CLASSIFY -> DISCOVER -> SELECT -> REACH -> FENCE -> BIND -> COMPILE -> RECEIPT
```

Reflective pressure is proposal-only:

```text
COMPILE -> RECEIPT -> REIFY -> PRESSURE -> RECOMPILE PROPOSAL -> GATE -> COMPILE'
```

No proposal may become a new executable compile without an explicit gate disposition.

## Constitutional invariants

- Knowledge may load. Capability may bind. Authority does not silently expand.
- LOADOUT carries attributable permission; it does not mint permission.
- Representation capability != intervention capability.
- Availability != relevance != binding != effect authority.
- Receipt != authority.
- Reflection != mutation.
- Context may inherit; effect authority does not silently inherit.
- Successful execution does not mint evidence, support, truth, admission, publication, canon, or merge authority.
- Dogram semantics may shape operators; Dogram runtime is not a v0 dependency.

## Kernel operators

- `REACH`: calculate declared/reachable effects and task capability reachability.
- `DELTA`: calculate stable differences between compiles or bounded records.
- `FENCE`: compare reachable effects with the exact allowed effect set.
- `BIND`: return `BIND`, `REFUSE`, or `UNRESOLVED` from reachable-effect evidence and fence state.
- `TRACE`: preserve the attributable decision path.
- `ABLATE`: produce a counterfactual compile candidate with one binding removed.

## External contracts

LOADOUT owns `loadout.compile/v0` and `loadout.context-pack/v0`.

The ALEX adapter emits `alex.run-envelope/v0` without making ALEX part of LOADOUT's ontology. The envelope pins compile identity, digest, trace, world/context refs, capability bindings, effect fence ref, egress policy, task shape, stop condition, requested outputs, and rule profile.

Historical `loadout.manifest/v0` receipts are immutable witnesses, not automatically promoted into the new canonical compile schema. The 3rdi hatch manifest is golden fixture #1.

## PROBE-BIND-001 executable semantics

For a capability with reachable effects `R` and allowed fence effects `F`:

```text
unresolved reachable effects -> UNRESOLVED
R - F != empty            -> REFUSE
R - F == empty            -> BIND
```

A representation-only lens has `R = {}`. A probe has one or more target-changing reachable effects. Labels and tool brands do not alter this classification.

## Compile record

The first canonical compile remains compatible with the ALEX-side `loadout.compile/v0` contract:

```text
schema
compile_id
parent_compile_id
issued_at
expires_at
world_cut_ref
context_pack_ref
compile_trace
capability_bindings
effect_fence_ref
effective_effects
owner_evidence_digest
egress_policy_ref
compile_digest
```

The digest is SHA-256 over canonical JSON excluding `compile_digest` itself.

An effect fence is necessary but not sufficient for an effectful binding. The compile input must also carry an attributable authorization object for every allowed reachable effect, including `authorization_source_ref` and `owner_gate_ref`. LOADOUT copies these references into the compile; it never synthesizes them.

## Meta-pressure hatch

`loadout.recompile-proposal/v0` is inert data. It references a base compile digest and proposes bounded replacement fields. A gate recomputes and validates the proposal digest, validates the base compile digest, allowed patch keys, and authority/capability non-expansion. The meta-gate may shorten expiry but not extend it, and may not change the effect-fence or egress-policy reference without a fresh owner-local gate. Applying a proposal requires a matching admitted gate receipt.

## First proving sequence

1. `PROBE-BIND-001` lens/unfenced/fenced plus hostile label/fence cases.
2. Deterministic `loadout.compile/v0` digest and exact ALEX-envelope lowering.
3. 3rdi historical manifest validation as a non-promoted witness.
4. `DELTA + ABLATE + REACH` counterfactual loadout proof.
5. Recompile proposal cannot bypass its gate.
6. CLI exposes deterministic JSON commands without network or ambient capability access.
