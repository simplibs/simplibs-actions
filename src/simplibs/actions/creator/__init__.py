from .create_action import create_action


_DESIGN_NOTES = """
# Action Creator Sub-Package

## Purpose
Provides the primary factory mechanics for synthesizing first-class `Action` types and
instances from arbitrary Python callables, functions, or decorated methods.

## Internal Components Registry

| Component        | Type     | Description                                                                     |
| :--------------- | :------- | :------------------------------------------------------------------------------ |
| `create_action`  | Function | Public factory and decorator for producing fully-typed, validated `Action`s.    |


## Architectural Design Decisions

1. **Single Entry Point Focus**: `create_action` is the sole public interface exposed by
   this sub-package. All internal helpers (signature validation, dynamic class synthesis,
   type extraction) are kept private to ensure a clean API boundary.
2. **First-Class Action Metaprogramming**: Converts standard callables into true `Action`
   subclasses at runtime, preserving function metadata while wrapping execution inside the
   standard `simplibs-actions` pipeline contract.
"""