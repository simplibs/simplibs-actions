from .Action import Action


_DESIGN_NOTES = """
# Action Base Sub-Package

## Purpose
Provides the abstract base class `Action` that defines core pipeline execution,
dunder-method composition, representation, and polymorphic resolution for all
action types in the package.

## Components Registry

| Component | Type  | Description                                                                     |
| :-------- | :---- | :------------------------------------------------------------------------------ |
| `Action`  | Class | Base class for callable data transformation units with operator composition.     |
"""