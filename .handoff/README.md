# .handoff/ — relevo entre Desarrollo y QA

Acuerdo ADR-004 (`DECISIONS.md`), aprobado por el operador el 2026-11-25. Este archivo es el reglamento del relevo;
lo que no esté aquí sigue `PROMPT-ZERO.md` y `CLAUDE.md`.

## Quién es quién

| Equipo | Quién | Qué hace | Dónde escribe |
|---|---|---|---|
| Operador | Tigarto | Decide; **es el único que cambia el turno** en `ESTADO.md`; aprueba los commits | `ESTADO.md` |
| Desarrollo | Claude (orquestadora) | Implementa el código, escribe la entrega a QA, decide las correcciones, lleva los registros | Todo el repositorio salvo `rondas/*-reporte_qa.md` y `pruebas_qa/` |
| Desarrollo | revisor (agente) | Verifica antes de entregar a QA y, al volver el reporte, reproduce (o no) cada hallazgo. No modifica nada | — |
| Desarrollo | experimentador (agente) | Corre experimentos con pruebas declaradas antes | `gemelo/experimentos/`, `gemelo/docs/` |
| Desarrollo | divulgador (agente) | Textos para no especialistas, solo tras un PASA de QA en lo que cuenta | `gemelo/docs/divulgacion/` |
| QA | Gemini (Antigravity) | Audita el código y las pruebas; escribe pruebas nuevas. Solo lectura sobre el resto. No hace commit | `rondas/NNN-reporte_qa.md`, `pruebas_qa/` |

## Turnos

- `ESTADO.md` dice de quién es el turno: `DESARROLLO`, `QA` u `OPERADOR`, y el número de ronda.
- **Nadie modifica archivos fuera de su turno.** En turno de QA, Desarrollo no toca el repositorio; en turno de
  Desarrollo, QA no escribe.

## Una ronda

1. Desarrollo escribe `rondas/NNN-para_qa.md` (plantilla en `plantillas/para_qa.md`).
2. El operador pasa el turno a QA.
3. QA escribe `rondas/NNN-reporte_qa.md` (plantilla en `plantillas/reporte_qa.md`) y, si hace falta, pruebas en
   `pruebas_qa/test_qa_NNN_<tema>.py`.
4. El operador pasa el turno a Desarrollo.
5. El revisor reproduce cada hallazgo.
6. Desarrollo corrige o justifica cada hallazgo; las pruebas de QA entran a `gemelo/tests/` solo si el operador lo aprueba.
7. Nueva ronda (NNN + 1) o PASA.
8. Commit, solo con la aprobación del operador.

`NNN` es el número de ronda con tres dígitos (`001`, `002`, …). Los archivos de una ronda no se borran ni se reescriben:
son la memoria del proyecto (en F-023 se perdió un informe por no guardarlo).

## Reglas para QA

- **Estados:** PASA / NO PASA / NO PROBADO por punto, con un veredicto global.
- **Resumen de máximo 5 líneas al inicio** del reporte: veredicto global, conteo de PASA / NO PASA / NO PROBADO y bloqueantes.
- **Cada hallazgo:** archivo y línea, escenario que lo demuestra, comando exacto y su salida. Lo que no se pudo
  comprobar, dicho explícitamente. Un hallazgo sin evidencia reproducible cuenta como NO PROBADO (F-028).
- **Sin efectos sobre el repositorio:** la suite y el notebook se corren sobre una copia en
  `%TEMP%/aco-qa/ronda-NNN/`; los experimentos, siempre con `--salida` a esa carpeta. El reporte incluye la salida de
  `git status --short` **antes y después** de la ronda: solo pueden aparecer el reporte y `pruebas_qa/`.
- `referencia/` es de solo lectura. No se borra ni se reescribe documentación.
- **Alcance:** cambios de código y de pruebas. Los textos de divulgación los verifica el revisor.

## Entorno y comandos

- Python: `C:/Users/Usuario/anaconda3/envs/aco-gemelo/python.exe`, **siempre con `-X utf8`**. Nunca el `python` del
  PATH (F-002, F-005).
- Pruebas del gemelo (desde `gemelo/`): `<python> -B -I -X utf8 -m pytest -q -p no:cacheprovider -W ignore`
- Pruebas del oráculo (desde la raíz): `<python> -B -I -X utf8 -m pytest oraculo -q -p no:cacheprovider -W ignore`
- **Pruebas de QA** (desde la raíz): `<python> -B -I -X utf8 -m pytest .handoff/pruebas_qa -q -p no:cacheprovider -W ignore`.
  `pruebas_qa/conftest.py` agrega `gemelo/` a la ruta de importación, porque fuera de `gemelo/` pytest no lee
  `gemelo/pyproject.toml` y no encuentra `aco_gemelo`.
- Notebook: `<python> -X utf8 -m nbconvert --to notebook --execute ...`; **no** `-m jupyter nbconvert` (F-027).
- Cuidado: `gemelo/tests/test_notebook.py` borra y regenera figuras versionadas en git; `aco_gemelo experimentos` escribe
  en `gemelo/experimentos/datos/` salvo que se le dé `--salida`. Por eso, siempre sobre una copia.
