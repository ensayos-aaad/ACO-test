# FAILURES — registro de fallas

Toda prueba fallida, montaje que no funcionó o error encontrado se registra aquí. **Nunca se borra.**
Formato: fecha · qué se intentó · qué pasó · evidencia · qué se aprendió / acción.

## 2026-11-16 — Sesión 0
- **F-001** · Se intentó leer `referencia/PROCEDENCIA.md` (PROMPT-ZERO §9.1) · No existía: ni `referencia/` estaba en el repositorio ni el fuente trae PROCEDENCIA.md · `git status` y el listado del fuente · Se copió el fuente y Claude Code creó PROCEDENCIA.md (ADR-001).
- **F-002** · Se intentó volcar los notebooks con `python -I` · `UnicodeEncodeError` (la consola usa cp1252) · traceback · En Windows, los scripts del oráculo deben usar `python -X utf8` o escribir a archivo en UTF-8.
- **F-003** · Se comprobó el entorno para el oráculo · `sympy` no está instalado · `ModuleNotFoundError` · Instalarlo antes de usar deneubourg [9] y [15] (pendiente de aprobación).
- **F-004** · Se ejecutó la Sesión 0 · Claude pasó directo a construir y omitió la apertura (PROMPT-ZERO §6.1): no presentó el resumen del estado en 5 líneas ni pidió al operador que declarara sesgos y suposiciones · Lo señaló el operador ("Revisa lo que llamamos resumen") · Cada sesión empieza con el resumen de 5 líneas y la declaración de sesgos, antes de cualquier construcción.
- **F-005** · Se verificó el entorno de Python (F-003) · Claude usó el `python` del PATH (`C:\Python311`, 3.11.5) en lugar del de Anaconda, que es el oficial del proyecto. Por eso F-003 dijo que faltaba sympy, cuando Anaconda tiene sympy 1.13.1 · `where python` y la prueba de import con `C:\Users\Usuario\anaconda3\python.exe` · F-003 queda **invalidado**. Toda ejecución de Python del proyecto usa la ruta completa de Anaconda (ver CHECKLIST-ENTORNO.md).
- **F-006** · Se registraron marcas de tiempo en el historial · La entrada de las "19:50" se escribió con una hora estimada, sin consultar el reloj. La hora real era anterior: a las 19:46 todavía no se había terminado · `date` a las 19:46 · Se corrige a 19:45. Las marcas de tiempo se toman siempre con `date`.
- **F-007** · Se hizo el inventario de `referencia/` para CONTEXT.md · No se detectó `referencia/resumen.pdf`, que no viene del fuente (el fuente tiene 172 archivos y la carpeta 174). Por eso se revisó el "cronograma tentativo" sin haber leído el PDF que lo contiene · El operador preguntó "¿lo revisaste del pdf resumen?" · Al inventariar se compara la lista de archivos de la carpeta con la del fuente (`git ls-files`) y se reporta todo lo que sobre.
- **F-010** · 2026-11-16 21:27 -0500 · Comparación de los 4 modos de la madre (mundo L, 6 agentes, 40 semillas, sin evaporación, valores por defecto) · Resultados:

  | Modo | Ticks hasta asentarse (media ± desv., máx.) | Verificadora llega | Ruta verificada / óptima | Bytes madre ↔ agentes |
  |---|---|---|---|---|
  | Ausente | 110 ± 48, máx. 301 | 32/40 | 1,96 | 0 |
  | Pista de baile | 73 ± 23, máx. 112 | 30/40 | 1,34 | 807 |
  | Rescate | 110 ± 48, máx. 301 | 32/40 | 1,99 | 1392 |
  | Difusión | 59 ± 24, máx. 135 | 31/40 | 1,33 | 1171 |

  Las 6 agentes se asientan en 40/40 con todos los modos · Script de comparación (scratchpad); la prueba `test_con_cualquier_modo_la_colonia_se_asienta_y_la_madre_acelera` fija lo esencial con 20 semillas · Lecturas: (1) la pista de baile y la difusión **bajan el tiempo, su dispersión y el largo de la ruta**; (2) **el rescate no cambia nada**: con el umbral del 50 % ninguna agente llega a contar como rezagada antes de asentarse, así que la hipótesis de `resumen.pdf` **no se pudo poner a prueba todavía** (hay que barrer el umbral o cambiar la métrica de experiencia); (3) **la verificadora sigue fallando en ~1 de cada 4 semillas** con cualquier modo: los rastros cruzados la llevan a callejones (I12 le prohíbe volver sobre sus pasos). Nada de esto se ajustó.
- **F-016** · 2026-11-17 04:00 -0500 · Activar la opción c en los mundos L y aleatorio (J7: salida cada tick, 10 viajes, límite 6000) · **Primera medición: en el mundo aleatorio solo 10/30 colonias se asentaban**, y el tráfico con la madre se disparaba (34 941 B frente a 749) · Diagnóstico con la semilla 1: una agente oscilaba durante miles de ticks entre la esquina (0, 7) y un callejón de una celda (1, 7). Al salir del callejón volvía a una celda de su ruta, la ruta se recortaba, y la regla de "no volver atrás" apuntaba a la celda equivocada y le prohibía la única salida. Un primer arreglo (que la explotadora evite las celdas de su ruta) **no atacó la causa y empeoró el resultado (1/30)** · **Arreglo final, fiel a S-ACO:** cada agente recuerda las **celdas pisadas en el viaje** (un mapa de bits de 8 B en 8 × 8), prefiere las no pisadas y, si ya pisó todas, solo evita la celda de la que acaba de llegar. Prueba de regresión: `test_no_queda_atrapada_en_un_callejon` · Resultado (30 semillas, pista de baile, ρ = 0,01):

  | Mundo | Asentadas | Verificadas (IC 95 %) | Ticks hasta asentarse (media) | Ruta / óptima | Bytes madre ↔ agentes |
  |---|---|---|---|---|---|
  | L, 1 viaje | 30/30 | 19/30 (46–78 %) | 75 | 1,31 | 828 |
  | L, opción c | 30/30 | 24/30 (63–90 %) | 433 | 1,67 | 4665 |
  | Aleatorio, 1 viaje | 30/30 | 19/30 (46–78 %) | 62 | 1,28 | 713 |
  | Aleatorio, opción c | 30/30 | 25/30 (66–93 %) | 390 | 1,42 | 4226 |

  Lecturas: la verificadora llega más veces (los intervalos todavía se solapan), a cambio de ensayos unas 6 veces más largos, unas 6 veces más tráfico y, en el mundo L, rutas verificadas más largas. El arreglo del callejón también cambió levemente las cifras de 1 viaje (la regla de elección cambió).
- **F-015** · 2026-11-17 03:37 -0500 · Opción c de F-014 (salidas escalonadas + 50 viajes por agente, escala de 1 nivel = 20 depósitos, k = 1; parámetros J1–J6 declarados a las 03:21, **antes** de implementar y correr) y nueva comparación con el oráculo (mismas tolerancias) · **C1 PASA · C2 PASA · C3 NO PASA · C4 PASA · C5 PASA** · `oraculo/RESULTADOS.md` (el anterior queda en el commit `87262a3`) · Histogramas (0–20 · … · 80–100):

  | | r = 1 | r = 2 |
  |---|---|---|
  | Oráculo | 35 · 11 · 8 · 10 · 36 % | 5 · 5 · 6 · 9 · 75 % |
  | Gemelo, antes (F-014) | 9 · 20 · 38 · 20 · 13 % | 9 · 20 · 38 · 20 · 13 % |
  | Gemelo, ahora | 41 · 8 · 6 · 11 · 34 % | 20 · 7 · 9 · 16 · 48 % |

  Lecturas: (1) con r = 1 el gemelo **reproduce la "U" del notebook** (extremos 75 %, cada rama gana la mitad: p = 0,49); (2) con r = 2 hay preferencia por la rama corta (gana en el 48 %, pierde en el 20 %) pero **más débil que en el oráculo** (75 %); la diferencia (0,27) supera la tolerancia (0,15). Causas posibles, **no comprobadas**: la percepción en niveles de 20 depósitos esconde las primeras diferencias; el gemelo deposita a la vuelta y el notebook al llegar; 300 decisiones frente a 500 medidas; (3) informativo: con 60 agentes la colonia **no converge** (80 % en el bin del medio), porque 60 × 50 = 3000 depósitos saturan los 15 niveles en ambas ramas y la regla deja de distinguirlas. La escala J3 está pensada para 6 agentes.
- **F-014** · 2026-11-17 03:17 -0500 · Comparación del gemelo con el oráculo en el puente doble (`oraculo/comparar.py`, tolerancias declaradas antes en `oraculo/TOLERANCIAS.md`) · **C1 PASA, C2 NO PASA, C3 NO PASA, C4 NO PASA, C5 PASA** · `oraculo/RESULTADOS.md`: con r = 1 solo el 22 % de los ensayos acaba en una sola rama (umbral 70 %); con r = 2 la rama corta gana en el 13 % (oráculo 75 %); el 38 % de los ensayos queda en el reparto 40–60 % (umbral 20 %) · **Causa, verificada:** los histogramas del gemelo son idénticos para r = 1 y r = 2 (y los mundos sí son distintos), porque **las 6 agentes salen del nido en el tick 0, cuando no hay feromona, y cada una elige rama una sola vez**. Su reparto es una binomial(6, ½) pura (teórica 11 · 23 · 31 · 23 · 11 %; medida 9 · 20 · 38 · 20 · 13 %). No hay ninguna retroalimentación, y con 60 agentes el reparto se concentra en el 50 % (88 %). En el notebook, en cambio, 1000 hormigas llegan **escalonadas** (una cada 2 s) y cada una ve la feromona de las anteriores. La regla de decisión es correcta (C1 PASA); lo que falta es el **mecanismo de interacción en el tiempo**. Arreglarlo es un cambio de diseño (salidas escalonadas o viajes repetidos, que tocan D3, I5 y G1) y queda para decisión del operador.
- **F-013** · 2026-11-17 03:02 -0500 · Comparación de los 4 modos con las métricas del artefacto 10 (mundo L, 6 agentes, **30 semillas**, sin evaporación) · Resultados:

  | Modo | Verificadas (IC 95 %) | Ticks hasta asentarse: media / varianza / máx. | Ruta / óptima | Conocimiento de la madre | Bytes madre ↔ agentes |
  |---|---|---|---|---|---|
  | Ausente | 20/30 (49–81 %) | 102 / 1857 / 301 | 1,78 | — | 0 |
  | Pista de baile | 21/30 (52–83 %) | 75 / 523 / 112 | 1,34 | — | 836 |
  | Rescate | 20/30 (49–81 %) | 102 / 1857 / 301 | 1,78 | 99 % | 1331 |
  | Difusión | 24/30 (63–90 %) | 58 / 527 / 135 | 1,47 | 83 % | 1185 |

  · `python -m aco_gemelo batch` con un YAML por modo · Lecturas: (1) **la madre reduce la varianza del tiempo de convergencia a menos de un tercio** (1857 → 523–527), que es la hipótesis de `resumen.pdf`, pero la logran la pista de baile y la difusión, **no el rescate**, que sigue sin dispararse (I14); (2) en la tasa de verificación los intervalos de confianza se solapan: **con 30 semillas no hay diferencia demostrable entre modos**; (3) en difusión la madre conoce menos mapa (83 %) porque la colonia termina antes; (4) defecto corregido: el `FIN` que difunde el motor se contaba como tráfico de la colonia aunque no hubiera madre.
- **F-012** · 2026-11-17 02:55 -0500 · Primera corrida por línea de comandos de las tres configuraciones de ejemplo (30 semillas cada una, **con evaporación ρ = 0,01**, que es el valor por defecto I3) · Resultados:

  | Configuración | Asentadas | Verificadas | Ruta verificada / óptima |
  |---|---|---|---|
  | `default.yaml` (L, pista de baile) | 30/30 | 18/30 | 1,27 |
  | `aleatorio.yaml` (obstáculos al azar, pista de baile) | 30/30 | 20/30 | 1,44 |
  | `puente_doble.yaml` (sin madre, sin evaporación) | 30/30 | 30/30 | 1,50 |

  · `python -m aco_gemelo batch --config configs/<nombre>.yaml --semillas 30` · Lecturas: (1) primera medición en **mundos de obstáculos aleatorios**: la colonia siempre se asienta; (2) con evaporación la verificadora falla más (18/30 frente a ~30/40 sin evaporación en F-010), como ya mostraba F-009; (3) en el **puente doble** la razón media de 1,50 indica que la verificadora termina en la rama larga cerca de la mitad de las veces: con solo 6 agentes que depositan una vez, la colonia **no llega a preferir la rama corta**. Eso no es todavía la comparación con el oráculo (artefacto 12), pero anticipa que C2 y C3 no se pueden evaluar con este ciclo de vida de un solo depósito.
- **F-011** · 2026-11-16 21:27 -0500 · Al probar la madre · Guardaba los pedidos de ruta sin límite y en modos que no los atienden; eso expulsaba las rutas de su memoria · 5 pruebas de presupuesto en NO PASA · Ahora guarda un pedido por agente y solo en el modo pista de baile. Con 32 B, en los modos con mapa no cabe ninguna ruta (el mapa de 8 × 8 ocupa 16 B y la tabla de agentes 13 B): el presupuesto mínimo útil es mayor.
- **F-009** · 2026-11-16 21:10 -0500 · Primera calibración de la colonia sin madre (mundo L, 6 agentes, 40 semillas, límite de 2000 ticks) · Las 6 agentes se asientan en 40/40 (en unos 100 ticks), pero **la verificadora solo llega en 32/40 sin evaporación y en 24/40 con ρ = 0,01**, y cuando llega su ruta mide en promedio 1,7–2,0 veces la óptima · Script de calibración (scratchpad) con `tau_max` 1,0 y 0,25 · Causas: (1) cada agente deposita **una sola vez** y se asienta (I5), así que no hay refuerzo repetido como en S-ACO y la evaporación solo borra; (2) los 6 rastros se cruzan y la verificadora, que no puede volver sobre sus pasos (I12), se mete en callejones; (3) las rutas individuales son largas (exploración casi al azar). No se ajustó nada para taparlo: es la **línea base sin madre** contra la que se medirán los modos de la madre (artefacto 7).
- **F-008** · 2026-11-16 20:50 -0500 · Se creó el entorno conda con las versiones de `base` · Falló: `sympy 1.13.1` no existe para Windows en el canal `defaults` (en `base` venía de pip) · `LibMambaUnsatisfiableError` · Se fijó sympy 1.13.2. Las versiones de `base` instaladas con pip no sirven tal cual para `environment.yml`.
