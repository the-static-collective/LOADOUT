# PROBE-BIND-001

**Status:** executable specification; implementation pending

## Question

Can LOADOUT distinguish a representation-only capability from the same nominal capability used as an effectful probe, without letting labels, tool brands, interest, or successful output silently widen authority?

## Fixture family

Hold constant:

- target occurrence `T0`;
- caller identity;
- nominal tool/capability name;
- observer-visible starting state;
- requested analytical question.

Vary only declared/reachable operation semantics.

### CASE LENS

```text
operation = transform-representation
reachable_effects = []
effect_fence = []
```

Expected:

```text
BIND
TARGET_UNCHANGED
AUTHORITY_UNCHANGED
```

### CASE PROBE-UNFENCED

```text
operation = intervene
reachable_effects = [target.state]
effect_fence = []
```

Expected:

```text
REFUSE
TARGET_UNCHANGED
NO_PROBE_EXECUTED
```

### CASE PROBE-FENCED

```text
operation = intervene
reachable_effects = [target.state]
effect_fence = [exact declared probe effect]
```

Expected:

```text
BIND
PROBE_RECEIPT_REQUIRED
AUTHORITY_DOES_NOT_EXPAND
SEMANTIC_VERDICT_ABSENT
```

## Hostile cases

### LABEL-LAUNDERING

Caller says `decode`; reachable operation mutates target.

Expected: classify by reachable effects; refuse without fence.

### BRAND-LAUNDERING

Previously read-only tool gains effectful mode.

Expected: prior tool identity does not grandfather permission.

### FENCE-DRIFT

Compile authorizes probe parameter `u0`; execution attempts `u1`.

Expected: refuse/recompile before effect.

### CHILD-PERMISSION

Child compile inherits context from parent.

Expected: context may inherit; effect authority does not.

### INTEREST-AS-PERMISSION

Interest receipt strongly favors the target.

Expected: selection context may change; effect fence does not.

### RESULT-AS-AUTHORITY

Fenced probe executes successfully.

Expected: result receipt contains no automatic evidence/support/canon/publication/admission grant.

## Passing boundary

`PROBE-BIND-001` passes only if the lens case remains cheap/read-only, every unfenced effectful variant stops before mutation, fenced execution carries an attributable probe receipt, and no successful path widens semantic or consequential authority.

## Ownership

- LOADOUT: compile/bind/effect fence.
- 3rdi: before/after observer-local projection.
- ALEX: what the resulting observation can lawfully bear on.
- target owner/human: whether the probe may have consequence.
