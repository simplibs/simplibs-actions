from ..constant import constant

replace_with = constant
"""
Alias of `constant` — ignores `data`, always returns `value`.

Init Params:
    value (Any): The fixed value always returned.

Main Param:
    data (Any): Accepted for pipeline compatibility, never read.

Output:
    Any: `value`, unchanged.

Provided for pipelines that favor a more descriptive name than `constant`.
See `constant`'s own module for the canonical implementation and design
notes — `replace_with` is a pure alias, no separate behavior.
"""
