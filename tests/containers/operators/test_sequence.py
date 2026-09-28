"""
Tests for sequence — chains any number of steps left to right.
"""
import pytest
from simplibs.actions.containers.operators.sequence import sequence
from simplibs.actions.containers.wrappers.lambda_action import lambda_action
from simplibs.actions.testing import assert_action
from simplibs.actions.testing.asserts.assert_action_construction import assert_action_construction


def test_sequence_chains_steps_left_to_right(subtests):
    """Verify that sequence threads data through each step in order."""
    strip = lambda_action(func=lambda x: x.strip())
    upper = lambda_action(func=lambda x: x.upper())

    action = sequence(steps=(strip, upper))

    assert_action(
        subtests,
        action,
        valid_values=["  hello  "],
        expected_outputs=["HELLO"],
        deep_check=False,
    )


def test_sequence_accepts_plain_callables_as_steps(subtests):
    """Verify that sequence resolves plain callables (not just Action instances) via as_action."""
    action = sequence(steps=(lambda x: x + 1, lambda x: x * 2))

    assert_action(
        subtests,
        action,
        valid_values=[3],
        expected_outputs=[8],
        deep_check=False,
    )


def test_sequence_single_step_just_runs_that_step(subtests):
    """Verify that a sequence of exactly one step runs that one step, nothing more."""
    action = sequence(steps=(lambda x: x * 10,))

    assert_action(
        subtests,
        action,
        valid_values=[4],
        expected_outputs=[40],
        deep_check=False,
    )


def test_sequence_rejects_invalid_steps_on_construction(subtests):
    """Verify that an empty tuple and a non-tuple value are both rejected on construction
    (the tuple_not_empty contract on the `steps` parameter)."""
    assert_action_construction(
        subtests,
        sequence,
        invalid_init_params=[
            ((), {"steps": ()}),
            ((), {"steps": []}),
        ],
        verbose=False,
    )


@pytest.mark.asyncio
async def test_sequence_acall_chains_async_and_sync_steps():
    """Verify that acall threads data through mixed async/sync steps in order."""

    async def async_strip(x: str) -> str:
        return x.strip()

    def sync_upper(x: str) -> str:
        return x.upper()

    async def async_exclaim(x: str) -> str:
        return f"{x}!"

    action = sequence(steps=(async_strip, sync_upper, async_exclaim))

    result = await action.acall("  hello  ")

    assert result == "HELLO!"


@pytest.mark.asyncio
async def test_sequence_acall_single_async_step():
    """Verify that acall handles a single async step properly."""

    async def async_double(x: int) -> int:
        return x * 2

    action = sequence(steps=(async_double,))

    result = await action.acall(5)

    assert result == 10