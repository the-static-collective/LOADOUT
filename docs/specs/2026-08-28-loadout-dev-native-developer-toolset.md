# LOADOUT.dev/v0 — Native Developer Toolset

**Date:** 2026-08-28  
**Status:** APPROVED ARCHITECTURAL DESIGN · IMPLEMENTATION NOT YET ADMITTED  
**Repository:** `the-static-collective/LOADOUT`  
**Neighbor runtime:** `the-static-collective/Dogram`  
**Amends:** `docs/specs/2026-08-28-probe-bind-open-berth.md`

## 0. Decision

LOADOUT will gain a native developer surface named **`LOADOUT.dev/v0`**.

It will not be a branded wrapper around Superpowers, Develoop, Riqor, PR Completion, GitHub, GitBook, Wolfram, or any single agent host.

Instead, LOADOUT.dev will extract the durable developer laws those systems currently help enforce and express them in Static Collective grammar:

> **LOADOUT COMPILES THE DEVELOPER WORLD. DOGRAM MAY EXECUTE THE SCORE. ORGANS TOUCH EXTERNAL WORLDS. RECEIPTS RETURN THE TOUCH.**

The first implementation belongs in LOADOUT because the primary problem is not calculation. It is bounded constitution:

- what developer capability is relevant;
- what may bind;
- what effects are reachable;
- what target is inside the cut;
- what evidence is required before a transition;
- what owner-local authority is required before consequence;
- what remains only a proposal;
- what receipt must return after an effect.

Dogram remains the deterministic execution substrate for pure workflow/mathal semantics as that substrate earns the required runtime capability.

Hard boundary:

```text
LOADOUT.dev != plugin manager
LOADOUT.dev != GitHub bot
LOADOUT.dev != universal agent runtime
LOADOUT.dev != Dogram VM
LOADOUT.dev != semantic authority
```

## 1. Why this belongs in LOADOUT

LOADOUT already owns the sequence:

```text
TASK
  ↓
CUT
  ↓
CLASSIFY
  ↓
DISCOVER
  ↓
SELECT
  ↓
FENCE
  ↓
BIND
  ↓
WORK
  ↓
RECEIPT
```

Developer work is a particularly hostile instance of this problem because one task may expose capabilities whose effects differ by orders of magnitude:

```text
read repository
inspect CI
run local test
write file
push branch
open PR
publish docs
merge PR
```

The presence of all these capabilities in one host must not flatten them into one permission class.

The existing LOADOUT law therefore remains primary:

> **Knowledge may load. Capability may bind. Authority does not silently expand.**

LOADOUT.dev specializes that law for software-development worlds.

## 2. Neighbor ownership

### LOADOUT owns

- developer-task cutting and classification;
- capability discovery and selection;
- provider-independent capability names;
- effect classification;
- target fences;
- workflow admission gates;
- adapter/body binding;
- owner-gate requirements;
- effect-intent issuance;
- binding/effect receipts;
- refusal when requested effects exceed the constituted world.

### Dogram owns

- deterministic pure transition semantics;
- graph/path calculations;
- branch comparison;
- state deltas;
- pure gate predicates when represented as admitted programs;
- canonical execution receipts;
- later execution of admitted `dev.*` mathal programs through Dogram Ω.

Dogram does **not** directly inherit ambient GitHub, GitBook, filesystem, shell, Wolfram evaluator, network, or merge authority merely because a workflow names such an operation.

### ALEX owns

- provenance and formation pressure over claims or research outputs;
- evidence-vs-inference distinctions;
- exact-SHA body-time patterns that LOADOUT.dev may reuse for attributable adapter bodies;
- evaluation of what an external result bears on.

ALEX does not decide whether LOADOUT may bind an effectful developer capability.

### External providers own

Their own external world state:

- GitHub repositories, refs, issues, pull requests, checks, reviews, merges;
- GitBook spaces, change requests, pages, and publication state;
- Wolfram computation/evaluation surfaces;
- future providers not yet named.

An adapter translates between LOADOUT.dev and a provider. It does not make the provider's vocabulary canonical inside LOADOUT.

## 3. Source systems are teachers, not ontology

The initial design is informed by currently useful external workflows:

- **Superpowers** — design-before-implementation, TDD, systematic debugging, evidence-before-completion;
- **Develoop** — issue formation, implementation contract, branch-to-PR lifecycle, bounded review repair;
- **Riqor** — explicit specialist perspective selection and architectural trade-off pressure;
- **PR Completion** — deterministic observation, scope-preserving repair, head-bound readiness, explicit landing authorization;
- **GitHub** — repository and collaboration effects;
- **GitBook** — proposal/change-request/publication effects;
- **Wolfram** — exact computation, formal checks, symbolic/mathematical experimentation.

LOADOUT.dev adopts durable laws from these systems but does not require their product names to appear in a native workflow.

Therefore:

```text
foreign workflow name != native semantic primitive
provider operation != developer law
provider availability != native binding
```

## 4. Native developer grammar

The first vocabulary is deliberately small.

```text
ORIENT
CUT
CONTRACT
DISCOVER
SELECT
BIND
FENCE
ISOLATE
PROBE
WITNESS
MUTATE
VERIFY
PROPOSE
PRESS
REPAIR
READY
ADMIT
LAND
RECEIPT
REFUSE
```

These are workflow-level verbs, not automatically executable commands.

### 4.1 Orientation and constitution

**ORIENT**  
Read only enough project/world context to establish where the task lives.

**CUT**  
Declare the bounded task world: repositories, issue/PR/docs targets, relevant state, and explicit exclusions.

**CONTRACT**  
Declare desired behavior, acceptance conditions, non-goals, and unresolved decisions.

**DISCOVER**  
Find candidate capabilities or bodies without invoking them.

**SELECT**  
Choose the smallest capability/body set that can perform the task.

**BIND**  
Constitute selected capabilities inside the current world under declared constraints.

**FENCE**  
Declare target and effect limits that bound reachable consequence.

### 4.2 Work

**ISOLATE**  
Create or select a bounded work surface such as a feature branch or worktree without granting later publication/landing authority.

**PROBE**  
Perform a discriminating observation or bounded experiment. A probe may be read-only or intervention-capable; the effect class controls binding.

**WITNESS**  
Record an attributable observation such as a failing test, passing test, check result, diff, review finding, or provider response.

**MUTATE**  
Change a bounded target under an admitted effect fence.

**VERIFY**  
Test a declared claim about the current state using fresh evidence appropriate to that claim.

### 4.3 Publication and pressure

**PROPOSE**  
Expose a candidate consequence without admitting it as final. Examples: issue, pull request, GitBook change request, candidate program patch.

**PRESS**  
Apply bounded review, adversarial checking, comparison, or specialist pressure to a proposal/current state.

**REPAIR**  
Make the smallest attributable in-scope change warranted by pressure or failed verification.

**READY**  
Record that the current exact state satisfies a declared readiness predicate. READY is state-bound and expires when its relevant state changes.

### 4.4 Consequence

**ADMIT**  
Cross an owner-local gate that authorizes a specific consequence against a specific current state.

**LAND**  
Execute the previously admitted consequence through an effectful adapter.

**RECEIPT**  
Return attributable structured evidence of what was attempted and what the external world reports happened.

**REFUSE**  
Stop a transition when required capability, evidence, target scope, state identity, effect fence, or authority is absent.

## 5. Core non-collapses

```text
ORIENT != retrieve everything
CUT != authority
CONTRACT != implementation
DISCOVER != invoke
SELECT != bind
BIND != authorize every operation
FENCE != target ownership
PROBE != read-only by definition
WITNESS != truth
MUTATE != publish
VERIFY != permanent readiness
PROPOSE != admit
PRESS != scope expansion
REPAIR != redesign
READY != ADMIT
ADMIT != LAND
LAND request != observed landed state
RECEIPT != authority
provider success != semantic truth
```

Additional developer-specific laws:

```text
issue != branch
branch != PR
PR != merge
CI pass != review pass
review pass != merge authority
merge authority != merge observation
old-head evidence != new-head evidence
read capability != write capability
write capability != publish capability
publish capability != landing capability
```

## 6. Provider-independent capability model

LOADOUT.dev workflows address semantic capabilities rather than product brands.

Candidate capability families:

```text
repo.inspect
repo.diff
repo.branch.create
repo.file.write
repo.commit.create
repo.push

issue.inspect
issue.propose
issue.update

review.inspect
review.request
review.respond
review.resolve

check.inspect
check.execute

proposal.create
proposal.update

landing.inspect
landing.request

docs.inspect
docs.propose
docs.publish

math.inspect
math.compute
math.evaluate
```

These names are provisional implementation-level vocabulary, not a universal ontology.

A provider adapter advertises which semantic capabilities it can realize.

Example:

```text
GitHub adapter
  -> repo.inspect
  -> repo.branch.create
  -> repo.file.write
  -> issue.*
  -> review.*
  -> proposal.*
  -> landing.*

GitBook adapter
  -> docs.inspect
  -> docs.propose
  -> docs.publish

Wolfram read/context adapter
  -> math.inspect
  -> bounded math.compute where supported

Wolfram evaluator body
  -> math.evaluate
  -> separate effect class because arbitrary evaluation may reach files,
     network, system commands, environment, or other ambient capability
```

Hard law:

> **CLASSIFICATION FOLLOWS REACHABLE EFFECTS, NOT THE PROVIDER BRAND OR CALLER LABEL.**

## 7. Effect classes

The first compiler should preserve at least these distinctions:

```text
OBSERVE
REPRESENT
LOCAL_COMPUTE
LOCAL_MUTATE
REMOTE_PROPOSE
REMOTE_MUTATE
PUBLISH
LAND
```

Conceptually:

```text
OBSERVE
  no intended target mutation

REPRESENT
  transform representation without mutating source target

LOCAL_COMPUTE
  deterministic/bounded computation over admitted inputs

LOCAL_MUTATE
  alter a local bounded work surface

REMOTE_PROPOSE
  create/update a proposal surface without final landing

REMOTE_MUTATE
  mutate remote collaborative state

PUBLISH
  expose documentation/artifacts into a published surface

LAND
  cross a repository/project authority boundary such as merge/queue/auto-merge request
```

An operation can be reclassified upward if its reachable effects exceed its nominal label.

`math.evaluate`, for example, cannot be assumed equivalent to `math.compute` if the evaluator can read/write files, access environment variables, execute system commands, or make network requests.

## 8. Developer world compile

A conceptual compile request:

```text
loadout.dev.compile/v0

input:
  task
  current world refs
  workflow intent
  requested semantic capabilities
  requested effects
  target cuts
  available adapter bodies
  owner receipts / gates when present

output:
  COMPILED | REFUSED | CAPABILITY_GAP | OWNER_GATE
  selected bodies
  bound capabilities
  effect fences
  state identities that invalidate prior gates when changed
  required receipts
```

Exact serialization belongs to implementation planning. This design fixes the distinctions, not a premature universal JSON schema.

## 9. Workflow programs

LOADOUT.dev should define named workflow programs that may later lower into Dogram mathals.

Initial family:

```text
dev.design@0
dev.issue@0
dev.implement@0
dev.debug@0
dev.verify@0
dev.review@0
dev.land@0
dev.docs@0
dev.research@0
```

These programs are compositions of native verbs and gate predicates. They do not directly name provider APIs.

### 9.1 `dev.design@0`

```text
ORIENT
  ↓
CUT
  ↓
CONTRACT
  ↓
EXPLORE alternatives
  ↓
PROPOSE design
  ↓
ADMIT design
  ↓
RECEIPT
```

Implementation effects must remain unavailable until the design gate required by the selected workflow is satisfied.

### 9.2 `dev.implement@0`

```text
ORIENT
  ↓
CUT
  ↓
CONTRACT
  ↓
BIND required capabilities
  ↓
FENCE effects
  ↓
ISOLATE
  ↓
WITNESS required precondition / RED where applicable
  ↓
MUTATE
  ↓
VERIFY focused
  ↓
VERIFY repository contract
  ↓
PROPOSE
  ↓
RECEIPT
```

### 9.3 `dev.debug@0`

```text
OBSERVE failure
  ↓
REPRODUCE
  ↓
TRACE origin
  ↓
CONTRACT one root-cause hypothesis
  ↓
PROBE hypothesis
  ↓
WITNESS regression failure
  ↓
MUTATE smallest root-cause fix
  ↓
WITNESS regression pass
  ↓
VERIFY surrounding contract
  ↓
RECEIPT
```

No repair transition is admitted merely because a symptom suggests an obvious patch.

### 9.4 `dev.review@0`

```text
OBSERVE proposal state H
  ↓
PRESS bounded scope
  ↓
CLASSIFY finding
      ├── valid + in-scope -> REPAIR -> VERIFY -> PRESS as warranted
      ├── valid + out-of-scope -> PROPOSE follow-up / preserve residual
      └── invalid/stale -> WITNESS disposition
  ↓
READY(H_current) when predicate passes
  ↓
RECEIPT
```

Review pressure may discover adjacent work but may not silently enlarge the proposal contract.

### 9.5 `dev.land@0`

```text
OBSERVE proposal
  ↓
VERIFY exact current state H
  ↓
VERIFY required checks(H)
  ↓
VERIFY required review(H)
  ↓
READY(H)
  ↓
ADMIT owner-local landing(H)
  ↓
LAND(H)
  ↓
OBSERVE landed state
  ↓
RECEIPT
```

Core invariant:

```math
H_current = H_ready = H_verified = H_admitted
```

If the relevant state changes, head-bound readiness and admission expire.

```text
HEAD / STATE DRIFT
  -> READY expires
  -> head-sensitive VERIFY receipts become stale
  -> landing ADMIT expires
  -> re-observe and re-verify
```

### 9.6 `dev.docs@0`

```text
ORIENT documentation world
  ↓
CUT target publication surface
  ↓
MUTATE proposal/change-request surface
  ↓
VERIFY rendered/content contract
  ↓
READY change request
  ↓
ADMIT publication
  ↓
PUBLISH
  ↓
OBSERVE published state
  ↓
RECEIPT
```

For GitBook specifically, published content must be changed through its change-request surface rather than direct publication mutation. The adapter therefore maps native `PROPOSE` to a GitBook change request and `PUBLISH` to the provider's explicit merge/publication operation.

## 10. Adapter membrane

Dogram or another pure workflow executor may emit an inert **EffectIntent**. It does not receive the adapter capability itself.

Conceptual shape:

```text
EffectIntent
  semantic_capability
  target
  requested_effect
  parameters_digest
  precondition_state
  workflow_receipt_refs
  owner_gate_ref? 
```

LOADOUT evaluates the intent against the compiled developer world.

```text
EffectIntent
   ↓
BOUND CAPABILITY?
   ↓
TARGET IN CUT?
   ↓
EFFECT INSIDE FENCE?
   ↓
BODY ELIGIBLE?
   ↓
STATE PRECONDITION CURRENT?
   ↓
OWNER GATE REQUIRED / SATISFIED?
   ↓
ADAPTER INVOCATION
   ↓
EffectReceipt
```

Hard non-collapse:

```text
EFFECT INTENT != EFFECT
PROGRAM STEP != PROVIDER CREDENTIAL
ADAPTER AVAILABLE != ADAPTER BOUND
ADAPTER BOUND != OWNER AUTHORIZED
```

## 11. Adapter/body identity

LOADOUT.dev should reuse the proven Chronobody idea rather than invent a second versioning philosophy.

A developer adapter body may carry:

```text
adapter_id
body_time_id
status
semantic_capabilities
source repo
exact source SHA when non-present/historical
runtime contract
entrypoint
verification metadata
authority: none
parents
```

The adapter body itself carries no external authority.

Credentials/session grants are local runtime material and remain distinct from the body identity.

```text
BODY != CREDENTIAL
BODY != AUTHORITY
BODY CAPABILITY DECLARATION != CURRENT PERMISSION
```

Replay of a historical body must resolve exact body time rather than an implicit newest implementation.

## 12. Receipts

LOADOUT.dev requires structured receipts at boundaries where state, capability, or authority could otherwise become ambiguous.

### 12.1 Compile receipt

Records at least:

- task/cut digest;
- workflow/program identity;
- selected adapter/body identities;
- bound semantic capabilities;
- effect fences;
- unresolved capability gaps;
- owner gates required;
- compiler disposition.

### 12.2 Witness/verification receipt

Records at least:

- claim being tested;
- exact relevant state identity;
- command/probe/check identity when applicable;
- observed result;
- whether result is fresh for that state;
- residual uncertainty.

### 12.3 Effect receipt

Records at least:

- adapter body identity;
- semantic capability;
- provider operation used;
- target;
- precondition state identity when applicable;
- effect fence;
- owner-gate reference when applicable;
- parameters digest / safe attributable summary;
- provider disposition;
- observed post-effect state when available;
- stderr/error/reason code without secrets.

### 12.4 Landing receipt

Additionally records:

- exact authorized head/state;
- readiness receipt refs;
- landing method/mode;
- owner approval receipt bound to that state;
- observed final merged/queued/not-landed state.

A submitted request must not be reported as landed until the provider surface confirms the landed state required by the workflow.

## 13. Specialist organs

Riqor-like specialist behavior should enter as explicit **pressure organs**, not invisible personas with ambient authority.

Candidate specialist capabilities:

```text
pressure.architecture
pressure.security
pressure.backend
pressure.multi-agent
pressure.ux
pressure.performance
```

A specialist organ may:

- inspect the bounded contract and evidence supplied to it;
- produce questions, trade-offs, findings, or proposals;
- emit attributable pressure receipts.

It may not automatically:

- widen the task cut;
- bind new effectful capabilities;
- mutate repositories;
- resolve its own findings as true;
- land changes.

This makes specialist selection a first-class, attributable workflow choice.

## 14. Failure and refusal family

Initial reason-code families should preserve why progress stopped.

Candidate examples:

```text
CUT_REQUIRED
CONTRACT_REQUIRED
CAPABILITY_UNAVAILABLE
CAPABILITY_NOT_BOUND
EFFECT_OUTSIDE_FENCE
TARGET_OUTSIDE_CUT
BODY_AMBIGUOUS
BODY_NOT_ELIGIBLE
STATE_STALE
WITNESS_REQUIRED
VERIFICATION_STALE
REVIEW_UNRESOLVED
OWNER_GATE_REQUIRED
OWNER_GATE_STALE
PROPOSAL_REQUIRED
LANDING_POLICY_AMBIGUOUS
PROVIDER_REFUSED
PROVIDER_UNAVAILABLE
```

These are workflow reasons, not exceptions that should be flattened into generic process failure.

## 15. Hostile conformance corpus

The first runtime implementation must earn the following boundaries.

### `MENTION-BIND-001`

Mentioning a provider/tool in task text does not bind it.

Expected:

```text
mention GitHub
+ task satisfiable without GitHub effect
-> no automatic GitHub write binding
```

### `DESIGN-GATE-001`

A workflow requiring design admission refuses implementation mutation before design approval.

### `RED-FIRST-001`

A TDD-required implementation path cannot manufacture a RED witness after implementation mutation and present it as precondition evidence.

Required ordering must be attributable.

### `ROOT-CAUSE-001`

A debugging workflow refuses repair admission when the selected policy requires root-cause investigation but only symptom evidence exists.

### `VERIFY-FRESH-001`

A verification receipt for state `A` cannot prove state `B` after a relevant mutation.

### `HEAD-DRIFT-001`

For a PR-like proposal:

```text
READY(H0)
ADMIT(H0)
head -> H1
LAND(H1) using H0 gate
```

must refuse.

### `EFFECT-FENCE-001`

A capability bound for `OBSERVE` or `REPRESENT` cannot invoke a reachable mutation path.

### `REVIEW-SCOPE-001`

A valid but out-of-scope review finding becomes residual/follow-up material rather than silently widening the current implementation contract.

### `DOC-PUBLISH-001`

A GitBook-like publication cannot bypass the provider's proposal/change-request membrane when that provider requires one.

### `WOLFRAM-FENCE-001`

Read-only documentation/context lookup and arbitrary evaluator execution are different capability/effect classes.

A `math.inspect` binding must not authorize evaluator behavior.

### `BODY-PIN-001`

Historical/replay adapter execution requires an exact attributable body rather than implicit latest-body resolution.

### `RESULT-LAUNDER-001`

Successful tool execution may not mint evidence, support, truth, publication authority, merge authority, or semantic admission merely from success.

### `LAND-OBSERVE-001`

A successful landing request is not equivalent to observed final landing when the provider performs asynchronous queue/auto-merge behavior.

## 16. First implementation cut

The first implementation should remain smaller than the full destination architecture.

### In scope

1. A provider-independent developer compile model in LOADOUT.
2. Typed capability/effect/fence representation sufficient for hostile tests.
3. A pure workflow state machine for a minimal subset of verbs:
   - `CUT`
   - `CONTRACT`
   - `BIND`
   - `FENCE`
   - `WITNESS`
   - `VERIFY`
   - `PROPOSE`
   - `READY`
   - `ADMIT`
   - `LAND`
   - `RECEIPT`
   - `REFUSE`
4. Inert EffectIntent / EffectReceipt types.
5. Adapter interface/protocol with fake deterministic adapters for tests.
6. At least GitHub-shaped, GitBook-shaped, and Wolfram-shaped conformance fixtures without requiring live credentials.
7. The hostile corpus in Section 15.
8. A CLI or direct JSON/stdin surface only if the implementation plan shows it is needed to prove cross-process determinism.

### Explicitly deferred

- live autonomous provider orchestration;
- background watchers;
- GitHub merge automation;
- GitBook publication automation;
- arbitrary Wolfram evaluator execution;
- dynamic plugin installation;
- remote adapter download;
- network federation between Cups;
- full Dogram Ω lowering;
- self-modifying developer workflows;
- universal developer ontology;
- secret/credential storage;
- replacing Superpowers/Develoop/PR Completion in all hosts immediately.

## 17. Dogram lowering path

LOADOUT.dev should be executable before it is Dogram-native, but designed so pure workflow logic can migrate into Dogram without changing external authority boundaries.

Progression:

```text
Phase A
LOADOUT host implementation
+ deterministic fake adapters
+ hostile corpus

Phase B
pure state/gate functions gain Dogram oracle equivalents

Phase C
selected dev.* workflows represented as Dogram programs

Phase D
Dogram emits inert EffectIntent
LOADOUT remains the capability/effect membrane

Phase E
host workflow logic may be peeled only after conformance is proven
```

The membrane remains even if nearly all pure workflow sequencing becomes mathal-defined.

Hard law:

> **DOGRAM MAY LEARN THE SCORE WITHOUT INHERITING THE KEYS TO THE BUILDING.**

## 18. Success criteria for v0

`LOADOUT.dev/v0` earns its first executable status when all of the following are true:

1. The same native workflow can be evaluated against multiple provider adapters without embedding provider names in the workflow law.
2. Read-only and effectful capabilities cannot be laundered into one another.
3. Effects outside the target cut/fence refuse before adapter mutation.
4. Verification and readiness are attributable to exact relevant state.
5. Head/state drift invalidates state-bound landing authority.
6. Review pressure cannot silently expand scope.
7. Provider success remains distinct from semantic authority.
8. Adapter bodies are attributable and replay cannot silently resolve newest-body state.
9. All Section 15 hostile fixtures have deterministic expected dispositions.
10. No live provider credentials are required for the conformance suite.

## 19. Architectural decision summary

Three shapes were considered.

### Option A — Developer toolset entirely inside Dogram

Rejected for v0.

It would mix pure deterministic execution with ambient provider effects before Dogram Ω has earned that boundary and would risk turning the math runtime into a credential-bearing orchestrator.

### Option B — Developer toolset entirely inside LOADOUT

Useful for first implementation but insufficient as the destination.

It preserves capability law but would leave deterministic workflow semantics host-bound and duplicate machinery Dogram is explicitly being built to execute.

### Option C — LOADOUT constitution + Dogram score + adapters at the membrane

**Selected.**

```text
LOADOUT
  compile / bind / fence / admit
        ↓
Dogram or pure workflow executor
  deterministic score / gate / receipt
        ↓
EffectIntent
        ↓
LOADOUT membrane
        ↓
versioned adapter body
        ↓
external provider
        ↓
EffectReceipt
```

Trade-offs:

- more explicit boundaries than direct provider scripting;
- requires receipt and state identity discipline;
- initially duplicates a small amount of host workflow logic before Dogram lowering;
- dramatically reduces provider lock-in and silent authority growth;
- creates a testable path toward a genuinely native developer runtime.

## 20. Seal

> **THE TOOL NAME IS NOT THE LAW.**

> **THE WORKFLOW NAMES THE REQUIRED TRANSITIONS. LOADOUT DECIDES WHAT MAY TOUCH THE WORLD. DOGRAM MAY EXECUTE THE PURE SCORE. THE OWNER RETAINS CONSEQUENCE.**

> **LOADOUT ARMS. DOGRAM PLAYS. ORGANS TOUCH. RECEIPTS RETURN.**
