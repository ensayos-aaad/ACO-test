# CONTEXT — inventario de referencia/ (Sesión 0)

Fuente: `UdeA-IoT/ESP-ACO` @ `3c48648` (ver [referencia/PROCEDENCIA.md](referencia/PROCEDENCIA.md)).
Generado: 2026-11-16 19:20 -0500. Los vacíos e inconsistencias se marcan como **[VACÍO]** o
**[INCONSISTENCIA]** y **no** se corrigen aquí.

Las referencias de celda usan el índice base 0 del notebook (`[n]` = celda número n).

## 1. Inventario de archivos

### 1.1 Relevante para el puente doble (núcleo del proyecto)

Carpeta `ACO/experimento_doble-puente/` y su gemela `ACO/hormigas-artificiales/`:

| Archivo | Tipo | Contenido |
|---|---|---|
| `deneubourg_puente_doble.ipynb` | Notebook, 17 celdas | Deducción de la fórmula 1.1, curva de amplificación, dinámica con retardo 1.2–1.3 (campo medio determinista), punto fijo y estabilidad con sympy, 4 ejercicios de repaso. **Candidato principal a oráculo.** |
| `experimento_doble_puente.ipynb` | Notebook, 8 celdas | Simulación estocástica de una sola corrida con sliders (ipywidgets) para r y α. Incluye pseudocódigo (celda [7]). |
| `montecarlo_aco.ipynb` | Notebook, 5 celdas | Montecarlo: N colonias de 1000 hormigas e histograma del tráfico final (estilo Fig. 1.4 del libro). **Candidato a oráculo para C2/C3.** |
| `simulacion_montecarlo_intro.ipynb` | Notebook, 8 celdas | Estimación de π por Montecarlo. Pedagógico; no modela ACO. |
| `README.md` | Texto | Descripción de la carpeta (la versión de `hormigas-artificiales/` es más completa y propone un orden de lectura). |
| `prompt.md` | Texto | Prompt usado para generar el material. |
| `hormigas-artificiales/modelo_estocastico_a_discreto.md` | Texto teórico | Del caso continuo (1.1–1.3) al discreto (ejercicio 1.5), glosario, tabla comparativa y mapa de ecuaciones. |
| `hormigas-artificiales/*.png` | Imágenes | Esquema del experimento y grafo. |

Los cuatro notebooks son **idénticos byte a byte** en ambas carpetas; solo difieren los README.

### 1.2 Otro material de ACO (fuera del alcance inmediato)

| Ruta | Contenido |
|---|---|
| `ACO/bases/README.md` | Bases conceptuales. |
| `ACO/metaheuristic-ACO/` | Parte 1: optimización combinatoria y TSP (notebook, figuras SVG de 2-opt). Parte 2: ejercicio TSP con ACO (notebook de solución), prompts y preguntas. |
| `ACO/s-aco/` | README extenso sobre S-ACO, `prompt.md` y grafo. |

### 1.3 Agentes, simulación y ESP32 (antecedentes de hardware/toolchain)

| Ruta | Contenido |
|---|---|
| `simulaciones/ejemplo1..6/` | Mundos NetLogo (`.nlogox`), agentes en Python y comunicación serial. |
| `simulaciones/ejemplo3/esp32/` | **Firmware ESP32 previo**: `main.cpp` + `platformio.ini` (PlatformIO, `board = nodemcu-32s`, `framework = arduino`, `monitor_speed = 9600`) y captura de una simulación en Wokwi. |
| `simulaciones/ejemplo6/` | Agente en ESP32 conectado a NetLogo; introducción a FSM. |
| `simuladores/netlogo/` | Agente aspiradora (código AIMA en Python, incluido `__pycache__`), ejemplos de NetLogo, `chapter02.pdf`. |
| `papers/` | Material de estigmergia (`stigmergy.pdf`), clases CS188 (PDF), simulaciones de Holland & Melhuish en NetLogo y `experimento_0`. |
| Raíz | `README.md` ("ESP-ACO / Ensayos varios"), 5 imágenes de tipos de agente, `.gitignore`. |

## 2. Parámetros del modelo tal como aparecen en los notebooks

### 2.1 Notación de PROMPT-ZERO frente a la de los notebooks

PROMPT-ZERO escribe la fórmula 1.1 como `p1 = (m1+k)^h / [(m1+k)^h + (m2+k)^h]`, con k ≈ 20 y h ≈ 2.
Los notebooks usan `p_s = (t_s + φ_s)^α / [(t_s + φ_s)^α + (t_s + φ_l)^α]`. Equivalencias:
k ↔ t_s (en su papel de offset), h ↔ α (o n), m ↔ φ.

### 2.2 Tabla de parámetros

| Notebook | Celda | Parámetro | Valor | Nota |
|---|---|---|---|---|
| deneubourg_puente_doble | [3] MD | α | ≈ 2 (empírico) | |
| deneubourg_puente_doble | [5] | k (offset) | **20** | Coincide con PROMPT-ZERO |
| deneubourg_puente_doble | [5] | n (exponente) | 1, 2, 4 | Barrido para la gráfica |
| deneubourg_puente_doble | [5] | m1 − m2 | −30 … 30 | Dominio de la gráfica |
| deneubourg_puente_doble | [7] | c (flujo) | 1.0 hormiga/paso | |
| deneubourg_puente_doble | [7] | t_s (cruce) | 5 pasos | |
| deneubourg_puente_doble | [7] | r | 2 | |
| deneubourg_puente_doble | [7] | T | 200 pasos | |
| deneubourg_puente_doble | [7] | α | 2 | |
| deneubourg_puente_doble | [7] | k (offset) | **5.0** | "equivalente a t_s" |
| deneubourg_puente_doble | [10] | α | 2 | Diagrama de punto fijo |
| experimento_doble_puente | [5] | t_s (offset) | **20.0** | |
| experimento_doble_puente | [5] | tiempo de cruce corto | 5 | Separado del offset |
| experimento_doble_puente | [5] | r (ratio_longitud) | 2.0 (slider 1.1–5.0) | |
| experimento_doble_puente | [5] | α | 2.0 (slider 0.5–4.0) | |
| experimento_doble_puente | [5] | hormigas por paso (ψ) | 2 | |
| experimento_doble_puente | [5] | tiempo total | 150 | |
| montecarlo_aco | [4] | t_s | **20.0** | Es a la vez offset **y** tiempo de cruce |
| montecarlo_aco | [4] | t_l | t_s · r | |
| montecarlo_aco | [4] | hormigas por experimento | 1000, una cada 2 s (ψ = 0.5) | |
| montecarlo_aco | [4] | ventana de medición | hormigas 501–1000 | Tráfico en la rama corta, en % |
| montecarlo_aco | [4] | experimentos | 1000 (slider 100–2500) | |
| montecarlo_aco | [4] | r | **1.0 por defecto** (slider 1.0–3.0) | |
| montecarlo_aco | [4] | α | 2.0 (slider 0.5–3.0) | |
| montecarlo_aco | [4] | bins del histograma | 0-20, 20-40, 40-60, 60-80, 80-100 | |

**Contraste con PROMPT-ZERO (k ≈ 20, h ≈ 2):** h = α = 2 coincide en todos los notebooks. k = 20
coincide en deneubourg [5], experimento_doble_puente [5] y montecarlo_aco [4], pero **no** en
deneubourg [7], que usa k = 5.0. Ver I2.

## 3. Qué sirve como oráculo y qué no

| Parte | ¿Ejecutable como oráculo? | Para qué criterio |
|---|---|---|
| deneubourg [5]: función `p1(k, n, delta)` | **Sí**, determinista | C1 (p1 para m1, m2 fijos) |
| deneubourg [7]: dinámica con retardo | **Sí**, determinista (campo medio) | C4 (forma de la convergencia) |
| deneubourg [9], [15]: f'(1/2) = α con sympy | **Sí** (necesita sympy) | C4 (estabilidad de puntos fijos) |
| deneubourg [10]: diagrama de punto fijo | Solo gráfico | C4 (apoyo visual) |
| montecarlo_aco [4]: `experimento_individual`, `montecarlo_aco` | **Sí**, estocástico, **sin semilla** | C2 (r = 1), C3 (r = 2) |
| experimento_doble_puente [5] | Parcial: estocástico, sin semilla y atado a la interfaz `interact` | Intuición; no se recomienda como oráculo |
| deneubourg [12]–[14] | No: ejercicios genéricos (x², x³, mapa logístico) | — |
| simulacion_montecarlo_intro | No: estima π | — |
| Celdas Markdown y `modelo_estocastico_a_discreto.md` | No: solo teoría | Fuente de las ecuaciones |

Para ejecutar el oráculo desde `oraculo/` hace falta extraer las funciones sin la parte de
gráficas y widgets.

**Entorno local:** ver [CHECKLIST-ENTORNO.md](CHECKLIST-ENTORNO.md). Con el Python de **Anaconda** (el oficial) están numpy, sympy, scipy y nbconvert. La
verificación anterior (sympy faltante) usó por error `C:\Python311` y queda invalidada (F-005).

## 4. Vacíos e inconsistencias (sin corregir)

- **I1 [INCONSISTENCIA]**: deneubourg [4] dice que el modelo discreto va "sin el offset t_s"
  (`p = m^n / (m^n + m^n)`), pero el código de [5] usa k = 20.
- **I2 [INCONSISTENCIA]**: el offset k vale 20 en [5] y 5.0 en [7] del mismo notebook. En [7] el
  offset y el tiempo de cruce valen lo mismo (5); en experimento_doble_puente [5] están separados
  (20 y 5); en montecarlo_aco [4] valen lo mismo (20). El "doble papel" de t_s se trata de tres
  maneras distintas.
- **I3 [INCONSISTENCIA]**: deneubourg [7] aproxima la llegada desde el otro extremo
  (`p_js(t − t_s)`) con el historial de la propia decisión (`p_s_hist`). Es una simplificación
  de un solo nido simétrico, no las ecuaciones 1.2–1.3 completas. La celda [6] reconoce que "no
  es un solver de ecuaciones con retardo especializado".
- **I4 [INCONSISTENCIA]**: en los notebooks estocásticos, la feromona solo se deposita al
  llegar al otro extremo (una unidad por hormiga), no en el término de salida `ψ p_is(t)` de
  1.2–1.3.
- **I5 [VACÍO]**: no hay semilla del RNG (`np.random` sin `seed`) en los notebooks
  estocásticos. Así no se pueden reproducir sus corridas (afecta a C5).
- **I6 [VACÍO]**: deneubourg no tiene salidas guardadas (no hay outputs). experimento_doble_puente
  [5] y montecarlo_aco [4] sí, pero son estocásticos y sin semilla. No hay valores numéricos de
  referencia guardados: el oráculo tiene que ejecutarse.
- **I7 [VACÍO]**: deneubourg [11] cita `estabilidad_puntos_fijos.md`, que no existe en el repositorio.
- **I8 [VACÍO]**: montecarlo_aco trae r = 1.0 por defecto; para C3 (r = 2) hay que cambiar el
  parámetro. No hay resultados guardados para comparar con la Fig. 1.4 del libro.
- **I9 [VACÍO]**: el repositorio fuente no tiene archivo LICENSE; el de trabajo es GPL v3.
  Falta aclarar la licencia del material copiado.
- **I15 [INCONSISTENCIA]** (detectada en el artefacto 12): `p1(k, n, delta)` de deneubourg [5] solo recibe la *diferencia* m1 − m2 y pone el otro conteo en 0, así que no es la fórmula 1.1 cuando las dos ramas tienen feromona (por ejemplo, m1 = 10 y m2 = 3 da 0,646 en vez de 0,630). El oráculo la usa solo donde coinciden (una rama en 0).
- **I16 [Observación]**: en deneubourg [7], `p_s_hist[0]` queda en 0 porque el ciclo empieza en t = 1; es un artefacto de inicialización, no un valor del modelo.
- **I10 [Observación]**: los notebooks de `experimento_doble-puente/` y `hormigas-artificiales/`
  están duplicados; la fuente canónica no está declarada.

---

## 5. Hormigas y NetLogo

Sección agregada el 2026-11-16 a las 19:45 -0500 (hora corregida, ver F-006), a pedido del operador.

### 5.1 Lo que hay en referencia/

**[VACÍO] I11:** en `referencia/` **no hay ningún modelo NetLogo de hormigas ni del puente doble**.
Todo el material de ACO está en notebooks de Python. Los 19 modelos NetLogo que hay tratan de
agentes AIMA, estigmergia con robots y comunicación serial:

| Ruta | Versión | Qué modela | Relación con hormigas/ACO |
|---|---|---|---|
| `papers/1/simulaciones/holland_melhuish_exp1.nlogox` y `test_exp1*.nlogox` (5) | NetLogo 7.0.4 | Experimento 1 de Holland & Melhuish (1999): colisiones de robots U-bot en una arena octagonal (régimen lineal frente a exponencial). Generado por Claude Sonnet 4.6, junio de 2026. | Indirecta: prerrequisito de los experimentos de **estigmergia**. Usa la razón arena/robot de 1760, "del mismo orden que nido de *Leptothorax* : hormiga". |
| `papers/1/README.md` | — | Conceptos de estigmergia (Grassé, 1959): definición operacional, estigmergia activa frente a pasiva, ciclo agente → entorno → agente. | **Directa**: la feromona de ACO es estigmergia cualitativa activa. "El entorno es el único canal". |
| `simulaciones/ejemplo1..6/*.nlogox` | NetLogo 7 | Mundo lineal de N celdas en anillo con un agente AIMA basado en modelo, primero en Python y luego en ESP32 por serial. | Ninguna. `ejemplo6/contexto.md` **excluye ACO de forma explícita** ("rama de trabajo deliberadamente separada"). |
| `simuladores/netlogo/aspiradora/codes/*` | NetLogo 7 | Mundo de la aspiradora de AIMA: agente reactivo simple y agente basado en modelo (Python + NetLogo). | Ninguna (es la base de agentes, ver §6). |
| `simuladores/netlogo/ejemplos/` | NetLogo 6/7 | Tutoriales (`tutorial2/3`, `dice-and-data`). | Ninguna. |
| `simuladores/netlogo/README.md`, `simuladores/README.md` | — | Enlaces a tutoriales de NetLogo, NetTango y marcos de *swarm robotics* (Pera-Swarm). | Recursos. |

**Patrón de arquitectura ya validado en la referencia (ejemplos 3 a 6):** NetLogo hace de
**entorno** y el ESP32 de **agente**, comunicados por serial. El protocolo es síncrono de
pregunta-respuesta (NetLogo envía el percepto y espera la acción); en el ESP32 la lectura es
no bloqueante con `Serial.available()` y `millis()`. PlatformIO, `nodemcu-32s`, 9600 baudios.
Es un antecedente directo para representar el puente doble con NetLogo como mundo y uno o varios
ESP32 como hormigas. Solo se registra aquí; la decisión le corresponde al operador.

### 5.2 Ejemplos externos (internet, consultados el 2026-11-16)

| Modelo | Fuente | Qué hace | Notas |
|---|---|---|---|
| **Ants** (Wilensky, 1997), Models Library › Biology | [ccl.northwestern.edu/netlogo/models/Ants](https://ccl.northwestern.edu/netlogo/models/Ants) | Forrajeo: la hormiga que encuentra comida vuelve al nido soltando un químico; las demás lo "olfatean" y siguen el gradiente. Nido violeta en el centro, **tres montones de comida** a distancias distintas. Sliders: `population` (se fija antes de SETUP), `diffusion-rate`, `evaporation-rate`. | Responde solo a químico **entre 0.05 y 2** (umbral inferior y saturación). Explota primero la comida cercana; las fuentes lejanas requieren un número crítico de hormigas. Usa `diffuse` y olfateo en 3 direcciones (`uphill-chemical`). **Licencia CC BY-NC-SA 3.0** (ver riesgo R1). La página no muestra los valores por defecto de los sliders. |
| **Ant Adaptation** | [ccl.northwestern.edu/netlogo/models/AntAdaptation](https://ccl.northwestern.edu/netlogo/models/AntAdaptation) | Extiende Ants: dos colonias que compiten y dejan feromona al pelear o al traer comida (basado en Hölldobler & Wilson, *The Ants*, 1990). | Más allá del alcance. |
| Variantes comunitarias de Ants (Andrew E.) | [add food](https://ccl.northwestern.edu/netlogo/models/community/Ants_AndrewE_add%20food3) | Más montones de comida; parámetro `CHEM-LOW-THRESHOLD`. | Muestra que el umbral es un parámetro de diseño. |
| **TSP with Ant Colony** | [modelingcommons.org/…/6053](https://modelingcommons.org/browse/one_model/6053) | Ant System (Dorigo) aplicado al TSP. NetLogo 3.1.4. | Versión antigua; la página no muestra los parámetros. |
| **TSP heuristics** (Jose Costas) | [modelingcommons.org/…/6054](https://modelingcommons.org/browse/one_model/6054) | ACO para TSP, 739 líneas, NetLogo 5.0.4. | Anterior a NetLogo 6; no corre en la web. |
| **AntSystem** (comunidad) | [ccl…/community/AntSystem](https://ccl.northwestern.edu/netlogo/models/community/AntSystem) | Ant System; cita a Dorigo, Maniezzo & Colorni (1996). | La página estaba en mantenimiento al consultarla y no se leyó nada del modelo. |
| CoMSES, etiqueta *ants* | [comses.net/codebases/?tags=ants](https://www.comses.net/codebases/?tags=ants) | Biblioteca con más modelos de hormigas (información social y privada en el forrajeo, *tandem runs* de *Temnothorax*). | Para explorar. |

**[VACÍO] I12:** no se encontró un modelo NetLogo público **específico del puente doble de
Deneubourg** (la búsqueda solo trajo artículos sobre el experimento). Sugerencia de las fuentes:
buscar "double bridge" o "binary bridge" en NetLogo Community Models, que estaba en mantenimiento.

### 5.3 Diferencias entre el modelo Ants de NetLogo y el modelo de los notebooks

| Aspecto | Notebooks (Deneubourg 1.1–1.3) | NetLogo Ants (Wilensky) |
|---|---|---|
| Espacio | Dos ramas abstractas (s, l) | Rejilla 2D de *patches* |
| Feromona | Contador φ por rama, **sin evaporación** | Campo químico por *patch* con **difusión y evaporación** |
| Decisión | Probabilística, `(k+φ)^α` normalizado | Gradiente local (`uphill-chemical`) con umbrales 0.05–2, más un movimiento aleatorio (`wiggle`) |
| Depósito | Una unidad al llegar al otro extremo | Continuo en el viaje de regreso al nido |
| Retardo | Explícito: t_s y r·t_s | Emerge de la distancia recorrida |

**R1 [Riesgo]:** el modelo Ants está bajo CC BY-NC-SA 3.0, que **no es compatible con GPL v3**
(la licencia de este repositorio). Usarlo de inspiración está bien; copiar su código aquí no.

---

## 6. Agentes según Russell & Norvig (AIMA, cap. 2)

### 6.1 Fuentes

- **En referencia/:** `simuladores/netlogo/aspiradora/chapter02.pdf`, que son las **diapositivas
  del cap. 2** "Intelligent Agents" de un curso de Berkeley (27 páginas; ejemplos en Lisp), **no el
  libro**. Leídas las páginas 1–14 y 18–27. También `simuladores/netlogo/aspiradora/aima/`, el
  código Python oficial de AIMA (`agents.py`, entre otros, con `__pycache__` incluido), y las 5
  imágenes de tipos de agente en la raíz de la referencia.
- **Externas:** apuntes de cursos que siguen el libro, por ejemplo
  [UMD (Nau)](https://www.cs.umd.edu/~nau/cmsc421/chapter02.pdf) y
  [readthedocs](https://artificialintelligence.readthedocs.io/en/latest/part1/chap2.html).
  No se consultó el texto del libro.

### 6.2 Lo que enseña el capítulo

1. **Agente y entorno:** el agente percibe con **sensores** y actúa con **actuadores**. La
   **función de agente** `f: P* → A` asigna a cada historia de perceptos una acción; el
   **programa de agente** la implementa y corre sobre una **arquitectura** física.
2. **Racionalidad:** con una **medida de desempeño** fija sobre la secuencia de estados del
   entorno, un agente racional elige la acción que maximiza el desempeño **esperado**, dada la
   secuencia de perceptos hasta ahora. Racional no es omnisciente ni clarividente; por eso
   racional ≠ exitoso. La racionalidad implica exploración, aprendizaje y autonomía.
3. **PEAS:** para diseñar un agente se especifica el entorno de tarea: *Performance, Environment,
   Actuators, Sensors* (ejemplo: el taxi automático).
4. **Tipos de entorno:** observable, determinista, episódico, estático, discreto y de un solo
   agente. "El tipo de entorno determina en gran medida el diseño del agente". El mundo real es
   parcialmente observable, estocástico, secuencial, dinámico, continuo y multiagente.
5. **Tipos de agente**, de menor a mayor generalidad: reactivo simple (reglas
   condición-acción), reactivo con estado o basado en modelo, basado en metas y basado en
   utilidad. Cualquiera puede convertirse en un **agente que aprende**.
6. **Límite del reactivo simple:** falla en entornos parcialmente observables y cae en bucles
   infinitos; la **aleatorización ayuda, "pero no mucho"** (diapositiva 22).

### 6.3 Cómo lo aplica ya la referencia

| Material | Tipo de agente | Lección |
|---|---|---|
| `aspiradora/codes/reflex_vacuum_agent` | Reactivo simple (`REFLEX-VACUUM-AGENT`) | Oscila sin fin cuando todo está limpio, por falta de memoria. |
| `aspiradora/codes/model_based_vacuum_agent` | Basado en modelo (estado interno y `NoOp`) | El estado interno resuelve la oscilación. |
| `simulaciones/ejemplo5` (Fase 2) | Basado en modelo, separado del mundo | Distingue **programa de agente** (capa 1, sin E/S) de **arquitectura** (capa 2, serial). |
| `simulaciones/ejemplo6` (Fase 3) | El mismo agente, en firmware ESP32 | Invariante: la interfaz de NetLogo no cambia; el ESP32 reemplaza a `agente.py` sin que se note. |

**[Por verificar] I13:** el README del agente basado en modelo atribuye
`MODEL-BASED-VACUUM-AGENT` a la "Fig. 2.11, AIMA". La numeración cambia según la edición y
no se pudo confirmar con el libro.

### 6.4 La hormiga del puente doble vista como agente AIMA

Esto es una interpretación de Claude, sin aprobar; queda como suposición A-003.

- **PEAS de una hormiga:**
  - *P*: desempeño **colectivo**, no individual (fracción del tráfico en la rama corta; criterios C2 y C3).
  - *E*: el puente con su feromona.
  - *A*: elegir rama y depositar feromona.
  - *S*: la feromona en la bifurcación (φ_s, φ_l).
- **Entorno:** parcialmente observable (solo ve la feromona local), **estocástico**, secuencial,
  dinámico (otras hormigas cambian φ mientras tanto), discreto en los notebooks, **multiagente**.
- **Tipo de agente:** una hormiga de Deneubourg es un **agente reactivo simple aleatorizado**: no
  tiene estado interno, y su "memoria" está en el entorno (**estigmergia**). La regla 1.1 es su
  regla condición-acción, con probabilidades en lugar de una acción fija.
- **Tensión interesante:** AIMA dice que la aleatorización ayuda "pero no mucho" a un agente
  reactivo *individual*. En la colonia, la combinación de aleatoriedad y feromona compartida
  **sí** lleva al camino corto: la racionalidad aparece a nivel colectivo. Esto puede servir como
  eje pedagógico para C6.
- **Programa frente a arquitectura** (lección de los ejemplos 5 y 6): la regla 1.1 sería la capa 1,
  la que se valida contra el oráculo, y la E/S del ESP32 (LEDs, serial, ESP-NOW) sería la capa 2.

---

## 7. Documento agregado por el operador: referencia/resumen.pdf

Sección agregada el 2026-11-16 a las 20:01 -0500. **[I14]** No viene del fuente ESP-ACO (ver F-007).

"Swarm Colectivo ESP32 + RPi — Propuesta Técnica", junio de 2026, versión 2 (7 páginas, preparada
para evaluación por un experto en sistemas embebidos).
- **Base:** Holland & Melhuish (1999), **clustering y ordenamiento de objetos por estigmergia** (no
  caminos mínimos). Hardware: 4–6 ESP32 y 1 Raspberry Pi, sin motores ni sensores.
- **Arquitectura en 3 capas:**
  1. Enjambre de ESP32 que es a la vez **mundo virtual distribuido** (cada nodo guarda un fragmento
     de la grilla) y robots virtuales. Se comunican por ESP-NOW peer-to-peer, el azar sale de `esp_random()`
     y hay 6 mensajes en structs de C de ≤16 bytes.
  2. RPi como **"nido digital" pasivo**: une los fragmentos de mapa, monitorea métricas y lleva registro.
     "No dirige ningún agente".
  3. **Rescate OTA:** al agente rezagado se le entrega el mapa global acumulado como **condición
     inicial, no como oráculo** (inspirado en el *tandem running* de *Leptothorax*).
- **Hipótesis central:** el rescate reduce la varianza del tiempo de convergencia (H&M reportan que el
  peor caso fue más de 9 veces el mejor, Tabla 2, Exp. 5).
- **Cronograma tentativo:** de julio a diciembre de 2026, 26 semanas, 5 fases y 13 actividades
  (Fundación ESP-NOW S1–S4; Clustering S5–S10; Métrica y umbral S9–S14; Rescate OTA S13–S18;
  Análisis y documentación S19–S26).

---

## 8. Enfoque actual del operador: gemelo de software del plano

Registrado el 2026-11-16 20:04 -0500. Por ahora el operador se enfoca **solo en el software** (una especie de gemelo
digital) del [plano de ensayo](bosquejo/). Sus ideas, resumidas fielmente:

1. **Python con hilos:** una matriz con el mundo, agentes que perciben la cuadrícula y una madre que ve el mundo
   *a través de los agentes*. Hilos que generan feromona para los agentes cercanos; un protocolo que
   cada cierto tiempo envía información a la reina; actualización del mundo hacia los agentes
   (exploradoras con memoria limitada). Métricas: convergencia, conocimiento del mundo y logro del objetivo.
2. **Agentes y madre en Python + mundo en NetLogo**, con una interacción visible y un protocolo claro para
   el descubrimiento del mundo; después, comunicación agentes ↔ madre por MQTT.
3. **ESP32 (agentes) + RPi (madre).** Los "sensores" son solo las celdas que ven del mundo; el
   conocimiento se sincroniza a través de la madre.

Pide inspirarse en hormigas y abejas, con una "madre oráculo que ve todo pero con memoria limitada", y usar
inteligencia de enjambre.
