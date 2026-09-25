import pytest
from simplibs.actions.containers.flow_control.for_each import for_each
from simplibs.actions.containers.flow_control.aliases.apply_to_each import apply_to_each
from simplibs.actions.testing.assert_action_alias import assert_action_alias


def test_apply_to_each_is_canonical_alias(subtests):
    # Arrange
    double = lambda x: x * 2
    action = apply_to_each(action=double)

    # Act & Assert
    assert_action_alias(
        subtests,
        alias=apply_to_each,
        canonical=for_each,
        sample_action=action,
        sample_input=[1, 2, 3],
        expected_output=[2, 4, 6],
    )