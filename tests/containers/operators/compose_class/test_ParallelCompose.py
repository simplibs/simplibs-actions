"""
Tests for ParallelCompose — the self-flattening Parallel used by Action.__and__ / `&`.
"""
from simplibs.actions.containers.operators.compose_class.ParallelCompose import ParallelCompose
from simplibs.actions.containers.operators.parallel import parallel
from simplibs.actions.containers.wrappers.lambda_action import lambda_action


def _make(fn):
    return lambda_action(func=fn)


def test_parallel_compose_is_a_parallel_subclass():
    """Verify that ParallelCompose is a subclass of parallel (same construction shape)."""
    assert issubclass(ParallelCompose, parallel)


def test_compose_wraps_two_plain_actions_as_two_flat_branches():
    """Verify that composing two ordinary actions produces exactly two branches, and a flat result."""
    double = _make(lambda x: x * 2)
    square = _make(lambda x: x * x)

    composed = ParallelCompose.compose(double, square)

    assert isinstance(composed, ParallelCompose)
    assert composed.branches == (double, square)
    assert composed(3) == (6, 9)


def test_compose_flattens_when_left_operand_is_already_composed():
    """Verify that the real bug this class fixes stays fixed: no nested tuple in the output shape."""
    a = _make(lambda x: x + 1)
    b = _make(lambda x: x * 2)
    c = _make(lambda x: x - 1)

    ab = ParallelCompose.compose(a, b)
    abc = ParallelCompose.compose(ab, c)

    assert isinstance(abc, ParallelCompose)
    assert abc.branches == (a, b, c)
    # The shape must stay flat: (r_a, r_b, r_c), never ((r_a, r_b), r_c).
    assert abc(3) == (4, 6, 2)


def test_compose_flattens_when_right_operand_is_already_composed():
    """Verify that an existing ParallelCompose as the second operand flattens too."""
    a = _make(lambda x: x + 1)
    b = _make(lambda x: x * 2)
    c = _make(lambda x: x - 1)

    bc = ParallelCompose.compose(b, c)
    abc = ParallelCompose.compose(a, bc)

    assert isinstance(abc, ParallelCompose)
    assert abc.branches == (a, b, c)
    assert abc(3) == (4, 6, 2)


def test_compose_flattens_when_both_operands_are_already_composed():
    """Verify that merging two existing ParallelCompose instances produces one flat instance."""
    a = _make(lambda x: x + 1)
    b = _make(lambda x: x * 2)
    c = _make(lambda x: x - 1)
    d = _make(lambda x: x - 2)

    ab = ParallelCompose.compose(a, b)
    cd = ParallelCompose.compose(c, d)
    abcd = ParallelCompose.compose(ab, cd)

    assert isinstance(abcd, ParallelCompose)
    assert abcd.branches == (a, b, c, d)


def test_and_operator_end_to_end_produces_one_flat_parallel_compose():
    """Integration test: composing via `&` (Action.__and__) must go through compose() and stay flat."""
    a = _make(lambda x: x + 1)
    b = _make(lambda x: x * 2)
    c = _make(lambda x: x - 1)

    pipeline = a & b & c

    assert isinstance(pipeline, ParallelCompose)
    assert len(pipeline.branches) == 3
    assert pipeline(3) == (4, 6, 2)