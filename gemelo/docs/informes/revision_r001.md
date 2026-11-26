# Revisión interna previa — ronda 001 de QA

**Autor:** agente `revisor` · **Fecha:** 2026-11-25 (≈ 15:08–15:15 -0500) · **Revisado:** cambios sin commit sobre `ffcf646`
(`gemelo/aco_gemelo/config.py`, `gemelo/aco_gemelo/motor/simulacion.py`, `gemelo/tests/test_reproducibilidad.py`).

**Veredicto: PASA.** Se puede entregar a QA.

| Punto | Veredicto | Evidencia |
|---|---|---|
| Ningún uso existente se rompe (run, batch, experimentos, YAML, notebook, configs) | PASA | `run --semilla 3 --motor hilos`, `run --png` sobre `aleatorio.yaml`, `batch` 0–2 y las 3 configuraciones de `configs/` funcionan; `run --semilla -3` y `batch --semilla-inicial -2` dan `Error:` y código 2 sin escribir CSV; un plan con `semillas: [0, -1]` y `semilla:` = −3, 3.0, "3" o true en el YAML dan error; `replace(ConfigEnsayo(), semilla=-3)` se rechaza |
| La prueba entre procesos detecta el mutante `mut_hash` | PASA | Sin mutante, PYTHONHASHSEED 0, 1 y 12345 dan la misma huella; con el mutante inyectado en los procesos hijos (`sitecustomize` temporal), la prueba falla con 3 huellas distintas (56, 58 y 46 ticks). El comando de la docstring funciona |
| Ninguna otra entrada de uso normal lleva una semilla negativa a `random.Random` | PASA (observación 1) | El oráculo usa semillas ≥ 0; el canal siembra con texto; `np.int64` ya fallaba antes en `random.Random` (Python 3.12.7) |
| Suite | PASA | 326 del gemelo (copia, 242 s) y 7 del oráculo; `git status` igual antes y después |
| Planes publicados | PASA | `modos.yaml` y `rescate.yaml` con `--salida`: sin diferencias (`diff -r`) |

## Observaciones leves (no bloquean)

1. `gemelo/aco_gemelo/agente/agente.py:136`: construir `Agente` a mano no valida la semilla (`Agente(1, …, semilla=-1)` tiene
   el mismo azar que `Agente(255, …, semilla=0)`). Ningún camino de uso pasa por ahí sin validar: el motor usa siempre la
   semilla de `ConfigEnsayo`.
2. `gemelo/aco_gemelo/experimentos.py:48` y `:74`: un plan con `semillas: -3` (o `0`) termina en `IndexError` con traza, en
   vez de un `Error:` limpio. **Ya pasaba antes** de esta ronda. Con una semilla negativa que no es la primera de la lista, el
   error salta en el proceso trabajador; se reporta y no escribe CSV.

**No comprobado:** `hilos_sincronos` con semilla negativa por separado (pasa por el mismo `ConfigEnsayo`); la reproducibilidad
entre procesos en otra máquina u otro sistema operativo (solo este Windows con Python 3.12.7); los registros de la raíz.
