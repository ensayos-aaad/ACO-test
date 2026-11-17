# Estado del gemelo de software antes de pasar al hardware

**Fecha:** 2026-11-17 · **Preparado por:** Claude Opus 5.5, a pedido del operador · **Repositorio:** `ensayos-aaad/ACO-test`

Este documento resume dónde está la implementación en software (fase 1 del gemelo), qué hallazgos dejó, qué
**bloquea** el paso al hardware (ESP32 como agentes, Raspberry Pi como madre) y qué conviene explorar antes.
El detalle de cada punto está en los archivos enlazados.

## 1. Resumen ejecutivo

- **El gemelo de software funciona de punta a punta:** mundo en cuadrícula, 6 agentes, madre con 4 modos, protocolo
  binario/JSON, motores determinista y de hilos, métricas, visualización y experimentos en lote.
- **Fidelidad con la referencia** (notebooks del puente doble, PROMPT-ZERO): **C1, C2, C4 y C5 pasan; C3 no pasa**,
  con la causa documentada (pocas decisiones y percepción de solo 16 niveles). C6 lo evalúa el operador.
- **Hipótesis de `resumen.pdf`** (el rescate reduce la varianza del tiempo de convergencia): **no queda apoyada** con la
  configuración actual. La madre tiende a mejorar la convergencia en mundos aleatorios, pero sin significancia estadística.
- **El agente ya está escrito como en un micro** (un ciclo `paso()` no bloqueante que solo habla por mensajes), y el
  protocolo cabe en paquetes de ESP-NOW (≤ 250 B). Es la base para migrar.
- **Antes del hardware** hay que cerrar 6 decisiones bloqueantes (sección 4), sobre todo el protocolo y el transporte.

## 2. Avance de la implementación en software

Avance = criterios de aceptación en PASA ÷ total (definición de `ARTEFACTOS.md`; no es una estimación a ojo).

| # | Artefacto | Estado | Avance | Nota para el hardware |
|---|---|---|---|---|
| 1 | Entorno reproducible (`gemelo/environment.yml`) | Hecho | 100 % | Solo para la simulación en el PC |
| 2 | Especificación del protocolo (`PROTOCOLO.md` v0.2) | Borrador | 67 % | **Falta la aprobación del operador** (bloqueante B1) |
| 3 | Codificadores JSON ↔ binario | Hecho | 100 % | Tabla única de mensajes: base para los structs de C o MicroPython |
| 4 | Mundo + BFS + escenarios (L, aleatorio, puente doble) | Hecho | 100 % | En hardware el mundo sigue siendo virtual (PC o RPi) |
| 5 | Canal en memoria (radio, retardo, pérdida) | Hecho | 100 % | Falta la implementación MQTT o ESP-NOW con la misma interfaz |
| 6 | Agente (ciclo no bloqueante, roles, viajes, verificadora) | Hecho | 100 % | Es el programa que se porta al ESP32 |
| 7 | Madre (4 modos, memoria en bytes) | Hecho | 100 % | Es el programa que se porta a la RPi |
| 8 | Motores (determinista con semilla + hilos) | Hecho | 100 % | El motor de hilos imita la asincronía de los micros |
| 9 | Configuración YAML + línea de comandos | Hecho | 100 % | |
| 10 | Métricas (convergencia, calidad, conocimiento, bytes) | Hecho | 100 % | El conteo de bytes estima el tráfico real |
| 11 | Visualización (PNG, GIF, MP4) | Hecho | 100 % | |
| 12 | Oráculo del puente doble + comparación C1–C5 | Hecho | 100 % | |
| 13 | Pruebas automáticas | Hecho | 100 % | 259 del gemelo + 7 del oráculo en PASA |
| 14 | Experimentos en lote | Hecho | 100 % | Planes `modos` y `rescate` (480 ensayos) |
| 15 | Notebook de análisis | Hecho | 100 % | |
| 16 | Demostración con NetLogo + puente Python | Por hacer | 0 % | **Próxima sesión.** Es el paso intermedio hacia el hardware (fase 2) |
| 17 | Guía de reproducción autocontenida | Por hacer | 0 % | |

**14 de 17 artefactos hechos**; el 2 (protocolo) está en borrador al 67 %, y el 16 y el 17 están por hacer.

### Criterios de PROMPT-ZERO frente al oráculo (`oraculo/RESULTADOS.md`)

| Criterio | Estado | Valor |
|---|---|---|
| C1 Regla de decisión | **PASA** | La frecuencia de elección coincide con `p1` del notebook (\|z\| máx. 0,94) |
| C2 Ruptura de simetría (r = 1) | **PASA** | 75 % de los ensayos acaba en una sola rama (umbral 70 %) |
| C3 Ramas desiguales (r = 2) | **NO PASA** | La rama corta gana en el 48 % (oráculo 75 %; tolerancia ±15 %). Causa en `oraculo/INVESTIGACION-C3.md` |
| C4 Puntos fijos | **PASA** | 6 % de ensayos en el reparto 40–60 % (umbral 20 %) |
| C5 Determinismo | **PASA** | Misma semilla, mismo resultado |
| C6 Pedagógico | NO PROBADO | Lo evalúa el operador |

## 3. Checklist de hallazgos

`[x]` = atendido (corregido o con decisión tomada) · `[ ]` = abierto. El detalle está en `FAILURES.md`, `CONTEXT.md`
(inconsistencias I1–I16 de la referencia) y `DECISIONES-PRUEBA.md`.

### Del gemelo

- [x] **F-009** Sin madre, la verificadora llega en el 60–80 % de las semillas: es la **línea base**.
- [x] **F-010 / F-013** La madre (pista de baile, difusión) acelera la convergencia y, con 1 viaje, reduce la varianza del tiempo a menos de un tercio.
- [x] **F-011** La madre guardaba pedidos de ruta sin límite → corregido.
- [x] **F-014** Las agentes salían juntas y elegían una sola vez (no había retroalimentación) → **opción c**: salidas escalonadas y viajes repetidos.
- [x] **F-015** Con la opción c, el gemelo reproduce la ruptura de simetría del notebook (C2) y los puntos fijos (C4).
- [x] **F-016** Atasco en callejones al repetir viajes → corregido al estilo S-ACO (celdas pisadas por viaje).
- [x] **F-017** C3: la causa principal son las pocas decisiones; la secundaria, la saturación de los 16 niveles → decisión J8: se documenta y se reconsidera en el hardware.
- [ ] **F-015 / F-017** Con ramas desiguales, el gemelo converge a la rama **larga** en ~1 de cada 3 ensayos (oráculo: 5 %). **Causa sin comprobar.**
- [ ] **F-018** Con 10 viajes, la madre **ya no** reduce la varianza del tiempo (sí lo hacía con 1 viaje).
- [ ] **F-019** La hipótesis de `resumen.pdf` no queda apoyada; la mejora del rescate en el mundo aleatorio (27/30 frente a 18/30) no resiste la corrección por comparaciones múltiples.
- [ ] **F-010 / F-018** La verificadora todavía falla en 3 a 12 de cada 30 ensayos, según el modo y el mundo (rastros cruzados y callejones).
- [ ] **F-016** Con viajes repetidos, las rutas verificadas del mundo L salen más largas (1,67 veces la óptima frente a 1,31).
- [ ] **F-015** Con 60 agentes la colonia no converge: la percepción de 16 niveles se satura. La escala depende del número de agentes.

### De la referencia (`referencia/`, solo lectura)

- [x] **I15** `p1` del notebook solo usa la *diferencia* de feromona: no es la fórmula 1.1 cuando hay feromona en las dos ramas. El oráculo la usa solo donde coinciden.
- [x] **I14 / F-007** `referencia/resumen.pdf` no viene del repositorio fuente (lo agregó el operador).
- [ ] **I9** El repositorio fuente no tiene licencia; este repositorio es GPL v3.
- [ ] **R1** El modelo Ants de NetLogo (Wilensky) es CC BY-NC-SA, incompatible con GPL: se usa solo como inspiración.

### Del método

- [x] **F-004, F-006, F-007** Fallas de proceso de Claude (apertura de sesión, horas estimadas, archivo no inventariado) → corregidas.
- [ ] Las decisiones de las rondas 1–3 (A–G, I1–I15, J1–J8) se aprobaron "con bendición", con carga cognitiva alta (`ASSUMPTIONS.md`): **están pendientes de revisión**.

## 4. Aspectos que bloquean el paso al hardware

| # | Bloqueante | Por qué bloquea | Quién lo resuelve |
|---|---|---|---|
| B1 | **Protocolo v0.2 sin aprobar** | El firmware de ESP32 y la madre en la RPi se escriben a partir de los mensajes; cambiarlos después obliga a rehacer ambos lados | Operador |
| B2 | **Transporte sin decidir: MQTT o ESP-NOW** | Las ideas del operador dicen MQTT (fase 2); `resumen.pdf` dice ESP-NOW. **La RPi no habla ESP-NOW**: haría falta un ESP32 como pasarela por serial. Con MQTT, el "radio" entre vecinos es simulado por el broker | Operador |
| B3 | **Lenguaje del agente sin decidir: MicroPython o C++** | El prompt del simulador dice MicroPython; la referencia (ejemplos 3–6) usa C++ con PlatformIO, ya probado. Faltan `esptool` y `mpremote` si es MicroPython | Operador |
| B4 | **Inventario de hardware sin verificar** | La RPi no está en `CHECKLIST-ENTORNO.md`; la cantidad de ESP32 (4–6 según `resumen.pdf`) no se ha confirmado | Operador |
| B5 | **Percepción de 4 bits** | Con muchas decisiones se satura (F-015, F-017). La decisión J8 la dejó para el hardware: 4 bits lineales, 4 bits logarítmicos u 8 bits cambian el tamaño de PERCEPCION (18 → 23 B) | Operador, con datos de F-017 |
| B6 | **Paso intermedio sin hacer (artefacto 16)** | La demostración con el mundo en NetLogo y los agentes en Python por mensajes es donde se prueba el protocolo **fuera de la memoria**, antes de los micros | Próxima sesión |

**No bloquean, pero conviene cerrarlos antes:** `paho-mqtt` no está instalado (fase 2); los mensajes entre agentes
(`BALIZA`, `ALERTA`, `SIGUEME`) y `STOP` no están implementados (decisión E1: "mundo + balizas"); el tráfico de las
confirmaciones (ACK) no se cuenta; la guía de reproducción (artefacto 17) no existe.

## 5. Cosas por explorar

| # | Pregunta | Cómo | Por qué importa para el hardware |
|---|---|---|---|
| X1 | ¿El rescate mejora de verdad la convergencia en mundos aleatorios? | Experimento **confirmatorio**: ~100 semillas por condición, pruebas declaradas antes | Decide si vale la pena el mecanismo de rescate (y su costo de red) en la RPi |
| X2 | ¿Aguanta la colonia la pérdida y el retardo de mensajes? | Barrer `canal.p_perdida` (0–30 %) y `canal.retardo` | ESP-NOW y WiFi pierden paquetes; **todavía no se ha medido** |
| X3 | ¿Cuántos viajes y qué evaporación convienen en la cuadrícula? | Barrer `viajes` (J7 = 10 es una suposición) y `rho` | Fijan la duración de un ensayo y el tráfico, es decir, la batería |
| X4 | ¿Por qué el gemelo converge a la rama larga en 1/3 de los ensayos? | Variar el número de agentes y el escalonamiento en el puente doble | Puede ser un efecto de tener pocos agentes, como en el hardware real (4–6) |
| X5 | ¿Qué Δt y qué memoria necesita la madre? | Barrer `madre.delta_t` y `madre.memoria` (con 32 B no le caben rutas, F-011) | Dimensiona la RPi y la frecuencia de mensajes |
| X6 | ¿Qué percepción adoptar (B5)? | Repetir la investigación de C3 con la configuración final | Cambia el mensaje PERCEPCION y el firmware |
| X7 | ¿Cuánto tráfico genera cada ESP32? | Usar los bytes por familia ya medidos, por agente y por segundo | Energía, canal de radio y elección de transporte (B2) |
| X8 | ¿Funciona el motor de hilos con madre igual de bien? | Repetir los experimentos con el motor de hilos (los tiempos varían entre corridas) | Es lo más parecido a micros asíncronos |

## 6. Siguiente sesión

1. **Artefacto 16:** demostración con el mundo en NetLogo y los agentes en Python, comunicados por el protocolo.
2. Revisar con el operador los bloqueantes B1–B4.
3. Artefacto 17: guía de reproducción autocontenida.
