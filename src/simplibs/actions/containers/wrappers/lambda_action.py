import asyncio
import inspect
from typing import Any, Callable
# Outers
from ...decorator import to_action
from ...creator._helpers.validations import raise_async_action_requires_acall_error


@to_action
def lambda_action(
    data: Any,
    func: Callable[[Any], Any]
) -> Any:
    """Adapter for a raw callable that did not originate from `to_action`."""

    # 1. Guard against passing an async callable into synchronous __call__
    if inspect.iscoroutinefunction(func):
        raise_async_action_requires_acall_error(func)

    # 2. Execute plain synchronous callable
    return func(data)


async def _lambda_action_acall(self, data: Any) -> Any:
    """Async counterpart of `lambda_action`'s own body.

    `func` here is an arbitrary, per-instance callable supplied at
    construction time — unlike every other container in this package,
    its sync/async nature can't be known once and for all when the
    class itself is built (contrast `create_call`'s `is_async`, decided
    from the FIXED source function `create_action` was given). Checked
    at call time instead: a genuinely `async def` `func` is awaited
    directly, with no thread hop at all; a plain synchronous `func`
    still gets the safe to-thread bridge.
    """

    # 1. A native coroutine function — await it directly, no thread hop
    if inspect.iscoroutinefunction(self.func):
        return await self.func(data)

    # 2. A plain synchronous callable — bridge it safely via a worker thread
    return await asyncio.to_thread(self.func, data)


def _lambda_action_is_async_getter(self: Any) -> bool:
    """Dynamic is_async property getter for lambda_action instances."""
    return inspect.iscoroutinefunction(self.func)


# Attach the hand-written async counterpart and dynamic is_async property directly onto the generated class —
# see design notes for why this can't be derived generically by create_action.
lambda_action.acall = _lambda_action_acall
lambda_action.is_async = property(_lambda_action_is_async_getter)

lambda_action = lambda_action
"""
Adapter that runs a raw, one-off callable as an Action.

Init Params:
    func (Callable[[Any], Any]): Any single-argument callable — a plain
        function, or an `async def` coroutine function.

Main Param:
    data (Any): Passed straight into `func`.

Output:
    Any: `func`'s return value.

This is `Action.resolve_action`'s last-resort branch for a callable that
is neither an `Action` nor a `Rule` — typically an ad-hoc
`lambda x: x.strip()` passed directly into `>>`/`resolve_action`, with no
intent of being a named, independently documented action. Cheapest, no
dynamic class synthesis needed for one-off use.

If `func` is a coroutine function, execute this action via
`await LambdaAction(func=...).acall(data)`. Invoking synchronous `__call__`
with an `async def` function will explicitly raise a diagnostic error
instructing the caller to use `.acall()` instead.

Example:
    >>> LambdaAction(func=str.strip)("  hi  ")
    'hi'
"""


_DESIGN_NOTES = """
# lambda_action — adapter for a raw callable

## Why it stays separate even though `create_action` does "the same thing"
Not a duplicate of `create_action`'s general capability — it serves a
different purpose: it's the fallback branch `Action.resolve_action` uses
for a plain callable with no intention of being promoted into a named,
independently documented action. Cheapest, safest path for one-off use.

## Reflected operators and plain callables
`func & action`/`func | action`/`func >> action` work automatically
through this path (`resolve_action` -> `lambda_action`) with no special
interpretation needed — unlike `Rule` (where `guard` must invent a "gate"
meaning), `lambda_action` is a plain transformer, so it behaves exactly
like any other Action under `&`/`|`/`>>`.

## Why `func`'s async-ness is checked dynamically, not at class-build time
Every other container's `acall` (`branch`, `for_each`, `retry`, `tap`,
`sequence`, `parallel`, `fallback`) delegates to CHILD `Action`
instances, each of which already knows its own sync/async nature from
the moment it was built (`create_action`'s `is_async` detection, fixed
once for the whole class). `lambda_action` is different: `func` is a
raw, arbitrary callable — potentially a different one on every instance,
sync or async, with no `Action` wrapper of its own to have already made
that determination. 

Consequently, both `acall` and the `is_async` property evaluate 
`inspect.iscoroutinefunction(self.func)` dynamically:
* `is_async` is implemented as a property on the generated class, reflecting 
  whether the specific instance wraps an `async def` coroutine function or a 
  plain sync callable.
* `_lambda_action_acall` checks the same condition at call time to decide 
  whether to `await` directly or use the thread-pool bridge.

## Dynamic sync-guard against un-awaited coroutines
Previously, passing a native `async def` function into `lambda_action`
and invoking its synchronous `__call__` would silently return an un-awaited
coroutine object (`<coroutine object ...>`), leading to deferred runtime
warnings and subtle bugs during garbage collection.

To guarantee parity with classes generated by `create_action` (where `__call__`
raises for async sources), `lambda_action` inspects `func` dynamically at
call time. If `func` is a coroutine function during synchronous execution, it
immediately calls `raise_async_action_requires_acall_error(func)`, providing a
clear, instant diagnostic that instructs the caller to use `.acall()` instead.
"""