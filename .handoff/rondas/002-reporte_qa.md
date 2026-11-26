# Ronda 002 — reporte de QA

<!-- Lo escribe solo QA (Gemini). Desarrollo no lo edita. -->

## Resumen (máximo 5 líneas)

- **Veredicto global:** PASA
- **Conteo:** 9 PASA · 0 NO PASA · 2 NO PROBADO
- **Bloqueantes:** ninguno (H1–H4 de la ronda 001 y O1–O3 de la revisión interna verificados y cerrados; 347 pruebas del gemelo, 7 del oráculo, 60 previas + 27 nuevas de `pruebas_qa` y 18/18 CSV publicados idénticos byte a byte).

---

- **Fecha y hora:** 2026-11-25 20:51 -0500
- **Commit base revisado:** `ffcf646` (cambios de rondas 001 y 002 sin commit en el árbol de trabajo)
- **Entrega revisada:** `rondas/002-para_qa.md`
- **Carpeta de trabajo:** `%TEMP%/aco-qa/ronda-002/` (`C:\Users\Usuario\AppData\Local\Temp\aco-qa\ronda-002\`)

## `git status --short` antes de la ronda

```
 M .handoff/ESTADO.md
 M CLAUDE.md
 M FAILURES.md
 M USO-DEL-PROTOCOLO.md
 M gemelo/aco_gemelo/__main__.py
 M gemelo/aco_gemelo/config.py
 M gemelo/aco_gemelo/experimentos.py
 M gemelo/aco_gemelo/motor/simulacion.py
 M gemelo/tests/test_cli.py
 M gemelo/tests/test_experimentos.py
?? .handoff/pruebas_qa/test_qa_001_hallazgos_cli_y_planes.py
?? .handoff/pruebas_qa/test_qa_001_reproducibilidad_y_borde.py
?? .handoff/rondas/001-para_qa.md
?? .handoff/rondas/001-reporte_qa.md
?? .handoff/rondas/002-para_qa.md
?? gemelo/docs/informes/revision_r001.md
?? gemelo/docs/informes/revision_r002.md
?? gemelo/tests/test_reproducibilidad.py
```

## Veredicto por punto

| # | Punto revisado | Estado | Evidencia (comando o archivo) |
|---|---|---|---|
| 1 | Suite completa del gemelo | PASA | `pytest -q` en `gemelo/` de la copia: `347 passed in 264.71s (0:04:24)` |
| 2 | Suite del oráculo | PASA | `pytest oraculo -q` desde la raíz de la copia: `7 passed in 9.33s` |
| 3 | Pruebas previas de `.handoff/pruebas_qa/` (rondas 000–001) | PASA | `pytest .handoff/pruebas_qa -q` desde la raíz de la copia (antes de añadir las de ronda 002): `60 passed in 328.93s (0:05:28)` — las 4 pruebas de H1/H2 que fallaban en la ronda 001 ahora pasan |
| 4 | Reproducción directa de H1, H2, H3 y H4 de la ronda 001 | PASA | H1 (`run --config neg.yaml --semilla 3 --png out.png`): `EXIT=0`, `PNG_EXISTS=True`; H2 (`semillas: true/false/1.5`): `EXIT=2`, `DIR_EXISTS=False`, `Error: semillas = ...`; H3 (`condiciones` usa `plan["semillas"][0]`, `correr_plan` valida antes de `mkdir`); H4 (comentario actualizado en `test_reproducibilidad.py:22-23`) |
| 5 | Grupo 1 de casos borde: `run` con `--semilla` (`0` y `3`) sobre YAML inválido, con y sin `--png`/`--animacion`, en los 3 motores (`determinista`, `hilos_sincronos`, `hilos`), y error sin `--semilla` | PASA | Sondas en `%TEMP%/aco-qa/ronda-002-probes/` y `test_qa_002_borde_cli_y_planes.py`: todos los overrides dan `rc=0` (PNG y GIF creados; `--semilla 0` muestra `Mundo (semilla 0):`); sin `--semilla` da `rc=2` |
| 6 | Grupo 2 de casos borde: planes válidos (`[0, 0, 1]`, `[2**31, 10**12, 2**64]`, `[5]`, `semillas` ausente → 30) con base de semilla inválida, y 14 planes inválidos sin carpeta ni CSV | PASA | Sondas y `test_qa_002_borde_cli_y_planes.py`: los 4 planes válidos pasan (`rc=0`, semillas exactas en CSV); los 14 inválidos (`[]`, `{a:1}`, `null`, `-3`, `0`, `"3"`, `[0,-1]`, `[0,true]`, `[0,false]`, `[0,1.5]`, `[0,null]`, factor inválido, clave desconocida, base inexistente) dan `rc=2` y `dir_exists=False` |
| 7 | Grupo 3 de casos borde: `batch` (`--semillas 0`, `-2`, `1`; `--semilla-inicial -2`, `-1`) sobre YAML con semilla inválida | PASA | Sondas y `test_qa_002_borde_cli_y_planes.py`: casos inválidos dan `rc=2`, `dir_exists=False`, `csv_exists=False`; `--semillas 1` da `rc=0` y genera el CSV con semilla `0` |
| 8 | Grupo 4 de casos borde: planes publicados `modos.yaml` y `rescate.yaml` contra `gemelo/experimentos/datos/` | PASA | `aco_gemelo experimentos --salida %TEMP%/aco-qa/ronda-002-exp-out/{modos,rescate}`: 18/18 CSV idénticos byte a byte (`TOTAL_CSV=18 DIFFS=0`) |
| 9 | Grupo 5 de casos borde: búsqueda de cualquier otro sitio que reconstruya configuración o mundo sin la semilla en uso | PASA | Barrido en todo el repositorio (`.py` y `.ipynb`, excluyendo `referencia/`, `.handoff/`, `tests/`): `__main__.py:31,33,47,64`, `experimentos.py:97,98,107`, `linea_base.py:47`, `oraculo/comparar.py:46-51`, `oraculo/investigacion_c3.py:108-111` pasan todos la semilla en uso; `analisis.ipynb:164-165` usa el mismo `datos` (`default.yaml`) sin reemplazo |
| 10 | Reproducibilidad entre procesos en otra máquina, otro sistema operativo u otra versión de Python | NO PROBADO | Solo probado en este Windows con Python 3.12.7 (`aco-gemelo`) |
| 11 | Causa del `TimeoutExpired` con tiempo negativo observado una vez por el revisor interno | NO PROBADO | No se reprodujo en las ejecuciones de QA (`60 passed` y `27 passed` sin timeouts) |

## Hallazgos (del más grave al más leve)

Sin hallazgos nuevos (bloqueantes ni no bloqueantes) en esta ronda.

Nota sobre la observación conocida fuera de ronda (`gemelo/aco_gemelo/agente/agente.py:136`): construir `Agente` manualmente sin pasar por `ConfigEnsayo` sigue sin validar la semilla, tal como se documentó y fuera del alcance de esta ronda.

## Pruebas nuevas en `pruebas_qa/`

| Archivo | Qué prueba | Resultado con el código actual |
|---|---|---|
| `test_qa_002_borde_cli_y_planes.py` | 27 pruebas de los grupos 1–3 de la ronda 002: `run --semilla 0/3` sobre YAML inválido en los 3 motores y con `--png`/`--animacion`; planes válidos con repetidos (`[0, 0, 1]`), semillas enormes (`2**31`, `10**12`, `2**64`), lista de 1 elemento (`[5]`) y `semillas` ausente (30) con base de semilla inválida; 11 planes con `semillas` inválidas verificando `dir_exists=False`; `batch` con `--semillas 0/-2/1` y `--semilla-inicial -2/-1` verificando ausencia de carpeta/CSV al fallar | PASA (27 passed) |

Comandos ejecutados en la copia (`%TEMP%/aco-qa/ronda-002/`, desde la raíz):
```
C:/Users/Usuario/anaconda3/envs/aco-gemelo/python.exe -B -I -X utf8 -m pytest .handoff/pruebas_qa -q -p no:cacheprovider -W ignore
# (antes de agregar test_qa_002_borde_cli_y_planes.py): 60 passed in 328.93s (0:05:28)

C:/Users/Usuario/anaconda3/envs/aco-gemelo/python.exe -B -I -X utf8 -m pytest .handoff/pruebas_qa/test_qa_002_borde_cli_y_planes.py -q -p no:cacheprovider -W ignore
# 27 passed in 24.12s (total acumulado en .handoff/pruebas_qa: 87 pruebas)
```

## Lo que no se pudo comprobar

- La reproducibilidad entre procesos en otra máquina, otro sistema operativo (Linux/macOS) u otra versión de Python (solo se verificó en este Windows con Python 3.12.7).
- La causa del `TimeoutExpired` con tiempo negativo reportado en una primera corrida del revisor interno (no se reprodujo durante QA).
- El notebook completo por separado fuera de `gemelo/tests/test_notebook.py` (que sí corrió y pasó dentro de las 347 pruebas del gemelo en la copia).

## `git status --short` después de la ronda

```
 M .handoff/ESTADO.md
 M CLAUDE.md
 M FAILURES.md
 M USO-DEL-PROTOCOLO.md
 M gemelo/aco_gemelo/__main__.py
 M gemelo/aco_gemelo/config.py
 M gemelo/aco_gemelo/experimentos.py
 M gemelo/aco_gemelo/motor/simulacion.py
 M gemelo/tests/test_cli.py
 M gemelo/tests/test_experimentos.py
?? .handoff/pruebas_qa/test_qa_001_hallazgos_cli_y_planes.py
?? .handoff/pruebas_qa/test_qa_001_reproducibilidad_y_borde.py
?? .handoff/pruebas_qa/test_qa_002_borde_cli_y_planes.py
?? .handoff/rondas/001-para_qa.md
?? .handoff/rondas/001-reporte_qa.md
?? .handoff/rondas/002-para_qa.md
?? .handoff/rondas/002-reporte_qa.md
?? gemelo/docs/informes/revision_r001.md
?? gemelo/docs/informes/revision_r002.md
?? gemelo/tests/test_reproducibilidad.py
```
