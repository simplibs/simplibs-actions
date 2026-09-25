import pytest
from simplibs.actions.containers.primitives.identity import identity
from simplibs.actions.containers.primitives.aliases.pass_through import pass_through
from simplibs.actions.testing.assert_action_alias import assert_action_alias


def test_pass_through_is_canonical_alias(subtests):
    # Arrange
    action = pass_through()

    # Act & Assert
    assert_action_alias(
        subtests,
        alias=pass_through,
        canonical=identity,
        sample_action=action,
        sample_input="hello_world",
        expected_output="hello_world",
    )