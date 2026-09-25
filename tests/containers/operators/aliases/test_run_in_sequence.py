import pytest
from simplibs.actions.containers.operators.sequence import sequence
from simplibs.actions.containers.operators.aliases.run_in_sequence import run_in_sequence
from simplibs.actions.testing.assert_action_alias import assert_action_alias


def test_run_in_sequence_is_canonical_alias(subtests):
    # Arrange
    double = lambda x: x * 2
    increment = lambda x: x + 1
    action = run_in_sequence(steps=(double, increment))

    # Act & Assert
    assert_action_alias(
        subtests,
        alias=run_in_sequence,
        canonical=sequence,
        sample_action=action,
        sample_input=5,
        expected_output=11,
    )