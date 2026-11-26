# Ronda 001 — reporte de QA

<!-- Lo escribe solo QA (Gemini). Desarrollo no lo edita. -->

## Resumen (máximo 5 líneas)

- **Veredicto global:** NO PASA
- **Conteo:** 9 PASA · 1 NO PASA · 1 NO PROBADO
- **Bloqueantes:** H1 (`gemelo/aco_gemelo/__main__.py:47`: `run --semilla 3` falla al final con código 2 si el YAML tenía semilla inválida y omite `--png`/`--animacion`); H2 (`gemelo/aco_gemelo/experimentos.py:48`: `semillas: true` en un plan se acepta en silencio como `[0]` y escribe CSV; `semillas: 1.5` y `false` abortan con traza `TypeError`/`IndexError`).

---

- **Fecha y hora:** 2026-11-25 18:12 -0500
- **Commit base revisado:** `ffcf646` (cambios sin commit en el árbol de trabajo)
- **Entrega revisada:** `rondas/001-para_qa.md`
- **Carpeta de trabajo:** `%TEMP%/aco-qa/ronda-001/` (`C:\Users\Usuario\AppData\Local\Temp\aco-qa\ronda-001\`)

## `git status --short` antes de la ronda

```
 M .handoff/ESTADO.md
 M CLAUDE.md
 M USO-DEL-PROTOCOLO.md
 M gemelo/aco_gemelo/config.py
 M gemelo/aco_gemelo/motor/simulacion.py
?? .handoff/rondas/001-para_qa.md
?? gemelo/docs/informes/revision_r001.md
?? gemelo/tests/test_reproducibilidad.py
```

## Veredicto por punto

| # | Punto revisado | Estado | Evidencia (comando o archivo) |
|---|---|---|---|
| 1 | Prueba nueva `tests/test_reproducibilidad.py` | PASA | `pytest tests/test_reproducibilidad.py -q` en copia: `8 passed in 14.75s` |
| 2 | Suite completa del gemelo | PASA | `pytest -q` en `gemelo/` de la copia: `326 passed in 276.67s (0:04:36)` |
| 3 | Suite del oráculo | PASA | `pytest oraculo -q` desde la raíz de la copia: `7 passed in 11.66s` |
| 4 | Comandos CLI de "Cómo probarlo" (`run --semilla -3`, `run --semilla 3`, `batch --semilla-inicial -2`) | PASA | `run --semilla -3` → `Error: semilla = -3...` (código 2); `run --semilla 3` → código 0; `batch --semilla-inicial -2` → `Error: semilla = -2...` (código 2, sin CSV) |
| 5 | Detección del mutante `mut_hash.py` por `test_mismo_ensayo_en_procesos_con_pythonhashseed_distinto` | PASA | Con `mut_hash.py` vía guion de docstring y vía `sitecustomize.py` (`PYTHONPATH=<mutDir>;<gemelo>`): la prueba falla con `AssertionError: assert 3 == 1` (56, 58 y 46 ticks; 3 huellas SHA-256 distintas) |
| 6 | Grupo 1 de casos borde: semillas negativas, flotantes, texto y booleanas por cada punto de entrada | NO PASA | YAML, `--semilla-inicial`, `dataclasses.replace`, `crear_mundo` (4 escenarios) y listas `semillas: [0, -1/1.5/"3"/true]` pasan; fallan H1 (`__main__.py:47`) y H2 (`experimentos.py:48`), más observación H3 (`experimentos.py:73-74,118`) |
| 7 | Grupo 2 de casos borde: semilla `0` y semillas grandes (`2**31`, `10**12`, `2**64`) y no colisión de 16 bits (`3` vs `3 + 65536`) | PASA | `test_qa_001_reproducibilidad_y_borde.py`: reproducibles dentro y entre procesos; `semilla=3` y `3+65536` dan resultados distintos |
| 8 | Grupo 3 de casos borde: huella entre procesos con `PYTHONHASHSEED` (`0`, `random`, `4294967295`) y motores `determinista` vs `hilos_sincronos` | PASA | 8 ejecuciones (4 `PYTHONHASHSEED` × 2 motores) produjeron la misma huella `verificada 56 8686990302c73efb5fd56a2dd97f3403529ee74c3c9b06be3c79a622d38c42c7` |
| 9 | Grupo 4 de casos borde: planes publicados `modos.yaml` y `rescate.yaml` contra `gemelo/experimentos/datos/` | PASA | `aco_gemelo experimentos --salida %TEMP%/aco-qa/ronda-001-exp-out/{modos,rescate}`: 18/18 CSV idénticos byte a byte (`TOTAL_CSV=18 DIFFS=0`) |
| 10 | Observaciones conocidas fuera de esta ronda (`agente.py:136`; `experimentos.py:48,74` con `semillas: -3` o `0`) | PASA | Confirmadas sin empeoramiento (`Agente(1, semilla=-1)` repite secuencia de `Agente(255, semilla=0)`; `CanalMemoria(-3)` no colisiona con `CanalMemoria(3)`; `semillas: -3` y `0` siguen dando `IndexError`) |
| 11 | Reproducibilidad entre procesos en otra máquina u otro sistema operativo | NO PROBADO | Solo probado en este equipo Windows con Python 3.12.7 (`aco-gemelo`) |

## Hallazgos (del más grave al más leve)

### H1 — `aco_gemelo run --semilla <válida>` falla al final con código 2 si el YAML tiene semilla inválida (regresión)

- **Gravedad:** bloquea
- **Dónde:** `gemelo/aco_gemelo/__main__.py:47`
- **Escenario que lo demuestra:** La opción `--semilla` está documentada como *"reemplaza la semilla del archivo"* (`__main__.py:107`). Si un archivo YAML contiene `semilla: -3` (o `1.5`, `"3"`, `true`, `null`) y se ejecuta `run --config <archivo> --semilla 3 --png <salida.png>`, `ejecutar(datos, 3, ...)` corre el ensayo completo con la semilla `3` e imprime toda la tabla de métricas en `stdout`, pero luego la línea 47 llama `config_ensayo(datos).n_agentes` **sin pasar `semilla`**. Con la nueva validación de esta ronda en `ConfigEnsayo.__post_init__`, esa llamada lanza `ValueError` por la semilla del YAML ya reemplazada, aborta con código 2 y omite la generación de `--png` / `--animacion`. Antes de esta ronda terminaba con código 0 y generaba las imágenes; además es inconsistente con `batch --config <archivo> --semilla-inicial 0 --semillas 2`, que sí retorna código 0.
- **Comando exacto:**
  ```powershell
  # Desde %TEMP%\aco-qa\ronda-001\gemelo
  "semilla: -3`nensayo:`n  limite: 50`n" | Set-Content -Encoding utf8 "$env:TEMP\aco-qa\ronda-001-repro\neg.yaml"
  C:/Users/Usuario/anaconda3/envs/aco-gemelo/python.exe -X utf8 -m aco_gemelo run --config "$env:TEMP\aco-qa\ronda-001-repro\neg.yaml" --semilla 3 --png "$env:TEMP\aco-qa\ronda-001-repro\out.png"
  ```
- **Salida:**
  ```
  Mundo (semilla 3):
  ... (53 líneas de salida normal del ensayo con semilla 3) ...
  rescate_verificadora         0
  rescate_sin_clasificar       0
  Error: semilla = -3: debe ser un entero mayor o igual que 0
  # Código de salida: 2 · Archivo out.png creado: False
  ```
- **Qué debería dar:** Código de salida `0`, generación del archivo `out.png` y sin error en `stderr`, usando `config_ensayo(datos, semilla).n_agentes` (o reutilizando el `ConfigEnsayo` ya construido).

### H2 — Un plan de experimentos acepta `semillas: true` en silencio (y genera CSV) y falla con traza sin capturar ante `semillas: 1.5` y `false`

- **Gravedad:** bloquea
- **Dónde:** `gemelo/aco_gemelo/experimentos.py:48` (y `:74` para `false`)
- **Escenario que lo demuestra:** En `cargar_plan`, la línea 48 hace `plan["semillas"] = list(range(semillas)) if isinstance(semillas, int) else list(semillas)`. En Python `bool` hereda de `int`:
  1. Con `semillas: true` en el YAML del plan, `isinstance(True, int)` es `True`, por lo que expande silenciosamente a `list(range(True)) == [0]`, ejecuta el experimento con semilla `0`, escribe los CSV y termina con código `0`.
  2. Con `semillas: 1.5`, `isinstance(1.5, int)` es `False` y `list(1.5)` lanza `TypeError: 'float' object is not iterable`, que no captura `__main__.py:127` (`except (ValueError, OSError)`), abortando con código `1` y traza completa.
  3. Con `semillas: false`, expande a `[]` y revienta en `experimentos.py:74` con `IndexError: list index out of range` (código `1` y traza; misma familia que la observación preexistente para `0`/`-3`, agravada por aceptar booleanos).
- **Comando exacto:**
  ```powershell
  # Desde %TEMP%\aco-qa\ronda-001\gemelo
  "semilla: 0`nensayo:`n  limite: 50`n" | Set-Content -Encoding utf8 "$env:TEMP\aco-qa\ronda-001-repro\base.yaml"
  "nombre: p_true`nbase: base.yaml`nsemillas: true`nfactores:`n  madre.modo: [ausente]`n" | Set-Content -Encoding utf8 "$env:TEMP\aco-qa\ronda-001-repro\plan_true.yaml"
  C:/Users/Usuario/anaconda3/envs/aco-gemelo/python.exe -X utf8 -m aco_gemelo experimentos --plan "$env:TEMP\aco-qa\ronda-001-repro\plan_true.yaml" --salida "$env:TEMP\aco-qa\ronda-001-repro\out_true" --procesos 1

  "nombre: p_float`nbase: base.yaml`nsemillas: 1.5`nfactores:`n  madre.modo: [ausente]`n" | Set-Content -Encoding utf8 "$env:TEMP\aco-qa\ronda-001-repro\plan_float.yaml"
  C:/Users/Usuario/anaconda3/envs/aco-gemelo/python.exe -X utf8 -m aco_gemelo experimentos --plan "$env:TEMP\aco-qa\ronda-001-repro\plan_float.yaml" --salida "$env:TEMP\aco-qa\ronda-001-repro\out_float" --procesos 1
  ```
- **Salida:**
  ```
  # Caso semillas: true
  Resultados en C:\Users\Usuario\AppData\Local\Temp\aco-qa\ronda-001-repro\out_true
  modo-ausente                                  verificadas   0/1  ticks     0.0  bytes madre        0
  # Código de salida: 0 · Archivos escritos: modo-ausente.csv, resumen.csv

  # Caso semillas: 1.5
  Traceback (most recent call last):
    ...
    File "C:\Users\Usuario\AppData\Local\Temp\aco-qa\ronda-001\gemelo\aco_gemelo\experimentos.py", line 48, in cargar_plan
      plan["semillas"] = list(range(semillas)) if isinstance(semillas, int) else list(semillas)
                                                                                 ^^^^^^^^^^^^^^
  TypeError: 'float' object is not iterable
  # Código de salida: 1
  ```
- **Qué debería dar:** Rechazar booleanos (`true`/`false`), flotantes (`1.5`), texto y cualquier valor que no sea un entero ≥ 1 o una lista no vacía de enteros ≥ 0 con `ValueError`, devolviendo `Error: ...` en `stderr`, código de salida `2` y sin escribir CSV.

### H3 — `experimentos.py` no valida toda la lista `plan["semillas"]` antes de correr y valida `config_ensayo(datos)` con la semilla del YAML base

- **Gravedad:** no bloquea
- **Dónde:** `gemelo/aco_gemelo/experimentos.py:73-74` y `:118`
- **Escenario que lo demuestra:**
  1. `condiciones()` solo valida `plan["semillas"][0]` (`experimentos.py:74`), por lo que con `semillas: [0, -1]` (o `[0, 1.5]`, `[0, "3"]`, `[0, true]`), `correr_plan` primero crea el directorio de salida (`:118`), luego ejecuta los ensayos de todas las semillas válidas previas (p. ej. semilla `0`) y recién falla en el trabajador al llegar a `-1`, dejando la carpeta vacía (sin CSV, código `2`).
  2. `condiciones()` llama `config_ensayo(datos)` (`:73`) sin pasar una semilla del plan, de modo que un plan válido (`semillas: [0, 1]`) que referencia una configuración base con `semilla: -3` falla por la semilla del archivo base tras crear la carpeta de salida.
- **Comando exacto:**
  ```powershell
  # Desde %TEMP%\aco-qa\ronda-001\gemelo
  "nombre: p_base_neg`nbase: neg.yaml`nsemillas: [0, 1]`nfactores:`n  madre.modo: [ausente]`n" | Set-Content -Encoding utf8 "$env:TEMP\aco-qa\ronda-001-repro\plan_base_neg.yaml"
  C:/Users/Usuario/anaconda3/envs/aco-gemelo/python.exe -X utf8 -m aco_gemelo experimentos --plan "$env:TEMP\aco-qa\ronda-001-repro\plan_base_neg.yaml" --salida "$env:TEMP\aco-qa\ronda-001-repro\out_base_neg" --procesos 1
  ```
- **Salida:**
  ```
  Error: semilla = -3: debe ser un entero mayor o igual que 0
  # Código de salida: 2 · Carpeta out_base_neg creada: True (vacía)
  ```
- **Qué debería dar:** Validar todas las semillas de `plan["semillas"]` en `cargar_plan`/`condiciones` antes de crear `carpeta`, y pasar `plan["semillas"][0]` a `config_ensayo(datos, plan["semillas"][0])` en `:73`.

### H4 — Comentario desactualizado sobre `historial` en `test_reproducibilidad.py`

- **Gravedad:** no bloquea
- **Dónde:** `gemelo/tests/test_reproducibilidad.py:22-23` y `:33`
- **Escenario que lo demuestra:** El comentario en `:22-23` afirma *"Imprime una huella del resultado completo (repr de la dataclass, sin el historial de posiciones...)"*, pero la línea `:33` ejecuta con `replace(config_ensayo(datos), registrar=True)`, por lo que `r.historial` sí se registra y sí entra en `repr(r)`.
- **Comando exacto:**
  ```powershell
  # Inspección directa de gemelo/tests/test_reproducibilidad.py líneas 22-34
  ```
- **Salida:**
  ```python
  # línea 22: # Imprime una huella del resultado completo (repr de la dataclass, sin el historial de posiciones,
  # línea 33: r = Simulacion(crear_mundo(datos), replace(config_ensayo(datos), registrar=True)).correr()
  ```
- **Qué debería dar:** Alinear el comentario indicando que `registrar=True` incluye `historial`, `serie`, `feromona` y `mapa_madre` en la huella (esto hace la prueba más estricta, no menos).

## Pruebas nuevas en `pruebas_qa/`

| Archivo | Qué prueba | Resultado con el código actual |
|---|---|---|
| `test_qa_001_reproducibilidad_y_borde.py` | 55 pruebas de los grupos 1–3: `dataclasses.replace`, `crear_mundo` en los 4 escenarios, semillas inválidas en YAML/CLI/planes (en lista), `--motor hilos_sincronos` con semilla negativa, semilla `0` y grandes (`2**31`, `10**12`, `2**64`), no colisión `3` vs `3 + 65536`, huella entre procesos con `PYTHONHASHSEED=0/random/4294967295` y coincidencia `determinista` == `hilos_sincronos` | PASA (55 passed) |
| `test_qa_001_hallazgos_cli_y_planes.py` | 4 pruebas que reproducen H1 (`run --semilla 3 --png` sobre YAML con `semilla: -3`) y H2 (plan con `semillas: true`, `false` y `1.5`) | NO PASA (4 failed) |

Comando ejecutado en la copia (`%TEMP%/aco-qa/ronda-001/`, desde la raíz):
```
C:/Users/Usuario/anaconda3/envs/aco-gemelo/python.exe -B -I -X utf8 -m pytest .handoff/pruebas_qa -q -p no:cacheprovider -W ignore
```
Resultado conjunto (incluyendo `test_qa_000_humo.py`): `4 failed, 56 passed in 160.11s (0:02:40)`.

## Lo que no se pudo comprobar

- La reproducibilidad entre procesos en otra máquina, otro sistema operativo (Linux/macOS) u otra versión de Python (solo se verificó en este Windows con Python 3.12.7 del entorno `aco-gemelo`).
- No se corrió el notebook con `nbconvert` por separado porque ya está cubierto por `gemelo/tests/test_notebook.py`, que pasó dentro de las 326 pruebas del gemelo en la copia temporal.

## `git status --short` después de la ronda

```
 M .handoff/ESTADO.md
 M CLAUDE.md
 M USO-DEL-PROTOCOLO.md
 M gemelo/aco_gemelo/config.py
 M gemelo/aco_gemelo/motor/simulacion.py
?? .handoff/pruebas_qa/test_qa_001_hallazgos_cli_y_planes.py
?? .handoff/pruebas_qa/test_qa_001_reproducibilidad_y_borde.py
?? .handoff/rondas/001-para_qa.md
?? .handoff/rondas/001-reporte_qa.md
?? gemelo/docs/informes/revision_r001.md
?? gemelo/tests/test_reproducibilidad.py
```
