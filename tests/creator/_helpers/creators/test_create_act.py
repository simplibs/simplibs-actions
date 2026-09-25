"""
Tests for create_act — synthesized `act` carrying func's own real signature.
"""
import inspect

from simplibs.actions.creator._helpers.creators.create_act import create_act


def _sample(data: dict, prefix: str = "USR") -> dict:
    """Prefix-tag a data dict."""
    return {**data, "prefix": prefix}


def test_create_act_calls_source_function_directly():
    """Verify that act carries func's exact signature (no extra `self`) and calls func directly."""
    params = list(inspect.signature(_sample).parameters.values())
    main_param, other_params = params[0], params[1:]
    return_annotation = inspect.signature(_sample).return_annotation

    act = create_act(main_param, other_params, return_annotation, _sample)

    result = act(data={"name": "Alice"}, prefix="ADMIN")

    assert result == {"name": "Alice", "prefix": "ADMIN"}


def test_create_act_honors_default_values():
    """Verify that act preserves func's own default values for non-main parameters."""
    params = list(inspect.signature(_sample).parameters.values())
    main_param, other_params = params[0], params[1:]
    return_annotation = inspect.signature(_sample).return_annotation

    act = create_act(main_param, other_params, return_annotation, _sample)

    assert act(data={"name": "Bob"}) == {"name": "Bob", "prefix": "USR"}


def test_create_act_carries_func_metadata():
    """Verify that act inherits func's docstring and __name__/__qualname__ (never 'act')."""
    params = list(inspect.signature(_sample).parameters.values())
    main_param, other_params = params[0], params[1:]
    return_annotation = inspect.signature(_sample).return_annotation

    act = create_act(main_param, other_params, return_annotation, _sample)

    assert act.__doc__ == _sample.__doc__
    assert act.__name__ == "_sample"
    assert act.__qualname__ == "_sample"
