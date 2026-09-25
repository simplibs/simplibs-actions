from ..fallback import fallback

try_or_fallback = fallback
"""
Alias of `fallback` — tries `action`; on failure either runs `on_error`
or returns the original data unchanged.

Init Params:
    action (Action | Rule | Callable[[Any], Any]): The primary action to
        attempt.
    on_error (Action | Rule | Callable[[Any], Any] | None): Runs instead
        of `action` if it raises.
    exceptions (type[BaseException] | tuple[type[BaseException], ...]):
        Which exception types are caught. Defaults to `Exception`.

Main Param:
    data (Any): The value passed to `action` (and to `on_error`, if used).

Output:
    Any: `action`'s result on success; `on_error`'s result, or `data`
        unchanged, on failure.

Kept as the previous (pre-merge) name of `fallback`, for anyone still
reaching for it by habit. See `fallback`'s own module for the canonical
implementation and design notes — `try_or_fallback` is a pure alias, no
separate behavior.
"""
