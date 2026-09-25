import pytest
from simplibs.actions.containers.primitives.constant import constant
from simplibs.actions.containers.primitives.aliases.replace_with import replace_with
from simplibs.actions.testing.assert_action_alias import assert_action_alias


def test_replace_with_is_canonical_alias(subtests):
    # Arrange
    action = replace_with(value=42)

    # Act & Assert
    assert_action_alias(
        subtests,
        alias=replace_with,
        canonical=constant,
        sample_action=action,
        sample_input="ignored_input",
        expected_output=42,
    )