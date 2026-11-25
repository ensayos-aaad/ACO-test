# Ronda 000 — reporte de QA

<!-- Lo escribe solo QA (Gemini). Desarrollo no lo edita. -->

## Resumen (máximo 5 líneas)

- **Veredicto global:** PASA
- **Conteo:** 6 PASA · 0 NO PASA · 0 NO PROBADO
- **Bloqueantes:** ninguno

---

- **Fecha y hora:** 2026-11-25 14:52 -0500
- **Commit base revisado:** `8685a9e`
- **Entrega revisada:** ninguna (prueba en seco del relevo ADR-004)
- **Carpeta de trabajo:** `%TEMP%/aco-qa/ronda-000/` (`C:\Users\Usuario\AppData\Local\Temp\aco-qa\ronda-000`)

## `git status --short` antes de la ronda

```
 M .handoff/ESTADO.md
```

*(Nota: `.handoff/ESTADO.md` ya estaba modificado por el operador al cambiar el turno a `QA` antes de iniciar esta ronda.)*

## Veredicto por punto

| # | Punto revisado | Estado | Evidencia (comando o archivo) |
|---|---|---|---|
| 1 | Verificación de turno y reglamento ADR-004 | PASA | `.handoff/ESTADO.md` (`TURNO: QA`, `RONDA: 000`), `.handoff/README.md`, `.handoff/plantillas/reporte_qa.md` |
| 2 | Copia limpia aislada en `%TEMP%/aco-qa/ronda-000/` | PASA | `robocopy "d:\experimento\ACO-test" "$env:TEMP\aco-qa\ronda-000" /E /XD ".git" "__pycache__" ".pytest_cache"` (código salida < 8) |
| 3 | Suite del gemelo en copia temporal (esperado: 318) | PASA | Desde `gemelo/` de la copia: `C:/Users/Usuario/anaconda3/envs/aco-gemelo/python.exe -B -I -X utf8 -m pytest -q -p no:cacheprovider -W ignore` → `318 passed in 214.88s (0:03:34)` |
| 4 | Suite del oráculo en copia temporal (esperado: 7) | PASA | Desde raíz de la copia: `C:/Users/Usuario/anaconda3/envs/aco-gemelo/python.exe -X utf8 -m pytest oraculo -q` → `7 passed, 17 warnings in 8.32s` |
| 5 | Prueba de humo QA e importación de `aco_gemelo` vía `conftest.py` | PASA | `.handoff/pruebas_qa/test_qa_000_humo.py`; desde la raíz: `C:/Users/Usuario/anaconda3/envs/aco-gemelo/python.exe -B -I -X utf8 -m pytest .handoff/pruebas_qa -q -p no:cacheprovider -W ignore` → `1 passed in 0.02s` |
| 6 | Cero efectos colaterales en el repositorio real | PASA | `git status --short` final: solo aparecen este reporte y `.handoff/pruebas_qa/test_qa_000_humo.py`, además del cambio previo del operador en `.handoff/ESTADO.md` |

## Hallazgos (del más grave al más leve)

Ninguno. Las suites del gemelo (318/318), del oráculo (7/7) y la prueba de humo de QA (1/1) pasaron en su totalidad sin fallos y sin efectos colaterales en el repositorio.

*(Nota menor informativa, no bloqueante: al ejecutar la suite del oráculo con el comando exacto solicitado sin `-W ignore`, pytest reportó 17 advertencias de terceros —`PyparsingDeprecationWarning` en `matplotlib` y `UserWarning: FigureCanvasAgg is non-interactive` al ejecutar `deneubourg_puente_doble.ipynb`—; todas las 7 pruebas pasaron.)*

## Pruebas nuevas en `pruebas_qa/`

| Archivo | Qué prueba | Resultado con el código actual |
|---|---|---|
| `test_qa_000_humo.py` | Importación de `aco_gemelo` desde `gemelo/` vía `conftest.py` y verificación de `__version__` no vacío | PASA (`1 passed in 0.02s`) |

Comando: `C:/Users/Usuario/anaconda3/envs/aco-gemelo/python.exe -B -I -X utf8 -m pytest .handoff/pruebas_qa -q -p no:cacheprovider -W ignore` (desde la raíz).

## Lo que no se pudo comprobar

- No aplica revisión de cambios funcionales ni de entrega `rondas/000-para_qa.md`, por tratarse de la prueba en seco (ronda 000) de configuración del flujo ADR-004.
- No se ejecutaron por separado comandos de `nbconvert` ni `aco_gemelo experimentos --salida ...` fuera de lo cubierto por la suite de 318 pruebas del gemelo.

## `git status --short` después de la ronda

```
 M .handoff/ESTADO.md
?? .handoff/pruebas_qa/test_qa_000_humo.py
?? .handoff/rondas/000-reporte_qa.md
```
