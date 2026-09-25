# Outers
from ...base_class import Action


as_action = Action.resolve_action
"""Module-level alias for `Action.resolve_action`.

Provides a clean, self-describing shorthand within container implementations,
eliminating the need to repeatedly access the static method via `Action.resolve_action(...)`.
"""


_DESIGN_NOTES = """
# as_action — module-level alias for Action.resolve_action

## Purpose
Every container that accepts "something runnable" (`then_branch`, `action`,
`on_error`, individual `sequence`/`parallel` steps...) needs to resolve a
given object into a uniform `Action` instance.
`Action.resolve_action` houses the core resolution logic. `as_action` serves
as a module-level alias to avoid repeated, verbose access via the class name
(`Action.resolve_action`) across container modules, making the call sites
substantially more self-describing and expressive.

## Why a direct assignment alias, not a wrapping function
No wrapper overhead or duplicate logic — all resolution mechanics (detecting
`Action`/`Rule`/callable and adapting accordingly) remain strictly encapsulated
inside `Action.resolve_action`. Assigning `as_action = Action.resolve_action`
directly guarantees zero execution overhead while retaining full IDE signature
hints, docstrings, and type safety.
"""