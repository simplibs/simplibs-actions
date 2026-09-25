from typing import Any
# Outers
from ...decorator import to_action
from .._helpers import as_action
# Inners
from ._validations import raise_invalid_attempts


@to_action
def retry(
    data: Any,
    action: Any,
    attempts: int = 3,
    exceptions: type[BaseException] | tuple[type[BaseException], ...] = Exception,
) -> Any:
    """Retries `action` up to `attempts` times total on failure."""

    # 1. Validate minimum required attempt count
    if attempts < 1:
        raise_invalid_attempts(attempts)

    # 2. Initialize tracking variable for last caught exception and normalize action
    last_exception: Exception | None = None
    inner = as_action(action)

    # 3. Repeatedly attempt execution up to `attempts` limit
    for _ in range(attempts):
        try:
            return inner(data)
        except exceptions as exc:
            last_exception = exc

    # 4. Re-raise the last caught exception when all attempts are exhausted
    raise last_exception


retry = retry
"""
Retries `action` over `data` up to `attempts` times total on failure.

Init Params:
    action (Action | Rule | Callable[[Any], Any]): The action to retry.
    attempts (int): Total number of attempts, not extra retries beyond
        the first (`attempts=3` means 3 tries total). Must be >= 1.
    exceptions (type[BaseException] | tuple[type[BaseException], ...]):
        Which exception types trigger a retry. Defaults to `Exception` —
        narrow this whenever possible so errors meant to fail immediately
        don't get silently retried.

Main Param:
    data (Any): The value passed to `action` on every attempt.

Output:
    Any: `action`'s result from the first successful attempt.

Raises the last caught exception if every attempt fails.

Example:
    >>> retry(action=flaky_call, attempts=5)(payload)
"""


_DESIGN_NOTES = """
# retry — retries an action on failure

## `attempts < 1` guard
Delegates validation to `raise_invalid_attempts`. Without an early guard,
`attempts=0` means `range(0)` never runs, `last_exception` stays `None`,
and `raise last_exception` becomes `raise None` -> `TypeError: exceptions
must derive from BaseException` — a confusing secondary error instead of
a clear diagnostic.

## `attempts`, not `retries`
`retries=3` reads as "3 retries on top of the first attempt", but the
real meaning was always "3 attempts total" — named accordingly.

## `exceptions` filter
Without it, `retry` would retry even on errors meant to fail immediately
(a programmer error inside `action`, not a transient/expected failure).
Default stays broad (`Exception`); narrow it whenever possible, same
consideration as `fallback`.
"""