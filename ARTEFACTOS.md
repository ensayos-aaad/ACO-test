# ARTEFACTOS — software del gemelo y su estado

Actualizado: 2026-11-19 23:40 -0500. Todo el producto va a **`gemelo/`**, salvo el oráculo, que va a `oraculo/`.

**Estado:** Por hacer · Borrador · En curso · Hecho.
**Avance** = criterios de aceptación del artefacto en estado PASA ÷ total de criterios. No es una
estimación subjetiva. El operador pidió porcentajes y PROMPT-ZERO los prohíbe "a ojo"; se usan
solo con esta definición.

| # | Artefacto | Directorio | Estado | Avance |
|---|---|---|---|---|
| 1 | Entorno reproducible (`environment.yml`) | `gemelo/` | **Hecho** | 100 % (3/3) |
| 2 | Especificación del protocolo | `gemelo/docs/` (hoy `PROTOCOLO.md`) | Borrador v0.3 | 67 % (2/3) |
| 3 | Codificadores JSON ↔ binario | `gemelo/aco_gemelo/protocolo/` | **Hecho** | 100 % (3/3) |
| 4 | Mundo + BFS + escenarios (L, aleatorio, puente doble) | `gemelo/aco_gemelo/mundo/` | **Hecho** | 100 % (4/4) |
| 5 | Canal en memoria (con retardo y pérdida simulados) | `gemelo/aco_gemelo/canal/` | **Hecho** | 100 % (3/3) |
| 6 | Agente (paso no bloqueante, roles, verificadora) | `gemelo/aco_gemelo/agente/` | **Hecho** (falta lo que depende de la madre) | 100 % (4/4) |
| 7 | Madre (4 modos, memoria en bytes) | `gemelo/aco_gemelo/madre/` | **Hecho** | 100 % (4/4) |
| 8 | Motores (determinista con semilla + hilos) | `gemelo/aco_gemelo/motor/` | **Hecho** | 100 % (3/3) |
| 9 | Configuración YAML + línea de comandos | `gemelo/configs/` · `gemelo/aco_gemelo/` | **Hecho** | 100 % (2/2) |
| 10 | Métricas (convergencia, calidad frente al BFS, conocimiento, bytes) | `gemelo/aco_gemelo/metricas/` | **Hecho** | 100 % (3/3) |
| 11 | Visualización (PNG, GIF y MP4 con el estilo del plano) | `gemelo/aco_gemelo/visual/` | **Hecho** | 100 % (2/2) |
| 12 | Oráculo del puente doble (a partir de los notebooks) | `oraculo/` | **Hecho** | 100 % (3/3) |
| 13 | Pruebas automáticas (pytest) | `gemelo/tests/` | **Hecho** | 100 % (1/1) |
| 14 | Experimentos en lote → CSV (4 modos × 30 semillas) | `gemelo/experimentos/` | **Hecho** | 100 % (2/2) |
| 15 | Notebook de análisis | `gemelo/notebooks/` | **Hecho** | 100 % (2/2) |
| 16 | Demostración del mundo en NetLogo + puente Python | `gemelo/netlogo/` | Por hacer | 0 % (0/3) |
| 17 | **Guía de reproducción autocontenida** | `gemelo/REPRODUCIR.md` | Por hacer | 0 % (0/4) |

**Orden de trabajo vigente** (aprobado el 2026-11-18 23:46 -0500; detalle en `PLAN-MEJORAS.md`): el 17 va **antes**
que el 16. `[x]` = hecho y revisado con PASA · `[~]` = implementado, pero con NO PASA o sin revisar · `[ ]` = por hacer.

- [x] **A.** Correcciones: F-020 (la madre ya no rescata a la verificadora), experimentos repetidos, notas en F-010/13/18/19.
- [x] **B + C.** Motor (B1–B7) y métricas (C1–C4). NO PASA (F-023) → corregido (F-024, F-025) → **PASA** (F-026). Tocó los artefactos 5, 8, 9, 10 y 11.
- [x] **D.** Notebook más explicable (D1–D8, amplía el artefacto 15): secciones 1–3 y 5, "Qué mirar", glosario, 4 informes por experimento (F-027, F-028). Lo técnico, con PASA; cerrado por decisión del operador: la última corrección de texto usa la redacción del revisor y no tuvo una cuarta pasada.
- [ ] **Artefacto 17.** ← *siguiente* Guía de reproducción, verificada por el revisor siguiéndola desde cero.
- [ ] **E.** Registros (E1–E4).
- [ ] **Artefacto 16.** Demostración con NetLogo, y su sección en la guía.

## Criterios de aceptación por artefacto

1. ✅ Se crea con `conda env create` · ✅ fija las versiones · ✅ las pruebas corren dentro del entorno (`tests/test_entorno.py`: 2 PASA, 2026-11-16 20:50 -0500).
2. ✅ Ejemplo binario verificado · el operador lo aprueba (pendiente) · ✅ incluye la verificadora (H4, v0.2).
3. ✅ Lo que se codifica y decodifica vuelve igual (JSON y binario; 16 mensajes × 4 contextos × 100 casos) · ✅ los tamaños coinciden con la especificación · ✅ el JSON y el binario llevan la misma información (`tests/test_protocolo.py`: 74 PASA, 2026-11-16 20:58 -0500).
4. ✅ La meta siempre es alcanzable (200 semillas por escenario) · ✅ el BFS con 8 vecinos no corta esquinas · ✅ la L coincide con el plano · ✅ el escenario de puente doble está parametrizado por r (`tests/test_mundo.py`: 18 PASA, 2026-11-16 20:54 -0500).
5. ✅ Entrega dentro del radio r · ✅ las pérdidas y retardos son los mismos con la misma semilla · ✅ cuenta mensajes y bytes por familia (`tests/test_canal.py`: 18 PASA, 2026-11-16 21:00 -0500).
6. ✅ Nunca entra en un obstáculo ni sale de la grilla (y nunca lo intenta) · ✅ la memoria K se respeta · ✅ cambia de rol por umbral · ✅ la verificadora solo explota y no vuelve sobre sus pasos (`tests/test_agente.py`: 25 PASA, 2026-11-16 21:10 -0500). Además: **C1 en PASA** a nivel del programa de agente (la regla reproduce la fórmula de Deneubourg en el puente doble, 6 casos, N = 20 000). **Queda para el artefacto 7:** que el agente envíe `FRAGMENTO` y `BALIZA` y que use `RECLUTA`, `RUTA`, `MAPA` y `STOP`.
7. ✅ Los 4 modos son seleccionables · ✅ actúa solo cada Δt · ✅ no supera su presupuesto de bytes · ✅ detecta a la rezagada por umbral (`tests/test_madre.py`: 33 PASA, 2026-11-16 21:27 -0500). El agente ya envía `FRAGMENTO` y usa `RECLUTA`, `RUTA` y `MAPA`. **No implementado:** `BALIZA`, `ALERTA`, `SIGUEME` (mensajes entre agentes, decisión E1) y `STOP`; tampoco el envío de `FIN`.
8. ✅ Misma semilla ⇒ mismo resultado (los 4 modos; también con pérdidas, retardos y mundo aleatorio) · ✅ el motor de hilos corre el mismo `paso()` (sin madre da exactamente lo mismo que el determinista) · ✅ el ensayo tiene límite de pasos (H1) (`tests/test_motor.py`: 17 PASA, 2026-11-17 02:49 -0500). El motor también lanza la verificadora y difunde `FIN`.
9. ✅ Toda la configuración sale del YAML (cada parámetro se puede cambiar; una clave desconocida es un error) · ✅ `run` y `batch` funcionan, también como `python -m aco_gemelo` (`tests/test_cli.py`: 28 PASA, 2026-11-17 02:55 -0500). Configuraciones de ejemplo: `default.yaml`, `aleatorio.yaml` y `puente_doble.yaml`.
10. ✅ Mide la convergencia según G1 (también como serie tick a tick) · ✅ calidad = largo de la ruta / largo del BFS · ✅ cuenta bytes por familia de mensaje (`tests/test_metricas.py`: 15 PASA, 2026-11-17 03:02 -0500). Además: **conocimiento del mundo de la madre** (fracción de celdas que conoce y clasifica bien) y resumen de lote con intervalos de confianza de Wilson al 95 %.
11. ✅ PNG del estado final (con la ruta de la verificadora) · ✅ animación GIF/MP4, un cuadro por tick (`tests/test_visual.py`: 11 PASA, 2026-11-17 03:10 -0500). Desde la línea de comandos: `run ... --png final.png --animacion ensayo.gif`. Ejemplo en `gemelo/docs/imagenes/`.
12. ✅ Reproduce p1 (celda [5]; error ≤ 1e-12) · ✅ la dinámica (celda [7]; p_s final = 0,924 ≥ 0,9) · ✅ el histograma de r = 1 (extremos 70,7 % ≥ 70 %, **muy justo**) y r = 2 (80–100 %: 75,1 % ≥ 70 %), con las tolerancias de `oraculo/TOLERANCIAS.md` declaradas antes de correr (`oraculo/test_oraculo.py`: 7 PASA, 2026-11-17 03:17 -0500). La comparación del gemelo (C1–C5) está en `oraculo/RESULTADOS.md`.
13. ✅ Todas las pruebas en PASA: 259 del gemelo y 7 del oráculo, en una sola corrida (2026-11-17 05:05 -0500). Última corrida: **318 del gemelo + 7 del oráculo en PASA** (2026-11-19 23:40 -0500, B + C cerrado con PASA del revisor, F-026).
14. ✅ Genera un CSV por condición (más `resumen.csv` con intervalos de confianza) · ✅ se puede reproducir con la semilla, sin importar el número de procesos (`tests/test_experimentos.py`: 11 PASA, 2026-11-17 04:49 -0500). Planes: `experimentos/modos.yaml` y `experimentos/rescate.yaml`; datos en `experimentos/datos/`.
15. ✅ Gráficas comparativas (4 figuras en `notebooks/figuras/`; desde el bloque D, 9 figuras y un GIF, con un ensayo comentado) · ✅ prueba estadística de la varianza con y sin rescate (Brown-Forsythe, más Mann-Whitney y Fisher, con Bonferroni) (`tests/test_notebook.py`: 1 PASA, 2026-11-17 04:58 -0500). Conclusiones calculadas desde los datos.
16. El mundo vive en los patches · `py:setup` usa el Python del entorno · un agente Python se mueve según el protocolo.
17. Ver la sección siguiente.

## Requisitos de la guía de reproducción (artefacto 17)

La meta es que **cualquiera con los recursos pueda reproducir el experimento sin preguntar nada**.
La guía debe:

1. **Listar los prerrequisitos con versiones** (los de `CHECKLIST-ENTORNO.md` y `environment.yml`), con el hardware de las fases 2 y 3 aparte.
2. **Ir paso a paso desde cero:** clonar el repo → crear el entorno → correr las pruebas → correr el escenario L con la semilla de referencia → **comparar con la salida esperada**, incluida en el repo (CSV y PNG de referencia).
3. **Explicar el porqué de cada experimento**, enlazando a lo que hay en el repo: `CONTEXT.md`, `DECISIONES-PRUEBA.md`, `PROTOCOLO.md`.
4. **Incorporar los experimentos previos de la referencia** que llevaron a esto, con lo que aportó cada uno:
   - Notebooks del puente doble (`referencia/ACO/experimento_doble-puente/`): el oráculo de la regla de feromona.
   - Agentes AIMA en NetLogo y Python (`referencia/simuladores/netlogo/aspiradora/`): la separación entre programa de agente y arquitectura.
   - Ejemplos 3 a 6 (`referencia/simulaciones/`): ESP32 ↔ NetLogo por serial, `py:setup` con Anaconda, puertos virtuales y un protocolo síncrono. Son la base de las fases 2 y 3.
   - Holland & Melhuish en NetLogo (`referencia/papers/1/`) y `referencia/resumen.pdf`: la estigmergia y la hipótesis del rescate.
   - Además, las **trampas conocidas de Windows**: consola en cp1252 → usar `-X utf8` (F-002); el `python` del PATH no es Anaconda (F-005).
5. **No depender de enlaces externos:** todo lo necesario está dentro del repo (la `referencia/` copiada).
