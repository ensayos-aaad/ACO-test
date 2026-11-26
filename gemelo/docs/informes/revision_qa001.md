# Reproducción de los hallazgos de QA — ronda 001

**Autor:** agente `revisor` · **Fecha:** 2026-11-25 (≈ 18:20–18:30 -0500) · **Revisado:** `.handoff/rondas/001-reporte_qa.md`
(Gemini) sobre el árbol de trabajo (sin commit sobre `ffcf646`) y sobre una copia de `ffcf646` sacada con `git archive`.
No se modificó el repositorio. Guardado en el repositorio por la orquestadora el 2026-11-25, después de cerrar la
ronda 002: en su momento solo quedó en la conversación (regla de `USO-DEL-PROTOCOLO.md` §7.3, incumplida y corregida).

| # | Veredicto | ¿Regresión de la ronda 001? |
|---|---|---|
| H1 | Se reproduce | **Sí** |
| H2 (`true`, `1.5`, `false`) | Se reproduce en los tres casos | **No**: `ffcf646` hace exactamente lo mismo |
| H3 (dos escenarios) | Se reproduce | Escenario 2: **sí** (misma causa que H1) |
| H4 | Se reproduce (medido) | No aplica |
| Pruebas de QA | Coinciden: 4 failed, 56 passed | — |

## Detalle

- **H1** (`__main__.py:47`, `config_ensayo(datos)` sin semilla): con un YAML con `semilla: -3` y `run --semilla 3 --png`, se
  imprimen las métricas, luego `Error: semilla = -3 ...`, código 2 y sin PNG. En `ffcf646`: código 0 y PNG, con métricas
  idénticas. Pasa también con 1.5, "3", true y null en el YAML, y **también sin `--png`** (el reporte lo describía más
  estrecho). Con el mismo YAML, `batch` da código 0.
- **H2** (`experimentos.py:48`): `true` → código 0 y CSV con una fila de `semilla=0`; `1.5` → código 1 con `TypeError`;
  `false` → código 1 con `IndexError` y además una carpeta vacía (el reporte no lo menciona). **Idéntico en `ffcf646`.**
- **H3:** escenario 2 (plan `[0, 1]` con base `semilla: -3`): código 2 y carpeta vacía; en `ffcf646`, código 0 con CSV:
  **regresión**, misma causa que H1 (`experimentos.py:73`). Escenario 1 (`[0, -1]`): rechazarlo es lo esperado; queda el
  orden (la carpeta se crea antes de validar).
- **H4:** el historial sí entra en la huella (`len historial 344`, `historial en repr: True`); el comentario estaba mal y la
  prueba es más estricta de lo que decía.
- **Pruebas de QA:** las 4 que fallan prueban exactamente H1 y H2. Ninguna de las que pasan parece pasar por casualidad;
  tres son débiles o merecen un ojo (una da por bueno el orden que H3 señala como defecto; otra solo comprueba
  reproducibilidad dentro de un proceso; otra vigila un truncado a 16 bits que ningún código hace).

## Afirmaciones del reporte de QA equivocadas o sin evidencia

1. **La gravedad de H2 no cuadra:** sale como "bloquea" de esta ronda, pero el código es idéntico al de `ffcf646` (y la frase
   "agravada por aceptar booleanos" es inexacta: ya pasaba igual). La fila 10 del mismo reporte da PASA a esa familia.
2. **H3.2 es la misma regresión que H1**, pero el reporte la marca "no bloquea" y no dice que sea regresión.
3. **H1 se describe más estrecho de lo que es:** falla también sin `--png` ni `--animacion`.
4. La tabla de veredictos sí cuadra (9/1/1 en 11 filas).

**No comprobado:** las filas 1–3 (suites), 5 (mutante), 9 (CSV publicados) y 11 (otra máquina); que en H3.1 la semilla 0
se ejecute antes de fallar (deducido del código, no medido).
