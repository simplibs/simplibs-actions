from ..lambda_action import lambda_action

callable_action = lambda_action
"""
Alias of `lambda_action` — adapter that runs a raw, one-off callable as
an Action.

Init Params:
    func (Callable[[Any], Any]): Any single-argument callable.

Main Param:
    data (Any): Passed straight into `func`.

Output:
    Any: `func`'s return value.

Provided for pipelines that favor a more descriptive name than
`lambda_action`. See `lambda_action`'s own module for the canonical
implementation and design notes — `callable_action` is a pure alias, no
separate behavior.
"""
