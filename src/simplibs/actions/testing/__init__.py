from .assert_action import assert_action
from .assert_action_alias import assert_action_alias
from .asserts import (
    assert_action_construction,
    assert_action_io_types,
    assert_action_output,
    assert_action_raises,
)

__all__ = [
    "assert_action",
    "assert_action_alias",
    "assert_action_construction",
    "assert_action_io_types",
    "assert_action_output",
    "assert_action_raises",
]


_DESIGN_NOTES = """
# Action Testing Framework Sub-Package

## Purpose
Exposes public testing tools and contract assertion facades for verifying custom Actions,
library containers, and identity aliases within pytest test suites.

## Internal Components Registry

| Component                   | Type     | Description                                                                 |
| :-------------------------- | :------- | :-------------------------------------------------------------------------- |
| `assert_action`             | Function | Master contract orchestrator for testing deterministic Action behaviors.    |
| `assert_action_alias`       | Function | Verification helper for validating identity (`is`) and smoke tests of aliases.|
| `assert_action_construction`| Function | Low-level assertion verifying constructor `ParamError` handling.            |
| `assert_action_io_types`    | Function | Low-level assertion verifying declared input/output type annotations.      |
| `assert_action_output`      | Function | Low-level assertion verifying deterministic output mapping.                 |
| `assert_action_raises`      | Function | Low-level assertion verifying exception raising on invalid inputs.          |


## Architectural Design Decisions

1. **Standalone Testing Access Point**: Since testing tools are intentionally excluded from
   the main package `__init__.py` (to avoid polluting production imports with test dependencies),
   this module serves as the complete, single-import entry point (`simplibs.actions.testing`).
2. **Flattened Re-Exports via `__all__`**: All high-level facades and low-level "blades" from
   `asserts` are re-exported at this root level for clean developer experience.
3. **Ecosystem-Wide Consistency**: Mirrors the testing patterns used across `simplibs-rules`
   (`assert_rule_contract`) and `simplibs-exception` (`assert_exception_function`).
4. **Subtests Integration**: Built natively around `pytest-subtests` to ensure isolated,
   granular failure reporting for individual inputs, outputs, and type assertions.
"""