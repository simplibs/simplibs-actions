from . import aliases
from .branch import branch
from .for_each import for_each
from .guard import guard


_DESIGN_NOTES = """
# Flow Control Containers Sub-Package

## Purpose
Provides flow control containers that manage data routing, conditional execution,
and collection iteration within action pipelines.

## Internal Components Registry

| Component  | Type      | Description                                                                     |
| :--------- | :-------- | :------------------------------------------------------------------------------ |
| `branch`   | Container | Soft conditional branching (routes data or passes through unchanged).           |
| `for_each` | Container | Iterative execution (applies an action to each item of an iterable).            |
| `guard`    | Container | Hard gate verification (passes data if rule holds, otherwise raises).           |
"""