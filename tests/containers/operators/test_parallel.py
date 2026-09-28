"""
Tests for parallel — runs N actions over the same data in parallel.
"""
import pytest
from simplibs.actions.containers.operators.parallel import parallel
from simplibs.actions.containers.wrappers.lambda_action import lambda_action
from simplibs.actions.testing import assert_action
from simplibs.actions.testing.asserts.assert_action_construction import assert_action_construction


def test_parallel_runs_every_branch_over_the_same_input(subtests):
    """Verify that parallel feeds the same data to every branch and collects results in order."""
    upper = lambda_action(func=lambda x: x.upper())
    lower = lambda_action(func=lambda x: x.lower())

    action = parallel(branches=(upper, lower))

    assert_action(
        subtests,
        action,
        valid_values=["Hi"],
        expected_outputs=[("HI", "hi")],
        deep_check=False,
    )


def test_parallel_accepts_plain_callables_as_branches(subtests):
    """Verify that parallel resolves plain callables (not just Action instances) via as_action."""
    action = parallel(branches=(lambda x: x + 1, lambda x: x * 2, lambda x: x - 1))

    assert_action(
        subtests,
        action,
        valid_values=[5],
        expected_outputs=[(6, 10, 4)],
        deep_check=False,
    )


def test_parallel_single_branch_still_returns_a_one_tuple(subtests):
    """Verify that a single branch still produces a one-element tuple, not a bare value."""
    action = parallel(branches=(lambda x: x * 10,))

    assert_action(
        subtests,
        action,
        valid_values=[4],
        expected_outputs=[(40,)],
        deep_check=False,
    )


def test_parallel_rejects_invalid_branches_on_construction(subtests):
    """Verify that an empty tuple and a non-tuple value are both rejected on construction
    (the tuple_not_empty contract on the `branches` parameter)."""
    assert_action_construction(
        subtests,
        parallel,
        invalid_init_params=[
            ((), {"branches": ()}),
            ((), {"branches": []}),
        ],
        verbose=False,
    )


@pytest.mark.asyncio
async def test_parallel_acall_runs_branches_concurrently():
    """Verify that acall executes all branches concurrently via asyncio.gather."""

    async def async_upper(x: str) -> str:
        return x.upper()

    def sync_lower(x: str) -> str:
        return x.lower()

    async def async_exclaim(x: str) -> str:
        return f"{x}!"

    action = parallel(branches=(async_upper, sync_lower, async_exclaim))

    result = await action.acall("Hi")

    assert result == ("HI", "hi", "Hi!")


@pytest.mark.asyncio
async def test_parallel_acall_single_branch_returns_tuple():
    """Verify that acall with a single branch still produces a one-element tuple."""

    async def async_double(x: int) -> int:
        return x * 2

    action = parallel(branches=(async_double,))

    result = await action.acall(4)

    assert result == (8,)