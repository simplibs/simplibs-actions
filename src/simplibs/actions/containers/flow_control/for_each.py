from typing import Any, Iterable
# Outers
from ...decorator import to_action
from .._helpers import as_action
# Inners
from ._validations import raise_not_iterable


@to_action
def for_each(
    data: Iterable[Any],
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


for_each = for_each
"""
Applies `action` to every item of an iterable input.

Init Params:
    action (Action | Rule | Callable[[Any], Any]): Runs once per item.

Main Param:
    data (Iterable[Any]): The collection whose items are processed.

Output:
    list[Any]: One result per input item, in order.

Example:
    >>> for_each(action=double)([1, 2, 3])
    [2, 4, 6]
"""


_DESIGN_NOTES = """
# for_each — apply an action to every item of an iterable

## Main parameter has a real data contract
Unlike most containers (where the main parameter is `Any`, because the
container itself doesn't care about the data's shape), `for_each` has a
genuine contract on `data` — it must be iterable. Kept as `Iterable[Any]`
in the annotation; `IsTyping` already decomposes `Iterable[Any]` on its
own (a supported origin), so `for_each` gets a meaningful type check for
free via `create_action`, ahead of the `iter()` call itself.
"""