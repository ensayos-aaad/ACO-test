# Costo de comunicación y presupuesto de memoria del protocolo v0.2

**Especificación de referencia:** `PROTOCOLO.md` v0.2 (`gemelo/aco_gemelo/protocolo/codec.py`)  
**Archivo de datos:** `resultados/experimento_30_semillas.csv`  
**Gráfica asociada:** `docs/img/fig2_costo_comunicacion_protocolo.png`

## 1. Arquitectura de mensajería y restricciones de hardware

El protocolo unificado opera con 16 tipos de mensaje agrupados en 4 familias y garantiza equivalencia exacta de información cuantizada entre JSON y binario, manteniendo cada trama muy por debajo del límite de 250 bytes de ESP-NOW.

| Familia | Mensajes activos en fase 1 | Tamaño trama binaria | Frecuencia de envío | Impacto en tráfico |
|---|---|---|---|---|
| 0 — Mundo ↔ Agente | `PERCEPCION` (18 B), `ACCION` (9 B) | 9–18 B | Cada tick por agente activo | Domina `bytes_totales` (>89 % del volumen en simulación) |
| 1 — Agente ↔ Agente | `BALIZA` (6 B), `ALERTA` (5 B), `SIGUEME` (6 B) | 5–6 B (cabecera corta 3 B) | Local (radio $r$), reservado para `modo_com=1` | 0 B en fase 1 estigmérgica (`modo_com=0`) |
| 2 — Agente → Madre | `ESTADO` (11 B), `FRAGMENTO` (12 B), `DANZA` (16 B para $L=14$), `PIDE_RUTA` (8 B) | 8–33 B | Cada $\Delta t$ o por evento de llegada | Bajo; escala linealmente con $\Delta t^{-1}$ |
| 3 — Madre → Agente | `INICIO` (14 B), `RECLUTA` ($\le 17$ B), `RUTA` (16 B), `MAPA` (24/56 B), `FIN` (8 B) | 8–56 B | Inicio, cada $\Delta t$ y cierre | Diferencia el costo `bytes_madre_agentes` entre modos |

## 2. Balance de tráfico y memoria por modo (media en 30 semillas)

| Modo de madre | `bytes_madre_agentes` (media) | `bytes_totales` (media) | Memoria máxima usada en madre (tope 64 B) |
|---|---|---|---|
| `AUSENTE` | 8.0 B (solo `FIN`) | 16 873.1 B | 0 B |
| `PISTA_DE_BAILE` | 792.7 B | 13 122.7 B | 59 B |
| `RESCATE` | 1 281.6 B | 18 146.7 B | 64 B |
| `DIFUSION` | 1 123.9 B | 10 865.5 B | 64 B |

## 3. Presupuesto de memoria en la madre (F3 / F-011)

- Con presupuesto por defecto de **64 B** (I15), la tabla de estado de 6 agentes ocupa 13 B y el mapa global de $8 \times 8$ ocupa 16 B (`conocidas` + `obstaculos`), dejando espacio para almacenar las rutas más cortas reportadas por `DANZA` y expulsando primero las de mayor longitud $L$.
- Aunque `PISTA_DE_BAILE` y `DIFUSION` añaden entre $793\text{ B}$ y $1124\text{ B}$ de coordinación madre ↔ agentes, reducen `bytes_totales` de red en un $22.2\%$ y un $35.6\%$ respectivamente frente a `AUSENTE` al acortar la duración de los ensayos.
