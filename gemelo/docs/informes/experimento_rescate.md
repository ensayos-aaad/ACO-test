# Experimento "rescate": umbral del modo rescate

Redactado 2026-11-20 03:31 -0500 (hora del archivo; la marca original, estimada, se corrigió tras la revisión del bloque D). Cifras de `experimentos/datos/rescate/` (240 ensayos). El análisis completo con pruebas declaradas está en `rescate_tras_F020.md`; este informe es su versión corta.

## Objetivo

Probar la hipótesis de `resumen.pdf`: si la madre rescata a las agentes rezagadas (les envía una ruta ya conocida), la colonia converge más y con menos variación en el tiempo. Con el umbral por defecto (0,5) el rescate no llegaba a nadie útil (F-020), así que se barre el umbral. Un rescate es un mensaje `RUTA` de la madre a una agente cuya "experiencia" está por debajo del umbral relativo.

## Configuración

- Plan `experimentos/rescate.yaml`: base `configs/default.yaml`, mundos `L` y `aleatorio`, modo `rescate`, `umbral_rescate` en {0,5; 0,8; 0,95; 1,0}, semillas 0 a 29, motor determinista.
- Repetir, desde `gemelo/`: `C:/Users/Usuario/anaconda3/envs/aco-gemelo/python.exe -X utf8 -W ignore -m aco_gemelo experimentos --plan experimentos/rescate.yaml`. Análisis: `experimentos/analisis_A2.py`.

## Qué es confirmatorio y qué no

Solo las pruebas (a) y (d) de `rescate_tras_F020.md` son confirmatorias (se fijaron el 2026-11-18 22:59 -0500 antes de repetir el plan tras F-020). Las pruebas de convergencia (b) y de varianza (c) se declararon antes de **repetir** el cálculo, pero sobre datos que ya se habían visto en F-018, y el resultado de F-019 fue exploratorio (pruebas fijadas tras mirar). Se las trata como exploratorias. Ningún dato nuevo de semillas distintas.

## Resultados (30 ensayos por fila)

| Mundo | Umbral | Verificadora llega (IC 95 %) | Sin madre | p Fisher (Bonferroni x6) | Ticks hasta asentarse, media | Rescates enviados / usados / llegan tarde (suma) | Bytes madre->agente por ensayo |
|---|---|---|---|---|---|---|---|
| L | 0,5 | 21 (0,52-0,83) | 21 | - | 465 | 0 / 0 / 0 | 22 |
| L | 0,8 | 24 (0,63-0,90) | 21 | 0,55 (1,00) | 435 | 79 / 57 / 22 | 57 |
| L | 0,95 | 22 (0,56-0,86) | 21 | 1,00 (1,00) | 431 | 121 / 86 / 35 | 78 |
| L | 1,0 | 23 (0,59-0,88) | 21 | 0,77 (1,00) | 424 | 128 / 92 / 36 | 81 |
| aleatorio | 0,5 | 18 (0,42-0,75) | 18 | - | 428 | 0 / 0 / 0 | 22 |
| aleatorio | 0,8 | 25 (0,66-0,93) | 18 | 0,084 (0,50) | 398 | 95 / 79 / 16 | 64 |
| aleatorio | 0,95 | 27 (0,74-0,97) | 18 | 0,015 (0,092) | 402 | 122 / 92 / 30 | 77 |
| aleatorio | 1,0 | 27 (0,74-0,97) | 18 | 0,015 (0,092) | 401 | 129 / 98 / 31 | 80 |

- (a) `rescate_verificadora` = 0 en los 240 ensayos (y en los 480 del conjunto con `modos`).
- Varianza de `ticks_asentadas`: desviaciones de 133 a 148 ticks con rescate frente a 145 (L) y 140 (aleatorio) sin madre; Brown-Forsythe con p corregido = 1,00 en las 6 comparaciones.
- Los 22 B de la fila 0,5 son `INICIO` (14 B) más `FIN` (8 B): sin rescates, la madre solo habla dos veces.

## Diagnóstico

- El mecanismo existe y se mide: cada envío termina "usado" (71-83 %) o "llega tarde" (`rescate_ya_llego`: la agente ya había llegado a la meta; `rescate_ya_tiene_ruta` vale 0 en todos los ensayos); nunca va a la verificadora, ni a agente ocupada ni a otro nido (contadores en 0).
- Costo: 2 a 4 mensajes `RUTA` extra por ensayo, unos 35 a 59 B de radio madre->agente por ensayo de ~430 ticks. En un ESP32 es despreciable; no hay razón de tráfico para no rescatar.
- Beneficio: tendencia de 27/30 frente a 18/30 en el mundo aleatorio (p corregido 0,092), sin efecto en `L`, y **sin reducción de varianza** (hipótesis de `resumen.pdf` no apoyada, F-019). Es una tendencia exploratoria, no un resultado.
- El rescate con umbral 0,5 es idéntico a `ausente` en todas las columnas de resultado; no es una configuración útil.
- Comparado con `ausente`, el tráfico total por ensayo baja un poco con rescate alto (p. ej. 75 147 B con umbral 1,0 frente a 76 972 B en L) porque el ensayo es más corto; el modo con 0,5 sube a 81 856 B por los informes a la madre (`ESTADO`, `DANZA`, `FRAGMENTO` y, si la verificadora falla, `PIDE_RESCATE`) que, sin rescates, no cambian nada.

## Límites

- 30 semillas: los IC de 27/30 y 18/30 se solapan casi hasta 0,75; pendiente un confirmatorio de ~100 semillas.
- Las 4 condiciones de umbral comparten semillas con `ausente`: son comparaciones apareadas tratadas como independientes (Fisher), lo que es conservador.
- Un solo valor de Δt (10 ticks) y de número de agentes (6).
