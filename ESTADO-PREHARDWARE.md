# Estado del gemelo de software antes de pasar al hardware

**Fecha:** 2026-11-25 (primera versión: 2026-11-17) · **Preparado por:** Claude Opus 5.5, a pedido del operador ·
**Repositorio:** `ensayos-aaad/ACO-test`

Este documento resume dónde está la implementación en software (fase 1 del gemelo), qué hallazgos dejó, qué
**bloquea** el paso al hardware (ESP32 como agentes, Raspberry Pi como madre) y qué conviene explorar antes.
El detalle de cada punto está en los archivos enlazados.

## 1. Resumen ejecutivo

- **El gemelo de software funciona de punta a punta y se reprodujo desde cero en la máquina de desarrollo** (en otra máquina u otro sistema operativo: NO PROBADO): mundo en cuadrícula, 6 agentes, madre con 4 modos, protocolo binario/JSON, tres motores, métricas, visualización, experimentos en lote y un notebook que explica un ensayo. La guía [`gemelo/REPRODUCIR.md`](gemelo/REPRODUCIR.md) la siguieron el revisor y el QA externo, este último desde un clon limpio y con un entorno conda nuevo (ronda 003).
- **Fidelidad con la referencia** (notebooks del puente doble, PROMPT-ZERO): **C1, C2, C4 y C5 pasan; C3 no pasa**,
  con la causa documentada (pocas decisiones y percepción de solo 16 niveles). C6 lo evalúa el operador.
- **Hipótesis de `resumen.pdf`** (el rescate reduce la varianza del tiempo de convergencia): **no queda apoyada** con la
  configuración actual. La madre tiende a mejorar la convergencia en mundos aleatorios, pero sin significancia estadística.
- **Reproducibilidad:** la misma semilla da el mismo ensayo también con pérdida y retardo en la red simulada, con el motor de hilos sincronizado (F-023 a F-026) y en procesos distintos (`gemelo/tests/test_reproducibilidad.py`, ronda 001 de QA).
- **El agente ya está escrito como en un micro** (un ciclo `paso()` no bloqueante que solo habla por mensajes), y **en
  binario** todos los mensajes caben en un paquete ESP-NOW (≤ 250 B; el mayor, 56 B). **En JSON, dos no caben**
  (`PERCEPCION`, 490 B, y `MAPA`, 396 B). Son tamaños de un mensaje típico de cada tipo en el mundo de 8 × 8, no el máximo.
- **Antes del hardware** hay que cerrar 6 decisiones bloqueantes (sección 4), sobre todo el protocolo y el transporte.

## 2. Avance de la implementación en software

Avance = criterios de aceptación en PASA ÷ total (definición de `ARTEFACTOS.md`; no es una estimación a ojo).

| # | Artefacto | Estado | Avance | Nota para el hardware |
|---|---|---|---|---|
| 1 | Entorno reproducible (`gemelo/environment.yml`) | Hecho | 100 % | Solo para la simulación en el PC; QA lo creó desde cero (ronda 003) |
| 2 | Especificación del protocolo (`PROTOCOLO.md` v0.3) | Borrador | 67 % | **Falta la aprobación del operador** (bloqueante B1) |
| 3 | Codificadores JSON ↔ binario | Hecho | 100 % | Tabla única de mensajes: base para los structs de C o MicroPython |
| 4 | Mundo + BFS + escenarios (L, aleatorio, puente doble, personalizado) | Hecho | 100 % | En hardware el mundo sigue siendo virtual (PC o RPi) |
| 5 | Canal en memoria (radio, retardo, pérdida) | Hecho | 100 % | Cada emisor con su propio azar (F-024, F-025). Falta la implementación MQTT o ESP-NOW con la misma interfaz |
| 6 | Agente (ciclo no bloqueante, roles, viajes, verificadora) | Hecho | 100 % | Es el programa que se porta al ESP32 |
| 7 | Madre (4 modos, memoria en bytes) | Hecho | 100 % | Es el programa que se porta a la RPi |
| 8 | Motores (determinista, de hilos y de hilos sincronizados) | Hecho | 100 % | El de hilos imita la asincronía de los micros; el sincronizado da lo mismo que el determinista |
| 9 | Configuración YAML + línea de comandos | Hecho | 100 % | Semillas validadas (F-029, F-030) |
| 10 | Métricas (convergencia, calidad, conocimiento, bytes) | Hecho | 100 % | El conteo de bytes estima el tráfico real |
| 11 | Visualización (PNG, GIF, MP4) | Hecho | 100 % | |
| 12 | Oráculo del puente doble + comparación C1–C5 | Hecho | 100 % | |
| 13 | Pruebas automáticas | Hecho | 100 % | 350 del gemelo + 7 del oráculo en PASA, más 98 del QA externo |
| 14 | Experimentos en lote | Hecho | 100 % | Planes `modos` y `rescate` (480 ensayos) |
| 15 | Notebook de análisis | Hecho | 100 % | Un ensayo explicado, el mapa de la madre, el tamaño de los mensajes y el tráfico |
| 16 | Demostración con NetLogo + puente Python | Por hacer | 0 % | **Es el paso intermedio hacia el hardware** (fase 2) |
| 17 | Guía de reproducción autocontenida | Hecho | 100 % | [`gemelo/REPRODUCIR.md`](gemelo/REPRODUCIR.md) |

**15 de 17 artefactos hechos y 45 de 49 criterios en PASA**; faltan el 16 (3 criterios) y la aprobación del protocolo (1).

### Criterios de PROMPT-ZERO frente al oráculo (`oraculo/RESULTADOS.md`)

| Criterio | Estado | Valor |
|---|---|---|
| C1 Regla de decisión | **PASA** | La frecuencia de elección coincide con `p1` del notebook (\|z\| máx. 0,94) |
| C2 Ruptura de simetría (r = 1) | **PASA** | 75 % de los ensayos acaba en una sola rama (umbral 70 %) |
| C3 Ramas desiguales (r = 2) | **NO PASA** | La rama corta gana en el 48 % (oráculo 75 %; tolerancia ±0,15, es decir, 15 puntos porcentuales). Causa en `oraculo/INVESTIGACION-C3.md` |
| C4 Puntos fijos | **PASA** | 6 % de ensayos en el reparto 40–60 % (umbral 20 %) |
| C5 Determinismo | **PASA** | Misma semilla, mismo resultado (y `RESULTADOS.md` se regenera idéntico, ronda 003) |
| C6 Pedagógico | NO PROBADO | Lo evalúa el operador |

## 3. Checklist de hallazgos

`[x]` = atendido (corregido o con decisión tomada) · `[ ]` = abierto. El detalle está en `FAILURES.md`, `CONTEXT.md`
(inconsistencias I1–I16 de la referencia) y `DECISIONES-PRUEBA.md`.

### Del gemelo

- [x] **F-009** Sin madre, la verificadora llega en el 60–80 % de las semillas: es la **línea base**.
- [x] **F-010 / F-013** Con 1 viaje, la madre (pista de baile, difusión) bajaba el tiempo hasta asentarse (110 → 73 y 59 ticks, F-010) y parecía reducir su varianza a menos de un tercio (F-013). **Con la configuración actual (10 viajes) la reducción de la varianza no se sostiene** (F-018, F-027), y la media apenas baja (465 → 433–441 ticks en L; 428 → 390–417 en el aleatorio; sin prueba sobre la media, `gemelo/docs/informes/experimento_modos.md`).
- [x] **F-011** La madre guardaba pedidos de ruta sin límite → corregido.
- [x] **F-014** Las agentes salían juntas y elegían una sola vez (no había retroalimentación) → **opción c**: salidas escalonadas y viajes repetidos.
- [x] **F-015** Con la opción c, el gemelo reproduce la ruptura de simetría del notebook (C2) y los puntos fijos (C4).
- [x] **F-016** Atasco en callejones al repetir viajes → corregido al estilo S-ACO (celdas pisadas por viaje).
- [x] **F-017** C3: la causa principal son las pocas decisiones; la secundaria, la saturación de los 16 niveles → decisión J8: se documenta y se reconsidera en el hardware.
- [x] **F-020 / F-022** La madre rescataba a la verificadora → corregido; desde entonces cada ensayo cuenta sus mecanismos (rescates, reclutamientos, rutas heredadas).
- [x] **F-023 a F-026** Con pérdida o retardo, el motor de hilos no repetía el resultado con la misma semilla, y una corrección hizo que el azar de la red repitiera el de las agentes → corregido: cada emisor con su propio azar y entrega en orden fijo.
- [x] **F-029** Una semilla inválida en el archivo rompía `run --semilla` y los planes (regresión, la atrapó el QA externo) → corregido.
- [x] **F-030** Una semilla negativa repetía en silencio el **mundo** de la positiva → se rechaza.
- [x] **F-031** El comparador de la guía no veía cambios de color en el PNG → corregido antes de entregarla a QA.
- [ ] **F-015 / F-017** Con ramas desiguales, el gemelo converge a la rama **larga** en ~1 de cada 3 ensayos (oráculo: 5 %). **Causa sin comprobar.**
- [ ] **F-019** La hipótesis de `resumen.pdf` no queda apoyada; la mejora del rescate en el mundo aleatorio (27/30 frente a 18/30, p corregido 0,092) no resiste la corrección por comparaciones múltiples.
- [ ] **F-010 / F-018** La verificadora todavía falla en 3 a 12 de cada 30 ensayos, según el modo y el mundo (rastros cruzados y callejones).
- [ ] **F-016** Con viajes repetidos, las rutas verificadas del mundo L salen más largas (1,67 veces la óptima frente a 1,31).
- [ ] **F-015** Con 60 agentes la colonia no converge: la percepción de 16 niveles se satura. La escala depende del número de agentes.
- [ ] Observaciones leves: construir un `Agente` a mano no valida la semilla; `tests/test_notebook.py` regenera figuras versionadas; la reproducción solo se probó en Windows con Python 3.12.7.

### De la referencia (`referencia/`, solo lectura)

- [x] **I15** `p1` del notebook solo usa la *diferencia* de feromona: no es la fórmula 1.1 cuando hay feromona en las dos ramas. El oráculo la usa solo donde coinciden.
- [x] **I14 / F-007** `referencia/resumen.pdf` no viene del repositorio fuente (lo agregó el operador).
- [ ] **I9** El repositorio fuente no tiene licencia; este repositorio es GPL v3.
- [ ] **R1** El modelo Ants de NetLogo (Wilensky) es CC BY-NC-SA, incompatible con GPL: se usa solo como inspiración.

### Del método

- [x] **F-004, F-006, F-007** Fallas de proceso de Claude (apertura de sesión, horas estimadas, archivo no inventariado) → corregidas.
- [x] **ADR-004** Desde el 2026-11-25, un segundo modelo (Gemini) hace de QA externo por rondas en `.handoff/`; en la ronda 001 atrapó una regresión que la revisión interna no vio (F-029).
- [ ] **F-028 / F-030** Los textos explicativos de Claude tienden a afirmar más de lo que el dato sostiene; hasta ahora lo ha atrapado el revisor (F-028, F-030, F-031), no las pruebas, y QA no objetó la frase de F-030. Es un patrón vigente.
- [ ] Las decisiones de las rondas 1–3 (A–G, I1–I15, J1–J8) se aprobaron "con bendición", con carga cognitiva alta (`ASSUMPTIONS.md`): **están pendientes de revisión**.

## 4. Aspectos que bloquean el paso al hardware

| # | Bloqueante | Por qué bloquea | Quién lo resuelve |
|---|---|---|---|
| B1 | **Protocolo v0.3 sin aprobar** | El firmware de ESP32 y la madre en la RPi se escriben a partir de los mensajes; cambiarlos después obliga a rehacer ambos lados | Operador |
| B2 | **Transporte sin decidir: MQTT o ESP-NOW** | Las ideas del operador dicen MQTT (fase 2); `resumen.pdf` dice ESP-NOW. **La RPi no habla ESP-NOW**: haría falta un ESP32 como pasarela por serial. Con MQTT, el "radio" entre vecinos es simulado por el broker. **Dato calculado** ([`gemelo/docs/informes/tamanos_de_mensaje.md`](gemelo/docs/informes/tamanos_de_mensaje.md); un mensaje típico de cada tipo en el mundo de 8 × 8, no el máximo): en binario todos los mensajes caben en ESP-NOW (el mayor, `MAPA` con feromona, 56 B); en JSON son entre 9,6 y 27,2 veces más grandes y `PERCEPCION` (490 B) y `MAPA` (396 B) no caben. Con ESP-NOW, el formato tiene que ser binario; JSON solo es defendible sobre MQTT. El tráfico por radio con la madre fue de 4,2 a 6,3 KB por ensayo, unos 10 a 14 B por tick para toda la colonia ([`experimento_modos.md`](gemelo/docs/informes/experimento_modos.md)) | Operador |
| B3 | **Lenguaje del agente sin decidir: MicroPython o C++** | El prompt del simulador dice MicroPython; la referencia (ejemplos 3–6) usa C++ con PlatformIO, ya probado. Faltan `esptool` y `mpremote` si es MicroPython. Ligado a B2: si el formato es binario, el agente debe codificar y decodificar los mensajes con los mismos bits que la tabla única del gemelo (artefacto 3), que hoy solo existe en Python | Operador |
| B4 | **Inventario de hardware sin verificar** | La RPi no está en `CHECKLIST-ENTORNO.md`; la cantidad de ESP32 (4–6 según `resumen.pdf`) no se ha confirmado | Operador |
| B5 | **Percepción de 4 bits** | Con muchas decisiones se satura (F-015, F-017). La decisión J8 la dejó para el hardware: 4 bits lineales, 4 bits logarítmicos u 8 bits cambian el tamaño de PERCEPCION (18 → 23 B) | Operador, con datos de F-017 |
| B6 | **Paso intermedio sin hacer (artefacto 16)** | La demostración con el mundo en NetLogo y los agentes en Python por mensajes es donde se prueba el protocolo **fuera de la memoria**, antes de los micros | Siguiente en el plan, después del bloque E |

**No bloquean, pero conviene cerrarlos antes:** `paho-mqtt` no está instalado (fase 2); los mensajes entre agentes
(`BALIZA`, `ALERTA`, `SIGUEME`) y `STOP` no están implementados (decisión E1: "mundo + balizas"); el tráfico de las
confirmaciones (ACK) no se cuenta; de los prerrequisitos de las fases 2 y 3 quedan sin probar la cadena `py:setup` →
Anaconda → `import serial` y el par de puertos COM1 ↔ COM2, y faltan Wokwi y la elección de la toolchain
(`CHECKLIST-ENTORNO.md`, `gemelo/REPRODUCIR.md` §1).

## 5. Cosas por explorar

| # | Pregunta | Cómo | Por qué importa para el hardware |
|---|---|---|---|
| X1 | ¿El rescate mejora de verdad la convergencia en mundos aleatorios? | Experimento **confirmatorio**: ~100 semillas por condición, pruebas declaradas antes. Tras corregir F-020 se repitió el experimento con 30 semillas ([`rescate_tras_F020.md`](gemelo/docs/informes/rescate_tras_F020.md), [`experimento_rescate.md`](gemelo/docs/informes/experimento_rescate.md)): el rescate se dispara con umbral ≥ 0,8, el 71–83 % de los envíos se usa, y hay una tendencia de 27/30 frente a 18/30 en el mundo aleatorio que no es significativa tras corregir (p 0,092) y sin reducción de varianza | Decide si vale la pena el mecanismo de rescate (y su costo de red) en la RPi |
| X2 | ¿Aguanta la colonia la pérdida y el retardo de mensajes? | Barrer `canal.p_perdida` (0–30 %) y `canal.retardo` | ESP-NOW y WiFi pierden paquetes. Hay datos con un solo valor de pérdida (0,2) y de retardo (1–3 ticks) en [`gemelo/experimentos/linea_base_f023/`](gemelo/experimentos/linea_base_f023/), hechos para comprobar la reproducibilidad, no para medir este efecto: **el barrido sigue sin hacerse** |
| X3 | ¿Cuántos viajes y qué evaporación convienen en la cuadrícula? | Barrer `viajes` (J7 = 10 es una suposición) y `rho` | Fijan la duración de un ensayo y el tráfico, es decir, la batería |
| X4 | ¿Por qué el gemelo converge a la rama larga en 1/3 de los ensayos? | Variar el número de agentes y el escalonamiento en el puente doble | Puede ser un efecto de tener pocos agentes, como en el hardware real (4–6) |
| X5 | ¿Qué Δt y qué memoria necesita la madre? | Barrer `madre.delta_t` y `madre.memoria` (con 32 B, en los modos con mapa no le cabe ninguna ruta, F-011) | Dimensiona la RPi y la frecuencia de mensajes |
| X6 | ¿Qué percepción adoptar (B5)? | Repetir la investigación de C3 con la configuración final | Cambia el mensaje PERCEPCION y el firmware |
| X7 | ¿Cuánto tráfico genera cada ESP32? | Por agente y por segundo, a partir de los bytes por familia | Energía, canal de radio y transporte (B2). **En parte respondido:** 10–14 B por tick para toda la colonia hacia y desde la madre (B2); falta pasarlo a bytes por segundo con un tick real |
| X8 | ¿Funciona el motor de hilos con madre igual de bien? | Repetir los experimentos con el motor de hilos | Es lo más parecido a micros asíncronos. El motor de hilos **sincronizado** ya da exactamente lo mismo que el determinista (F-024); el de hilos libre no tiene esa garantía con madre, porque el momento en que actúa la madre depende del sistema operativo (`gemelo/aco_gemelo/motor/simulacion.py`, artefacto 8), y su variación entre corridas no se ha vuelto a medir |

## 6. Siguiente

1. **Bloque E** de `PLAN-MEJORAS.md`: registros (E1, qué se tomó de Gemini; E2, este documento; E3 y E4).
2. **Artefacto 16:** demostración con el mundo en NetLogo y los agentes en Python, comunicados por el protocolo (posible ronda de QA).
3. Revisar con el operador los bloqueantes B1–B4 y lo aprobado "con bendición".
4. Idea del operador en `IDEAS.md` (2026-11-25): organizar el proceso experimental y de replicación con MLflow o una herramienta similar.
