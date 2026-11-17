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
| `PROTOCOLO.md`    | Borrador v0.1 de los mensajes del gemelo (campos, bits, frecuencias) |
| `DECISIONES-PRUEBA.md` | Preguntas de diseño con todas las opciones: ✅ elegida / ❌ descartada |
| `ARTEFACTOS.md`   | Los 17 artefactos de software (→ `gemelo/`), su estado, su avance y los requisitos de reproducción |
| `oraculo/`        | Reservada para el oráculo; solo README, sin código           |

**Sesión 0** (PROMPT-ZERO §9): pasos 1 y 2 hechos. Paso 3 (aprobar CONTEXT.md y hacer el
commit) a la espera del operador. Paso 4 (pregunta sobre la representación física) pendiente.
- Oráculos candidatos: `deneubourg_puente_doble.ipynb` [5], [7], [9] y `montecarlo_aco.ipynb` [4].
- Hay que decidir el valor del offset k: el notebook usa 20 y 5 en distintas celdas (I2).
- Python oficial: **Anaconda** (`C:\Users\Usuario\anaconda3\python.exe`). El `python` del PATH
  es otro (`C:\Python311`). Lo pendiente del entorno está en `CHECKLIST-ENTORNO.md`.
- Artefacto (§3) por definir: propósito, público, representación física, toolchain y presupuesto.
  Antecedente en la referencia: PlatformIO + `nodemcu-32s` + Wokwi (`simulaciones/ejemplo3`).

Criterios de aceptación C1–C6: todos **NO PROBADO** (son candidatos; el operador aún no los aprueba).

## Convenciones

- **Historial con marcas de tiempo**: cada vez que se actualice este archivo, añadir
  una entrada nueva al inicio de "Historial" con fecha, hora y zona horaria
  (`AAAA-MM-DD HH:MM -0500`) y un resumen breve de lo realizado o decidido.
- Mantener actualizada la sección "Estado actual" cuando cambie la estructura del proyecto.

## Historial

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
