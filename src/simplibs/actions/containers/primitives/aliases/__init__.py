from .pass_through import pass_through
from .replace_with import replace_with

__all__ = [
    "pass_through", "replace_with"
]


_DESIGN_NOTES = """
# Primitive Containers Aliases Sub-Package

## Purpose
Descriptive semantic aliases for primitive containers, providing alternative naming
options for pipelines without altering underlying execution behavior.

## Internal Components Registry

| Component      | Type  | Description                                                                     |
| :------------- | :---- | :------------------------------------------------------------------------------ |
| `pass_through` | Alias | Descriptive alias for `identity` (returns `data` unchanged).                   |
| `replace_with` | Alias | Descriptive alias for `constant` (ignores `data`, always returns fixed `value`).|
"""