from dataclasses import dataclass
from typing import Any, Sequence
from ..base_class import Action


class TypeMismatchError(TypeError):
    """Vyhozeno, pokud výstup jednoho kroku neodpovídá vstupu následujícího krok u."""
    pass


class StructureError(ValueError):
    """Vyhozeno, pokud pipeline obsahuje nevalidní nebo nepodporovanou strukturu."""
    pass


@dataclass(frozen=True)
class StepMetadata:
    """Metadata o jednom konkrétním uzlu v pipeline."""
    step_index: int
    path: str  # Např. "SequenceCompose[0] -> ParallelCompose[1]"
    action: Action
    input_type: Any
    output_type: Any
    is_wrapper: bool = False  # Zda jde o obalovač (Guard, Tap, Fallback apod.)


@dataclass(frozen=True)
class PipelineDiagnostic:
    """Souhrnná diagnostika celé pipeline."""
    root_action: Action
    steps: Sequence[StepMetadata]
    is_fully_typed: bool


_DESIGN_NOTES = """
# Design Notes — testing/models.py

## K prověření / k dořešení:
1. Reprezentace neznámých typů: Pokud akce nemá zadaný `_input_type` (např. při `use_validations=False`),
   měl by být reprezentován jako `inspect.Parameter.empty`, `typing.Any` nebo `None`?
   - Doporučení: Odlišovat `Any` (explicitní libovolný typ) od `None`/`EMPTY` (anotace chybí).
2. Zmražení instancí: `StepMetadata` používá `frozen=True` pro imutabilitu v diagnostických reportech.
"""