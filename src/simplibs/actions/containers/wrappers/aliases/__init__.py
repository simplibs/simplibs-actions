from .callable_action import callable_action
from .log_step import log_step
from .retry_on_failure import retry_on_failure
from .run_side_effect import run_side_effect

__all__ = [
    "callable_action", "log_step", "retry_on_failure", "run_side_effect"
]


_DESIGN_NOTES = """
# Action Wrappers Aliases Sub-Package

## Purpose
Descriptive semantic aliases for wrapper containers, providing clear, intent-revealing
names for pipeline construction without changing underlying container behavior.

## Internal Components Registry

| Component          | Type  | Description                                                                     |
| :----------------- | :---- | :------------------------------------------------------------------------------ |
| `callable_action`  | Alias | Descriptive alias for `lambda_action` (wraps raw callables into actions).       |
| `log_step`         | Alias | Descriptive alias for `log_action` (logs data at a specific pipeline step).     |
| `retry_on_failure` | Alias | Descriptive alias for `retry` (retries execution on failure up to N times).     |
| `run_side_effect`  | Alias | Descriptive alias for `tap` (runs side effect and passes data through).         |
"""