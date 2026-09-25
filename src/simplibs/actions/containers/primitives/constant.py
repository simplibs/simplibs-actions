from typing import Any
# Outers
from ...decorator import to_action


@to_action
def constant(
    data: Any,
    value: Any
) -> Any:
    """Ignores `data`, always returns `value`."""
    return value


constant = constant
"""
Ignores `data`, always returns `value`.

Init Params:
    value (Any): The fixed value always returned.

Main Param:
    data (Any): Accepted for pipeline compatibility, never read.

Output:
    Any: `value`, unchanged.

Useful as a default for `fallback`'s `on_error` / `branch`'s
`else_branch`, or as a source step at the start of a pipeline where the
incoming `data` is purely formal.

Example:
    >>> Constant(value=0)(anything)
    0
"""


_DESIGN_NOTES = """
# constant — ignores input, returns a fixed value

## `data` stays in the signature even though it's unused
`to_action` treats the first parameter as the main pipeline input
regardless of whether the function body reads it — `constant` must
accept `data` to remain callable like any other step inside `sequence`
or any other container that calls it as `(data)`.
"""
