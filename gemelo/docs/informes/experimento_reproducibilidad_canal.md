# Reproducibilidad del canal: motores y pérdidas (F-023 a F-025)

Redactado 2026-11-20 03:31 -0500 (hora del archivo; la marca original, estimada, se corrigió tras la revisión del bloque D). Cifras de `experimentos/linea_base_f023/` (informe de la línea base: `informe.md`; antes: `datos/`; vigente: `datos_despues_n1/`).

## Objetivo

Saber si el mismo ensayo con la misma semilla da el mismo resultado en los dos motores (el determinista, un solo hilo; y `hilos_sincronos`, un hilo por agente y otro para la madre, más parecido a micros independientes) cuando el canal de radio pierde o retrasa mensajes. En un ESP32 el orden en que llegan los mensajes concurrentes no está garantizado; en el gemelo sí debe estarlo, o los experimentos no se pueden repetir ni comparar.

## Configuración

- Script `experimentos/linea_base_f023/linea_base.py`: 4 modos de la madre x 2 mundos (L, aleatorio; configuración de `modos.yaml`) x 3 canales (`ideal`; `perdidas` con p = 0,2; `retardo` de 1 a 3 ticks) x semillas 0 a 29 = 720 ensayos por motor; `hilos_sincronos` se corre dos veces, el determinista una (y una segunda copia `determinista_b.csv`).
- Repetir, desde `gemelo/`: `C:/Users/Usuario/anaconda3/envs/aco-gemelo/python.exe -X utf8 -W ignore experimentos/linea_base_f023/linea_base.py --salida experimentos/linea_base_f023/datos_despues_n1` (unos 21 min con 8 núcleos). Comparación: `experimentos/linea_base_f023/comparar.py`.
- Estado de las dos versiones: "antes" = commit `42e0943` (F-023), "vigente" = tras F-024 (generador del canal por emisor, entrega ordenada) y F-025 (N1: semilla del canal con etiqueta propia).

## Qué es confirmatorio y qué no

Hipótesis H1 a H3 declaradas el 2026-11-19 20:59 -0500 antes de correr (descriptivas, conteos exactos, sin pruebas de hipótesis): H1 canal ideal estable, H2 inestabilidad con pérdidas y retardo, H3 determinista reproducible consigo mismo. Son confirmatorias, pero con la salvedad de que H2 estimaba 40-60 % y salió 30 % y 15 %. La comparación de tasas entre "antes" y "vigente" (Fisher, Mann-Whitney) **no se declaró antes** y no se corrigió por comparaciones múltiples: es exploratoria.

## Resultados

Ensayos cuyo resultado completo (fila de `metricas.fila`) difiere, de 240 por canal:

| Canal | Antes: sincronos A frente a B | Antes: determinista frente a sincronos A | Vigente: sincronos A frente a B | Vigente: determinista frente a sincronos A | Vigente: determinista dos corridas |
|---|---|---|---|---|---|
| ideal | 0 | 0 | 0 | 0 | n/a |
| perdidas (0,2) | 71 | 67 | 0 | 0 | 0 |
| retardo [1, 3] | 37 | 32 | 0 | 0 | 0 |

Antes, por modo con pérdidas (de 60): ausente 0, pista_de_baile 8, rescate 11, difusion 52. Con retardo: 0, 18, 1, 18. Sin madre no hay mensajes de la madre que se reordenen, y por eso `ausente` nunca difiere.

Efecto de la corrección sobre los resultados (determinista, 240 ensayos por canal, valores medios por ensayo, sacados de los CSV):

| Canal | Verificadora antes -> vigente | Ticks totales antes -> vigente | Bytes totales antes -> vigente | Ensayos que cambian |
|---|---|---|---|---|
| ideal | 177 -> 177 | 443,2 -> 443,2 | 75 480 -> 75 480 | 0 |
| perdidas | 177 -> 188 | 444,1 -> 442,1 | 75 621 -> 75 295 | 146 |
| retardo | 181 -> 180 | 447,3 -> 447,3 | 76 170 -> 76 174 | 118 |

Con el canal ideal el determinista reproduce 240/240 los CSV del experimento "modos" (F-022). Comparación por condición (16 condiciones con pérdidas/retardo, exploratoria): tasa de verificación sin diferencia (p mínimo de Fisher 0,33, sin corregir) y ticks sin diferencia (Mann-Whitney, p mínimo 0,56).

## Diagnóstico

- Antes, con pérdidas el 30 % de los ensayos y con retardo el 15 % no se repetían entre dos corridas idénticas del motor de hilos: el canal sacaba números aleatorios en el orden en que llegaban los hilos. Es el equivalente en un ESP32 a que el resultado dependa de quién ganó la carrera por el medio.
- Ahora cada emisor tiene su propio generador y la entrega se ordena por (tick de entrega, tick de envío, emisor, orden): 0/240 en los tres canales, medidos como contador, no inferidos.
- El cambio altera ensayos individuales con pérdidas o retardo porque cambió quién consume qué números del azar; las tasas no se mueven más allá del ruido con 30 semillas. La diferencia de 177 a 188 verificadoras con pérdidas (11 más de 240) parece ruido: no se contrastó con una prueba declarada.
- Lo que garantiza este resultado: el orden de la red simulada es reproducible. No garantiza nada sobre el orden real de un ESP32.

## Límites

- Un solo valor de pérdida (0,2) y de retardo ([1, 3]); 30 semillas por condición.
- No hay datos de F-022 con pérdidas ni retardo, así que "antes" es la línea base de F-023, no los resultados previos de otro experimento.
- El agregado de "antes" mezcla modos con mucho y poco tráfico madre-agente; las cifras de 52-67 de 120 citadas en F-023 no son comparables 1 a 1 con 71 y 37 de 240 (otra mezcla de condiciones).
- `datos_despues/` (con el defecto N1) se conserva como registro, no se debe usar.
