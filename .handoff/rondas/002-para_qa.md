# Ronda 002 — entrega de Desarrollo a QA

- **Fecha y hora:** 2026-11-25 20:18 -0500
- **Commit base:** `ffcf646`. Los cambios de las rondas 001 y 002 están **sin commit**, en el árbol de trabajo (`git diff ffcf646`).
- **Quién entrega:** Claude (orquestadora)
- **Revisión interna previa:** PASA (`gemelo/docs/informes/revision_r002.md`); sus 3 observaciones leves, atendidas antes de entregar.
- **Reproducción de tu reporte 001 por el revisor:** H1–H4 se reproducen; H1 y H3.2 son regresión de la ronda 001; H2 y H3.1
  ya pasaban en `ffcf646` (ver F-029 en `FAILURES.md`).

## Objetivo del cambio

Corregir los hallazgos de tu reporte `rondas/001-reporte_qa.md` y cerrar lo que la revisión interna encontró al verificarlo.

| Hallazgo | Corrección |
|---|---|
| H1 (`__main__.py`) | `run` usa la semilla en uso (`--semilla` o la del archivo) también al leer `n_agentes`; ya no valida la del archivo cuando `--semilla` la reemplaza |
| H2 (`experimentos.py`) | `semillas` del plan se valida al leer el plan (`_semillas`): un entero ≥ 1 o una lista no vacía de enteros ≥ 0, sin booleanos. Lo demás da `ValueError` → `Error: ...`, código 2 |
| H3 (`experimentos.py`) | `condiciones` valida con una semilla del plan (la del archivo base no se usa); `correr_plan` valida todo **antes** de crear la carpeta de salida |
| H4 (`tests/test_reproducibilidad.py`) | Comentario corregido: la huella incluye historial, serie, feromona y mapa de la madre |
| O3 de la revisión (`__main__.py`, ya pasaba antes) | `batch --semillas 0` o negativo: error limpio y código 2, sin crear nada (antes `IndexError` con traza) |

Una semilla inválida **dentro de la lista** del plan da el mismo texto que en los demás puntos de entrada
(`semilla = X (en 'semillas' del plan): debe ser un entero mayor o igual que 0`); un número o un tipo inválido en
`semillas` da su propio mensaje (`semillas = 0: si es un número, debe ser al menos 1`, `semillas = True: debe ser ...`).

## Archivos modificados en esta ronda (además de los de la 001)

| Archivo | Qué cambió |
|---|---|
| `gemelo/aco_gemelo/__main__.py` | H1 y O3 |
| `gemelo/aco_gemelo/experimentos.py` | `_entero`, `_semillas`, validación en `condiciones` con la semilla del plan, orden validar → crear carpeta |
| `gemelo/tests/test_reproducibilidad.py` | H4 (comentario) |
| `gemelo/tests/test_cli.py` | 7 pruebas: H1 (5 valores de semilla en el archivo) y O3 (`--semillas` 0 y −2) |
| `gemelo/tests/test_experimentos.py` | 14 pruebas: H2/H3 (12 valores inválidos de `semillas`), semilla inválida en la base, y el orden validar → crear (factor inválido) |
| `FAILURES.md` | F-029 |

Tus pruebas de `.handoff/pruebas_qa/` **no** se incorporaron a `gemelo/tests/` (falta la aprobación del operador).

## Cómo probarlo

Sobre una copia en `%TEMP%/aco-qa/ronda-002/`. `<python>` = `C:/Users/Usuario/anaconda3/envs/aco-gemelo/python.exe`.

```
# desde gemelo/ de la copia
<python> -B -I -X utf8 -m pytest -q -p no:cacheprovider -W ignore
# desde la raíz de la copia
<python> -B -I -X utf8 -m pytest oraculo -q -p no:cacheprovider -W ignore
<python> -B -I -X utf8 -m pytest .handoff/pruebas_qa -q -p no:cacheprovider -W ignore
```

Y tus comandos de reproducción de H1 y H2 del reporte 001, que ahora deben dar código 0 con PNG (H1) y código 2 sin
carpeta ni CSV (H2).

## Casos borde que QA debería validar

1. Combinaciones de `run`: `--semilla` válida con YAML inválido, con y sin `--png`/`--animacion`, con los tres motores; y
   sin `--semilla` con YAML inválido (debe dar error).
2. Planes: `semillas` con repetidos (`[0, 0, 1]`), enteros enormes, una lista de un elemento, `semillas` ausente (por
   defecto 30); y que ningún plan inválido deje carpeta ni CSV.
3. `batch`: `--semillas` 0, negativo y 1; `--semilla-inicial` negativo; que no quede nada escrito cuando falla.
4. Que los planes publicados no cambian (18 CSV byte a byte).
5. Cualquier otro sitio que reconstruya una configuración o un mundo sin la semilla en uso (es el patrón de la regresión
   H1; la revisión interna no encontró otro, pero es lo que se le escapó en la ronda 001).

## Lo que Desarrollo no probó

- Otra máquina, sistema operativo o versión de Python (solo este Windows con Python 3.12.7).
- Una primera corrida de `.handoff/pruebas_qa` del revisor dio un `TimeoutExpired` con tiempo negativo (−4124 s) en
  `test_qa_001_semillas_grandes_reproducibles_entre_procesos[0]`; repetida, pasó. Probable suspensión del equipo o salto
  de reloj; no se midió la causa.

## Observaciones conocidas, fuera de esta ronda

- Construir `Agente` a mano no valida la semilla (`agente.py:136`); ningún camino de uso pasa por ahí sin validar.

## Resultados esperados

- Gemelo: **347 passed**. Oráculo: **7 passed**. `.handoff/pruebas_qa`: **60 passed** (las 4 que fallaban en la 001 ahora pasan).
- H1: código 0 y PNG creado. H2 (`true`, `1.5`, `false`): código 2, `Error: ...`, sin carpeta ni CSV.
- 18 CSV publicados idénticos byte a byte.
- `git status --short` del repositorio real: solo los cambios de las rondas 001 y 002 listados arriba, las entregas y
  reportes de `.handoff/rondas/`, los informes `revision_r001.md` y `revision_r002.md`, y tus archivos de `pruebas_qa/`.
