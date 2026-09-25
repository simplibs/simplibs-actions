from . import aliases
from .constant import constant
from .identity import identity


_DESIGN_NOTES = """
# Primitive Containers Sub-Package

## Purpose
Provides basic atomic building blocks (primitives) for pipelines, such as returning
data unchanged or injecting fixed values.

## Internal Components Registry

| Component  | Type      | Description                                                                     |
| :--------- | :-------- | :------------------------------------------------------------------------------ |
| `constant` | Container | Ignores input data and always returns a fixed value.                            |
| `identity` | Container | No-op pass-through container that returns input data unchanged.                 |
"""