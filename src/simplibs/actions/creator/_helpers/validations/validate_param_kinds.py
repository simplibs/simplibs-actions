import inspect
from typing import Any, Callable
from simplibs.exception import ParamError


def validate_param_kinds(
    params: list[inspect.Parameter],
    func: Callable[..., Any],
) -> None:
    """Validates that function parameters do not use unsupported parameter kinds."""

    # 1. Define set of unsupported parameter kinds for Action architecture
    unsupported_kinds = {
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.VAR_POSITIONAL,
        inspect.Parameter.VAR_KEYWORD,
    }

    # 2. Inspect each parameter and raise error if an unsupported kind is encountered
    for param in params:
        if param.kind in unsupported_kinds:
            raise ParamError(
                error_name="UNSUPPORTED_PARAM_KIND",
                label=f"parameter '{param.name}'",
                value=str(param.kind),
                problem=(
                    f"Function '{func.__qualname__}()' contains parameter '{param.name}' ",
                    f"with kind '{param.kind}', which is not supported by the Action architecture.",
                ),
                expected="Standard POSITION_OR_KEYWORD or KEYWORD_ONLY parameter.",
                how_to_fix=(
                    "Remove variadic (*args, **kwargs) or positional-only (before '/') parameters.",
                    "Convert input signature parameters to explicit named arguments.",
                ),
                exception=TypeError,
            )


_DESIGN_NOTES = """
# validate_param_kinds — signature kind validator

## Purpose
Enforces the signature structural contract of `create_action`. Ensures that wrapped functions
do not rely on variadic arguments (`*args`, `**kwargs`) or positional-only syntax (`/`),
maintaining predictable initialization and main payload parameter mapping.
"""