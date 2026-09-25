from .assert_action_construction import assert_action_construction
from .assert_action_io_types import assert_action_io_types
from .assert_action_output import assert_action_output
from .assert_action_raises import assert_action_raises


_DESIGN_NOTES = """
# Action Testing Assertions Sub-Package

## Purpose
Provides low-level, single-responsibility assertion primitives ("blades") used internally
by the `assert_action` facade to verify individual aspects of an `Action` contract.

## Internal Components Registry

| Component                   | Type     | Description                                                                 |
| :-------------------------- | :------- | :-------------------------------------------------------------------------- |
| `assert_action_construction`| Function | Verifies constructor parameter error handling (`ParamError` raising).       |
| `assert_action_io_types`    | Function | Verifies declared input and output type annotations (`_input_type`/`_output_type`). |
| `assert_action_output`      | Function | Verifies deterministic output mapping for valid input values.               |
| `assert_action_raises`      | Function | Verifies expected exception raising for invalid input values.               |


## Architectural Design Decisions

1. **Single-Responsibility Blades**: Each assertion module in this sub-package verifies
   exactly one dimension of an Action's execution behavior or structural declaration.
2. **Facade Sub-layer**: These primitives are designed to be composed together by the
   high-level `assert_action` facade, but can also be imported individually for highly
   targeted testing scenarios.
"""