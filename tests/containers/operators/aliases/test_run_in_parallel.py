import pytest
from simplibs.actions.containers.operators.parallel import parallel
from simplibs.actions.containers.operators.aliases.run_in_parallel import run_in_parallel
from simplibs.actions.testing.assert_action_alias import assert_action_alias


def test_run_in_parallel_is_canonical_alias(subtests):
    # Arrange
    double = lambda x: x * 2
    increment = lambda x: x + 1
    action = run_in_parallel(branches=(double, increment))

    # Act & Assert
    assert_action_alias(
        subtests,
        alias=run_in_parallel,
        canonical=parallel,
        sample_action=action,
        sample_input=5,
        expected_output=(10, 6),
    )