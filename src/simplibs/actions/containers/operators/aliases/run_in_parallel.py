from ..parallel import parallel

run_in_parallel = parallel
"""
Alias of `parallel` — runs N actions over the same data in parallel.

Init Params:
    branches (tuple[Action | Rule | Callable[[Any], Any], ...]): The
        actions to run. Must contain at least one branch.

Main Param:
    data (Any): The value passed unchanged to every branch.

Output:
    tuple[Any, ...]: One result per branch, in the same order as `branches`.

Provided for pipelines that favor a more descriptive name than `parallel`.
See `parallel`'s own module for the canonical implementation and design
notes — `run_in_parallel` is a pure alias, no separate behavior.
"""
