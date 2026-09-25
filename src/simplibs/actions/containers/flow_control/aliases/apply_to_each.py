from ..for_each import for_each

apply_to_each = for_each
"""
Alias of `for_each` — applies `action` to every item of an iterable input.

Init Params:
    action (Action | Rule | Callable[[Any], Any]): Runs once per item.

Main Param:
    data (Iterable[Any]): The collection whose items are processed.

Output:
    list[Any]: One result per input item, in order.

Provided for pipelines that favor a more descriptive name than `for_each`.
See `for_each`'s own module for the canonical implementation and design
notes — `apply_to_each` is a pure alias, no separate behavior.
"""
