import inspect
from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_async_action_requires_acall_error(action_or_func: Any) -> NoReturn:
    """Raise ParamError when an async-sourced Action's synchronous __call__ is invoked.

    An Action built from an `async def` source function (or a raw async callable
    passed to `lambda_action`) has no meaningful synchronous result to return —
    calling it via `action(data)` would otherwise silently return an un-awaited
    coroutine instead of the actual value. Raising here turns that into a clear,
    actionable error at the call site rather than a confusing downstream
    comparison failure or a "coroutine was never awaited" warning.
    """

    # 1. Resolve human-readable name whether an instance or raw callable was passed
    if inspect.isroutine(action_or_func) or hasattr(action_or_func, "__name__"):
        name = getattr(action_or_func, "__name__", str(action_or_func))
    else:
        name = type(action_or_func).__name__

    # 2. Raise structured ParamError wrapping a TypeError exception
    raise ParamError(
        error_name="ASYNC_ACTION_REQUIRES_ACALL",
        label="__call__",
        value=name,
        problem=(
            f"'{name}' wraps an async source function and cannot be "
            f"called synchronously via __call__.",
        ),
        expected="An async caller using `await action.acall(data)`.",
        how_to_fix=(
            "Call this action with `await action.acall(data)` instead of `action(data)`.",
        ),
        exception=TypeError,
    )


_DESIGN_NOTES = """
# raise_async_action_requires_acall_error — diagnostic for the sync/async call mismatch

## Purpose
Called from the generated `__call__` of any Action built from an `async def` source
function (see `create_call`'s own design notes) AND from `lambda_action` when passed
an async callable. Without this guard, `action(data)` on such an Action would return
a coroutine object rather than the actual result — a silent, easy-to-miss bug (a
stale-looking value that compares unequal to everything, plus a "coroutine was never
awaited" warning at garbage collection time, far from the actual call site). Raising
immediately turns that into one clear, actionable error exactly where the mistake was made.

## FlexibleTarget Resolution
Supports both instantiated `Action` objects (where `type(self).__name__` identifies the
generated Action class) and raw async callables passed directly to `lambda_action`
(where `__name__` identifies the underlying coroutine function).
"""