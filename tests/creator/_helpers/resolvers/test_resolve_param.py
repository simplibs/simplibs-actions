"""
Tests for resolve_param — splitting a function's parameters into main + others.
"""
import inspect

from simplibs.actions.creator._helpers.resolvers.resolve_param import resolve_param
from simplibs.exception.exceptions import ParamError
from simplibs.exception.testing import assert_exception_function


def _sample(data: dict, prefix: str = "USR") -> dict:
    return data


def test_resolve_param_defaults_to_first_parameter():
    """Verify that main_name=None selects the first parameter as main, the rest as others."""
    params = list(inspect.signature(_sample).parameters.values())

    main_param, other_params = resolve_param(params, None, _sample)

    assert main_param.name == "data"
    assert [p.name for p in other_params] == ["prefix"]


def test_resolve_param_honors_explicit_main_name():
    """Verify that an explicit main_name selects the matching parameter regardless of position."""
    params = list(inspect.signature(_sample).parameters.values())

    main_param, other_params = resolve_param(params, "prefix", _sample)

    assert main_param.name == "prefix"
    assert [p.name for p in other_params] == ["data"]


def test_resolve_param_raises_on_missing_main_name(subtests):
    """Verify that resolve_param raises when the explicit main_name isn't found among the params."""
    params = list(inspect.signature(_sample).parameters.values())

    assert_exception_function(
        subtests,
        resolve_param,
        invalid_params=(params, "nonexistent", _sample),
        valid_params=(params, "prefix", _sample),
        exception_type=ParamError,
        label="main parameter 'nonexistent'",
        exception=ValueError,
    )


def test_resolve_param_raises_on_empty_params(subtests):
    """Verify that resolve_param raises when the source function has no parameters at all."""
    assert_exception_function(
        subtests,
        resolve_param,
        invalid_params=([], None, _sample),
        exception_type=ParamError,
        label="function parameters",
        exception=TypeError,
    )
