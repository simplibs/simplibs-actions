To je skvělý nápad! Příprava pomocných testovacích utilit pro pipeline (katalogizovaných např. jako `simplibs.actions.testing`) dá vývojářům do rukou možnost ověřovat strukturu a typovou kompatibilitu svých složených řetězců (design-time / test-time) zcela bez vykonávání reálné business logiky (bez I/O, databází či API).

Níže předkládám návrh **souborové struktury** a **kompletní návrh obsahu jednotlivých souborů** včetně podrobných komentářů a sekcí `_DESIGN_NOTES` (s poznámkami, co je potřeba při implementaci ještě prověřit).

---

### 1. Souborová struktura nového modulu `testing/`

Navrhuji umístit testovací nástroje přímo do balíčku `simplibs.actions.testing` (případně jako podbalíček `simplibs/actions/testing/`):

```text
simplibs/actions/testing/
├── __init__.py           # Exporty veřejného rozhraní pro pytest (assert_pipeline_compatible, inspect_pipeline, atd.)
├── models.py             # Datové struktury pro diagnostiku (PipelineDiagnostic, TypeMismatchError, ExecutionGraph)
├── inspector.py          # Rekurzivní rozbalení a skenování stromu akcí (ParallelCompose, SequenceCompose, Fallback, Guard, Tap)
├── compatibility.py      # Statická typová kontrola (porovnání _input_type a _output_type)
├── dry_runner.py         # Testovací spouštěč "nanečisto" (simulovaný průchod dat pipeline bez side-effects)
└── _validations.py       # Diagnostické výjimky a chybová hlášení formátovaná v simplibs stylu

```

---

### 2. Návrhy obsahu jednotlivých souborů

#### `simplibs/actions/testing/models.py`

Definuje diagnostické datové třídy a výjimky.

```python
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

```

---

#### `simplibs/actions/testing/inspector.py`

Klíčový modul, který dokáže **rekurzivně rozbalit** složené akce (`SequenceCompose`, `ParallelCompose`, `fallback`, `guard`, `tap`) do ploché či stromové struktury pro analýzu.

```python
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

```

---

#### `simplibs/actions/testing/compatibility.py`

Poskytuje testovací asserty pro pytest (statická typová kontrola).

```python
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

```

---

#### `simplibs/actions/testing/dry_runner.py`

Umožňuje simulovaný průchod pipeline bez volání skutečné vykonávací logic.

```python
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

```

---

#### `simplibs/actions/testing/__init__.py`

Čisté veřejné rozhraní modulu.

```python
from .models import TypeMismatchError, StructureError, PipelineDiagnostic, StepMetadata
from .inspector import inspect_pipeline
from .compatibility import assert_pipeline_compatible
from .dry_runner import dry_run_pipeline

__all__ = [
    "TypeMismatchError",
    "StructureError",
    "PipelineDiagnostic",
    "StepMetadata",
    "inspect_pipeline",
    "assert_pipeline_compatible",
    "dry_run_pipeline",
]

```

---

### Shrnutí navrženého konceptu

Tímto máme kompletně připravenou a zachycenou myšlenku pro budoucí vývoj:

1. **`inspector.py`** se postará o inteligentní rozbalení stromu akce (vyřeší rozbalování flat verzí `SequenceCompose`, `ParallelCompose`, i pasivních wrapperů jako `tap` či `guard`).
2. **`compatibility.py`** přinese asserty pro pytest (`assert_pipeline_compatible`), které v milisekundách odhalí chyby ve skladbě řetězce ještě před spuštěním testované aplikace.
3. **`dry_runner.py`** nabídne pokročilejší simulaci toku dat.

Tuto strukturu takto máme předpřipravenou a až se k tomu budeš chytit vrátit, stačí na tuto definici navázat!