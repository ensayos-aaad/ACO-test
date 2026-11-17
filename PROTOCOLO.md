# PROTOCOLO — mensajes del gemelo ACO (borrador v0.2)

**Estado:** propuesta de Claude, **sin aprobar** por el operador · v0.2 del 2026-11-16 20:58 -0500
**Implementación:** `gemelo/aco_gemelo/protocolo/codec.py` (la tabla `MENSAJES` es la fuente de verdad; las pruebas comprueban los tamaños de este documento).

**Cambios de la v0.2** (por las decisiones de DECISIONES-PRUEBA.md):
- Vecindad de 8 por defecto (C2): `mov` de 3 bits, `PERCEPCION` con 9 celdas.
- Verificadora (D3, H4): bit `verificadora` en `INICIO`, flag `verificacion` en la cabecera y motivos de `FIN`.
- `SIGUEME` lleva el campo `n` y hasta 4 movimientos del tamaño de `mov`.
- Orden de bits: un solo flujo, del más significativo al menos significativo (antes decía *little-endian*).
**Alcance:** las 3 fases del gemelo (Python → Python + NetLogo + MQTT → ESP32 + RPi), ver CONTEXT §8.

## 0. Principios

1. **Un solo protocolo para las 3 fases.** Entre fases cambia el transporte (memoria → MQTT →
   WiFi/ESP-NOW), no los mensajes.
2. **JSON y binario llevan exactamente la misma información.** El JSON es la versión legible del
   binario, con los mismos campos y los **mismos valores ya cuantizados**. Así, lo que se mide en la
   fase 1 vale en la fase 3.
3. **Los mensajes entre agentes son cortos ("feromónicos"):** cabecera corta, carga de 2 a 3 bytes,
   alcance local (radio r) y sin garantía de entrega.
4. **Los agentes no conocen la meta** hasta percibirla (η = 1 por defecto). La meta no viaja en
   ningún mensaje de configuración.
5. **Todo cabe en un paquete ESP-NOW** (≤ 250 bytes) para mundos de hasta 16 × 16.

## 1. Tipos de dato comunes

| Tipo | Bits | Codificación | Nota |
|---|---|---|---|
| `celda` | 8 | `y << 4 \| x`, con x, y ∈ 0..15 | Mundos de hasta 16 × 16. El plano es de 8 × 8. |
| `id` | 8 | 0x00 = madre · 0x01–0xFD = agentes · 0xFE = mundo · 0xFF = difusión | Hasta 253 agentes |
| `dir` | 3 | 0 = N, 1 = E, 2 = S, 3 = O (4-vecindad) · 4–7 = NE, SE, SO, NO (8-vecindad) | |
| `mov` | 2 o 3 | Igual que `dir`. Usa 2 bits si la vecindad es 4 y 3 bits si es 8 | Se usa en las rutas |
| `q4` / `q8` | 4 / 8 | Valor cuantizado: v ≈ q · v_max / (2ⁿ − 1) | Feromona, pesos |
| `sat8` | 8 | Contador que se satura en 255 | Experiencia, llegadas |

Orden de bits: el mensaje es un solo flujo de bits, del más significativo al menos significativo. Un campo
de 16 bits va con el byte alto primero. Las listas de tamaño variable se rellenan con ceros hasta el byte.

## 2. Cabeceras

**Byte 0 (común a todos los mensajes):**

| Campo | Bits | Significado |
|---|---|---|
| `ver` | 2 | Versión del protocolo (0 = v0.x) |
| `fam` | 2 | 0 = Mundo ↔ Agente · 1 = Agente ↔ Agente · 2 = Agente → Madre · 3 = Madre → Agente |
| `tipo` | 3 | Tipo dentro de la familia (el 7 se reserva para `ACK`) |
| `corta` | 1 | 1 = cabecera corta (solo en la familia 1) |

**Cabecera corta (3 bytes = 24 bits), para mensajes feromónicos:**
`byte0` (8) · `src` id (8) · `seq` (8). Sin destino: va a todos los vecinos dentro del radio r.

**Cabecera larga (7 bytes = 56 bits):**
`byte0` (8) · `src` (8) · `dst` (8) · `seq` (8) · `tick` (16, módulo 65536) · `flags` (8)

| Flag (bit) | Significado |
|---|---|
| 0 `ack` | Se pide confirmación (`ACK` con el mismo `seq`) |
| 1 `rescate` | El contenido es la **condición inicial** de un rescate |
| 2 `ultimo` | Último fragmento de una serie |
| 3 `verificacion` | Lo envía la agente verificadora (en `DANZA`: "llegué siguiendo solo el rastro") |
| 4–7 | Reservados |

`seq`: contador de 8 bits por emisor, que vuelve a 0. Sirve para detectar pérdidas y duplicados.

## 3. Catálogo de mensajes

### Familia 0 — Mundo ↔ Agente (sensores y actuadores simulados)

En las fases 2 y 3 el mundo (NetLogo) es la **autoridad**: el agente pide una acción, el mundo la valida
y le responde con lo que percibe.

**0.0 `PERCEPCION`** (mundo → agente, cada tick)

| Campo | Bits | Significado |
|---|---|---|
| `pos` | 8 | Celda actual del agente |
| `ok` | 1 | 1 = la última acción se ejecutó · 0 = fue bloqueada |
| reservado | 7 | |
| `vecinas[k]` | 8 × k | k = 5 (la propia + N, E, S, O) o 9 (8-vecindad), en orden fijo |
| ↳ `clase` | 2 | 00 = libre · 01 = obstáculo · 10 = meta · 11 = fuera de la grilla |
| ↳ `ocupada` | 1 | Hay otro agente en la celda |
| ↳ `nido` | 1 | Es la celda de inicio |
| ↳ `fero` | 4 | Feromona de la celda (q4) |

Carga: 16 + 40 = **56 bits (7 B)** con 4-vecindad · 16 + 72 = 88 bits (11 B) con 8-vecindad.
Total con cabecera larga: **14 B** / 18 B.

**0.1 `ACCION`** (agente → mundo, cada tick)

| Campo | Bits | Significado |
|---|---|---|
| `accion` | 2 | 00 = quieto · 01 = mover · 10 = mover y depositar · 11 = depositar sin mover |
| `dir` | 3 | Dirección del movimiento |
| reservado | 3 | |
| `deposito` | 8 | Cantidad de feromona (q8) |

Carga: **16 bits (2 B)** · total 9 B.

### Familia 1 — Agente ↔ Agente (cortos, feromónicos, cabecera corta)

Alcance: radio r. Sin `ACK`: si se pierden, no pasa nada.

**1.0 `BALIZA`** ("feromona virtual" con gradiente de saltos)

| Campo | Bits | Significado |
|---|---|---|
| `pos` | 8 | Celda del emisor |
| `estado` | 2 | 00 = explorando · 01 = volviendo con ruta · 10 = siguiendo ruta · 11 = rescatado |
| `rol` | 1 | 0 = exploradora · 1 = explotadora |
| reservado | 1 | |
| `saltos_meta` | 4 | Saltos estimados hasta la meta (q4; 15 = desconocido) |
| `fuerza` | 8 | Intensidad de la señal (q8); cae con la distancia y el tiempo |

Carga: **24 bits (3 B)** · total **6 B**.

**1.1 `ALERTA`** (obstáculo, congestión o callejón sin salida)

| Campo | Bits | Significado |
|---|---|---|
| `celda` | 8 | Celda afectada |
| `motivo` | 2 | 00 = obstáculo · 01 = congestión · 10 = callejón · 11 = reservado |
| `ttl` | 3 | Cuántas veces más se puede reenviar |
| reservado | 3 | |

Carga: **16 bits (2 B)** · total **5 B**.

**1.2 `SIGUEME`** (*tandem running*: guiar a un compañero)

| Campo | Bits | Significado |
|---|---|---|
| `ruta_id` | 8 | Ruta que conoce el líder |
| `n` | 3 | Cuántos movimientos siguen (0–4) |
| `movs` | n × `mov` | Los próximos movimientos, completados a byte |

Carga: hasta **24 bits (3 B)** · total **6 B**.

### Familia 2 — Agente → Madre

**2.0 `ESTADO`** (latido, cada Δt)

| Campo | Bits | Significado |
|---|---|---|
| `pos` | 8 | Celda actual |
| `estado` | 2 | Igual que en `BALIZA` |
| `rol` | 1 | |
| reservado | 5 | |
| `experiencia` | 8 | Celdas distintas visitadas (sat8): la "métrica de experiencia" |
| `llegadas` | 8 | Veces que llegó a la meta (sat8) |

Carga: **32 bits (4 B)** · total **11 B**.

**2.1 `FRAGMENTO`** (lo que el agente descubrió del mapa, en bloques de 4 × 4)

| Campo | Bits | Significado |
|---|---|---|
| `origen` | 8 | Celda de la esquina superior izquierda del bloque |
| `conocidas` | 16 | Mapa de bits: qué celdas del bloque se han observado |
| `obstaculos` | 16 | Mapa de bits: cuáles de ellas son obstáculo |

Carga: **40 bits (5 B)** · total **12 B**. Un mundo de 8 × 8 son 4 bloques.
En cada mapa de 16 bits, la celda (origen.x + dx, origen.y + dy) ocupa el bit 15 − (4·dy + dx): por filas, con el bit más significativo primero.

**2.2 `DANZA`** (el agente encontró la meta y anuncia la ruta, como la danza del meneo)

| Campo | Bits | Significado |
|---|---|---|
| `ruta_id` | 8 | Identificador local de la ruta |
| `inicio` | 8 | Celda de partida |
| `largo` | 8 | Número de movimientos L, que también mide la calidad (más corta = mejor) |
| `movs` | 2·L | La ruta (3·L con 8-vecindad), completada a byte |

Carga: 24 + 3L bits con 8 vecinos (24 + 2L con 4). Con la ruta del plano (L ≈ 14) y 8 vecinos: **9 B** · total **16 B**. Con L = 60: 26 B · total 33 B.

**2.3 `PIDE_RESCATE`** (el agente decide por sí mismo que está rezagado)

| Campo | Bits | Significado |
|---|---|---|
| `experiencia` | 8 | Su métrica actual |
| `motivo` | 2 | 00 = sin progreso · 01 = atrapado · 10 = memoria llena · 11 = reservado |
| reservado | 6 | |

Carga: **16 bits (2 B)** · total **9 B**.

**2.4 `PIDE_RUTA`**: `ruta_id` (8). Carga **1 B** · total **8 B**.

### Familia 3 — Madre → Agente(s)

**3.0 `INICIO`** (configuración del ensayo; difusión)

| Campo | Bits | Significado |
|---|---|---|
| `ancho` − 1, `alto` − 1 | 4 + 4 | Dimensiones (1–16) |
| `nido` | 8 | Celda de inicio |
| `vecindad` | 1 | 0 = 4 · 1 = 8 |
| `modo_com` | 1 | 0 = solo estigmergia · 1 = también mensajes entre agentes |
| `modo_madre` | 2 | 00 = ausente · 01 = pista de baile · 10 = rescate · 11 = difusión cada Δt |
| `verificadora` | 1 | 1 = este agente es la verificadora: solo explota el rastro |
| reservado | 3 | |
| `semilla` | 16 | Semilla del generador aleatorio del agente (en el hardware real puede sustituirse por `esp_random()`) |
| `delta_t` | 8 | Ticks entre sincronizaciones |
| `K` | 8 | Memoria del agente (pasos recordados) |

Carga: **56 bits (7 B)** · total **14 B**. La meta **no** se envía.

**3.1 `RECLUTA`** (pista de baile: anuncia las mejores rutas)

| Campo | Bits | Significado |
|---|---|---|
| `n` | 2 | Rutas anunciadas (0–3) |
| reservado | 6 | |
| por ruta: `ruta_id`, `largo`, `peso` | 8 + 8 + 8 | `peso` (q8) = probabilidad de reclutamiento |

Carga: 8 + 24n bits. Con n = 3: **10 B** · total **17 B**.

**3.2 `RUTA`** (respuesta a `PIDE_RUTA`): mismos campos que `DANZA`.

**3.3 `MAPA`** (conocimiento global de la madre; se difunde cada Δt, o va a un solo agente como rescate con `flags.rescate`)

| Campo | Bits | Significado |
|---|---|---|
| `incluye_fero` | 1 | Si va la capa de feromona |
| reservado | 7 | |
| `conocidas` | N·M | Mapa de bits |
| `obstaculos` | N·M | Mapa de bits |
| `fero` | 4·N·M | Feromona agregada (q4), solo si `incluye_fero` = 1 |

Con 8 × 8: 8 + 128 = **17 B** sin feromona · 8 + 384 = **49 B** con ella · total 24 B / 56 B.

**3.4 `STOP`** (retroalimentación negativa, como la señal de stop de las abejas)

| Campo | Bits | Significado |
|---|---|---|
| `objetivo` | 1 | 0 = ruta · 1 = celda |
| `motivo` | 2 | 00 = obstáculo nuevo · 01 = congestión · 10 = ruta dominada · 11 = reservado |
| reservado | 5 | |
| `id` | 8 | `ruta_id` o `celda` |

Carga: **16 bits (2 B)** · total **9 B**.

**3.5 `FIN`**: `motivo` (2) + reservado (6) = 1 B · total 8 B.
Motivos: 00 = camino verificado · 01 = se agotó el límite de pasos · 10 = la verificadora falló (ciclo o sin rastro) · 11 = abortado.

**x.7 `ACK`** (cualquier familia salvo la 1): solo la cabecera larga; `seq` es el que se confirma.

## 4. Resumen de tamaños y frecuencias (mundo de 8 × 8, 8-vecindad)

| Mensaje | Sentido | Total (B) | Cuándo | Entrega |
|---|---|---|---|---|
| PERCEPCION | Mundo → Ag | 18 | Cada tick | Garantizada |
| ACCION | Ag → Mundo | 9 | Cada tick | Garantizada |
| BALIZA | Ag → vecinos | **6** | Cada tick o cada n ticks | Sin garantía |
| ALERTA | Ag → vecinos | **5** | Por evento | Sin garantía |
| SIGUEME | Ag → vecino | **6** | Por evento | Sin garantía |
| ESTADO | Ag → Madre | 11 | Cada Δt | Sin garantía |
| FRAGMENTO | Ag → Madre | 12 | Si hay novedades, ≤ 1 por Δt | Sin garantía |
| DANZA | Ag → Madre | 16 (L = 14) | Al llegar a la meta | Con ACK |
| PIDE_RESCATE | Ag → Madre | 9 | Por evento | Con ACK |
| INICIO | Madre → todos | 14 | Al empezar el ensayo | Con ACK |
| RECLUTA | Madre → todos | ≤ 17 | Cada Δt (modo pista de baile) | Sin garantía |
| MAPA | Madre → todos o uno | 24 / 56 | Cada Δt (modo difusión) o en un rescate | Rescate con ACK |
| STOP | Madre → todos | 9 | Por evento | Sin garantía |

En MQTT, "garantizada" sería QoS 1 y "sin garantía" QoS 0.

## 5. Ejemplo de equivalencia JSON ↔ binario

`BALIZA` del agente 3 en la celda (2,5), siguiendo una ruta, explotadora, a 6 saltos de la meta,
fuerza 200:

```json
{"ver":0,"fam":1,"tipo":0,"corta":1,"src":3,"seq":41,
 "pos":82,"estado":2,"rol":1,"saltos_meta":6,"fuerza":200}
```
Binario (6 B): `0x11 0x03 0x29 0x52 0xA6 0xC8`
(`0x11` = ver 00 · fam 01 · tipo 000 · corta 1; `0x03` = src; `0x29` = seq 41; `0x52` = celda y = 5, x = 2; `0xA6` = estado 10 · rol 1 ·
res 0 · saltos 0110; `0xC8` = 200).

## 6. Correspondencia propuesta con temas MQTT (fase 2)

| Familia | Tema |
|---|---|
| 0 | `aco/<ensayo>/mundo/<id>/percepcion` · `aco/<ensayo>/agente/<id>/accion` |
| 1 | `aco/<ensayo>/vecinos/<celda>`: el mundo o un puente reenvía solo a los agentes dentro del radio r |
| 2 | `aco/<ensayo>/madre/entrada` |
| 3 | `aco/<ensayo>/madre/difusion` · `aco/<ensayo>/agente/<id>/madre` |

Con MQTT, el "radio r" de la familia 1 **lo simula** quien reenvía, porque el broker no sabe de
distancias. En hardware real (ESP-NOW) el alcance de radio sería físico, pero no equivale a r celdas
del mundo virtual.

## 7. Puntos abiertos (para decidir de a uno)

- La resolución de la feromona: q4 en `PERCEPCION` y `MAPA` frente a q8. Afecta la regla τ^α.
- ¿Se mantiene `BALIZA` cada tick o cada n ticks? Es el costo de red principal entre agentes.
- ¿Quién detecta el rezago: el agente (`PIDE_RESCATE`), la madre (por `ESTADO`) o los dos? (Es la contradicción de `resumen.pdf`.)
- El tamaño de bloque de `FRAGMENTO` (4 × 4) y si la madre acepta un límite de memoria en bytes.
- ¿Basta con mundos de hasta 16 × 16? Una `celda` de 16 bits permitiría hasta 256 × 256.
