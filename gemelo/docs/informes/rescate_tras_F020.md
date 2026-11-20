# Rescate tras corregir F-020 (bloque A2)

## Pruebas declaradas antes de correr (2026-11-18 22:59 -0500)

Planes: `experimentos/modos.yaml` y `experimentos/rescate.yaml`, 30 semillas por condición, mundos L y aleatorio.
Datos anteriores en `experimentos/datos/_antes_F020/`.

- (a) ¿Llega algún rescate a la verificadora (`rescate_verificadora`)? Se espera 0 en todos los ensayos.
- (b) Convergencia (`verificada`): rescate con umbral 0,8 / 0,95 / 1,0 frente a `ausente` (plan `modos`), por mundo. Fisher exacta bilateral, Bonferroni con 6 comparaciones (alfa corregido 0,05/6).
- (c) Varianza de `ticks_asentadas` con y sin rescate (mismas 6 comparaciones): Brown-Forsythe (Levene centrada en la mediana), Bonferroni x6.
- (d) Mecanismos por condición: `rescates_enviados`, `rescate_usado`, `rescate_ya_llego` (llegan tarde), más descartes.
- Todo lo que se mire fuera de esto se marcará como exploratorio.

## Objetivo y configuración

Repetir los planes `modos` y `rescate` tras corregir F-020 (la madre ya no rescata a la verificadora) y decir qué cambia
respecto de F-018/F-019. Configuración base `configs/default.yaml` (salida cada tick, 10 viajes, 6 agentes + verificadora),
30 semillas por condición (0 a 29), motor determinista, mundos L y aleatorio. Datos nuevos en `experimentos/datos/{modos,rescate}/`,
anteriores en `experimentos/datos/_antes_F020/`. Análisis: `experimentos/analisis_A2.py`.

## Resultados

**(a) Rescates a la verificadora:** `rescate_verificadora` = 0 en las 16 condiciones (480 ensayos). PASA.

**(b) Convergencia** (verificadora llega, de 30; Fisher bilateral, Bonferroni x6; IC 95 % de Wilson del rescate):

| Mundo | Umbral | Rescate | Sin madre | IC rescate | p | p Bonferroni |
|---|---|---|---|---|---|---|
| L | 0,8 | 24 | 21 | 0,63-0,90 | 0,552 | 1,00 |
| L | 0,95 | 22 | 21 | 0,56-0,86 | 1,000 | 1,00 |
| L | 1,0 | 23 | 21 | 0,59-0,88 | 0,771 | 1,00 |
| aleatorio | 0,8 | 25 | 18 | 0,66-0,93 | 0,084 | 0,50 |
| aleatorio | 0,95 | 27 | 18 | 0,74-0,97 | 0,015 | 0,092 |
| aleatorio | 1,0 | 27 | 18 | 0,74-0,97 | 0,015 | 0,092 |

Ninguna es significativa tras corregir (alfa 0,05).

**(c) Varianza de `ticks_asentadas`** (Brown-Forsythe, Bonferroni x6): desviaciones estándar 133-148 con rescate frente a 145 (L) y 140 (aleatorio)
sin madre; p entre 0,81 y 0,91 sin corregir, 1,00 corregido en las 6. Sin diferencia.

**(d) Mecanismos** (suma de 30 ensayos; umbral 0,5 y demás modos sin rescate: 0 envíos):

| Mundo | Umbral | Enviados | Usados | Llegan tarde (`ya_llego`) | Ocupada / no cabe / otro nido / verificadora |
|---|---|---|---|---|---|
| L | 0,8 | 79 | 57 | 22 | 0 / 0 / 0 / 0 |
| L | 0,95 | 121 | 86 | 35 | 0 / 0 / 0 / 0 |
| L | 1,0 | 128 | 92 | 36 | 0 / 0 / 0 / 0 |
| aleatorio | 0,8 | 95 | 79 | 16 | 0 / 0 / 0 / 0 |
| aleatorio | 0,95 | 122 | 92 | 30 | 0 / 0 / 0 / 0 |
| aleatorio | 1,0 | 129 | 98 | 31 | 0 / 0 / 0 / 0 |

Cada envío termina en "usado" o "llega tarde": 71-83 % se usan.

## Comparación con antes de la corrección

- **Los resultados de ensayo son idénticos fila por fila**: `verificada`, `ticks_asentadas`, `ticks_total`, longitudes, etc. coinciden en los 16 CSV.
  Solo difieren la memoria de la madre y el tráfico madre a agente. Causa: la verificadora ignoraba el rescate, así que el envío era inútil.
- Con umbral 0,5 (el del plan `modos`, modo `rescate`) hoy hay **0 rescates** y el modo `rescate` es idéntico a `ausente`
  (21/30 y 18/30, mismos ticks). Antes se enviaban ~25 mensajes extra por condición (58 contra 30 mensajes madre a agente en L; 55 contra 30 en aleatorio), todos a la verificadora.
  Los 30 restantes son un mensaje por ensayo (presumiblemente `FIN`; no verificado en código).
- Se observa que el tráfico madre a agente baja entre 22 y 28 mensajes por condición con 0,8 y 1,0, coherente con los 24 rescates a la verificadora de F-020.

## Diagnóstico

- **F-018 se sostiene en cifras** (27/30 contra 18/30 en el mundo aleatorio, no significativo tras corregir; sin efecto en L). Cambia su interpretación:
  con umbral 0,5 el rescate nunca ayudó porque no llegaba a ninguna agente útil, y con >=0,8 el efecto (si existe) viene de rescates reales a rezagadas, ahora medidos (79-129 envíos).
- **F-019 se sostiene**: el rescate no reduce la varianza (p corregido = 1,00 en las 6). Que antes estuviera contaminado no cambia nada porque los resultados no varían.
- Los datos de F-018/F-019 no estaban sesgados en resultado, solo en la lectura del mecanismo.
- Hay una tendencia de mejora de convergencia en el mundo aleatorio con rescate alto (p corregido 0,09), no confirmada.

## Limitaciones

- 30 semillas: poca potencia (el IC de 27/30 es 0,74-0,97 y el de 18/30 es 0,42-0,76). Un confirmatorio con ~100 semillas seguiría siendo lo adecuado.
- Los datos "antes" no traen columnas de mecanismos, así que la comparación de envíos se hace por tráfico madre a agente y por las cifras de F-020.
- Una semilla = un mundo en el aleatorio; con motor determinista no hay repetición del mismo mundo.
- Todo lo de la sección "Comparación" y el diagnóstico más allá de (a)-(d) es exploratorio.
