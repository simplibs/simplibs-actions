"""
Tests for create_call — synthesized __call__ that delegates into self.act(...).
"""
import inspect

from simplibs.actions.creator._helpers.creators.create_call import create_call


def _sample(data: dict, prefix: str = "USR") -> dict:
    return data


def test_create_call_forwards_main_param_and_bound_attributes_to_act():
    """Verify that __call__ forwards its main argument plus self's bound attributes into self.act(...)."""
    params = list(inspect.signature(_sample).parameters.values())
    main_param, other_params = params[0], params[1:]
    return_annotation = inspect.signature(_sample).return_annotation

    call = create_call(main_param, other_params, return_annotation)

    captured = {}

    class _Dummy:
        prefix = "ADMIN"

        def act(self, **kwargs):
            captured.update(kwargs)
            return kwargs

    instance = _Dummy()
    result = call(instance, {"name": "Alice"})

    assert captured == {"data": {"name": "Alice"}, "prefix": "ADMIN", "_validate_call": True}
    assert result == captured


def test_create_call_docstring_describes_param_and_return_type():
    """Verify that the generated __call__ carries a docstring naming the param/return types."""
    params = list(inspect.signature(_sample).parameters.values())
    main_param, other_params = params[0], params[1:]
    return_annotation = inspect.signature(_sample).return_annotation

    call = create_call(main_param, other_params, return_annotation)

    assert "data" in call.__doc__
    assert "dict" in call.__doc__
