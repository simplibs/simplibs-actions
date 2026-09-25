from .raise_invalid_attempts import raise_invalid_attempts


_DESIGN_NOTES = """
# Action Wrappers Validations Sub-Package

## Purpose
Internal structured exception emission helpers dedicated to validating parameters
for wrapper containers (such as attempt limits in retry logic).

## Internal Components Registry

| Component                 | Type     | Description                                                                     |
| :------------------------ | :------- | :------------------------------------------------------------------------------ |
| `raise_invalid_attempts`  | Function | Raises a structured `ParamError` when `retry` attempts count is less than 1.   |
"""