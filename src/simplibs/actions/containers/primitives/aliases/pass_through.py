from ..identity import identity

pass_through = identity
"""
Alias of `identity` — returns `data` unchanged.

Init Params:
    (none)

Main Param:
    data (Any): The value returned unchanged.

Output:
    Any: The same object passed in as `data`.

Provided for pipelines that favor a more descriptive name than `identity`.
See `identity`'s own module for the canonical implementation and design
notes — `pass_through` is a pure alias, no separate behavior.
"""
