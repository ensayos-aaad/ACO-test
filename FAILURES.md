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
