"""
Tests for raise_action_instance_error — guard against an already-instantiated Action passed to create_action.
"""
from simplibs.actions.containers.primitives.identity import identity
from simplibs.actions.creator._helpers.validations.raise_action_instance_error import raise_action_instance_error
from simplibs.exception.exceptions import ParamError
from simplibs.exception.testing import assert_exception_function


def test_raise_action_instance_error(subtests):
    """Verify that an already-instantiated Action raises a structured ParamError."""
    instance = identity()

    assert_exception_function(
        subtests,
        raise_action_instance_error,
        invalid_params=(instance,),
        exception_type=ParamError,
        value=type(instance).__name__,
        label="func",
        expected="A function, callable object, or uninstantiated Action class type.",
        problem="Received an instantiated Action",
        how_to_fix="Pass the raw function or class type directly",
        exception=TypeError,
    )
