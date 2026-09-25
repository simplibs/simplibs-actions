"""
Tests for raise_invalid_action_target — validation of Action resolution targets.
"""
import pytest

from simplibs.actions.base_class._validations.raise_invalid_action_target import raise_invalid_action_target
from simplibs.exception.exceptions import ParamError
from simplibs.exception.testing import assert_exception_function


@pytest.mark.parametrize("invalid_obj", [42, 3.14, None, object()])
def test_raise_invalid_action_target(subtests, invalid_obj):
    """Verify that any non-Action, non-Rule, non-callable target raises a structured ParamError."""
    assert_exception_function(
        subtests,
        raise_invalid_action_target,
        invalid_params=(invalid_obj,),
        exception_type=ParamError,
        value=type(invalid_obj).__name__,
        label="action target candidate",
        expected="An Action instance, a Rule, or a callable function/object.",
        problem="cannot be converted into an Action",
        how_to_fix="Ensure you pass a valid callable entity",
        exception=TypeError,
    )
