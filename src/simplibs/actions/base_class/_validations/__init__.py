from .raise_invalid_action_target import raise_invalid_action_target


_DESIGN_NOTES = """
# Action Base Validations Sub-Package

## Purpose
Internal diagnostic and validation helpers used by the `Action` base class to enforce
type safety and provide formatted diagnostics during action resolution and composition.

## Internal Components Registry

| Component                      | Type     | Description                                                                 |
| :----------------------------- | :------- | :-------------------------------------------------------------------------- |
| `raise_invalid_action_target`  | Function | Raises a formatted `ParamError` when an object cannot be converted to Action.|
"""