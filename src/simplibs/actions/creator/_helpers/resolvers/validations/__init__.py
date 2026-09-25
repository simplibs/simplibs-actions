from .raise_main_param_not_found import raise_main_param_not_found
from .raise_no_parameters import raise_no_parameters


_DESIGN_NOTES = """
# Action Factory Resolver Validations Sub-Package

## Purpose
Structured exception emission helpers used during signature parameter resolution to ensure
target functions contain valid parameters and signatures.

## Internal Components Registry

| Component                    | Type     | Description                                                                     |
| :--------------------------- | :------- | :------------------------------------------------------------------------------ |
| `raise_main_param_not_found` | Function | Emits `ParamError` when a specified `main_param_name` is missing from signature.|
| `raise_no_parameters`        | Function | Emits `ParamError` when a function without any parameters is provided.          |
"""