# READ-ONLY-HOST-ADAPTER-001 Design

## Status

Approved architectural slice against `LOADOUT/main@41e5e5055d0a87518c67af4d63442662a508eed4`.

This design moves LOADOUT.dev across one real host boundary without introducing network, credential, write, publication, or deployment authority.

It also preserves the already-built `LIVE-SURFACE / CURRENT-ORGAN v0` branch as executable ancestry. That branch is not assumed current merely because it once passed tests; its compatible payload must be reconciled onto current LOADOUT before this adapter is allowed to depend on it.

## Goal

Replace the fake-only development boundary with one bounded real adapter that can read an exact local Git repository state and return attributable results through the existing LOADOUT.dev effect membrane.

```text
declared read intent
    -> LOADOUT.dev fence
    -> LocalGitReadAdapter
    -> exact immutable git object/ref read
    -> attributable result receipt
```

The adapter proves a real host interaction. It does not authorize mutation.

## Core laws

```text
READ != WRITE
HOST ACCESS != AUTHORITY EXPANSION
CURRENT REF != IMMUTABLE OBJECT
RESOLUTION != ADMISSION
REPOSITORY PRESENCE != REQUESTED SCOPE
ADAPTER RESULT != EVIDENCE OF SEMANTIC TRUTH
```

The adapter returns bytes/identity facts about Git objects. It does not interpret repository meaning.

## Dependency on LIVE-SURFACE / CURRENT-ORGAN v0

PR #5 contains a compatible candidate implementation for:

- owner manifests;
- exact commit pinning;
- allowed-root/path fencing;
- `RESOLVED / UNRESOLVED / REFUSE`;
- stale fallback labeling;
- resolution receipts;
- no silent write-authority expansion.

Before adapter implementation begins, reconcile the minimum still-valid #5 payload onto current `main` with its tests. Do not merge its stale ancestry wholesale if current LOADOUT has changed.

The adapter remains independently useful to LOADOUT.dev, but CURRENT-ORGAN should be its first concrete consumer because that path already has a declared need for attributable repository evidence.

## Existing LOADOUT.dev boundary

Current `src/loadout/dev/adapters.py` defines:

```python
class Adapter(Protocol):
    body_time_id: str
    def invoke(self, intent: EffectIntent) -> tuple[str, str | None]: ...
```

and `FakeAdapter` for deterministic tests.

The new adapter should implement the same protocol or a backward-compatible refinement rather than creating a second effect system.

## Adapter scope

Name:

```text
LocalGitReadAdapter
```

Allowed v0 capabilities:

```text
git.resolve_ref
git.read_blob
```

No generic shell capability is exposed.

### `git.resolve_ref`

Consumes an explicitly declared repository root and ref name. Returns one exact commit/object SHA when Git can resolve it.

Permitted host command shape:

```text
git -C <repo-root> rev-parse --verify <ref>^{commit}
```

No shell interpolation. Arguments are passed as an argv sequence.

### `git.read_blob`

Consumes:

- explicitly declared repository root;
- exact commit SHA;
- repository-relative path.

Returns exact UTF-8 file bytes only when the path is inside the repository and resolves to a regular blob at the requested commit.

Permitted host command shape:

```text
git -C <repo-root> show <commit-sha>:<path>
```

The adapter never silently substitutes the working tree for the requested immutable object.

## Repository-root fence

The repository root is supplied when the adapter is constructed. Callers cannot change it through an intent.

Construction resolves the root to an absolute normalized path. If the directory is absent, not a Git repository, or cannot be inspected read-only, construction/ref invocation produces a typed refusal/unresolved result according to existing LOADOUT.dev conventions.

The adapter never traverses parent repositories searching for a usable `.git` directory.

## Path fence

Paths must be normalized repository-relative POSIX-style paths.

Refuse:

- absolute paths;
- empty paths;
- `.` / `..` traversal components;
- NULs;
- paths outside the declared allowed roots from CURRENT-ORGAN/live-surface policy;
- symlink/worktree fallback reads that bypass the immutable Git object requested.

`git show <sha>:<path>` is the source of file bytes; filesystem path opening is not used for immutable blob reads.

## Intent/result contract

Do not widen `EffectIntent` into a Git-specific mega-object. Use its existing capability/effect/scope fields and put only capability-specific bounded input in the existing payload/data surface if one exists.

If current `EffectIntent` has no lawful structured payload slot, add one narrowly typed optional mapping in the existing model rather than inventing a parallel command protocol.

The adapter returns the existing `(status, result_ref)` protocol unless implementation review proves that returning structured result bytes through this tuple would be lossy. If refinement is required, it must remain backward compatible with `FakeAdapter` and existing workflow tests.

Recommended result records are content-addressed in memory by the caller/receipt layer rather than written by the adapter.

## Body-time identity

`body_time_id` is explicit adapter constitution supplied by the caller. It is not inferred from the current clock.

A recommended value binds:

```text
adapter implementation version
+ declared repository root identity
+ git executable version if captured
```

but the exact composition belongs to implementation planning. The critical law is that adapter body identity is attributable and stable during one workflow occurrence.

## Failure states

Distinguish at minimum:

```text
REFUSE / CAPABILITY_NOT_ALLOWED
REFUSE / TARGET_OUTSIDE_CUT
REFUSE / PATH_OUTSIDE_FENCE
REFUSE / INVALID_REF
UNRESOLVED / GIT_UNAVAILABLE
UNRESOLVED / OBJECT_NOT_FOUND
UNRESOLVED / NON_UTF8_BLOB
```

Do not translate all subprocess failures into one generic exception.

No failed read may mutate workflow state as if a successful host effect occurred.

## Security / authority boundary

The adapter must never execute:

- `git checkout`;
- `git switch`;
- `git merge`;
- `git reset`;
- `git commit`;
- `git push`;
- `git fetch`;
- `git pull`;
- hooks;
- arbitrary shell commands.

It performs no network access and accepts no credentials.

Environment passed to Git should be minimal and should disable pager/editor interaction. No user-controlled environment variables are forwarded as command semantics.

## TDD hostile floor

Minimum test matrix:

1. resolve exact commit from a temporary Git repository;
2. read exact historical blob after working tree later changes;
3. wrong ref -> typed refusal/unresolved, no exception leak;
4. missing blob -> unresolved;
5. path traversal -> refusal before subprocess invocation;
6. requested path outside CURRENT-ORGAN allowed roots -> refusal;
7. same SHA/path -> byte-identical repeated result;
8. mid-run branch movement does not alter a previously pinned SHA read;
9. attempts to request a write-shaped capability refuse;
10. command argv is fixed enough that filenames/ref names cannot inject shell syntax;
11. FakeAdapter behavior remains unchanged;
12. current LOADOUT.dev workflow tests remain green.

## CURRENT-ORGAN integration proof

After the adapter is independently green, one integration fixture should:

1. create a temporary Git repository containing `.live/current-organ.json` and one allowed entrypoint;
2. resolve current head through `git.resolve_ref`;
3. read the manifest at the pinned SHA;
4. resolve the allowed entrypoint at the same SHA;
5. emit the existing live-surface resolution receipt;
6. move the branch head;
7. prove the original occurrence still reads the original pinned object.

This proves:

```text
live across occurrences
pinned within an occurrence
```

without network dependence.

## Boundaries

This slice does not add:

- GitHub API access;
- network fetches;
- repository writes;
- merge authority;
- deploy/publish/send authority;
- semantic interpretation of file contents;
- automatic CURRENT-ORGAN binding for every task;
- hidden capability expansion when Git is present.

## Acceptance

Complete when the reconciled CURRENT-ORGAN floor is current and green, `LocalGitReadAdapter` passes hostile read-only tests, one real temporary-repository integration proves exact pinning across branch drift, and no write/network command is reachable from the adapter surface.

> **TOUCH THE WORLD ONCE. KEEP THE HAND OPEN. LEAVE NO FINGERPRINT ON THE SOURCE.**
