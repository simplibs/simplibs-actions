from typing import Any, Callable
from simplibs.validate.decorators.log_this._helpers.unwrap_log_this import unwrap_log_this
from simplibs.validate.decorators.validate_call._helpers.unwrap_validate_call import unwrap_validate_call


def unwrap_log_this_and_validate_call(
    func: Callable[..., Any]
) -> Callable[..., Any]:
    """Peel off any pre-existing @validate_call/@log_this layers, in any
    order or depth, until neither decorator's marker remains.

    Args:
        func: The callable to unwrap. May carry zero, one, or many
            interleaved `@validate_call`/`@log_this` layers, in any order.

    Returns:
        The underlying callable, guaranteed free of both decorators'
        wrapper markers.
    """

    # 1. Repeatedly unwrap both decorators until neither peels anything
    #    off anymore — a single pass of each cannot handle interleaved
    #    stacking (see design notes below).
    while True:
        unwrapped = unwrap_log_this(unwrap_validate_call(func))
        if unwrapped is func:
            return func
        func = unwrapped


_DESIGN_NOTES = """
# unwrap_log_this_and_validate_call — normalize func before wrapping it again

## The problem this solves
`create_act` embeds the function it's given as a closure variable
(`__func__`) inside a freshly generated wrapper — it has no `__wrapped__`
chain of its own pointing back at that function. If the function handed
to `create_action` had already been decorated with `@validate_call` or
`@log_this` before arriving here, that decoration would end up sealed
inside `__func__` permanently, while `create_action`'s own
`validate_call`/`log_this` application (around `act` itself) adds a
SECOND, independent layer on top. Every call would then validate/log
twice — once from the caller's own decoration, once from `create_action`'s.

## Why a fixed-point loop, not one pass of each unwrap function
`unwrap_validate_call`/`unwrap_log_this` each correctly strip their own
respective decorator's layers — but only for the markers they know how
to recognize, and only for as many layers as are contiguously stacked
under the SAME marker. A function decorated as
`@validate_call` above `@log_this` above another `@validate_call` needs
peeling in alternation: `unwrap_validate_call` strips the outer
`validate_call` layer, exposing a `log_this` layer that only
`unwrap_log_this` will recognize, which in turn exposes another
`validate_call` layer underneath. Calling each unwrap function exactly
once, in a fixed order, would miss this — it only handles layers of one
kind stacked contiguously at the very top.

The `while True` loop instead runs both unwrap functions on every pass
and only stops once a full pass changes nothing (`unwrapped is func`) —
this correctly reaches the true underlying function regardless of how
many layers of either decorator exist, or in what order they were
applied, without `create_action` ever needing to know that in advance.

## Why this lives under `resolvers/`, not `creators/`
It doesn't build a class member the way `create_init_and_slots`/
`create_call`/`create_act` do — it resolves what the *true* source
function actually is, conceptually the same kind of job
`resolve_param`/`resolve_class_name` already do (resolving which
parameter is main, resolving what the class should be named). This is
the same resolution step, just applied to the function's own identity
rather than its signature.
"""
