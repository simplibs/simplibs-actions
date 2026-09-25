from . import aliases
from .lambda_action import lambda_action
from .log_action import log_action
from .retry import retry
from .tap import tap


_DESIGN_NOTES = """
# Action Wrapper Containers Sub-Package

## Purpose
Provides wrapper containers that adapt raw callables, log flowing pipeline data,
retry actions upon failure, or execute side effects without altering data streams.

## Internal Components Registry

| Component       | Type      | Description                                                                     |
| :-------------- | :-------- | :------------------------------------------------------------------------------ |
| `lambda_action` | Container | Adapter wrapping raw callables into callable Action instances.                  |
| `log_action`    | Container | Observes and logs data flowing through a pipeline step without modifying it.    |
| `retry`         | Container | Retries action execution up to N times on specified exceptions.                 |
| `tap`           | Container | Executes an action as a side-effect and passes original data through unchanged.  |
"""