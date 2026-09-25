Mít v knihovně zabudované **testing utility** (např. ve složce `simplibs.actions.testing` nebo jako pomocné funkce v `simplibs.actions.inspection`), které šetří boilerplate kód při psaní unit testů, je **vynikající architektonický krok**. Výrazně to zvyšuje hodnotu knihovny pro vývojáře, protože jim to umožní chytat chyby v architektuře pipeline hned v CI/CD pipeline / pytestu bez nutnosti spouštět celé end-to-end prostředí.

Zde je rozpracovaná myšlenka, jak by takový testovací nástroj pro akce a pipeline mohl vypadat a co všechno by mohl ověřovat.

---

### Jak by mohl vypadat nástroj `check_pipeline_compatibility`?

Základní myšlenkou je **rekurzivně/sekvenčně "rozbalit" pipeline** (protože sekvence v sobě mohou mít vnořené jiné sekvence, paralelní větve, fallbacky atd.) a zkontrolovat typové i kontraktové vazby mezi jednotlivými sousedními kroky.

#### Příklad pomocného testovacího nástroje:

```python
from typing import Any, NamedTuple
from simplibs.actions import Action


class TypeMismatchError(Exception):
    """Vyhozeno, pokud výstup kroku neodpovídá vstupu následujícího kroku."""
    pass


class PipelineDiagnostic(NamedTuple):
    step_index: int
    step_action: Action
    input_type: Any
    output_type: Any


def inspect_pipeline(pipeline: Action) -> list[PipelineDiagnostic]:
    """Sestaví seznam diagnostických údajů pro všechny kroky v sekvenční pipeline."""
    # Pokud jde o SequenceCompose, vytáhneme ploché kroky (flattened steps)
    steps = getattr(pipeline, "steps", [pipeline])
    diagnostics = []

    for idx, step in enumerate(steps):
        in_t = getattr(step, "_input_type", None)
        out_t = getattr(step, "_output_type", None)
        diagnostics.append(
            PipelineDiagnostic(
                step_index=idx,
                step_action=step,
                input_type=in_t,
                output_type=out_t,
            )
        )
    return diagnostics


def assert_pipeline_compatible(pipeline: Action, strict: bool = False) -> None:
    """Testovací assert nástroj pro pytest.
    
    Projde pipeline a ověří, že output_type kroku N je kompatibilní
    s input_type kroku N+1.
    """
    diagnostics = inspect_pipeline(pipeline)

    for i in range(len(diagnostics) - 1):
        curr_step = diagnostics[i]
        next_step = diagnostics[i + 1]

        out_type = curr_step.output_type
        in_type = next_step.input_type

        # 1. Pokud typy chybí a jsme ve strict režimu
        if strict and (out_type is None or in_type is None):
            raise TypeMismatchError(
                f"Krok {curr_step.step_index} ({curr_step.step_action}) nebo "
                f"krok {next_step.step_index} ({next_step.step_action}) nemá definované anotace "
                f"(_input_type / _output_type)."
            )

        # 2. Pokud jsou oba typy známé, ověříme kompatibilitu
        if out_type is not None and in_type is not None:
            if not _is_type_compatible(out_type, in_type):
                raise TypeMismatchError(
                    f"\nNekompatibilní předání dat v pipeline mezi kroky {i} a {i+1}:\n"
                    f"  Krok {i} ({curr_step.step_action.__class__.__name__}) vrací: {out_type}\n"
                    f"  Krok {i+1} ({next_step.step_action.__class__.__name__}) očekává: {in_type}"
                )

```

---

### Co všechno by takový testovací nástroj mohl u pipeline testovat?

Porovnání `_input_type` a `_output_type` je jen začátek. Testovací framework pro vaše akce může nabízet komplexní **Pipeline Health Check**:

#### 1. Kontrola "Slepých uliček" a Nulových rozhraní (Dead-end Steps)

* **Co testovat:** Zda v sekvenci není krok, který vrací `None` (nebo `NoReturn`), ale po něm následuje další krok, který vyžaduje reálná data (např. `int` nebo `dict`).
* **Přínos:** Odhalí situaci, kdy vývojář omylem do středu `sequence` zařadil akci, která "požírá" data (např. nějakou void proceduru místo transformace).

#### 2. Validace strukturálních vlastností složených operátorů (Parallel & Fallback)

* **Pro `Parallel` (`&`):** Ověří, že **všechny větvící se akce** přijímají stejný `_input_type` (nebo jeho nadtyp). Pokud paralelní akce A očekává `User` a paralelní akce B očekává `Order`, nemohou běžet nad stejným rozhraním paralely.
* **Pro `Fallback` (`|`):** Ověří, že hlavní i náhradní větev (`on_error`) vracejí stejný nebo kompatibilní `_output_type`, aby zbytek pipeline za fallbackem dostával konzistentní datový typ nezávisle na tom, zda došlo k chybě.

#### 3. Testovací Runner / Dry-Run (Dummy Execution)

Testovací nástroj může nabídnout funkci `dry_run_pipeline(pipeline, mock_input)`:

* Projde pipeline krok po kroku.
* Místo reálného vykonání business logiky (která může sahat do databáze nebo na API) pouze **ověří validaci na vstupu/výstupu každé akce** nebo nahradí vnitřní volání mockovanými daty.
* Vygeneruje **Report průchodu** (Pipeline Execution Graph) s časovou náročností a datovými typy v každém uzlu.

#### 4. Detekce chybějících dekorátorů / Anotací

Nástroj např. `assert_action_fully_typed(pipeline)` proskenuje celou sekvenci a ověří, že:

* Všechny uživatelské funkce/akce byly vytvořeny s `use_validations=True`.
* Žádná akce v produkční pipeline nebyla ponechána bez typových anotací.

---

### Jak by to vypadalo v praxi u uživatele (např. v Pytestu)?

Uživatel vaší knihovny píše test pro svou novou objednávkovou pipeline:

```python
# tests/test_pipelines.py
from simplibs.actions.testing import assert_pipeline_compatible, inspect_pipeline
from my_app.pipelines import process_order_pipeline

def test_process_order_pipeline_structure():
    # 1. Statická kontrola typů bez spuštění DB/API
    assert_pipeline_compatible(process_order_pipeline, strict=True)

def test_pipeline_visualization():
    # 2. Výpis struktury do logu pro snadný debugging
    for info in inspect_pipeline(process_order_pipeline):
        print(f"[{info.step_index}] {info.step_action.__class__.__name__}: {info.input_type} -> {info.output_type}")

```

Pokud uživatel v pipeline omylem prohodí dva kroky (např. pošle `UnparsedJSON` do akce očekávající `DbUserRecord`), test selže **okamžitě** během milisekundy s přesným chybovým hlášením, kde k nesouladu došlo.

### Závěr

Vytvoření takového modulu (např. `simplibs.actions.testing`) je skvělá přidaná hodnota. Uživatelům knihovny dá do rukou mocný nástroj na **static assertion** jejich datových řetězců, čímž zásadně zrychlí vývoj a testování.