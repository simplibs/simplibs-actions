from .ParallelCompose import ParallelCompose
from .SequenceCompose import SequenceCompose


__all__ = [
    "ParallelCompose", "SequenceCompose"
]


_DESIGN_NOTES = """
# Action Operator Composition Classes Sub-Package

## Purpose
Specialized self-flattening container subclasses used internally by `Action` operator
overloads (`&` and `>>`) to maintain flat execution trees and prevent unwanted nesting.

## Internal Components Registry

| Component         | Type  | Description                                                                     |
| :---------------- | :---- | :------------------------------------------------------------------------------ |
| `ParallelCompose` | Class | Self-flattening variant of `parallel` used internally by `Action.__and__`.      |
| `SequenceCompose` | Class | Self-flattening variant of `sequence` used internally by `Action.then` (`>>`).  |
"""