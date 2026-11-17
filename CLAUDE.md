# ACO-test — instrucciones permanentes

Este proyecto se trabaja bajo el método definido en @PROMPT-ZERO.md. Léelo completo al
iniciar cada sesión y síguelo.

Reglas que no se negocian:
- referencia/ es SOLO LECTURA. Nunca la modifiques.
- Una pregunta a la vez; ningún cambio de arquitectura sin aprobación explícita del operador.
- Ningún commit sin que el operador lo apruebe.
- Estados de requisitos: PASA / NO PASA / NO PROBADO. Sin porcentajes de avance "a ojo": el único porcentaje permitido es el de `ARTEFACTOS.md` (criterios en PASA ÷ total).
- El operador declaró sobrecarga de información (ASSUMPTIONS): respuestas ejecutivas, el detalle en los archivos.

## Descripción del proyecto

**ACO-test**: implementación de ESP-ACO en ESP32 (modelo del puente doble de
Deneubourg et al., *Ant Colony Optimization*, Dorigo & Stützle, cap. 1) bajo el método
PACHE/HITL-KE en modo ingeniería. El notebook de Jupyter de `referencia/` es el oráculo:
el firmware es correcto solo si reproduce el notebook dentro de tolerancias declaradas
de antemano.

- Repositorio de trabajo: `ensayos-aaad/ACO-test` (rama `main`).
- Repositorio fuente (solo lectura): `UdeA-IoT/ESP-ACO`, a copiar en `referencia/`.
- Licencia: GNU GPL v3 (ver [LICENSE](LICENSE)).
- Operador y responsable de las decisiones: Tigarto.

## Estado actual

| Archivo / carpeta | Contenido                                                    |
|-------------------|--------------------------------------------------------------|
| `README.md`       | Portada: insignias de IA (Claude Opus 5.5), fases, mapa de documentos, uso de IA |
| `LICENSE`         | GPL v3                                                       |
| `CLAUDE.md`       | Este archivo: reglas permanentes, contexto e historial       |
| `PROMPT-ZERO.md`  | Método de trabajo, criterios C1–C6 y tarea de la Sesión 0    |
| `referencia/`     | Copia de solo lectura de `UdeA-IoT/ESP-ACO` @ `3c48648` (ver `PROCEDENCIA.md`) |
| `CONTEXT.md`      | Inventario de la referencia, parámetros, oráculos, vacíos (I1–I13), NetLogo/hormigas (§5), agentes AIMA (§6) |
| `DECISIONS.md`    | Decisiones en formato ADR (ADR-001, ADR-002: propuestas)     |
| `FAILURES.md`     | Registro de fallas (F-001 a F-006); nunca se borra           |
| `ASSUMPTIONS.md`  | Suposiciones y sesgos declarados (A-001 a A-004)             |
| `CHANGELOG.md`    | Cambios por sesión                                           |
| `CHECKLIST-ENTORNO.md` | Software necesario: instalado `[x]` / falta `[ ]`       |
| `PROTOCOLO.md`    | Borrador v0.2 de los mensajes del gemelo (campos, bits, frecuencias) |
| `DECISIONES-PRUEBA.md` | Preguntas de diseño con todas las opciones: ✅ elegida / ❌ descartada |
| `ARTEFACTOS.md`   | Los 17 artefactos de software (→ `gemelo/`), su estado, su avance y los requisitos de reproducción |
| `oraculo/`        | Reservada para el oráculo; solo README, sin código           |
| `gemelo/`         | **El código**: `aco_gemelo/` (mundo, protocolo, canal, agente, madre, motor), `tests/`, `environment.yml` |
| `bosquejo/`       | Plano de ensayo (a mano y en limpio)                         |

## Para retomar (estado al 2026-11-17 02:45 -0500)

**Dónde quedamos:** fase 1 del gemelo en construcción. Hechos los artefactos
**1 (entorno), 3 (protocolo), 4 (mundo), 5 (canal), 6 (agente), 7 (madre), 8 (motor), 9 (configuración y
línea de comandos), 10 (métricas) y 11 (visualización)**: 241 pruebas en PASA.
El detalle y el avance de los 17 artefactos están en `ARTEFACTOS.md`.

**Cómo comprobar que todo sigue bien** (desde `gemelo/`):
`C:/Users/Usuario/anaconda3/envs/aco-gemelo/python.exe -I -X utf8 -m pytest -q -W ignore`
(si el entorno no existe: `conda env create -f gemelo/environment.yml`).

**Cómo correr un ensayo** (desde `gemelo/`, con el Python de `aco-gemelo`):
`python -X utf8 -m aco_gemelo run --config configs/default.yaml [--semilla N] [--motor hilos]` y
`python -X utf8 -m aco_gemelo batch --config configs/default.yaml --semillas 30` (deja un CSV en `resultados/`,
que git ignora).

**Siguiente paso: artefacto 12, oráculo del puente doble** (`oraculo/`): reproducir, a partir de los notebooks de
`referencia/` (sin modificarlos, citando archivo y celda), p1 (deneubourg [5]), la dinámica (deneubourg [7]) y el
histograma de r = 1 y r = 2 (montecarlo_aco [4]), con tolerancias declaradas **antes** de correr. Ojo con F-012:
con el ciclo de vida de un solo depósito, la colonia del gemelo no prefiere la rama corta; C2 y C3 probablemente
den NO PASA y eso es un resultado válido.

**Ver un ensayo:** `python -X utf8 -m aco_gemelo run --config configs/default.yaml --png final.png --animacion ensayo.gif`.

**Problemas abiertos que dejó la madre (F-010):**
- La verificadora falla en ~1 de cada 4 semillas con cualquier modo (rastros cruzados + no puede volver
  sobre sus pasos, I12). Es el principal obstáculo para el criterio de convergencia G1.
- El modo rescate no llega a dispararse con el umbral del 50 % (I14): la hipótesis de `resumen.pdf`
  sigue sin probarse.
- Sin implementar: `BALIZA`, `ALERTA`, `SIGUEME` (comunicación entre agentes, E1) y `STOP`.
- `gemelo/tests/apoyo.py` (banco provisional) se conserva para las pruebas unitarias; el motor da los mismos tiempos.

**Después:**
11 visualización → 12 oráculo → 14 experimentos → 15 notebook → 16 demostración NetLogo → 17 guía de reproducción.

**Pendiente de revisión por el operador** (aprobado "con bendición", ver ASSUMPTIONS.md):
- `DECISIONES-PRUEBA.md`: ronda 1 (A–G) y ronda 2 (I1–I15, valores elegidos por Claude).
  El cambio de fondo es I4/I5: el depósito es a la vuelta, no a la ida.
- `PROTOCOLO.md` v0.2: sigue sin aprobación formal.
- Se hicieron JSON y binario a la vez (desviación de B2).
- ADR-001 y ADR-002 siguen como propuestas.

**Forma de trabajo acordada:** un artefacto a la vez; al terminar cada uno, Claude da la seña y el
operador decide si se sigue o se para. No se hace commit sin su aprobación. Respuestas ejecutivas.
El modelo en uso se anota en los commits (los artefactos 1 y 3–6 son de Claude Fable 5.2).

Criterios de PROMPT-ZERO: **C1 PASA** a nivel del programa de agente (prueba en
`gemelo/tests/test_agente.py`); C2–C6 **NO PROBADO**.

## Convenciones

- **Historial con marcas de tiempo**: cada vez que se actualice este archivo, añadir
  una entrada nueva al inicio de "Historial" con fecha, hora y zona horaria
  (`AAAA-MM-DD HH:MM -0500`) y un resumen breve de lo realizado o decidido.
- Mantener actualizada la sección "Estado actual" cuando cambie la estructura del proyecto.

## Historial

### 2026-11-17 03:10 -0500
- Artefacto 10 sincronizado (`1121178`).
- **Artefacto 11 hecho** (Claude Opus 5.5): `gemelo/aco_gemelo/visual/` con `png_final` y `animar` (GIF con Pillow, MP4 con ffmpeg), en el estilo del plano: obstáculos sombreados, I rojo, F morado, agentes como pastillas verdes con su número, verificadora ámbar, feromona verde y la madre azul arriba con su enlace (no aparece en modo ausente). El motor ahora guarda la feromona por tick y la ruta de la verificadora. Opciones nuevas en `run`: `--png`, `--animacion`, `--fps`. 11 pruebas nuevas en PASA (241 en total). Ejemplo en `gemelo/docs/imagenes/`.
- `.gitattributes`: GIF y MP4 como binarios. Sin commit todavía.

### 2026-11-17 03:02 -0500
- Artefacto 9 sincronizado (`b7d3fb9`). **Cambio de modelo a Claude Opus 5.5** por decisión del operador; el código del artefacto 10 lo escribió Fable 5.2 y lo cerró Opus 5.5.
- **Artefacto 10 hecho:** `gemelo/aco_gemelo/metricas/` (fila por ensayo, conocimiento del mundo de la madre, resumen de lote con IC de Wilson); el `Resultado` gana `modo_madre`, `conocimiento` y `serie` (métricas tick a tick); `batch` imprime el resumen con intervalos. 15 pruebas nuevas en PASA (230 en total).
- **F-013:** la madre (pista de baile o difusión) baja la varianza del tiempo de convergencia a menos de un tercio; el rescate sigue sin dispararse; con 30 semillas las tasas de verificación no se distinguen entre modos.
- Sin commit todavía.

### 2026-11-17 02:55 -0500
- Artefacto 8 sincronizado (`a29641c`).
- **Artefacto 9 hecho** (Claude Fable 5.2): `gemelo/aco_gemelo/config.py` (YAML → mundo y `ConfigEnsayo`; clave desconocida = error), `gemelo/aco_gemelo/__main__.py` (`run` y `batch`, con CSV) y tres configuraciones comentadas en `gemelo/configs/`. 28 pruebas nuevas en PASA (215 en total).
- **F-012:** primera medición con obstáculos aleatorios (se asientan 30/30; verificadas 20/30). En el puente doble la verificadora acaba en la rama larga la mitad de las veces: con un solo depósito por agente la colonia no llega a preferir la rama corta.
- Sin commit todavía.

### 2026-11-17 02:49 -0500
- **Artefacto 8 hecho** (Claude Fable 5.2): `gemelo/aco_gemelo/motor/` con `Simulacion` (fases colonia → verificadora → cierre con `FIN`), `ActorMundo`, `ConfigEnsayo` y `Resultado`. Motor determinista y motor de hilos (un hilo por agente y otro para la madre; el mundo espera la acción de cada agente, como en el ejemplo 5 de la referencia). 17 pruebas nuevas en PASA (187 en total); las de hilos, estables en 3 repeticiones.
- Sin madre, el motor de hilos da exactamente el mismo resultado que el determinista. Con madre, los tiempos pueden variar entre corridas con hilos; por eso los experimentos usan el determinista.
- El motor reproduce los tiempos del banco con el que se midieron F-009 y F-010. Sin commit todavía.

### 2026-11-17 02:45 -0500
- Se retoma tras el corte por límite de la sesión anterior. Estado verificado: el artefacto 7 estaba sin commit y del artefacto 8 (motor) **no quedó nada en disco**; 170 pruebas en PASA. Se sincroniza el artefacto 7 (aprobado por el operador antes del corte).
- Pregunta del operador: ¿los obstáculos pueden ser aleatorios siempre que haya camino entre inicio y fin? Sí, ya está: `mundo_aleatorio` (artefacto 4) regenera el mundo hasta que el BFS encuentra camino. Falta usarlo en las corridas (hasta ahora solo se midió en el mundo L) y aplicarle la distancia mínima I13.

### 2026-11-16 21:27 -0500
- **Artefacto 7 hecho** (Claude Fable 5.2): `gemelo/aco_gemelo/madre/` (4 modos, actúa cada Δt, memoria con presupuesto en bytes que olvida primero las rutas largas, detección de rezagadas, registro del resultado de la verificadora). El agente ahora informa su mapa (`FRAGMENTO`), se deja reclutar (`RECLUTA` → `PIDE_RUTA` → `RUTA`), hereda rutas (también de rescate) y explora lo que la colonia no conoce (`MAPA`). 33 pruebas nuevas en PASA (170 en total).
- **F-010:** la pista de baile y la difusión bajan el tiempo (110 → 73 y 59 ticks), su dispersión y el largo de la ruta (1,96 → 1,34 veces la óptima). El rescate no se dispara. La verificadora sigue fallando en ~1 de cada 4 semillas.
- **F-011:** defecto corregido en la memoria de la madre (pedidos sin límite).
- Sin commit todavía.

### 2026-11-16 21:11 -0500
- Cierre de sesión por límite del plan: se agrega la sección **"Para retomar"** con el estado, el siguiente paso (artefacto 7) y lo pendiente de revisión. Artefacto 6 sincronizado.

### 2026-11-16 21:10 -0500
- **Artefacto 6 hecho** (Claude Fable 5.2): `gemelo/aco_gemelo/agente/` (programa de agente con `paso()` no bloqueante; ciclo IDA → DANZA → VOLVIENDO con depósito → SIGUIENDO → ASENTADA; memoria K con ruta sin bucles; rol por umbral; verificadora). El mundo ganó `percibir()` y `aplicar_accion()`. 25 pruebas nuevas en PASA (137 en total). `tests/apoyo.py` es un banco de pruebas provisional que hace de mundo hasta que exista el motor (artefacto 8).
- **C1 en PASA** a nivel del programa de agente: la regla de decisión reproduce la fórmula 1.1 de Deneubourg en el puente doble.
- **Hallazgo F-009 (línea base sin madre):** las agentes siempre se asientan, pero la verificadora solo llega en el 60–80 % de las semillas y con rutas 1,7–2 veces más largas que la óptima. No se ajustó; es lo que deben mejorar los modos de la madre.
- Sin commit todavía. Siguiente: artefacto 7 (madre).

### 2026-11-16 21:03 -0500
- Artefacto 5 sincronizado (`44d9deb`).
- El operador vuelve a "echar la bendición" y delega los parámetros: **ronda 2 en DECISIONES-PRUEBA.md, sección I** (I1–I15), con el respaldo de cada valor (literatura, literatura de memoria o suposición).
- Cambio de fondo: **el depósito de feromona es a la vuelta, sin bucles (S-ACO), no a la ida** (I4), y D3 se ajusta (I5): llegar → DANZA → volver al nido depositando → ir de nuevo a la meta y quedarse → verificadora.
- Con esto el artefacto 6 (agente) ya no está bloqueado.

### 2026-11-16 21:00 -0500
- **Artefacto 5 hecho** (Claude Fable 5.2): `gemelo/aco_gemelo/canal/` con la interfaz `Canal` (lista para una versión MQTT) y `CanalMemoria`: difusión por radio r (distancia de 8 vecinos), destino directo o difusión general, retardo y pérdida con semilla, mensajes que viajan serializados (binario o JSON) y contadores de tráfico por familia. 18 pruebas en PASA (112 en total).
- Límites declarados: la familia 0 (sensor/actuador) no se pierde ni se retrasa; los mensajes con `FLAG_ACK` se entregan siempre, pero el tráfico de las confirmaciones no se cuenta todavía.
- Hechos: artefactos 1, 3, 4 y 5. Siguiente: 6 (agente), que necesita cerrar antes H1, H2, H5 y los parámetros numéricos (α, ρ, τ0, depósito, K, umbral de rol).

### 2026-11-16 20:58 -0500
- **Artefacto 3 hecho** (Claude Fable 5.2): `gemelo/aco_gemelo/protocolo/` con los 16 mensajes declarados una sola vez (`MENSAJES`) y los codificadores JSON y binario derivados de esa tabla. 74 pruebas en PASA (94 en total).
- `PROTOCOLO.md` pasa a **v0.2**: 8 vecinos, verificadora (H4 resuelto), `SIGUEME` con `n`, orden de bits MSB primero. Sigue sin la aprobación del operador.
- Desviación de B2: se hicieron JSON **y** binario a la vez, porque al declarar los campos una sola vez el binario salía casi gratis y garantiza la equivalencia. A confirmar por el operador.

### 2026-11-16 20:54 -0500
- **Artefacto 4 hecho** (Claude Fable 5.2): `gemelo/aco_gemelo/mundo/` con `Mundo` (8 vecinos sin cortar esquinas, BFS, feromona por celda con saturación y q4) y los escenarios `mundo_l`, `mundo_aleatorio` y `puente_doble(r, ancho)`. 18 pruebas en PASA (20 con las del entorno).
- Punto abierto nuevo, H5: inicio y meta al azar pueden quedar casi pegados (ensayo trivial).
- Ejecutar las pruebas: desde `gemelo/`, `<python de aco-gemelo> -m pytest -q`. Sin commit todavía.

### 2026-11-16 20:50 -0500
- **Artefacto 1 hecho** (modelo: Claude Fable 5.2): `gemelo/environment.yml` + entorno conda `aco-gemelo` + `gemelo/tests/test_entorno.py` (2 pruebas en PASA). sympy quedó en 1.13.2 (F-008). El código del gemelo se ejecuta con `C:/Users/Usuario/anaconda3/envs/aco-gemelo/python.exe`.
- Siguiente: artefacto 4 (mundo + BFS + escenarios). Sin commit todavía.

### 2026-11-16 20:31 -0500
- `README.md` raíz actualizado: insignia "Built with AI" (la misma de la referencia) + insignia del modelo **Claude Opus 5.5**, estado por fases, mapa de documentos y una sección de uso de IA.

### 2026-11-16 20:29 -0500
- Sesgo declarado por el operador: **recibe más información de la que puede procesar y "echa la bendición"**. Se registra en ASSUMPTIONS; las decisiones de la ronda 1 quedan como aprobadas con carga alta. Desde ahora, respuestas ejecutivas.
- Se crea `ARTEFACTOS.md`: 17 artefactos con directorio, estado y avance objetivo, más los requisitos de una guía de reproducción **autocontenida** que incorpora los experimentos previos de la referencia.
- Sincronización con GitHub aprobada por el operador ("Sincroniza").

### 2026-11-16 20:25 -0500
- A pedido del operador, las preguntas se hacen **por bloques** (excepción a "una pregunta a la vez") y se registran en `DECISIONES-PRUEBA.md` **con todas las opciones**, incluidas las descartadas.
- Ronda 1 respondida (A–G). Claves: el gemelo **extiende** PROMPT-ZERO (ADR-003); meta = fase 1 + demostración con NetLogo; agente = paso de ciclo no bloqueante (1 hilo = 1 micro, más un planificador determinista); 8 vecinos sin cortar esquinas; 6 agentes; Ant System con η = 1; feromona q4 en las celdas + balizas; al llegar a la meta: DANZA → la madre recluta → **verificadora final** (D3, idea del operador); madre con 4 modos y memoria en bytes; 30 semillas.
- Quedan abiertos: H1–H4 (límite de pasos, empates de la verificadora, depósito a la ida, protocolo de la verificadora).

### 2026-11-16 20:09 -0500
- Se crea `PROTOCOLO.md` (borrador v0.1, sin aprobar): 4 familias (Mundo↔Agente, Agente↔Agente feromónicos, Agente→Madre, Madre→Agente) y 16 mensajes con campos, bits y frecuencias. JSON y binario llevan la misma información cuantizada; los mensajes feromónicos ocupan 5–6 B.

### 2026-11-16 20:04 -0500
- El operador fija el foco: gemelo de software del plano en 3 fases (Python, Python + NetLogo + MQTT, ESP32 + RPi). Ideas registradas en CONTEXT §8; análisis en curso.

### 2026-11-16 20:01 -0500
- Se lee `referencia/resumen.pdf` (agregado por el operador; no viene del fuente; F-007 y CONTEXT §7):
  enjambre de ESP32 + RPi basado en Holland & Melhuish, con rescate OTA y un cronograma de julio a diciembre de 2026.
- Revisión del cronograma: a la semana S20, el plan prevé las fases 1 a 4 terminadas, pero no hay
  nada implementado. Quedan unas 6 semanas.

### 2026-11-16 19:46 -0500
- Se crea `CHECKLIST-ENTORNO.md` con el software necesario, verificado por comandos y sin
  instalar nada.
- Falta: extensión Wokwi; ipywidgets 7.8.1 es incompatible con Notebook 7 y JupyterLab 4; el
  PATH apunta a `C:\Python311` en vez de Anaconda; elegir la toolchain y el entorno conda; probar
  NetLogo `py` y el par COM1 ↔ COM2; `gh` es opcional.
- F-005: la verificación anterior de Python usó el intérprete equivocado; sympy **sí** está en
  Anaconda (1.13.1). F-006: se corrige la hora estimada de la entrada anterior.

### 2026-11-16 19:45 -0500 (hora corregida, ver F-006)
- Se registra en FAILURES la omisión de la apertura de sesión (F-004) y se presenta el resumen
  de 5 líneas.
- `CONTEXT.md` §5: hormigas y NetLogo. La referencia no tiene ningún modelo NetLogo de hormigas
  (I11) y no se encontró uno público del puente doble (I12). Ejemplos externos: Ants de
  Wilensky (licencia CC BY-NC-SA, incompatible con GPL, R1), Ant Adaptation y ACO para TSP.
- `CONTEXT.md` §6: agentes según AIMA cap. 2 (en la referencia hay diapositivas, no el libro) y
  la hormiga vista como agente reactivo aleatorizado con estigmergia (A-003, sin aprobar).
- Sigue sin commit, a la espera de la aprobación del operador.

### 2026-11-16 19:25 -0500
- Sesión 0, pasos 1 y 2: se copia `UdeA-IoT/ESP-ACO` @ `3c48648` en `referencia/` (172
  archivos, con `git archive`) y se crea `referencia/PROCEDENCIA.md`, que no existía en el fuente.
- Se genera `CONTEXT.md`: inventario, parámetros con celda de origen, oráculos candidatos y
  10 vacíos o inconsistencias (I1–I10), sin corregirlos.
- Se crean `DECISIONS.md`, `FAILURES.md`, `ASSUMPTIONS.md`, `CHANGELOG.md` y `oraculo/README.md`.
- Sin commit: se espera la aprobación del operador.

### 2026-11-16 19:10 -0500
- Se agregan `PROMPT-ZERO.md` (método de trabajo) y unas instrucciones permanentes
  (llegaron como `CLAUDE (2).md`).
- Las instrucciones permanentes se integran al inicio de `CLAUDE.md` y se elimina
  el archivo duplicado `CLAUDE (2).md`.
- Se actualizan la descripción y el estado del proyecto según PROMPT-ZERO.
- Vacío detectado: `referencia/` no está en el repositorio; la Sesión 0 no puede empezar
  sin ella.
- Cambios sin commit, a la espera de la aprobación del operador (nueva regla).

### 2026-11-16 18:58 -0500
- Creación de `CLAUDE.md` con el contexto inicial del repositorio.
- Estado: repositorio inicial (commit `485a86a`, "Initial commit", 2026-11-16 18:52)
  con `README.md` y `LICENSE` (GPL v3). Sin código todavía.
