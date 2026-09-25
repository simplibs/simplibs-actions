from ..retry import retry

retry_on_failure = retry
"""
Alias of `retry` — retries `action` over `data` up to `attempts` times
total on failure.

Init Params:
    action (Action | Rule | Callable[[Any], Any]): The action to retry.
    attempts (int): Total number of attempts. Must be >= 1.
    exceptions (type[BaseException] | tuple[type[BaseException], ...]):
        Which exception types trigger a retry.

Main Param:
    data (Any): The value passed to `action` on every attempt.

Output:
    Any: `action`'s result from the first successful attempt.

Provided for pipelines that favor a more descriptive name than `retry`.
See `retry`'s own module for the canonical implementation and design
notes — `retry_on_failure` is a pure alias, no separate behavior.
"""
