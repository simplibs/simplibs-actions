from typing import Any
# Outers
from ...decorator import to_action
from .._helpers import as_action


@to_action
def fallback(
    data: Any,
    action: Any,
    on_error: Any | None = None,
    exceptions: type[BaseException] | tuple[type[BaseException], ...] = Exception,
) -> Any:
    """Tries `action`; on failure either runs `on_error` or returns the original data."""

    # 1. Attempt to execute the primary action over data
    try:
        return as_action(action)(data)

    # 2. Catch specified exception types
    except exceptions:

        # 2.1 If a fallback action is provided, execute it with data
        if on_error is not None:
            fallback_action = as_action(on_error)
            return fallback_action(data)

        # 2.2 Otherwise safely return original data unchanged
        return data


async def _fallback_acall(self, data: Any) -> Any:
    """Async counterpart of `fallback`'s own body.

    Mirrors the synchronous version's control flow exactly, one line at
    a time, substituting `await ...acall(...)` for each direct call —
    see this module's own design notes for why that substitution alone
    is necessary rather than optional.
    """

    # 1. Attempt to execute the primary action over data
    try:
        return await as_action(self.action).acall(data)

    # 2. Catch specified exception types
    except self.exceptions:

        # 2.1 If a fallback action is provided, execute it with data
        if self.on_error is not None:
            return await as_action(self.on_error).acall(data)

        # 2.2 Otherwise safely return original data unchanged
        return data


# Attach the hand-written async counterpart directly onto the generated class —
# see design notes for why this can't be derived generically by create_action.
fallback.acall = _fallback_acall

fallback = fallback
"""
Tries `action` over `data`; on failure either runs `on_error` or returns
the original `data` unchanged.

Init Params:
    action (Action | Rule | Callable[[Any], Any]): The primary action to
        attempt.
    on_error (Action | Rule | Callable[[Any], Any] | None): Runs instead
        of `action` if it raises. If omitted, `data` is returned unchanged
        on failure.
    exceptions (type[BaseException] | tuple[type[BaseException], ...]):
        Which exception types are caught. Defaults to `Exception` — narrow
        this whenever possible so real bugs inside `action` are not
        silently swallowed as "expected failure".

Main Param:
    data (Any): The value passed to `action` (and to `on_error`, if used).

Output:
    Any: `action`'s result on success; `on_error`'s result, or `data`
        unchanged, on failure.

Merges what used to be two separate containers (`Try`/`Fallback`) into
one: `on_error=None` behaves like the old `Try` without a catch action
(returns `data`); `on_error=<action>` behaves like the old `Fallback`,
now with an optional `exceptions` filter for both cases at once.
Callable both synchronously (`fallback(action=..., ...)(data)`) and
asynchronously (`await fallback(action=..., ...).acall(data)`).

Example:
    >>> fallback(action=risky_parse, on_error=default_value)(raw_input)
"""


_DESIGN_NOTES = """
# fallback — merges Try + Fallback

## Why one function instead of two classes
`Try` and `Fallback` were two names for the same "attempt / do something
else on failure" idea. `Fallback` could not restrict which exception
types it caught (always `except Exception`, including programmer
errors); `Try` without a catch action returned the original data.
`fallback` unifies both, with an optional `exceptions` filter shared by
both use cases.

## `except exceptions` — deliberately broad default
The default `exceptions=Exception` catches almost anything, including
programmer errors inside `action`, not just expected failures. Kept as
the default for backward-compatible `Try` behavior, but callers should
narrow `exceptions` whenever possible (`exceptions=ValueError`, etc.) so
`fallback` doesn't hide real bugs under an "expected failure" label.

## No flattening needed for `|`
Unlike `parallel`, nesting `fallback` calls behaves identically whether
grouped as `(a | b) | c` or `a | (b | c)` — sequential try/except is
naturally associative regardless of nesting depth. No compose_class
counterpart exists for this reason; there is nothing broken to fix.

## Why `acall` is hand-attached here too
Same underlying reason as `sequence`/`parallel`: `fallback`'s own source
function is plain `def`, and `Action`'s default `acall` would run the
whole try/except inside one thread, calling each child's synchronous
`__call__` rather than its `.acall(...)` — which would immediately break
the moment `action` or `on_error` turns out to be built from an
`async def` source (that child's own `__call__` is designed to raise —
see `create_call`'s design notes). `_fallback_acall` mirrors the sync
body exactly, one line at a time, substituting `await ...acall(...)` for
each direct call — same control flow, same exception handling, just
async-aware at each step.
"""
