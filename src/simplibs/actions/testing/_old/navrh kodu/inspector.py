from typing import Any, List
from ..base_class import Action
from ..containers.operators.compose_class import SequenceCompose, ParallelCompose
from .models import StepMetadata, PipelineDiagnostic


def inspect_pipeline(pipeline: Action, parent_path: str = "root") -> PipelineDiagnostic:
    """Rekurzivně prohledá pipeline a vrátí seznam všech kroků a jejich I/O typů."""
    steps: List[StepMetadata] = []
    _flatten_steps(pipeline, steps, current_path=parent_path)

    fully_typed = all(s.input_type is not None and s.output_type is not None for s in steps)
    return PipelineDiagnostic(root_action=pipeline, steps=steps, is_fully_typed=fully_typed)


def _flatten_steps(action: Action, steps_acc: List[StepMetadata], current_path: str) -> None:
    """Vnitřní rekurzivní rozbalovač složených akcí."""
    in_t = getattr(action, "_input_type", None)
    out_t = getattr(action, "_output_type", None)

    # 1. Rozbalení SequenceCompose
    if isinstance(action, SequenceCompose):
        inner_steps = getattr(action, "steps", ())
        for idx, step in enumerate(inner_steps):
            _flatten_steps(step, steps_acc, f"{current_path}.seq[{idx}]")
        return

    # 2. Rozbalení ParallelCompose
    if isinstance(action, ParallelCompose):
        branches = getattr(action, "branches", ())
        for idx, branch in enumerate(branches):
            _flatten_steps(branch, steps_acc, f"{current_path}.parallel[{idx}]")
        return

    # 3. Rozbalení obalovacích akcí (Guard, Tap, Fallback)
    # Poznamka: Zde zjišťujeme, zda akce v sobě nebalí další akce/pravidla
    inner_action = getattr(action, "action", None) or getattr(action, "on_error", None)

    steps_acc.append(
        StepMetadata(
            step_index=len(steps_acc),
            path=current_path,
            action=action,
            input_type=in_t,
            output_type=out_t,
            is_wrapper=inner_action is not None
        )
    )


_DESIGN_NOTES = """
# Design Notes — testing/inspector.py

## K prověření / k dořešení:
1. Rozpoznávání vnitřních atributů u generator-created akcí:
   Akce vytvořené přes `create_action` mají své parametry z `__init__` uloženy jako atributy instance
   (např. `fallback.action`, `fallback.on_error`, `guard.rule`, `tap.action`).
   Je potřeba ověřit, zda přístup přes `getattr(action, "action", None)` spolehlivě funguje u všech
   standardních kontejnerů v `simplibs.actions`.
2. Detekce `Rule` uvnitř `Guard`:
   Pokud `guard` obsahuje `Rule`, pravidlo nemá `_input_type` / `_output_type` stejné jako `Action`.
   Vnímat `Rule` jako funkci `(Data) -> bool`?
   - U `guard`: `input_type = T`, `output_type = T` (neboť guard vrací nezměněná data, pokud pravidlo prošlo).
3. Detekce `Tap`:
   U `tap`: bez ohledu na výstup vnitřní akce je `output_type` roven `input_type` (vždy vrací původní data).
   Inspect by to měl zohlednit!
"""