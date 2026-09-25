from typing import Any, get_origin, get_args
from ..base_class import Action
from .inspector import inspect_pipeline
from .models import TypeMismatchError


def _is_type_compatible(source_type: Any, target_type: Any) -> bool:
    """Ověří, zda je `source_type` přiřaditelný/kompatibilní s `target_type`."""
    if target_type is Any or source_type is Any:
        return True
    if source_type == target_type:
        return True

    # Základní podpora pro subclassing
    if isinstance(source_type, type) and isinstance(target_type, type):
        try:
            return issubclass(source_type, target_type)
        except TypeError:
            pass

    # TODO: Přidat pokročilou kontrolu pro Union, Optional, Generics
    return False


def assert_pipeline_compatible(pipeline: Action, strict: bool = False) -> None:
    """Testovací assert pro pytest. Projde pipeline a ověří kompatibilitu I/O typů.

    Args:
        pipeline: Běžná nebo složená akce ke kontrole.
        strict: Pokud je True, vyžaduje, aby VŠECHNY kroky měly definované
                `_input_type` a `_output_type` (nesmí chybět anotace).

    Raises:
        TypeMismatchError: Pokud výstup kroku N neodpovídá vstupu kroku N+1.
    """
    diag = inspect_pipeline(pipeline)
    steps = diag.steps

    for i in range(len(steps) - 1):
        curr_step = steps[i]
        next_step = steps[i + 1]

        out_t = curr_step.output_type
        in_t = next_step.input_type

        if strict and (out_t is None or in_t is None):
            raise TypeMismatchError(
                f"Krok {curr_step.step_index} ({curr_step.action.__class__.__name__} na '{curr_step.path}') "
                f"nebo krok {next_step.step_index} ({next_step.action.__class__.__name__} na '{next_step.path}') "
                f"nemá definované typové anotace!"
            )

        if out_t is not None and in_t is not None:
            if not _is_type_compatible(out_t, in_t):
                raise TypeMismatchError(
                    f"\n[Pipeline Type Mismatch] Nekompatibilní předání dat mezi kroky {i} a {i+1}:\n"
                    f"  Zdroj  : krok {i} ({curr_step.action.__class__.__name__}) na path '{curr_step.path}'\n"
                    f"           vrací type -> {out_t}\n"
                    f"  Cíl    : krok {i+1} ({next_step.action.__class__.__name__}) na path '{next_step.path}'\n"
                    f"           očekává type -> {in_t}"
                )


_DESIGN_NOTES = """
# Design Notes — testing/compatibility.py

## K prověření / k dořešení:
1. Kompatibilita generických typů (typing module):
   Pythonovské `issubclass(list[str], list[Any])` vyhodí `TypeError`.
   Pro produkční verzi bude nutné využít buď utilitu z `simplibs.types` / `IsTyping`,
   nebo zjednodušenou kontrolu rozbalující `get_origin()` a `get_args()`.
2. Paralelní větvění (ParallelCompose):
   U `ParallelCompose` nejdou kroky po sobě (0 -> 1 -> 2), ale všechny dostávají STEJNÝ vstup
   a vracejí `tuple[out1, out2, ...]`.
   Kontrola kompatibility pro `ParallelCompose` musí ověřit:
   a) Zda je `input_type` předchozího kroku kompatibilní se VŠEMI větvemi paralely.
   b) Zda výstupní typ paralely odpovídá `tuple[branch1._output_type, branch2._output_type, ...]`.
3. Fallback větvění:
   U `fallback` je výstupní typ roven `Union[action._output_type, on_error._output_type]`.
"""