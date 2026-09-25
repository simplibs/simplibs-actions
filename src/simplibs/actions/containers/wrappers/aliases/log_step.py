from ..log_action import log_action

log_step = log_action
"""
Alias of `log_action` — logs `data` at one point in a pipeline and passes
it through unchanged.

Init Params:
    logger (Callable[[Any], None]): Receives the message/data to log.
    message (str | None): Optional label prefixed to the logged value.

Main Param:
    data (Any): The value observed and passed through.

Output:
    Any: The same `data`, unchanged.

Provided for pipelines that favor a more descriptive name than `log_action`.
See `log_action`'s own module for the canonical implementation and design
notes — `log_step` is a pure alias, no separate behavior.
"""