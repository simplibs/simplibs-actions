from .raise_invalid_predicate import raise_invalid_predicate


_DESIGN_NOTES = """
# Action Container Helper Validations Sub-Package

## Purpose
Internal structured exception emission helpers dedicated to validating condition
and predicate inputs used by container helper functions.

## Internal Components Registry

| Component                 | Type     | Description                                                                     |
| :------------------------ | :------- | :------------------------------------------------------------------------------ |
| `raise_invalid_predicate` | Function | Raises a structured `ParamError` when an input is neither a `Rule` nor callable.|
"""