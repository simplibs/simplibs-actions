from .to_action import to_action


_DESIGN_NOTES = """
# Action Decorator Sub-Package

## Purpose
Provides the primary `@to_action` decorator interface for converting standard functions
and methods into fully-featured, two-phase (curried) `Action` builders.

## Internal Components Registry

| Component    | Type     | Description                                                                 |
| :----------- | :------- | :-------------------------------------------------------------------------- |
| `to_action`  | Function | Public decorator wrapping callables into two-phase `Action` constructs.     |


## Architectural Design Decisions

1. **Syntactic Convenience Layer**: `to_action` acts as the high-level, declarative facade
   over `create_action`. It enables clean, decorator-driven action definitions across custom
   codebases while maintaining consistency with built-in library containers.
2. **Two-Phase Execution Guarantee**: Functions decorated with `@to_action` automatically
   support separate configuration (keyword arguments) and execution (`data` input) phases,
   fitting seamlessly into pipeline compositions.
"""