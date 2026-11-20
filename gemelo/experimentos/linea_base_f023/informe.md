# Línea base de F-023 (antes de corregir el canal y INICIO)

Commit del código medido: `42e0943`. Script: `linea_base.py` (misma carpeta). Datos: `datos/`.

## Declaración previa (2026-11-19 20:59 -0500, antes de correr nada)

Qué se mide: por ensayo, `motivo`, `ticks_asentadas`, `ticks_total`, `verificada`, `conocimiento`,
`bytes_totales` (y la fila completa de `metricas.fila`, para la comparación exacta).

Diseño: 4 modos de la madre x 2 mundos (L, aleatorio; configuración de `modos.yaml`) x 3 canales
(`ideal` = el de F-022; `perdidas` = p_perdida 0,2; `retardo` = retardo [1, 3] ticks) x semillas 0..29.
Motor `determinista` (una corrida) y `hilos_sincronos` (dos corridas por ensayo). Total 24 condiciones.

Descriptivo, sin pruebas de hipótesis: se cuentan ensayos que difieren (conteos exactos, no hay
estadística inferencial). Los umbrales son cualitativos y se fijan aquí:

- H1: con canal `ideal`, `hilos_sincronos` repetido da 0 diferencias y el determinista reproduce 240/240
  filas de `datos/modos/` (F-022). (Si no, la línea base no sirve.)
- H2: con `perdidas` y con `retardo`, `hilos_sincronos` difiere entre corridas en una fracción relevante
  (F-023: 52-67 de 120; espero del orden de 40-60 % de los ensayos con madre; en modo `ausente` espero menos
  o ninguna, porque no hay tráfico madre-agente; es una conjetura).
- H3: el determinista con perdidas/retardo es reproducible consigo mismo (se corre dos veces una muestra
  para comprobarlo: 0 diferencias).
- Datos de F-022 con pérdidas: no existen en el repositorio (los CSV de `datos/modos` y `datos/rescate`
  usan el canal por defecto). Por eso la comparación contra F-022 se hace solo con el canal `ideal`; el
  "antes" de pérdidas/retardo es esta misma línea base.

Después de las correcciones se repite el script tal cual y se compara contra `datos/` fila a fila
(la comparación se hace con un script aparte, ver abajo).

## Resultados (corrida 2026-11-19 20:59-21:21, 21 min; commit 42e0943)

Total: 24 condiciones x 30 semillas = 720 ensayos por motor; `hilos_sincronos` se corrió dos veces.

| Canal | hilos_sincronos A vs B (difieren) | determinista vs sincronos A | determinista vs si mismo |
|---|---|---|---|
| ideal (F-022) | 0 / 240 | 0 / 240 | n/a |
| perdidas (p = 0,2) | 71 / 240 | 67 / 240 | 0 / 240 |
| retardo [1, 3] | 37 / 240 | 32 / 240 | 0 / 240 |

(La columna A vs B compara la fila completa de `metricas.fila`; con solo los 6 campos clave los
conteos son algo menores, ver `datos/diferencias.csv`.)

Por modo (perdidas, A vs B sobre 60 ensayos de L + aleatorio): ausente 0, pista_de_baile 8, rescate 11,
difusion 52. Con retardo: ausente 0, pista_de_baile 18, rescate 1, difusion 18.

Contra F-022 (`datos/modos/`, canal ideal): el determinista reproduce **240 / 240** ensayos en los 6 campos
clave (diferencias 0). No hay datos de F-022 con pérdidas ni retardo en el repositorio, así que no hay
comparación posible para esos canales: esta línea base es su único "antes".

## Lectura

- H1 se cumple (0 diferencias en canal ideal, 240/240 contra F-022).
- H2 se cumple solo en parte: la inestabilidad existe con pérdidas y retardo, pero es menor de lo que esperé
  (30 % y 15 % del total; 0 en `ausente`, porque sin madre no hay mensajes aleatorios entre agentes y madre;
  `difusion` es el modo más afectado: 52 de 60 con pérdidas). Cifra más cercana a F-023 (52-67 de 120): aquí 71
  y 37 de 240 por canal, con mezcla distinta de condiciones; no son comparables 1 a 1.
- H3 se cumple: determinista con pérdidas/retardo es reproducible consigo mismo (0/240 y 0/240).
- Nota: tras la corrida se corrigió en el script una comparación contra F-022 que marcaba falsas diferencias
  (`None` frente a celda vacía en `conocimiento`); `diferencias.csv` tiene ya el valor corregido (0) y se
  comprobó aparte (240 filas, 0 diferencias). El parche no cambia los datos de ensayo.

## Cómo repetir tras las correcciones

Desde `gemelo/`: `python -X utf8 -W ignore experimentos/linea_base_f023/linea_base.py --salida experimentos/linea_base_f023/datos_despues`
(21 min con 8 núcleos; los motores de hilos son lentos). Esperado tras corregir: sincronos A vs B = 0 en los
tres canales; determinista ideal = 240/240 igual a F-022; en perdidas/retardo el determinista cambiará respecto
a `datos/determinista.csv` (INICIO deja de consumir números del canal), y eso se cuantifica ensayo a ensayo.
Limitación: 30 semillas, un solo valor de pérdida (0,2) y de retardo ([1,3]).

## Después de la corrección 1 (2026-11-19, un generador por emisor en el canal)

Corrida con el mismo script, salida en `datos_despues/`. Comparación con `comparar.py` (exploratoria: **no** se
declararon pruebas antes; los p no están corregidos por comparaciones múltiples).

- `hilos_sincronos` A frente a B: **0/240** en los tres canales (antes: 0, 71 y 37). Determinista frente a sincronos: 0/240.
- Determinista, canal ideal: **0/240** distintos (sigue igual a F-022).
- Determinista con pérdidas: 144/240 ensayos cambian; con retardo: 118/240. Es lo esperado: cambió el azar.
- Agregado por condición (16 condiciones): ninguna diferencia en la tasa de verificación (Fisher, p mínimo 0,08)
  ni en los ticks totales (Mann-Whitney, p mínimo 0,24). Los ensayos individuales cambian; las tasas no se mueven
  más allá del ruido con 30 semillas.

Comando: `python -X utf8 experimentos/linea_base_f023/comparar.py experimentos/linea_base_f023/datos/determinista.csv experimentos/linea_base_f023/datos_despues/determinista.csv`

## Después del arreglo de N1 (2026-11-19, semilla del canal con etiqueta propia)

La revisión de F-024 encontró que el azar del canal repetía el de las agentes (N1). Con el arreglo, misma corrida,
salida en `datos_despues_n1/` (**la vigente**; `datos_despues/` queda como registro de la versión con N1).

- `hilos_sincronos` A frente a B y frente al determinista: **0/240** en los tres canales.
- Determinista, canal ideal: **0/240** distintos.
- Determinista frente a la línea base original: 146/240 (pérdidas) y 118/240 (retardo) ensayos cambian.
- Por condición (16): sin diferencia en la tasa de verificación (Fisher, p mínimo 0,33) ni en los ticks
  (Mann-Whitney, p mínimo 0,56). Exploratorio, como la comparación anterior.
