# ASSUMPTIONS — suposiciones de diseño y sesgos declarados

Cada suposición es una hipótesis que hay que probar, no un requisito. Las intuiciones del operador
que no se han verificado se etiquetan como **malicia indígena**.

| ID | Suposición | Origen | Estado | Cómo se verificaría |
|---|---|---|---|---|
| A-001 | `deneubourg_puente_doble.ipynb` y `montecarlo_aco.ipynb` son los oráculos adecuados para C1–C4 | Claude, Sesión 0 | Sin verificar | Que el operador lo apruebe tras leer CONTEXT.md §3 |
| A-002 | k = 20, h = α = 2 son los valores de trabajo para C1 | PROMPT-ZERO §2 y deneubourg [5] | Sin verificar | Decisión del operador ante la inconsistencia I2 |
| A-003 | La hormiga de Deneubourg se modela como agente reactivo simple aleatorizado (AIMA cap. 2), y su memoria es la feromona del entorno (estigmergia) | Claude, CONTEXT §6.4 | Sin verificar | Que el operador lo apruebe; contraste con AIMA y con Dorigo & Stützle |
| A-004 | El patrón NetLogo (entorno) ↔ serial ↔ ESP32 (agente) de los ejemplos 3 a 6 sirve para el puente doble | Claude, CONTEXT §5.1 | Sin verificar | Decisión del operador sobre la representación física (PROMPT-ZERO §3) |

## Sesgos y límites declarados por el operador

| Fecha | Declaración | Consecuencia |
|---|---|---|
| 2026-11-16 20:29 -0500 | **"El operador humano está recibiendo más información de la que puede procesar y conocer, de modo que se echa la bendición."** Algunas aprobaciones pueden darse por confianza y no por comprensión plena. | Las decisiones de esta sesión se marcan como **aprobadas con carga cognitiva alta**: se revisan antes de cerrarlas como definitivas. Claude reduce el volumen: respuestas ejecutivas, una tabla, una pregunta, y el detalle en los archivos, no en el chat. |
| 2026-11-16 21:03 -0500 | **Segunda "bendición":** el operador delega los parámetros pendientes con la instrucción "usa algo según la literatura". | Claude elige los valores (DECISIONES-PRUEBA.md, sección I) e indica cuáles tienen respaldo y cuáles son suposición. Todos quedan a revisión. Cambio importante frente a lo ya decidido: el depósito pasa a hacerse a la vuelta (I4, I5). |

(El operador declara sus sesgos al abrir cada sesión.)
