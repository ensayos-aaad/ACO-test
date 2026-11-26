# Ronda 001 — entrega de Desarrollo a QA

- **Fecha y hora:** 2026-11-25 15:19 -0500
- **Commit base:** `ffcf646`. Los cambios de esta entrega están **sin commit**, en el árbol de trabajo (`git diff ffcf646`).
- **Quién entrega:** Claude (orquestadora)
- **Revisión interna previa:** PASA (`gemelo/docs/informes/revision_r001.md`)

## Objetivo del cambio

Cerrar las dos observaciones leves que el revisor dejó abiertas al cerrar el bloque B + C (F-026 en `FAILURES.md`):

1. **Reproducibilidad entre procesos:** ninguna prueba comprobaba que el mismo ensayo dé lo mismo en procesos distintos.
   Un generador sembrado con `hash()` de un texto (depende de `PYTHONHASHSEED`) pasaba toda la suite
   (mutante `gemelo/docs/informes/revision_F025/mut_hash.py`).
2. **Semillas negativas:** Python siembra con el valor absoluto (`random.Random(-3)` da lo mismo que `random.Random(3)`),
   así que la semilla −3 repetía en silencio el mundo y las decisiones de la 3. Ahora se rechazan. No cambia ningún
   resultado publicado: todos usan semillas de 0 a 29 (y 2026 en `configs/`).

Toca el criterio 5 del artefacto 8 y C5 de `PROMPT-ZERO.md` (determinismo auditable: semilla registrada, corrida reproducible).

## Archivos modificados

| Archivo | Qué cambió |
|---|---|
| `gemelo/aco_gemelo/motor/simulacion.py` | `ConfigEnsayo.__post_init__` rechaza una semilla que no sea un entero ≥ 0 (`ValueError`, antes de las demás validaciones) |
| `gemelo/aco_gemelo/config.py` | `crear_mundo` rechaza lo mismo antes de sembrar `random.Random(semilla)` |
| `gemelo/tests/test_reproducibilidad.py` (nuevo) | 8 pruebas: el mismo ensayo con todo el azar activo (mundo aleatorio, madre en difusión, pérdida 0,3, retardo 0–3) en 3 procesos con PYTHONHASHSEED 0, 1 y 12345 da la misma huella (sha256 del `repr` del resultado); semillas −1, −3 y −2026 rechazadas en `crear_mundo`, `config_ensayo` y `ConfigEnsayo`; 1.5, "3" y True rechazadas; 0 y 2026 siguen valiendo |

## Cómo probarlo

Sobre una copia en `%TEMP%/aco-qa/ronda-001/` (ver `.handoff/README.md`, "Entorno y comandos"). `<python>` =
`C:/Users/Usuario/anaconda3/envs/aco-gemelo/python.exe`.

```
# desde gemelo/ de la copia
<python> -B -I -X utf8 -m pytest tests/test_reproducibilidad.py -q -p no:cacheprovider -W ignore
<python> -B -I -X utf8 -m pytest -q -p no:cacheprovider -W ignore
# desde la raíz de la copia
<python> -B -I -X utf8 -m pytest oraculo -q -p no:cacheprovider -W ignore
```

Línea de comandos (desde `gemelo/` de la copia):

```
<python> -X utf8 -m aco_gemelo run --config configs/default.yaml --semilla -3      # debe dar "Error: semilla = -3 ..." y código 2
<python> -X utf8 -m aco_gemelo run --config configs/default.yaml --semilla 3       # debe funcionar
<python> -X utf8 -m aco_gemelo batch --config configs/default.yaml --semillas 3 --semilla-inicial -2   # error, sin CSV
```

Para comprobar que la prueba entre procesos detecta el defecto, la docstring de
`test_mismo_ensayo_en_procesos_con_pythonhashseed_distinto` explica cómo correr el guion con el mutante `mut_hash`.

## Casos borde que QA debería validar

1. Semillas negativas, flotantes, texto y booleanas por cada punto de entrada: YAML (`semilla:`), `--semilla`,
   `--semilla-inicial`, un plan de experimentos con `semillas: [0, -1]`, y `dataclasses.replace(ConfigEnsayo(), semilla=-3)`.
2. La semilla 0 y semillas muy grandes (p. ej. 2**31, 10**12) siguen funcionando y son reproducibles.
3. La huella entre procesos con otros valores de PYTHONHASHSEED (p. ej. `random`) y con los motores `hilos_sincronos` y
   `determinista` (deben coincidir entre sí).
4. Que los planes publicados no cambian: `aco_gemelo experimentos --plan experimentos/modos.yaml --salida <temp>` (y
   `rescate.yaml`) frente a `gemelo/experimentos/datos/`, byte a byte.

## Lo que Desarrollo no probó

- La reproducibilidad entre procesos en otra máquina u otro sistema operativo (solo este Windows, Python 3.12.7).
- `hilos_sincronos` con semilla negativa por separado (pasa por el mismo `ConfigEnsayo`).

## Observaciones conocidas, fuera de esta ronda (ya pasaban antes)

- Construir `Agente` a mano no valida la semilla (`agente.py:136`); ningún camino de uso pasa por ahí sin validar.
- Un plan con `semillas: -3` o `0` termina en `IndexError` con traza (`experimentos.py:48` y `:74`) en vez de un error limpio.

## Resultados esperados

- `tests/test_reproducibilidad.py`: 8 passed. Suite del gemelo: **326 passed**. Oráculo: **7 passed**.
- Los 18 CSV de `gemelo/experimentos/datos/modos/` y `rescate/` idénticos byte a byte a los regenerados.
- `git status --short` del repositorio real, antes y después de la ronda: solo los 2 archivos modificados, la prueba
  nueva, `gemelo/docs/informes/revision_r001.md`, esta entrega y (al final) el reporte de QA y `pruebas_qa/`.
