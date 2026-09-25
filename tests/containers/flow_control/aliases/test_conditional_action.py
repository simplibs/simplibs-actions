import pytest
from simplibs.actions.containers.flow_control.branch import branch
from simplibs.actions.containers.flow_control.aliases.conditional_action import conditional_action
from simplibs.actions.testing.assert_action_alias import assert_action_alias


def test_conditional_action_is_canonical_alias(subtests):
    # Arrange
    is_positive = lambda x: x > 0
    double = lambda x: x * 2
    negate = lambda x: -x
    action = conditional_action(
        condition=is_positive,
        then_branch=double,
        else_branch=negate,
    )

    # Act & Assert
    assert_action_alias(
        subtests,
        alias=conditional_action,
        canonical=branch,
        sample_action=action,
        sample_input=10,
        expected_output=20,
    )