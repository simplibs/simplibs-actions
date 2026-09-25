"""
Tests for Action — the abstract base class: resolve_action + operator-based composition.

NOTE: the `rule & action` / `rule | action` reflected-operator tests assume Rule.__and__/
__or__ decline (return NotImplemented) when the other operand carries `__not_rule__`, per
the design comment in Action.py, falling back to Action.__rand__/__ror__. If Rule's actual
behavior differs, those two assertions will need adjusting.
"""
import pytest

from simplibs.actions.base_class import Action
from simplibs.actions.containers.flow_control.guard import guard
from simplibs.actions.containers.operators.compose_class.ParallelCompose import ParallelCompose
from simplibs.actions.containers.operators.compose_class.SequenceCompose import SequenceCompose
from simplibs.actions.containers.wrappers.lambda_action import lambda_action
from simplibs.exception.exceptions import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.rules import is_integer


def test_resolve_action_returns_action_instance_unchanged():
    """Verify that an existing Action instance passes through resolve_action untouched."""
    instance = lambda_action(func=lambda x: x)
    assert Action.resolve_action(instance) is instance


def test_resolve_action_wraps_rule_in_guard():
    """Verify that a Rule instance is wrapped into a guard Action."""
    resolved = Action.resolve_action(is_integer)
    assert isinstance(resolved, guard)


def test_resolve_action_wraps_plain_callable_in_lambda_action():
    """Verify that a plain callable is wrapped into a lambda_action Action."""
    resolved = Action.resolve_action(lambda x: x + 1)
    assert isinstance(resolved, lambda_action)
    assert resolved(5) == 6


def test_resolve_action_rejects_non_callable(subtests):
    """Verify that a non-Action, non-Rule, non-callable target raises a structured ParamError."""
    assert_exception_function(
        subtests,
        Action.resolve_action,
        invalid_params=(42,),
        exception_type=ParamError,
        label="action target candidate",
        exception=TypeError,
    )


def test_rshift_chains_into_flat_sequence_compose():
    """Verify that `>>` chains two actions into a SequenceCompose that runs left to right."""
    double = lambda_action(func=lambda x: x * 2)
    add_one = lambda_action(func=lambda x: x + 1)

    pipeline = double >> add_one

    assert isinstance(pipeline, SequenceCompose)
    assert pipeline(5) == 11


def test_rshift_flattens_three_way_chain_into_one_sequence():
    """Verify that chaining three actions produces one flat SequenceCompose, not nested ones."""
    a = lambda_action(func=lambda x: x + 1)
    b = lambda_action(func=lambda x: x * 2)
    c = lambda_action(func=lambda x: x - 3)

    pipeline = a >> b >> c

    assert isinstance(pipeline, SequenceCompose)
    assert len(pipeline.steps) == 3
    assert pipeline(5) == 9  # ((5 + 1) * 2) - 3


def test_and_runs_both_actions_in_parallel_and_flattens():
    """Verify that `&` runs both actions over the same input and flattens into ParallelCompose."""
    double = lambda_action(func=lambda x: x * 2)
    square = lambda_action(func=lambda x: x * x)

    pipeline = double & square

    assert isinstance(pipeline, ParallelCompose)
    assert pipeline(3) == (6, 9)


def test_or_runs_fallback_action_on_failure():
    """Verify that `|` runs the right-hand action when the left-hand one raises."""

    def _boom(_x):
        raise ValueError("boom")

    failing = lambda_action(func=_boom)
    safe = lambda_action(func=lambda x: x)

    pipeline = failing | safe

    assert pipeline(7) == 7


def test_then_is_equivalent_to_rshift():
    """Verify that `.then(...)` produces the same composition as the `>>` operator."""
    double = lambda_action(func=lambda x: x * 2)
    add_one = lambda_action(func=lambda x: x + 1)

    via_then = double.then(add_one)
    via_operator = double >> add_one

    assert via_then(5) == via_operator(5) == 11


def test_rrshift_supports_rule_then_action():
    """Verify that `rule >> action` first verifies the rule, then continues with the action."""
    add_one = lambda_action(func=lambda x: x + 1)

    pipeline = is_integer >> add_one

    assert pipeline(5) == 6
    with pytest.raises(Exception):
        pipeline("not-an-int")


def test_rand_supports_rule_and_action():
    """Verify that `rule & action` verifies the rule AND runs the action, both over the same input."""
    double = lambda_action(func=lambda x: x * 2)

    pipeline = is_integer & double

    assert pipeline(4) == (4, 8)
