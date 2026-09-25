import pytest
from simplibs.actions.containers.wrappers.tap import tap
from simplibs.actions.containers.wrappers.aliases.run_side_effect import run_side_effect
from simplibs.actions.testing.assert_action_alias import assert_action_alias


def test_run_side_effect_is_canonical_alias(subtests):
    # Arrange
    side_effects = []
    capture_func = lambda x: side_effects.append(x)
    action = run_side_effect(action=capture_func)

    # Act & Assert
    assert_action_alias(
        subtests,
        alias=run_side_effect,
        canonical=tap,
        sample_action=action,
        sample_input="payload",
        expected_output="payload",
    )
    assert side_effects == ["payload"]