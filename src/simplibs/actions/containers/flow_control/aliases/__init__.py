from .apply_to_each import apply_to_each
from .conditional_action import conditional_action
from .guarded_action import guarded_action

__all__ = [
    "apply_to_each", "conditional_action", "guarded_action"
]


_DESIGN_NOTES = """
# Flow Control Aliases Sub-Package

## Purpose
Descriptive semantic aliases for core flow control containers, providing alternative
naming options for pipelines without altering underlying behavior.

## Internal Components Registry

| Component            | Type  | Description                                                                     |
| :------------------- | :---- | :------------------------------------------------------------------------------ |
| `apply_to_each`      | Alias | Descriptive alias for `for_each` (processes iterable items).                    |
| `conditional_action` | Alias | Descriptive alias for `branch` (soft conditional routing).                      |
| `guarded_action`     | Alias | Descriptive alias for `guard` (hard gate condition check).                      |
"""