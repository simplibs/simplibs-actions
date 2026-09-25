from . import aliases
from . import compose_class
from .fallback import fallback
from .parallel import parallel
from .sequence import sequence


_DESIGN_NOTES = """
# Action Operator Containers Sub-Package

## Purpose
Provides fundamental composition operator containers that enable building complex,
branching, parallel, and sequential action pipelines.

## Internal Components Registry

| Component  | Type      | Description                                                                     |
| :--------- | :-------- | :------------------------------------------------------------------------------ |
| `fallback` | Container | Attempts primary action and executes fallback or passes data on failure.        |
| `parallel` | Container | Runs N actions independently over the same input data, returning a tuple.       |
| `sequence` | Container | Chains N actions sequentially, feeding output of each step into the next.       |
"""