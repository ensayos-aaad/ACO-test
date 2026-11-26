# Revisión interna previa — ronda 002 de QA (correcciones de la ronda 001)

**Autor:** agente `revisor` · **Fecha:** 2026-11-25 · **Revisado:** cambios sin commit sobre `ffcf646` (ronda 001 más las
correcciones de H1–H4). Temporales en la carpeta de trabajo del revisor.

**Veredicto: PASA.** Los 4 hallazgos de la ronda 001 están corregidos; sin regresiones ni defectos nuevos de lógica.

| # | Punto | Estado | Evidencia |
|---|---|---|---|
| 1 | H1–H4 corregidos | PASA | H1: `run --semilla 3 --png --animacion` sobre YAML con semilla −3, 1.5, "3", true o null → código 0 y archivos creados; sin `--semilla`, código 2. H2: `semillas:` true, false, 1.5, 0, −3, "3", [0,−1], [0,1.5], [0,true], [], {a:1} o null → `Error:`, código 2, sin carpeta. H3: plan [0,1] con base `semilla: -3` corre con 0 y 1. H4: comentario corregido |
| 2 | Ninguna otra llamada reconstruye configuración o mundo sin la semilla en uso | PASA | `config_ensayo(`, `crear_mundo(`, `ConfigEnsayo(`, `Simulacion(` en todo el repositorio (CLI, experimentos, oráculo, línea base, notebook): todas pasan la semilla o usan la del mismo `datos` |
| 3 | La validación no rompe planes válidos | PASA | 1, 30, [0,0,1], [5], [2³¹, 10¹², 2⁶⁴]; plan real con [0, 0, 2⁶⁴] y base inválida corre; `modos.yaml` y `rescate.yaml`: 18/18 CSV idénticos byte a byte |
| 4 | Las pruebas nuevas fallan sin el arreglo | PASA (O1) | Sobre la ronda 001 fallan los 18 casos nuevos; 5 mutantes de una línea, todos detectados |
| 5 | Suites | PASA | Gemelo 344, oráculo 7, `.handoff/pruebas_qa` 60. Una primera corrida de `pruebas_qa` dio un `TimeoutExpired` con tiempo negativo (−4124 s): probable suspensión o salto de reloj; la prueba sola pasa en 28 s y la carpeta repetida da 60 |
| 6 | Defectos nuevos | PASA | Ninguno |

## Observaciones leves (atendidas por la orquestadora antes de entregar)

- **O1:** ninguna prueba protegía el orden "validar antes de crear la carpeta" de `correr_plan` (un mutante que crea la
  carpeta antes pasaba). → Prueba nueva `test_un_plan_invalido_no_crea_la_carpeta_de_salida` (factor inválido), que
  detecta ese mutante.
- **O2:** F-029 decía "mensaje de error igual en todos los puntos de entrada"; solo es cierto para una semilla inválida
  dentro de la lista. → Redacción corregida en F-029.
- **O3 (ya pasaba en `ffcf646`):** `batch --semillas 0` o `-2` terminaba en `IndexError` con traza y dejaba la carpeta. →
  Error limpio (`--semillas N: debe ser al menos 1`, código 2) antes de crear nada, con prueba.

**No comprobado:** otra máquina, sistema operativo o versión de Python; la causa del tiempo de espera negativo; el notebook
por separado (cubierto por `test_notebook.py`).
