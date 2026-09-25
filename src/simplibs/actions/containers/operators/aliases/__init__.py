from .run_in_parallel import run_in_parallel
from .run_in_sequence import run_in_sequence
from .try_or_fallback import try_or_fallback

__all__ = [
    "run_in_parallel", "run_in_sequence", "try_or_fallback"
]


_DESIGN_NOTES = """
# Action Operator Aliases Sub-Package

## Purpose
Descriptive semantic aliases for operator containers, offering explicit function names
for pipelines without altering underlying execution behavior.

## Internal Components Registry

| Component         | Type  | Description                                                                     |
| :---------------- | :---- | :------------------------------------------------------------------------------ |
| `run_in_parallel` | Alias | Descriptive alias for `parallel` (runs N actions over data in parallel).        |
| `run_in_sequence` | Alias | Descriptive alias for `sequence` (chains N steps left to right).                |
| `try_or_fallback` | Alias | Backward-compatible alias for `fallback` (tries action, falls back on failure). |
"""