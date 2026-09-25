"""
Tests for parallel — runs N actions over the same data in parallel.
"""
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
    )


def test_parallel_accepts_plain_callables_as_branches(subtests):
    """Verify that parallel resolves plain callables (not just Action instances) via as_action."""
    action = parallel(branches=(lambda x: x + 1, lambda x: x * 2, lambda x: x - 1))

    assert_action(
        subtests,
        action,
        valid_values=[5],
        expected_outputs=[(6, 10, 4)],
    )


def test_parallel_single_branch_still_returns_a_one_tuple(subtests):
    """Verify that a single branch still produces a one-element tuple, not a bare value."""
    action = parallel(branches=(lambda x: x * 10,))

    assert_action(
        subtests,
        action,
        valid_values=[4],
        expected_outputs=[(40,)],
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