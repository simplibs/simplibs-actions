_DESIGN_NOTES = """
# Create Action Private Internal Sub-Package

## Purpose
Internal building blocks and factory components used by `create_action` to inspect,
validate, synthesize, and resolve dynamic `Action` classes from standard function targets.

## Sub-Packages Registry

| Sub-Package   | Description                                                                     |
| :------------ | :------------------------------------------------------------------------------ |
| `constants`   | Shared sentinel values, tokens, and default constants used across action codegen.|
| `creators`    | Synthesizers generating dynamic `__init__`, `__call__`, and `act` class methods. |
| `resolvers`   | Reflection utilities for resolving class names, target signatures, and params.  |
| `validations` | Exception builders and parameter signature validation guards for action targets.|
"""