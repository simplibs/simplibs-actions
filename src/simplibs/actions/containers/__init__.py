# Composition Classes
from .operators.compose_class import ParallelCompose, SequenceCompose

# Flow Control Containers
from .flow_control import branch, for_each, guard

# Operator Containers
from .operators import fallback, parallel, sequence

# Primitive Containers
from .primitives import constant, identity

# Wrapper Containers
from .wrappers import lambda_action, log_action, retry, tap

# Aliases Sub-Package / Namespace Import
from . import flow_control, operators, primitives, wrappers

# Aggregated Aliases Namespace
class _Aliases:
    """Namespace grouping all alias functions across container sub-packages."""
    # Flow Control Aliases
    apply_to_each = flow_control.aliases.apply_to_each
    conditional_action = flow_control.aliases.conditional_action
    guarded_action = flow_control.aliases.guarded_action

    # Operator Aliases
    run_in_parallel = operators.aliases.run_in_parallel
    run_in_sequence = operators.aliases.run_in_sequence
    try_or_fallback = operators.aliases.try_or_fallback

    # Primitive Aliases
    pass_through = primitives.aliases.pass_through
    replace_with = primitives.aliases.replace_with

    # Wrapper Aliases
    callable_action = wrappers.aliases.callable_action
    log_step = wrappers.aliases.log_step
    retry_on_failure = wrappers.aliases.retry_on_failure
    run_side_effect = wrappers.aliases.run_side_effect


aliases = _Aliases()


__all__ = [
    # Composition Classes
    "ParallelCompose",
    "SequenceCompose",
    # Flow Control
    "branch",
    "for_each",
    "guard",
    # Operators
    "fallback",
    "parallel",
    "sequence",
    # Primitives
    "constant",
    "identity",
    # Wrappers
    "lambda_action",
    "log_action",
    "retry",
    "tap",
    # Aliases
    "aliases",
]


_DESIGN_NOTES = """
# Main Action Containers Package

## Purpose
The `containers` package forms the core structural foundation of the action system. It provides
a rich set of higher-order action containers that manage execution flow, error handling, batching,
parallelism, side effects, and pipeline primitive building blocks.

## Internal Sub-Packages Registry

| Sub-Package    | Type               | Description                                                                     |
| :------------- | :----------------- | :------------------------------------------------------------------------------ |
| `_helpers`     | Internal Helpers   | Private utilities for action normalization, inspection, and sequence unwrapping.|
| `flow_control` | Public Containers  | Branching (`branch`), iteration (`for_each`), and conditional evaluation (`guard`).|
| `operators`    | Public Containers  | Main composition containers (`sequence`, `parallel`, `fallback`) and classes.  |
| `primitives`   | Public Containers  | Fundamental pipeline building blocks (`identity`, `constant`).                  |
| `wrappers`     | Public Containers  | Decorating and utility containers (`lambda_action`, `log_action`, `retry`, `tap`).|
"""