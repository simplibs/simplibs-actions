from .raise_action_instance_error import raise_action_instance_error
from .validate_param_kinds import validate_param_kinds
from .validate_params_annotations import validate_params_annotations
from .validate_return_annotations import validate_return_annotations


_DESIGN_NOTES = """
# Action Factory Validations Sub-Package

## Purpose
Provides structural and signature validation helpers used during `create_action` class
synthesis. Guarantees that wrapped functions conform to parameter kind limits and feature
explicit, validatable type annotations.

## Internal Components Registry

| Component                      | Type     | Description                                                                     |
| :----------------------------- | :------- | :------------------------------------------------------------------------------ |
| `raise_action_instance_error`  | Function | Emits structured `ParamError` when an already instantiated Action is passed.    |
| `validate_param_kinds`         | Function | Ensures signatures do not use unsupported kinds (*args, **kwargs, /).          |
| `validate_params_annotations`  | Function | Validates presence and rule compatibility of parameter type annotations.        |
| `validate_return_annotations`  | Function | Validates presence and rule compatibility of return type annotations.           |
"""