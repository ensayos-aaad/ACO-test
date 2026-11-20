# Experimento "modos": cuatro modos de la madre en dos mundos

Redactado 2026-11-20 03:31 -0500 (hora del archivo; la marca original, estimada, se corrigió tras la revisión del bloque D). Cifras leídas de `experimentos/datos/modos/` (480 ensayos del plan; los CSV son idénticos byte a byte antes y después de F-024).

## Objetivo

Ver si la madre (el nodo central, futura Raspberry Pi) mejora que la colonia de 6 agentes (futuros ESP32) encuentre y confirme la ruta corta, y cuánto tráfico cuesta. Los 4 modos son: `ausente` (sin madre, línea base), `pista_de_baile` (la madre guarda las rutas que le cuentan las agentes y recluta con ellas), `rescate` (ayuda a agentes rezagadas, umbral 0,5) y `difusion` (reenvía rutas y mapas a todas). "Converge" = `verificada`: una agente extra (verificadora) sale al final y llega al destino sin ayuda por la ruta que dejó la colonia.

## Configuración

- Plan `experimentos/modos.yaml`: base `configs/default.yaml` (6 agentes + verificadora, salida cada tick, 10 viajes, Δt = 10 ticks, canal ideal, mensajes binarios), mundos `L` y `aleatorio` (8x8), 4 modos, semillas 0 a 29 (30 ensayos por condición, 8 condiciones). Motor determinista.
- Repetir, desde `gemelo/`: `C:/Users/Usuario/anaconda3/envs/aco-gemelo/python.exe -X utf8 -W ignore -m aco_gemelo experimentos --plan experimentos/modos.yaml` (unos 2,5 min con 8 procesos).

## Qué es confirmatorio y qué no

Nada de este informe es confirmatorio. Los datos se vieron en F-013 y F-018 antes de fijar pruebas. Las pruebas de abajo se fijaron al redactar este informe (2026-11-20, antes de las 03:31 -0500) **con los datos ya conocidos**, así que son **exploratorias**: (1) Fisher exacta bilateral de `verificada` de cada modo contra `ausente`, por mundo; (2) Brown-Forsythe (Levene centrada en la mediana) de `ticks_asentadas` contra `ausente`; 6 comparaciones cada una, Bonferroni x6 (alfa corregido 0,0083). IC 95 % de Wilson.

## Resultados (30 ensayos por fila)

| Mundo | Modo | Verificadora llega | IC 95 % | p Fisher (x6) | Ticks hasta asentarse, media (desv.) | p BF (x6) | Bytes a Madre / de Madre por ensayo | Msgs madre->agente |
|---|---|---|---|---|---|---|---|---|
| L | ausente | 21/30 | 0,52-0,83 | - | 465 (145) | - | 0 / 0 | 0 |
| L | pista_de_baile | 24/30 | 0,63-0,90 | 0,55 (1,00) | 433 (120) | 0,69 (1,00) | 3 884 / 795 | 49 |
| L | rescate | 21/30 | 0,52-0,83 | 1,00 (1,00) | 465 (145) | 1,00 (1,00) | 4 861 / 22 | 2 |
| L | difusion | 25/30 | 0,66-0,93 | 0,36 (1,00) | 441 (169) | 0,90 (1,00) | 4 630 / 1 709 | 92 |
| aleatorio | ausente | 18/30 | 0,42-0,75 | - | 428 (140) | - | 0 / 0 | 0 |
| aleatorio | pista_de_baile | 25/30 | 0,66-0,93 | 0,084 (0,50) | 390 (112) | 0,26 (1,00) | 3 514 / 725 | 45 |
| aleatorio | rescate | 18/30 | 0,42-0,75 | 1,00 (1,00) | 428 (140) | 1,00 (1,00) | 4 466 / 22 | 2 |
| aleatorio | difusion | 25/30 | 0,66-0,93 | 0,084 (0,50) | 417 (161) | 0,93 (1,00) | 4 365 / 1 585 | 86 |

Todas las colonias se asientan (30/30 en las 8 condiciones). Las que no "verifican" terminan por `verificadora_fallo` (la verificadora no llega; 5 a 12 de 30). Contadores de mecanismo (suma de 30 ensayos): `pista_de_baile` envía 1 296 (L) y 1 166 (aleatorio) `RECLUTA`, 114 y 120 rutas heredadas; `difusion` difunde 1 323/1 373 rutas/mapas en L y 1 242/1 290 en aleatorio, con 102 y 118 rutas heredadas; `rescate` con umbral 0,5 envía 0 rescates y 0 recluta (su fila es idéntica a `ausente` en todos los resultados; solo cuesta el tráfico de los informes a la madre: `ESTADO`, `DANZA`, `FRAGMENTO` y, si la verificadora falla, `PIDE_RESCATE`). La madre usa como máximo su presupuesto de 64 B de memoria (`memoria_madre_max` = 64).

Tráfico, en bytes totales por ensayo (binario; medias por condición): 69 000 a 82 000, de los cuales entre el 92 y el 100 % es la conversación mundo<->agente (`PERCEPCION` y `ACCION`, 4 800 a 5 700 mensajes); por ensayo, el mínimo es el 90 %. En un ESP32 real esa conversación es sensor y actuador locales, no radio. Lo que sí viaja por radio (agente<->madre, con madre) es de 4,2 a 6,3 KB por ensayo de 400 a 480 ticks, unos 10 a 14 B por tick para toda la colonia.

## Diagnóstico

- Ninguna diferencia es significativa tras corregir. La más fuerte (pista de baile y difusión en el mundo aleatorio, 25/30 frente a 18/30, p = 0,084 sin corregir) es una tendencia, no un resultado.
- Con 10 viajes la madre no reduce la dispersión del tiempo de forma detectable (la desviación va de 112 a 169 ticks; `difusion` es incluso mayor que `ausente`). La reducción "a menos de un tercio" de F-013 correspondía a una configuración anterior (un viaje por agente) y no se reproduce con la actual; no se repitió aquí aquella configuración.
- `rescate` con umbral 0,5 es equivalente a no tener madre: coherente con el contador (0 envíos). Su umbral se barre en `experimento_rescate.md`.
- Costo: `difusion` envía el doble de bytes madre->agentes que `pista_de_baile` (1 709 frente a 795 B) sin mejor resultado; con ESP-NOW a 250 B por paquete todos estos mensajes caben (ver `tamanos_de_mensaje.md`).

## Límites

- 30 semillas: con 18/30 frente a 25/30 la potencia es baja; un confirmatorio con ~100 semillas, pruebas declaradas antes, sigue pendiente.
- Una semilla define un único mundo; en `L` solo cambian el azar de las agentes y de la madre.
- Canal ideal (sin pérdidas ni retardo); con pérdidas, ver `experimento_reproducibilidad_canal.md`.
- Los "ticks" no tienen tiempo real asignado; bytes por segundo requieren fijar la duración del tick.
