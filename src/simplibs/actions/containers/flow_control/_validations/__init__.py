from .raise_guard_failed import raise_guard_failed
from .raise_not_iterable import raise_not_iterable


_DESIGN_NOTES = """
# Flow Control Validations Sub-Package

## Purpose
Internal structured exception emission helpers dedicated to validating input data
and conditions across flow control containers.

## Internal Components Registry

| Component            | Type     | Description                                                                     |
| :------------------- | :------- | :------------------------------------------------------------------------------ |
| `raise_guard_failed` | Function | Raises a structured `ParamError` when a hard gate `guard` condition fails.      |
| `raise_not_iterable` | Function | Raises a structured `ParamError` when `for_each` receives non-iterable data.    |
"""