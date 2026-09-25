from ..guard import guard

guarded_action = guard
"""
Alias of `guard` — hard gate, passes `data` through unchanged if `rule`
holds, otherwise raises.

Init Params:
    rule (Rule | Callable[[Any], bool]): The predicate `data` must satisfy.

Main Param:
    data (Any): The value being checked against `rule`.

Output:
    Any: The original `data`, unchanged, if `rule` holds.

Provided for pipelines that favor a more descriptive name than `guard`.
See `guard`'s own module for the canonical implementation and design
notes — `guarded_action` is a pure alias, no separate behavior.
"""
