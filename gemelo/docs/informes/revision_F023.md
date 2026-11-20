# Revisión F-023 — reproducciones de cada defecto (antes de corregir)

**Autor:** agente `revisor` · **Fecha:** 2026-11-19 (≈ 21:00–21:25 -0500) · **Código revisado:** commit `42e0943`
(`gemelo/aco_gemelo/` y `configs/` sin cambios respecto a ese commit).
**Para qué:** el informe original de F-023 (2026-11-18) se perdió con la sesión; este lo reemplaza y sirve de
**prueba de aceptación** de las correcciones. Los scripts están en `revision_F023/` y se corren desde `gemelo/` con
`PYTHONPATH=. <python de aco-gemelo> -B -X utf8 docs/informes/revision_F023/<script>`. Los `mut_*.py` son mutantes
que se cargan con `-p` para ver si una prueba detecta la falta de su mejora.

**Resultado:** los 8 puntos de F-023 se reproducen; ninguno desapareció. Base: 281 pruebas en PASA.

| # | Defecto | Reproducción | Hoy | Debería dar |
|---|---|---|---|---|
| 1 | `hilos_sincronos` no es determinista con pérdidas o retardo | `p1.py`, `p1b.py` (L, semillas 0–4, 4 modos) | Distintos del determinista: canal por defecto 0/20 · pérdidas 0,2: 8/20 · retardo (0,3): 11/20 · ambos: 12/20. Caso mínimo: `DIFUSION`, semilla 0, retardo (0,3): 89 frente a 91 ticks | 0 distintos en todo, repitiendo cada caso ≥ 3 veces. Causa: un solo `_rng` compartido en `CanalMemoria.enviar` |
| 2 | `INICIO` gasta números del generador del canal | `p2.py`, `p2c.py`, `p2d.py` | Con pérdidas 0,2 y retardo (0,3), semillas 0–9 × 3 modos con madre: 22/30 cambian `ticks_total` y 7/30 `motivo`. Con `INICIO` neutralizado: 0/60 distintos frente a `79dd6d8` (antes de B): es la única causa | Lo mismo que `79dd6d8`, **o** documentar el cambio y medir de nuevo. Los datos de F-022 con pérdidas no están en el repo |
| 3 | Un ensayo abortado rompe la visualización | `p3c.py` (L semilla 0, `n_agentes=1`, la agente queda FALLIDA en el tick 2) | `KeyError('abortado')` en `visual.py:206-207` | Un PNG con un texto para "abortado" (`animar` usa la misma `_texto`) |
| 4 | El escenario personalizado acepta inicio = meta | `p4.py` (5×5, inicio = meta = (2,2)) | Se acepta con `largo_optimo = 0`; `pista_de_baile` cae con `ZeroDivisionError` (`madre.py:201`); los otros modos dan "verificada" con 0 movimientos | `ValueError` en `crear_mundo`. Además: con `escenario: L`, `obstaculos`/`inicio`/`meta` se ignoran sin aviso; obstáculos duplicados se aceptan (leve) |
| 5 | Pruebas que no detectan su propio defecto | `mut_b3.py`, `mut_b5.py`, `mut_b7.py`, `p5_b5.py` | `test_b3` pasa con el mutante (en `DIFUSION` semilla 1 máxima = final = 40). `test_b5` pasa sin el `sorted` (el determinista ya llama en orden). `test_b7` pasa 3/3 con la madre sin ordenar (1 semilla, canal por defecto, 1 corrida) | `test_b3`: un caso con máxima > final (`PISTA_DE_BAILE` semilla 0: 34 frente a 26) y `max ≤ ConfigMadre.memoria`. `test_b5`: enviar `ACCION` 3, 1, 2 y comprobar que se aplican 1, 2, 3 (ideal: un choque). `test_b7`: varias semillas, pérdidas y retardo, repetido. Extra: `test_b4` debe asegurar que al menos una semilla termine verificada o con falla |
| 6 | La lectura final (B4) cambia `conocimiento` y desalinea el último cuadro de `mapa_madre` | `p6.py` (retardo (2,4), `DIFUSION`/`RESCATE`, semillas 0–14) | 1/30: `DIFUSION` semilla 3 da `conocimiento` 0,671875; el último cuadro equivale a 0,640625 (41 frente a 43 celdas) | El último cuadro coincide con `conocimiento` en el 100 % (cuadro de cierre, o calcular antes de leer), y el efecto queda documentado |
| 7 | `delta_t` > 255 falla con madre | `p7.py` | 256 y 300 con `pista_de_baile`: `ValueError ... no cabe en 8 bits` al construir `INICIO`. Igual con `agente.K = 256` | `ValueError` claro al validar la configuración |
| 8 | Documentación | — | Ver la lista | Corregida |

**Punto 8, la lista:** `simulacion.py:90` (`Resultado.motivo` sin "abortado") · `simulacion.py:180` ("uno de los dos
motores"; son tres) · `simulacion.py:20-23` y `Madre.leer` (`madre.py:135-141`) dicen que con hilos se llega al mismo
resultado, falso con pérdidas o retardo · docstring de `CanalMemoria`: no dice que a lo que lleva ACK igual se le
sortea retardo · `configs/default.yaml:9`: falta `personalizado` y un ejemplo · `crear_mundo` (`config.py:110`) no
menciona el personalizado · `INICIO` se envía pero ninguna agente lo lee (solo cuenta como tráfico), y
`semilla & 0xFFFF` la recorta sin aviso · falta anotar en `PLAN-MEJORAS.md`/`FAILURES.md` el efecto de B4 (punto 6).

**No comprobado:** las cifras originales de F-023 (no hay datos guardados; estas muestras son más chicas y apuntan en
la misma dirección); la animación GIF/MP4 con un ensayo abortado; una forma natural de abortar sin forzar el estado.
