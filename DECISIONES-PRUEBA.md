# DECISIONES DE LA PRUEBA — gemelo de software (fase 1)

Registro ejecutivo. **No se borra ninguna opción**: la elegida se marca con ✅, las demás quedan
como ❌ descartadas y ⏳ significa pendiente. ⭐ = recomendación de Claude (no es una decisión).
Creado el 2026-11-16. El operador pidió responderlas por bloques, no de a una.
**Ronda 1 cerrada:** 2026-11-16 20:25 -0500. Todas las preguntas A–G están respondidas; quedan abiertas las consecuencias H1–H4 y los parámetros numéricos.

## A. Gobierno y alcance

| ID | Pregunta | Opciones | Estado |
|---|---|---|---|
| A1 | ¿Qué relación tiene el gemelo con PROMPT-ZERO? | ✅ ⭐ **a)** Lo extiende: se mantienen el método y los registros, y §3 (el artefacto) = gemelo<br>❌ **b)** Lo reemplaza<br>❌ **c)** Rama paralela | ✅ a |
| A2 | Meta de la prueba para diciembre de 2026 | ❌ ⭐ **a)** Fase 1 completa (Gantt 1–13 en versión gemelo)<br>✅ **b)** Fase 1 + demostración mínima con NetLogo<br>❌ **c)** Incluir hardware (ESP32/RPi) | ✅ b |
| A3 | Disponibilidad real | ❌ **a)** 1 sesión por semana<br>❌ **b)** 2 sesiones por semana<br>❌ **c)** 3 o más por semana<br>✅ **d)** Indefinida (respuesta del operador): se planifica por **prioridad de etapas**, no por fechas | ✅ d |
| A4 | Entorno de Python | ❌ **a)** `base` de Anaconda<br>✅ ⭐ **b)** Entorno conda propio con `environment.yml` (reproducible) | ✅ b |

## B. Arquitectura de ejecución

| ID | Pregunta | Opciones | Estado |
|---|---|---|---|
| B1 | Motor de ejecución | ❌ **a)** Actores con 2 motores (formulación original)<br>❌ **b)** Solo hilos reales (no se puede reproducir exactamente)<br>❌ **c)** Solo determinista por ticks<br>✅ **d)** El operador delegó la decisión con el criterio "lo más real al llevarlo a los micros". Claude eligió: **cada agente es un paso de ciclo no bloqueante** `paso(ahora)` (patrón `loop()`/`millis()` de la referencia, ejemplo 6; `asyncio` en MicroPython) que solo se comunica por su `Canal`, sin memoria compartida. **Demostración: un hilo por agente (= un micro)**. **Pruebas: el mismo `paso()` con un planificador determinista con semilla** que simula retardos y pérdidas | ✅ d |
| B2 | Formato de serialización inicial | ✅ ⭐ **a)** JSON (legible) y binario después<br>❌ **b)** Binario desde el principio<br>❌ **c)** Ambos desde el principio | ✅ a |

## C. Mundo

| ID | Pregunta | Opciones | Estado |
|---|---|---|---|
| C1 | Escenarios | ✅ ⭐ **a)** "L" del plano fija + aleatorio con semilla<br>❌ **b)** Solo la "L"<br>❌ **c)** Solo aleatorio | ✅ a |
| C2 | Vecindad | ❌ ⭐ **a)** 4 vecinos<br>✅ **b)** 8 vecinos (`mov` de 3 bits; `PERCEPCION` de 11 B; el BFS óptimo también usa 8-vecindad) | ✅ b |
| C2.1 | Con 8 vecinos, ¿se puede pasar en diagonal rozando la esquina de un obstáculo? | ✅ ⭐ **a)** No: la diagonal exige que las dos celdas ortogonales estén libres<br>❌ **b)** Sí: solo importa que la celda destino esté libre | ✅ a |
| C3 | Escenario "puente doble" para validar contra los notebooks | ✅ ⭐ **a)** Sí<br>❌ **b)** No | ✅ a |
| C4 | Número de agentes por defecto | ❌ **a)** 4<br>✅ ⭐ **b)** 6 (el máximo del PDF)<br>❌ **c)** Más de 6 | ✅ b |

## D. Agentes (hormiga / abeja)

| ID | Pregunta | Opciones | Estado |
|---|---|---|---|
| D1 | Regla de decisión | ✅ ⭐ **a)** Ant System τ^α · η^β<br>❌ **b)** Deneubourg (k + τ)^α<br>❌ **c)** Las dos, configurables | ✅ a |

> **Nota de coherencia D1 + C3:** con η = 1, feromona inicial τ₀ = k = 20, depósito de 1 por hormiga y ρ = 0, la regla de Ant System τ^α **es** la de Deneubourg (k + m)^α. El escenario de puente doble valida entonces la misma regla contra los notebooks, sin necesidad de implementar una segunda.
| D2 | Heurística η | ✅ ⭐ **a)** η = 1: el agente no conoce la meta<br>❌ **b)** Distancia Manhattan solo si percibe la meta<br>❌ **c)** Distancia Manhattan siempre | ✅ a |
| D3 | Qué hace al llegar a la meta | ❌ ⭐ **a)** Regresa al inicio reforzando la ruta<br>❌ **b)** Reaparece en el inicio<br>❌ **c)** Se queda en la meta (sin más)<br>✅ **d)** Propuesta del operador: **se queda en la meta y avisa a la madre** (`DANZA`). La madre actualiza a las demás (`RECLUTA`/`MAPA`); ellas tienen ya una noción del punto más feromonizado y van hacia la meta. **Cuando llega la última, se considera conocido el camino.** Luego se lanza **una agente verificadora** desde el origen, que debe llegar a la meta y confirmar que encuentra allí a las otras | ✅ d |
| D3.1 | ¿Cómo se mueve la verificadora? | ✅ ⭐ **a)** Solo explota: en cada paso va a la vecina con más feromona (sin azar)<br>❌ **b)** Con la misma regla probabilística que las demás<br>❌ **c)** Sigue la mejor ruta que tiene la madre (`RUTA`) | ✅ a |
| D4 | Roles | ✅ ⭐ **a)** Exploradora / explotadora, con cambio por umbral<br>❌ **b)** Un solo rol | ✅ a |

## E. Feromona y comunicación

| ID | Pregunta | Opciones | Estado |
|---|---|---|---|
| E1 | Dónde vive la feromona | ❌ ⭐ **a)** En el mundo (estigmergia pura)<br>❌ **b)** La emiten los agentes como balizas<br>✅ **c)** En el mundo + balizas en el modo "mensajes" | ✅ c |
| E2 | En celdas o en aristas | ✅ ⭐ **a)** Celdas<br>❌ **b)** Aristas | ✅ a |
| E3 | Resolución de la feromona | ✅ ⭐ **a)** q4 (16 niveles)<br>❌ **b)** q8 (256 niveles)<br>❌ **c)** Número decimal solo en la simulación | ✅ a |

## F. Madre

| ID | Pregunta | Opciones | Estado |
|---|---|---|---|
| F1 | Modos a implementar | ✅ ⭐ **a)** Los 4: ausente, pista de baile, rescate, difusión cada Δt<br>❌ **b)** Ausente + difusión cada Δt (prompt de Claude Design)<br>❌ **c)** Ausente + rescate (`resumen.pdf`) | ✅ a |
| F2 | Quién detecta al agente rezagado | ✅ ⭐ **a)** La madre (umbral sobre `experiencia` relativa)<br>❌ **b)** El agente (`PIDE_RESCATE`)<br>❌ **c)** Los dos, configurable | ✅ a |
| F3 | Memoria de la madre | ❌ **a)** Ilimitada<br>✅ ⭐ **b)** Presupuesto en bytes (valor por fijar; propuesta: 64 B)<br>❌ **c)** Solo las K mejores rutas | ✅ b |

## G. Métricas

| ID | Pregunta | Opciones | Estado |
|---|---|---|---|
| G1 | Criterio de convergencia | ❌ **a)** Quórum: X % de los agentes en la misma ruta durante W ticks<br>❌ **b)** La mejor ruta = la óptima del BFS<br>❌ **c)** Los dos<br>✅ **d)** Se deriva de D3: **todas las agentes en la meta + la verificadora confirma**. La calidad se mide aparte (largo de la ruta de la verificadora / largo del BFS)<br>❌ **e)** Exigir que la ruta sea la óptima<br>❌ **f)** Quórum de X % + verificadora | ✅ d |
| G2 | Número de semillas por condición | ❌ **a)** 10<br>✅ ⭐ **b)** 30<br>❌ **c)** 100 | ✅ b |

## H. Consecuencias que se deducen de lo elegido (para la siguiente ronda)

| ID | Consecuencia | Por qué |
|---|---|---|
| H1 | **Hace falta un límite de pasos por ensayo.** Si se acaba sin converger, se registra NO PASA | Con G1 = "todas", una sola rezagada bloquea el ensayo para siempre. Aquí encaja el **modo rescate** de la madre: es justo el remedio para la rezagada |
| H2 | **La verificadora necesita una regla para empates y detección de ciclos** | Con D3.1 = solo explotar y E3 = q4, varias vecinas pueden empatar (16 niveles) o puede haber máximos locales. Si cae en un ciclo, el rastro no basta: es NO PASA, y es un resultado informativo |
| H3 | **El depósito se hace a la ida** | Con D3 = d, las agentes no regresan; el refuerzo lo dan la ida y la DANZA → RECLUTA de la madre |
| H5 | **¿Distancia mínima entre inicio y meta?** Hoy pueden salir casi pegados (con la semilla 2026 el óptimo es de 2 movimientos), y ese ensayo es trivial | Detectado al construir el artefacto 4. Opciones: sin mínimo · mínimo fijo (p. ej. óptimo ≥ 5) · mínimo relativo al tamaño del mundo. ⏳ |
| H4 | **Hay que agregar al protocolo** un tipo de agente "verificadora" en `INICIO` y la confirmación final | `DANZA` con una flag de verificación + `FIN` con el motivo "verificada" |
