from ..sequence import sequence

run_in_sequence = sequence
"""
Alias of `sequence` — chains any number of steps left to right.

Init Params:
    steps (tuple[Action | Rule | Callable[[Any], Any], ...]): The steps to
        run in order. Must contain at least one step.

Main Param:
    data (Any): The initial input fed to the first step.

Output:
    Any: The final step's return value.

Provided for pipelines that favor a more descriptive name than `sequence`.
See `sequence`'s own module for the canonical implementation and design
notes — `run_in_sequence` is a pure alias, no separate behavior.
"""
