from .EMPTY import EMPTY


_DESIGN_NOTES = """
# Action Factory Constants Sub-Package

## Purpose
Provides internal sentinel constants used during parameter signature inspection and dynamic
Action class construction.

## Internal Components Registry

| Component | Type     | Description                                                                     |
| :-------- | :------- | :------------------------------------------------------------------------------ |
| `EMPTY`   | Sentinel | Unique sentinel object representing absent parameter defaults or type hints.    |
"""