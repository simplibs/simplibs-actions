# 1. Base Class
from .base_class import Action

# 2. Composition Classes
from .containers.operators.compose_class import ParallelCompose, SequenceCompose

# 3. Primary Containers & Aggregated Aliases Namespace
from .containers import (
    aliases,
    branch,
    constant,
    fallback,
    for_each,
    guard,
    identity,
    lambda_action,
    log_action,
    parallel,
    retry,
    sequence,
    tap,
)

# 4. Creators & Decorators
from .creator import create_action
from .decorator import to_action


__all__ = [
    # Base
    "Action",
    # Composition Classes
    "ParallelCompose",
    "SequenceCompose",
    # Flow Control Containers
    "branch",
    "for_each",
    "guard",
    # Operator Containers
    "fallback",
    "parallel",
    "sequence",
    # Primitive Containers
    "constant",
    "identity",
    # Wrapper Containers
    "lambda_action",
    "log_action",
    "retry",
    "tap",
    # Factory & Decorator
    "create_action",
    "to_action",
    # Aggregated Aliases Namespace
    "aliases",
]


_DESIGN_NOTES = """
# Main Simplibs Actions Package

## Purpose
Root public entry point for `simplibs-actions`. Exposes the complete high-level API
surface for constructing, composing, decorating, and executing data transformation pipelines.

## Public Components Registry

| Component         | Type     | Origin Sub-Package | Description                                                               |
| :---------------- | :------- | :----------------- | :------------------------------------------------------------------------ |
| `Action`          | Class    | `base_class`       | Core abstract base class defining operator composition and execution.     |
| `SequenceCompose` | Class    | `containers`       | Intermediate lazy composition wrapper created via `>>` / `+` operators.   |
| `ParallelCompose` | Class    | `containers`       | Intermediate lazy composition wrapper created via `&` operator.           |
| `branch`          | Function | `containers`       | Soft conditional branching container (`if/then/else`).                    |
| `for_each`        | Function | `containers`       | Collection-processing container over input iterables.                      |
| `guard`           | Function | `containers`       | Hard gate container validating data against a rule before proceeding.     |
| `fallback`        | Function | `containers`       | Exception mitigation container providing alternative branch execution.    |
| `parallel`        | Function | `containers`       | Parallel branch execution container returning tuple of outputs.           |
| `sequence`        | Function | `containers`       | Sequential step execution container feeding results left-to-right.        |
| `constant`        | Function | `containers`       | Primitive container ignoring input and returning a fixed value.           |
| `identity`        | Function | `containers`       | Primitive container returning input data unchanged.                       |
| `lambda_action`   | Function | `containers`       | Wrapper transforming raw single-argument callables into Actions.          |
| `log_action`      | Function | `containers`       | Wrapper logging pipeline data without modifying the payload.             |
| `retry`           | Function | `containers`       | Wrapper executing action multiple times on specified exception catches.   |
| `tap`             | Function | `containers`       | Wrapper executing side-effect functions while passing input through.      |
| `create_action`   | Function | `creator`          | Low-level factory function synthesizing typed `Action` classes/instances. |
| `to_action`       | Function | `decorator`        | High-level decorator turning standard callables into two-phase Actions.   |
| `aliases`         | Instance | `containers`       | Aggregated namespace offering descriptive naming alternatives for containers|


## Architectural Design Decisions

1. **Single Source of Truth for Aliases**: The `aliases` namespace instance is instantiated strictly
   once within `containers/__init__.py` and simply re-exported here. This guarantees object identity
   (`actions.aliases is actions.containers.aliases`) and eliminates duplication.
2. **Flattened Public API**: All primary building blocks are re-exported at the package root
   so downstream code can import directly from `simplibs.actions`.
3. **Explicit Alias Namespacing**: Aliases are intentionally contained inside the `aliases`
   object namespace to prevent polluting the top-level namespace while providing auto-complete
   and clear intent (`actions.aliases.run_in_sequence`).
4. **Isolation of Testing Tools**: Testing utilities (`assert_action`, `assert_action_alias`)
   are strictly excluded from this root package to keep production imports light and avoid
   unnecessary test-framework dependencies in non-testing environments.
"""