"""Experimental non-canonical top-level residue probe."""


def changed_keys(before, after):
    """Return changed top-level keys without classifying their meaning."""
    keys = set(before.keys()) | set(after.keys())
    return tuple(sorted(key for key in keys if before.get(key, object()) != after.get(key, object())))
