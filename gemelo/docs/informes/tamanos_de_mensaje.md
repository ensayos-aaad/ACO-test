# Tamaño de los mensajes: binario frente a JSON y el límite de ESP-NOW

Redactado 2026-11-20 03:31 -0500 (hora del archivo; la marca original, estimada, se corrigió tras la revisión del bloque D). Cifras calculadas con `aco_gemelo.protocolo.tamanos.tamanos()` (contexto por defecto: mundo 8x8, 8 vecinos, un mensaje típico de cada tipo, no el máximo). Protocolo v0.3, sin aprobar.

## Objetivo

Decidir con números si el protocolo cabe en un paquete ESP-NOW (máximo 250 B de carga) y qué formato conviene, para el bloqueante B2 de `ESTADO-PREHARDWARE.md` (MQTT o ESP-NOW).

## Configuración

Repetir, desde `gemelo/`: `C:/Users/Usuario/anaconda3/envs/aco-gemelo/python.exe -X utf8 -W ignore -c "from aco_gemelo.protocolo.tamanos import tamanos; [print(f) for f in tamanos()]"`. No es un experimento estadístico: el tamaño es determinista, sin semillas. El tráfico por ensayo viene de `experimentos/datos/modos/`.

## Resultados

| Familia | Mensaje | Binario (B) | JSON (B) | JSON / binario | JSON cabe en 250 B |
|---|---|---|---|---|---|
| 0 Mundo-Agente | PERCEPCION | 18 | 490 | 27,2 | **no** |
| 0 | ACCION | 9 | 117 | 13,0 | si |
| 1 Agente-Agente | BALIZA | 6 | 110 | 18,3 | si |
| 1 | ALERTA | 5 | 83 | 16,6 | si |
| 1 | SIGUEME | 6 | 88 | 14,7 | si |
| 2 Agente-Madre | ESTADO | 11 | 140 | 12,7 | si |
| 2 | FRAGMENTO | 12 | 129 | 10,8 | si |
| 2 | DANZA | 16 | 154 | 9,6 | si |
| 2 | PIDE_RESCATE | 9 | 109 | 12,1 | si |
| 2 | PIDE_RUTA | 8 | 94 | 11,8 | si |
| 3 Madre-Agente | INICIO | 14 | 209 | 14,9 | si |
| 3 | RECLUTA (3 rutas) | 17 | 205 | 12,1 | si |
| 3 | RUTA | 16 | 154 | 9,6 | si |
| 3 | MAPA (sin feromona) | 24 | 396 | 16,5 | **no** |
| 3 | STOP | 9 | 116 | 12,9 | si |
| 3 | FIN | 8 | 95 | 11,9 | si |

Calculado además, mismo código: `MAPA` con feromona incluida mide 56 B en binario y 523 B en JSON. En binario el mayor mensaje (56 B) usa el 22 % del límite; en JSON, 2 de 16 tipos no caben (`PERCEPCION` y `MAPA`) y los demás ocupan entre 33 % y 84 % del paquete. Los JSON son entre 9,6 y 27,2 veces más grandes; la mediana de las 16 razones es 12,8.

Tráfico medido por ensayo, en binario (`modos`, ~440 ticks, 7 nodos): mundo-agente 71 900 B (pista de baile en L; 5 300 mensajes, de 13,5 B de media = mitad `PERCEPCION`, mitad `ACCION`); agente-madre 3 900 B (330 mensajes, 11,8 B de media); madre-agente 795 B (49 mensajes). Es decir, el 94 % de los bytes es la conversación del mundo con cada agente. Estimación por escalado (no medida): con JSON, esos 5 300 mensajes ocuparían del orden de 1,6 MB por ensayo en vez de 72 KB.

## Diagnóstico para el ESP32

- La familia 0 es sensor y actuador: en el hardware real es lectura de pines dentro del mismo chip, no radio. Por eso `PERCEPCION` en JSON (490 B) no es un problema de ESP-NOW; sí lo es en la fase 2 (mundo en NetLogo, agentes por MQTT): ahí cada agente recibe y devuelve unos 600 B por tick en JSON (490 + 117).
- Lo que sí viaja por radio (familias 1 a 3) es, medido, unos 4 700 B por ensayo de ~440 ticks, algo más de 10 B por tick para 7 nodos en binario; cada agente manda un `ESTADO` de 11 B cada 10 ticks (1,1 B por tick). Para fijar bytes por segundo hay que decidir cuánto dura un tick (no está fijado); como ilustración, a un tick de 100 ms la colonia entera usaría ~100 B/s, muy por debajo de lo que sostiene ESP-NOW o MQTT sobre Wi-Fi.
- Conclusión para B2: **en binario, ESP-NOW cabe sobrado** (mayor mensaje 56 B). **En JSON, ESP-NOW no sirve para dos mensajes**, y los demás consumen buena parte del paquete; JSON solo es defendible sobre MQTT, que no tiene ese límite de 250 B. Pero la Raspberry Pi no habla ESP-NOW: con ESP-NOW hace falta un ESP32 pasarela por serial hacia la madre. Una arquitectura posible (no probada) es binario sobre ESP-NOW entre agentes y JSON/MQTT solo entre pasarela, madre y NetLogo; el gemelo ya genera las dos representaciones con la misma información cuantizada.
- Si B5 sube la percepción de 4 a 8 bits, `PERCEPCION` binario pasa de 18 a 23 B (cifra de `ESTADO-PREHARDWARE.md`, no recalculada aquí): irrelevante para el límite.
- No se cuentan cabeceras de ESP-NOW/MQTT/TCP ni confirmaciones; en MQTT se sumarían del orden de decenas de bytes por mensaje (no medido).

## Límites

- Un ejemplo por mensaje; los mensajes de longitud variable (`DANZA`, `RUTA`, `RECLUTA`, `MAPA`) crecen con la ruta, el número de rutas y el mundo; aquí se usan ruta de 14 pasos, 3 rutas en `RECLUTA` y mundo de 8x8. Un mundo mayor agranda `MAPA` y `PERCEPCION` solo por el número de vecinas.
- El protocolo está en borrador v0.3 sin aprobar (B1); cualquier cambio rehace estas cifras.
- La estimación del JSON por ensayo (~1,6 MB) usa el promedio de los tamaños JSON de `PERCEPCION` y `ACCION` (303,5 B) por el número de mensajes medido; no se corrió el experimento con `formato: json`.
