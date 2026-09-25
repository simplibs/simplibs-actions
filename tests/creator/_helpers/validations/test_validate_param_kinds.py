"""
Tests for validate_param_kinds — validation of allowed parameter kinds for Action source functions.
"""
import inspect

import pytest

from simplibs.actions.creator._helpers.validations.validate_param_kinds import validate_param_kinds
from simplibs.exception.exceptions import ParamError
from simplibs.exception.testing import assert_exception_function


def _valid_func(data: dict, prefix: str = "USR") -> dict:
    """Dummy function with only POSITIONAL_OR_KEYWORD parameters."""
    return data


def _positional_only_func(data, /, prefix: str = "USR") -> dict:
    """Dummy function carrying a POSITIONAL_ONLY parameter."""
    return data


def _var_positional_func(data: dict, *args) -> dict:
    """Dummy function carrying a VAR_POSITIONAL (*args) parameter."""
    return data


def _var_keyword_func(data: dict, **kwargs) -> dict:
    """Dummy function carrying a VAR_KEYWORD (**kwargs) parameter."""
    return data


@pytest.mark.parametrize("bad_func", [_positional_only_func, _var_positional_func, _var_keyword_func])
def test_validate_param_kinds(subtests, bad_func):
    """Verify that positional-only, *args, and **kwargs parameters all raise a structured ParamError."""
    bad_params = list(inspect.signature(bad_func).parameters.values())
    good_params = list(inspect.signature(_valid_func).parameters.values())

    assert_exception_function(
        subtests,
        validate_param_kinds,
        invalid_params=(bad_params, bad_func),
        valid_params=(good_params, _valid_func),
        exception_type=ParamError,
        expected="Standard POSITION_OR_KEYWORD or KEYWORD_ONLY parameter.",
        problem="which is not supported by the Action architecture",
        how_to_fix="Remove variadic (*args, **kwargs) or positional-only",
        exception=TypeError,
    )
