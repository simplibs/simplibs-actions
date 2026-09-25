import inspect


EMPTY = inspect.Parameter.empty


_DESIGN_NOTES = """
# EMPTY — shared alias for inspect.Parameter.empty

## Purpose
`inspect.Parameter.empty` (the same sentinel object as `inspect.Signature.empty`)
is used everywhere signature introspection needs to ask "does this
parameter/return value actually carry an annotation or default, or is
that slot simply unset?" Every helper under `_create_action/` (`resolve_param`,
`create_init_and_slots`, `create_call`, `create_act`) needs this same
sentinel repeatedly — importing the full `inspect` module just to write
`inspect.Parameter.empty` at every call site is more ceremony than the
check deserves.

## Why `Parameter.empty`, not `Signature.empty`
Both names point at the exact same sentinel object in CPython
(`inspect.Signature.empty is inspect.Parameter.empty`), so the choice is
purely cosmetic. `Parameter.empty` reads more naturally at every call
site in this package, since every check here is phrased as "does this
*parameter* have a default/annotation" — `return_annotation` is
technically a `Signature` attribute, not a `Parameter`, but comparing it
against `EMPTY` reads the same either way, and using one imported name
everywhere avoids a pointless second import.

## Why a bare alias, not a wrapper function
There is nothing to wrap — `EMPTY` is a sentinel value compared with
`is`, not a callable. A function like `is_empty(x)` would be one extra
indirection with no benefit over `x is EMPTY`, the standard idiom
`inspect` itself expects call sites to use.

## Why it lives under `constants/`, not directly under `_create_action/`
Grouped with any other cross-cutting constant this package accumulates
later, rather than sitting as a lone top-level module — a dedicated
`constants` package keeps `_create_action/`'s top level reserved for
actual behavior (`creators/`, `resolvers/`), not miscellaneous shared
values.
"""
