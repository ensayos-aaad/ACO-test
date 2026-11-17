# ARTEFACTOS — software del gemelo y su estado

Actualizado: 2026-11-16 20:29 -0500. Todo el producto va a **`gemelo/`**, salvo el oráculo, que va a `oraculo/`.

**Estado:** Por hacer · Borrador · En curso · Hecho.
**Avance** = criterios de aceptación del artefacto en estado PASA ÷ total de criterios. No es una
estimación subjetiva. El operador pidió porcentajes y PROMPT-ZERO los prohíbe "a ojo"; se usan
solo con esta definición.

| # | Artefacto | Directorio | Estado | Avance |
|---|---|---|---|---|
| 1 | Entorno reproducible (`environment.yml`) | `gemelo/` | Por hacer | 0 % (0/3) |
| 2 | Especificación del protocolo | `gemelo/docs/` (hoy `PROTOCOLO.md`) | Borrador | 33 % (1/3) |
| 3 | Codificadores JSON ↔ binario | `gemelo/aco_gemelo/protocolo/` | Por hacer | 0 % (0/3) |
| 4 | Mundo + BFS + escenarios (L, aleatorio, puente doble) | `gemelo/aco_gemelo/mundo/` | Por hacer | 0 % (0/4) |
| 5 | Canal en memoria (con retardo y pérdida simulados) | `gemelo/aco_gemelo/canal/` | Por hacer | 0 % (0/3) |
| 6 | Agente (paso no bloqueante, roles, verificadora) | `gemelo/aco_gemelo/agente/` | Por hacer | 0 % (0/4) |
| 7 | Madre (4 modos, memoria en bytes) | `gemelo/aco_gemelo/madre/` | Por hacer | 0 % (0/4) |
| 8 | Motores (determinista con semilla + hilos) | `gemelo/aco_gemelo/motor/` | Por hacer | 0 % (0/3) |
| 9 | Configuración YAML + línea de comandos | `gemelo/configs/` · `gemelo/aco_gemelo/` | Por hacer | 0 % (0/2) |
| 10 | Métricas (convergencia, calidad frente al BFS, conocimiento, bytes) | `gemelo/aco_gemelo/metricas/` | Por hacer | 0 % (0/3) |
| 11 | Visualización (PNG, GIF y MP4 con el estilo del plano) | `gemelo/aco_gemelo/visual/` | Por hacer | 0 % (0/2) |
| 12 | Oráculo del puente doble (a partir de los notebooks) | `oraculo/` | Borrador | 0 % (0/3) |
| 13 | Pruebas automáticas (pytest) | `gemelo/tests/` | Por hacer | 0 % (0/1) |
| 14 | Experimentos en lote → CSV (4 modos × 30 semillas) | `gemelo/experimentos/` | Por hacer | 0 % (0/2) |
| 15 | Notebook de análisis | `gemelo/notebooks/` | Por hacer | 0 % (0/2) |
| 16 | Demostración del mundo en NetLogo + puente Python | `gemelo/netlogo/` | Por hacer | 0 % (0/3) |
| 17 | **Guía de reproducción autocontenida** | `gemelo/REPRODUCIR.md` | Por hacer | 0 % (0/4) |

## Criterios de aceptación por artefacto

1. Se crea con `conda env create` · fija las versiones · las pruebas corren dentro del entorno.
2. ✅ Ejemplo binario verificado · el operador lo aprueba · incluye la verificadora (H4).
3. Lo que se codifica y decodifica vuelve igual (JSON y binario) · los tamaños coinciden con la especificación · el JSON y el binario llevan la misma información.
4. La meta siempre es alcanzable · el BFS con 8 vecinos no corta esquinas · la L coincide con el plano · el escenario de puente doble está parametrizado por r.
5. Entrega dentro del radio r · las pérdidas y retardos son los mismos con la misma semilla · cuenta mensajes y bytes.
6. Nunca entra en un obstáculo ni sale de la grilla · la memoria K se respeta · cambia de rol por umbral · la verificadora solo explota y detecta ciclos.
7. Los 4 modos son seleccionables · actúa solo cada Δt · no supera su presupuesto de bytes · detecta a la rezagada por umbral.
8. Misma semilla ⇒ mismo resultado · el motor de hilos corre el mismo `paso()` · el ensayo tiene límite de pasos (H1).
9. Toda la configuración sale del YAML · `run` y `batch` funcionan.
10. Mide la convergencia según G1 · calidad = largo de la ruta / largo del BFS · cuenta bytes por familia de mensaje.
11. PNG del estado final · animación GIF/MP4.
12. Reproduce p1 (celda [5]) · la dinámica (celda [7]) · el histograma de r = 1 y r = 2 dentro de la tolerancia que se declare.
13. Todas las pruebas en PASA.
14. Genera un CSV por condición · se puede reproducir con la semilla.
15. Gráficas comparativas · prueba estadística de la varianza con y sin rescate.
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
