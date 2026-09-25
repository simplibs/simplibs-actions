"""
Tests for SequenceCompose — the self-flattening Sequence used by Action.then / `>>`.
"""
from simplibs.actions.containers.operators.compose_class.SequenceCompose import SequenceCompose
from simplibs.actions.containers.operators.sequence import sequence
from simplibs.actions.containers.wrappers.lambda_action import lambda_action


def _make(fn):
    return lambda_action(func=fn)


def test_sequence_compose_is_a_sequence_subclass():
    """Verify that SequenceCompose is a subclass of sequence (same construction shape)."""
    assert issubclass(SequenceCompose, sequence)


def test_compose_wraps_two_plain_actions_as_two_flat_steps():
    """Verify that composing two ordinary actions produces exactly two steps, and the right result."""
    a = _make(lambda x: x + 1)
    b = _make(lambda x: x * 2)

    composed = SequenceCompose.compose(a, b)

    assert isinstance(composed, SequenceCompose)
    assert composed.steps == (a, b)
    assert composed(3) == 8  # (3 + 1) * 2


def test_compose_flattens_when_left_operand_is_already_composed():
    """Verify that composing onto an existing SequenceCompose flattens instead of nesting."""
    a = _make(lambda x: x + 1)
    b = _make(lambda x: x * 2)
    c = _make(lambda x: x - 3)

    ab = SequenceCompose.compose(a, b)
    abc = SequenceCompose.compose(ab, c)

    assert isinstance(abc, SequenceCompose)
    assert abc.steps == (a, b, c)
    assert abc(3) == 5  # ((3 + 1) * 2) - 3


def test_compose_flattens_when_right_operand_is_already_composed():
    """Verify that composing an existing SequenceCompose in as the second operand flattens too."""
    a = _make(lambda x: x + 1)
    b = _make(lambda x: x * 2)
    c = _make(lambda x: x - 3)

    bc = SequenceCompose.compose(b, c)
    abc = SequenceCompose.compose(a, bc)

    assert isinstance(abc, SequenceCompose)
    assert abc.steps == (a, b, c)


def test_compose_flattens_when_both_operands_are_already_composed():
    """Verify that merging two existing SequenceCompose instances produces one flat instance."""
    a = _make(lambda x: x + 1)
    b = _make(lambda x: x * 2)
    c = _make(lambda x: x - 1)
    d = _make(lambda x: x - 2)

    ab = SequenceCompose.compose(a, b)
    cd = SequenceCompose.compose(c, d)
    abcd = SequenceCompose.compose(ab, cd)

    assert isinstance(abcd, SequenceCompose)
    assert abcd.steps == (a, b, c, d)


def test_rshift_operator_end_to_end_produces_one_flat_sequence_compose():
    """Integration test: chaining via `>>` (Action.then) must go through compose() and stay flat."""
    a = _make(lambda x: x + 1)
    b = _make(lambda x: x * 2)
    c = _make(lambda x: x - 3)

    pipeline = a >> b >> c

    assert isinstance(pipeline, SequenceCompose)
    assert len(pipeline.steps) == 3
    assert pipeline(5) == 9  # ((5 + 1) * 2) - 3