from typing import Any, Dict
from ..base_class import Action


def dry_run_pipeline(pipeline: Action, initial_input: Any) -> Dict[str, Any]:
    """Provede průchod pipeline 'nanečisto'.

    Při dry-runu se ověřují pouze typové validace a struktura dat na vstupu
    a výstupu jednotlivých kroků, aniž by docházelo k volání těžké business logiky.
    """
    # TODO: Implementovat mockovací runner pro simulaci průchodu
    return {
        "status": "success",
        "input": initial_input,
        "steps_executed": 0
    }


_DESIGN_NOTES = """
# Design Notes — testing/dry_runner.py

## K prověření / k dořešení:
1. Jak potlačit vykonání `act` metody během dry-runu?
   Jelikož `create_action` skládá `act` (business logiku) a validace zvlášť, dry-runner by mohl
   pouze volat `validate_call` vrstvy s mockovanými výstupy podle `_output_type`.
2. Generování dummy/mock dat:
   Pokud kroky v pipeline mění typ (např. `str` -> `UserDTO` -> `int`), dry-runner musí být schopen
   mezi kroky předávat "dummy" hodnotu odpovídající `_output_type` předchozího kroku.
"""