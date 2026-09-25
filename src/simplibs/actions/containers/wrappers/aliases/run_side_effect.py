from ..tap import tap

run_side_effect = tap
"""
Alias of `tap` — runs `action` as a side effect over `data`, returns
`data` unchanged.

Init Params:
    action (Action | Rule | Callable[[Any], Any]): Runs for its side
        effect; its return value is discarded.

Main Param:
    data (Any): The value observed by `action` and returned unchanged.

Output:
    Any: The same `data`, unchanged.

Provided for pipelines that favor a more descriptive name than `tap`.
See `tap`'s own module for the canonical implementation and design
notes — `run_side_effect` is a pure alias, no separate behavior.
"""
