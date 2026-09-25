import pytest
from simplibs.actions.containers.flow_control.guard import guard
from simplibs.actions.containers.flow_control.aliases.guarded_action import guarded_action
from simplibs.actions.testing.assert_action_alias import assert_action_alias


def test_guarded_action_is_canonical_alias(subtests):
    # Arrange
    is_positive = lambda x: x > 0
    action = guarded_action(rule=is_positive)

    # Act & Assert
    assert_action_alias(
        subtests,
        alias=guarded_action,
        canonical=guard,
        sample_action=action,
        sample_input=42,
        expected_output=42,
    )