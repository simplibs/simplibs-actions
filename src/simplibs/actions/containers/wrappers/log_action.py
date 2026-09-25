from typing import Any, Callable
# Outers
from ...decorator import to_action


@to_action
def log_action(
    data: Any,
    logger: Callable[[Any], None],
    message: str | None = None,
) -> Any:
    """Logs the data flowing through one pipeline point, unchanged."""

    # 1. Log with custom message prefix if provided
    if message:
        logger(f"{message}: {data!r}")

    # 2. Log data directly without prefix
    else:
        logger(data)

    # 3. Pass original data through unchanged
    return data


log_action = log_action
"""
Logs `data` at one point in a pipeline and passes it through unchanged.

Init Params:
    logger (Callable[[Any], None]): Receives the message/data to log.
    message (str | None): Optional label prefixed to the logged value.

Main Param:
    data (Any): The value observed and passed through.

Output:
    Any: The same `data`, unchanged.

Observes and logs data flowing through a specific step in a pipeline without
modifying the data stream.

Example:
    >>> log_action(logger=print, message="after parse")(parsed)
"""


_DESIGN_NOTES = """
# log_action — observes data at one pipeline point

## Purpose
`log_action` acts as a transparent observation tap inside action chains. It passes incoming
`data` through completely untouched while sending formatted output to the supplied `logger`.

## Alias
This container is also aliased as `log_step` in `wrappers/aliases/log_step.py` for pipelines
where `log_step` reads more naturally in a sequence.
"""