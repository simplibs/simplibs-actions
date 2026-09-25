import pytest
from simplibs.actions.containers.wrappers.lambda_action import lambda_action
from simplibs.actions.containers.wrappers.aliases.callable_action import callable_action
from simplibs.actions.testing.assert_action_alias import assert_action_alias


def test_callable_action_is_canonical_alias(subtests):
    # Arrange
    strip_func = lambda s: s.strip()
    action = callable_action(func=strip_func)

    # Act & Assert
    assert_action_alias(
        subtests,
        alias=callable_action,
        canonical=lambda_action,
        sample_action=action,
        sample_input="  hello world  ",
        expected_output="hello world",
    )