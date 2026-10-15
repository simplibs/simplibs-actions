import asyncio
from typing import Any, Iterable
# Outers
from ...decorator import to_action
from .._helpers import as_action
# Inners
from ._validations import raise_not_iterable


@to_action
def for_each(
    data: Iterable,
    action: Any,
) -> list[Any]:
    """Applies `action` to every item of an iterable input."""

    # 1. Validate that input data is iterable and obtain an iterator
    try:
        items = iter(data)
    except TypeError:
        raise_not_iterable(data)

    # 2. Normalize the inner action
    inner = as_action(action)

    # 3. Apply the inner action to every item in the collection
    return [inner(item) for item in items]


async def _for_each_acall(self, data: Iterable) -> list[Any]:
    """Async counterpart of `for_each`'s own body.

    Runs `action` over every item CONCURRENTLY via `asyncio.gather` —
    same reasoning as `parallel`'s own `acall`: mapping the same action
    across many independent items is exactly the shape of work async
    concurrency benefits most, and `asyncio.gather` preserves input
    order in its results regardless of which item's coroutine actually
    finishes first.
    """

    # 1. Validate that input data is iterable, materializing it up front
    #    (asyncio.gather needs concrete coroutines to schedule, so the
    #    items must be known before any of them can be awaited)
    try:
        items = list(data)
    except TypeError:
        raise_not_iterable(data)

    # 2. Normalize the inner action
    inner = as_action(self.action)

    # 3. Await every item's result concurrently, in the original order
    return list(await asyncio.gather(*(inner.acall(item) for item in items)))


# Attach the hand-written async counterpart directly onto the generated class —
# see design notes for why this can't be derived generically by create_action.
for_each.acall = _for_each_acall

for_each = for_each
"""
Applies `action` to every item of an iterable input.

Init Params:
    action (Action | Rule | Callable[[Any], Any]): Runs once per item.

Main Param:
    data (Iterable): The collection whose items are processed. A generator (or any
        other one-shot iterator) is accepted: the synchronous path reads it lazily,
        one item at a time; `acall` materializes it first.

Output:
    list[Any]: One result per input item, in order.

Callable both synchronously (`for_each(action=...)(items)`, items
processed one after another) and asynchronously
(`await for_each(action=...).acall(items)`, items processed
CONCURRENTLY via `asyncio.gather`).

Example:
    >>> for_each(action=double)([1, 2, 3])
    [2, 4, 6]
"""


_DESIGN_NOTES = """
# for_each — apply an action to every item of an iterable

## Main parameter has a real data contract
Unlike most containers (where the main parameter is `Any`, because the
container itself doesn't care about the data's shape), `for_each` has a
genuine contract on `data` — it must be iterable. It is annotated as plain
`Iterable`, not `Iterable[Any]`: the plain form checks exactly that
(`isinstance(data, Iterable)`) and touches no item, so `create_action` gives
`for_each` its type check ahead of the `iter()` call without walking the data.

## Why not `Iterable[Any]`
`Iterable[Any]` constrains nothing about the items (they are `Any`), but its
decomposition still walks the whole value to check them — and walks it twice,
once in the generated `__call__` and once in `act`. For a generator that meant
the validation consumed it and the body received an exhausted iterator: the
result was silently `[]`. Since `simplibs-rules` 0.4.0 `Iterable[T]` rejects
one-shot iterators outright, which would make the synchronous path refuse the
very input `for_each` is designed to stream through (and disagree with `acall`,
which is not validated and accepts it). Plain `Iterable` keeps both paths
consistent: lists and other re-iterable containers are processed as before, a
generator reaches the body untouched and is read lazily, a non-iterable value is
rejected by the type check.

## Why `acall` is hand-attached, and why it uses `asyncio.gather`
Same underlying reasoning as `parallel`'s own design notes for why
`Action`'s default `acall` would be wrong here (it would process the
whole loop inside one thread, and call each item's raising synchronous
`__call__` instead of its `.acall(...)`) — and the same positive reason
to prefer `asyncio.gather` over a plain sequential `await` loop:
`for_each` over an I/O-bound `action` is architecturally identical to
`parallel` over I/O-bound branches — many independent invocations of the
same shape, with no dependency between them — so it gets the identical
concurrency benefit.

## Why `items = list(data)`, not `iter(data)`, in the async path
The synchronous body only ever needs one item at a time and can stream
through a lazy iterator. `asyncio.gather` needs every coroutine handed
to it up front, which means every item must already be known before any
of them can be awaited — hence materializing the full list first. The
`TypeError` guard behaves identically either way: a non-iterable `data`
fails immediately at the `list(data)`/`iter(data)` call itself, before
any item is ever touched.
"""
