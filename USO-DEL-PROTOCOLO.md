# Uso del protocolo de trabajo con IA — caso 3: ACO-test

**Qué es este documento:** la evaluación del método de trabajo con IA (PACHE/HITL-KE, aquí en modo ingeniería,
según [`PROMPT-ZERO.md`](PROMPT-ZERO.md)) aplicado a este proyecto. Es el **tercer uso** del protocolo. Los dos
anteriores fueron simulaciones de análisis: el conflicto Irán–EE. UU. y la elección presidencial en Colombia.
**Este documento no los describe:** Claude no tiene acceso a esos trabajos. Al final hay una tabla para
compararlos, que completa el operador.

**Quién lo escribe:** Claude (Opus 5.5), la IA que trabajó en el proyecto, a pedido del operador (Tigarto),
el 2026-11-19. **Sesgo declarado:** la IA evalúa un método que la guió a ella misma; es parte interesada.
Por eso cada afirmación cita su evidencia en el repositorio (`F-###` = [`FAILURES.md`](FAILURES.md)).

**Datos del caso:** 4 sesiones, del 2026-11-16 al 2026-11-19 · 29 commits · 1 operador · 3 modelos de IA (Claude Fable
5.2, Claude Opus 5.5 y, fuera del método, Gemini) · 3 agentes de IA con roles fijos (revisor, experimentador,
divulgador) · 24 registros de falla (F-001 a F-024) · 314 pruebas automáticas del gemelo + 7 del oráculo · 41 de 49
criterios de los artefactos en PASA.

---

## 1. Qué permitió: cómo guió a la IA

| Pieza del protocolo | Cómo guió a la IA | Evidencia |
|---|---|---|
| **Un oráculo externo** (el notebook de `referencia/`, solo lectura) | La IA no decide si su código "está bien": lo decide la comparación con algo que no escribió ella | `oraculo/`, C1–C5 en `oraculo/RESULTADOS.md` |
| **Tolerancias y pruebas declaradas antes de correr** | Quita el margen para "ajustar hasta que pase" | `oraculo/TOLERANCIAS.md` se fechó antes del código (F-014); J1–J6 se declararon antes de implementar (F-015) |
| **Estados PASA / NO PASA / NO PROBADO, sin porcentajes a ojo** | Obliga a decir qué se comprobó y qué no. El único porcentaje es contable (criterios en PASA ÷ total) | `ARTEFACTOS.md` |
| **El fallo como evidencia** (`FAILURES.md`, nunca se borra) | Los errores de la IA quedan escritos con causa y corrección; no se pueden "olvidar" en la sesión siguiente | F-004, F-005, F-006, F-021 |
| **El repositorio como memoria** (`CLAUDE.md`, "Para retomar", historial con hora) | Cada sesión empieza donde terminó la anterior, aunque la IA no recuerde nada | Sesiones cortadas por límite de uso (2026-11-16, 2026-11-17 y 2026-11-18) se retomaron sin pérdida |
| **Una decisión a la vez, con opciones y recomendación** | La IA no cambia arquitectura ni método por su cuenta; el operador elige | `DECISIONES-PRUEBA.md` registra también las opciones descartadas |
| **Las intuiciones del operador etiquetadas** ("malicia indígena" = hipótesis, no requisito) y **un cuaderno sin filtro** (`IDEAS.md`) | La IA explora las intuiciones sin convertirlas en requisitos, y la verificación no filtra las ideas al entrar | La verificadora final (D3) nació de una intuición del operador; `IDEAS.md` |
| **Separar quien construye de quien verifica** (agente `revisor`, que no conoce el razonamiento) | Los defectos los encuentra alguien sin el sesgo de quien hizo el trabajo | F-023: 8 defectos con 281 pruebas en PASA |
| **Línea base antes de corregir** (agente `experimentador`) | Se puede afirmar con números qué cambió y qué no | F-024: los CSV publicados salieron idénticos byte a byte |

## 2. Qué evitó

1. **Sobreajustar al oráculo.** C3 (la rama corta gana con r = 2) no pasa. En vez de ajustar parámetros hasta lograrlo, la
   causa se investigó y se documentó con hipótesis escritas antes de correr (F-017), y el operador decidió dejarlo en
   NO PASA (J8).
2. **Conclusiones sin medir.** La IA afirmó tres veces que "el rescate no se dispara", deduciéndolo del resultado sin
   medir el mecanismo. El registro de fallas y la comparación con otro trabajo lo destaparon: la madre rescataba a la
   verificadora (F-020, F-021). Desde entonces se miden los mecanismos, no solo el resultado.
3. **Pruebas que no prueban.** Con mutantes (versiones del código a las que se les quita una mejora), el revisor mostró que
   3 de 4 pruebas nuevas pasaban aunque faltara lo que decían probar. Se corrigieron y ahora fallan con su mutante (F-024).
4. **Resultados que no se pueden repetir.** El motor con hilos daba resultados distintos con la misma semilla si había
   pérdidas o retardo (hasta 71 de 240 ensayos). Las pruebas no lo veían; el revisor sí (F-023). Corregido: 0 de 240 (F-024).
5. **Corregir sin saber qué se rompe.** Antes de cada corrección que cambia resultados se midió el "antes". Así se pudo
   afirmar que ninguna conclusión publicada cambió.
6. **Errores de entorno repetidos.** El intérprete equivocado (F-005) y la consola en cp1252 (F-002) quedaron escritos
   como reglas permanentes y no se repitieron.

## 3. Qué hubo de malo

### Fallas de la IA (registradas)

| Falla | Registro |
|---|---|
| Se saltó la apertura de sesión que el método exige y pasó directo a construir | F-004 |
| Verificó con el intérprete de Python equivocado y concluyó algo falso (que faltaba sympy) | F-005 |
| Escribió una hora estimada en el historial, sin consultar el reloj | F-006 |
| Hizo un inventario incompleto (no vio un archivo agregado) y revisó un cronograma sin haberlo leído | F-007 |
| Infirió un mecanismo a partir del resultado, sin medirlo, tres veces seguidas | F-021 |
| Entregó un bloque cuyas pruebas pasaban, pero con 8 defectos | F-023 |
| En la sesión 4 hizo una comparación estadística sin declarar las pruebas antes (quedó marcada como exploratoria) | F-024 |
| En la sesión 4 escribió una prueba con un valor esperado equivocado (cuadros de la animación) y la corrigió al ver el fallo | Sesión 2026-11-19 |

### Fallas del flujo humano–IA

1. **La aprobación del operador es el cuello de botella.** El operador declaró que recibe más información de la que puede
   procesar y "echa la bendición" (`ASSUMPTIONS.md`). Hay decisiones aprobadas sin revisión a fondo: las rondas A–G,
   I y J, el protocolo v0.3 y las ADR-001 y ADR-002. El "humano en el bucle" existe, pero con poco ancho de banda.
2. **Las aprobaciones de una palabra** ("Procede") permiten avanzar, pero no son verificación: verifican el revisor y las
   pruebas, no el operador.
3. **La memoria de los agentes era volátil.** El informe completo del revisor de F-023 se perdió al cerrar la sesión; solo
   quedó el resumen. En la sesión siguiente hubo que rehacerlo (desde el 2026-11-19 los informes se guardan en el repositorio).
4. **Excepciones al método por comodidad:** "una pregunta a la vez" se cambió por preguntas en bloque a pedido del operador.
   Ahorra tiempo, pero aumenta la carga de cada aprobación.

### Costos del método

- Cada corrección lleva prueba, prueba con mutante, línea base, documentación y revisión. Para un prototipo desechable
  es demasiado; para algo que va a hardware y a clase, el costo se justifica.
- Mucha documentación: 16 documentos Markdown en la raíz (contando este). Ayuda a la IA a retomar, pero satura al operador,
  que pidió respuestas ejecutivas.
- Los límites de uso de la IA cortaron 3 de las 4 sesiones a mitad de un bloque; el método amortiguó el corte, pero no lo evita.

## 4. Un contraste no planeado: el mismo trabajo sin el protocolo

El operador le dio a otra IA (Gemini, en la nube) el proyecto en el estado del artefacto 7. El análisis está en
[`otras/ANALISIS-gemini-artefacto9.md`](otras/ANALISIS-gemini-artefacto9.md). Gemini **no** siguió el método:

- Borró la documentación; 1 de sus 190 pruebas fallaba siempre; sus resultados no tenían el script que los produce.
- **Pero hizo algo mejor:** midió los mecanismos (cuántos rescates se envían y se usan), y eso destapó F-020, que el
  método no había atrapado. También comunicó mejor con informes y figuras.

Lectura: el protocolo protege la trazabilidad y la honestidad de las afirmaciones, pero no garantiza medir lo correcto.
No es un experimento controlado: distinto modelo, otro punto de partida y otras instrucciones.

## 5. Lo que este caso tiene distinto: un equipo de agentes de IA

**A diferencia de los casos 1 y 2, aquí se usaron agentes.** Los propuso la misma IA, cuando el operador preguntó cómo
mejorar el trabajo (2026-11-18, bloque A). Son tres, cada uno con un rol fijo escrito en `.claude/agents/`:

- **revisor:** verifica sin conocer el razonamiento de quien construyó; solo lee y ejecuta.
- **experimentador:** corre experimentos con las pruebas declaradas antes.
- **divulgador:** escribe para no especialistas. Lo agregó el operador.

La IA principal hace de orquestadora: reparte el trabajo, verifica lo que entregan y es la única que habla con el operador.
Ningún agente hace commit.

### Con agentes frente a sin agentes

| Aspecto | Sin agentes (una sola IA) | Con agentes | ¿Mejora o empeora? | Evidencia |
|---|---|---|---|---|
| Independencia de la verificación | La misma IA revisa lo que hizo, con el mismo sesgo y el mismo razonamiento a la vista | El revisor no conoce el razonamiento; parte de los criterios | **Mejora** | F-023: 8 defectos con 281 pruebas en PASA |
| Calidad de las pruebas | La IA escribe pruebas que confirman lo que cree | El revisor las ataca con mutantes | **Mejora** | 3 de 4 pruebas no detectaban su defecto (F-024) |
| Trabajo en paralelo | Una tarea a la vez | Revisor y experimentador trabajaron a la vez (≈ 25 min) mientras la orquestadora preparaba pruebas | **Mejora** el tiempo de reloj | Sesión 2026-11-19 |
| Contexto de la IA principal | Cada salida de herramienta se acumula en la conversación | Solo entra el informe final de cada agente | **Mejora**: la conversación principal crece menos | Diseño de la herramienta de agentes |
| Lectura repetida | Se lee el repositorio una vez | Cada agente arranca de cero y vuelve a leer reglas, registros y código | **Empeora** el gasto | Ver la estimación de tokens |
| Coordinación | No hace falta | Hay que evitar que una corrección cambie el código mientras otro agente mide | **Empeora** la complejidad | 2026-11-19: hubo que corregir en una copia aparte (*worktree*) para no contaminar la línea base |
| Memoria entre sesiones | La de la conversación, igual de volátil | Los informes se perdían al cerrar la sesión si no se guardaban | **Igual o peor** si no se guardan | F-023: se perdió el informe del revisor; se rehízo |
| Confianza en lo que entregan | — | Lo que entrega un agente es salida de un modelo: la orquestadora tiene que verificarlo | **Costo extra** de verificación | El experimentador corrigió un error de su propio script (falsas diferencias) |
| Disponibilidad | Siempre | Los agentes definidos en archivos se cargan solo al iniciar una sesión | **Limitación** de la herramienta | `CLAUDE.md`, "Equipo de agentes" |

### Gasto de tokens

**Lo medido** (sesión del 2026-11-19, según los totales que reporta la herramienta al terminar cada agente):

| Tarea de un agente | Tokens del agente | Llamadas a herramientas | Duración |
|---|---|---|---|
| Revisor: reproducir los 8 defectos de F-023 | ≈ 104 000 | 48 | ≈ 26 min |
| Experimentador: línea base antes de corregir | ≈ 58 000 | 28 | ≈ 23 min |
| Revisor: nueva revisión de B + C | ≈ 99 000 | 38 | ≈ 18 min |
| Revisor: confirmar el arreglo de N1 y N2 | ≈ 75 000 | 32 | ≈ 8 min |
| Experimentador: informes cortos por experimento (bloque D, D8) | ≈ 66 000 | 10 | ≈ 3 min |
| Revisor: revisar el bloque D | ≈ 129 000 | 52 | ≈ 10 min |
| Revisor: confirmar las correcciones del bloque D | ≈ 96 000 | 34 | ≈ 30 min |
| Revisor: revisión corta final del bloque D | ≈ 71 000 | 24 | ≈ 5 min |
| **Total medido** | **≈ 697 000** | **266** | |

**Lo que no se puede medir con lo disponible:** los tokens de la conversación principal, los de las sesiones anteriores y
un contrafactual real (hacer la misma tarea sin agentes y medirla). Por eso la comparación de gasto es una **estimación**:

- **Más gasto total, probablemente.** Cada agente vuelve a leer el contexto que la orquestadora ya tenía; en estas
  tareas, una parte importante de sus tokens fue releer reglas, registros y código.
- **Menos crecimiento de la conversación principal.** Si la orquestadora hubiera hecho esas 76 llamadas, sus salidas se
  habrían quedado en su contexto, y ese contexto se vuelve a procesar en cada turno siguiente. Con agentes, solo entran los
  informes (unos pocos miles de tokens cada uno). Este efecto compensa parte del gasto extra, pero no se puede afirmar que
  lo compense entero.
- **Conclusión sobre el gasto:** los agentes **no** se justifican por ahorro de tokens; no hay evidencia de ahorro. Se
  justifican por **calidad**: verificación independiente y defectos encontrados que la IA principal no vio. En este caso,
  8 defectos a cambio de ≈ 104 000 tokens del revisor, y en la segunda revisión (≈ 99 000) un defecto nuevo que
  la corrección había introducido y que la IA principal no vio: el azar del canal repetía el de las agentes (N1).
  En el bloque D, las dos pasadas del revisor (≈ 225 000 tokens) no encontraron fallas de código, sino **textos que
  afirmaban más de lo que el dato sostiene** (F-028): un tipo de error que ninguna prueba automática atrapa.
  El patrón se repitió en las correcciones: cada frase nueva de la IA principal para explicar un mecanismo volvió a
  fallar ante el revisor (tres pasadas). Lo que cerró el ciclo fue usar la redacción que propuso el propio revisor.

## 6. Ajustes propuestos al protocolo

1. **Aprobación del operador por riesgo:** detallada solo para lo que cambia resultados, arquitectura o método; lo demás,
   a criterio del equipo de agentes, con registro.
2. **Una sesión corta y periódica** solo para revisar lo aprobado "con bendición".
3. **Todo informe de un agente se guarda en el repositorio** antes de actuar sobre él.
4. **Medir mecanismos, no solo resultados**, como regla del método (lección de F-021 y de Gemini).
5. **Pruebas con mutante** para cada mejora: una prueba que no falla sin su mejora no cuenta.
6. **Declarar antes también las comparaciones rápidas**, aunque sean de una línea.

## 7. Límites de esta evaluación

- Un solo operador y un solo proyecto por caso; no se puede generalizar.
- La IA evalúa su propio trabajo bajo el método.
- El proyecto no ha llegado al hardware: falta saber si el método se sostiene cuando la verificación depende de
  mediciones físicas que reporta el operador (PROMPT-ZERO §6.4).

## 8. Comparación entre los tres usos (por completar)

| | Caso 1: conflicto Irán–EE. UU. | Caso 2: elección presidencial en Colombia | Caso 3: ACO-test |
|---|---|---|---|
| Modo del método | *(operador)* | *(operador)* | Ingeniería |
| Qué hace de oráculo o contraste | *(operador)* | *(operador)* | Notebook de referencia + revisor independiente |
| Cómo se registra la falla | *(operador)* | *(operador)* | `FAILURES.md` (24 registros) |
| Qué evitó, lo principal | *(operador)* | *(operador)* | Sobreajustar al oráculo; afirmar sin medir |
| Lo malo, lo principal | *(operador)* | *(operador)* | Ancho de banda del operador; memoria volátil de los agentes |
| Uso de agentes de IA | No | No | Sí: revisor, experimentador y divulgador, propuestos por la IA |
| Resultado verificable | *(operador)* | *(operador)* | 41/49 criterios en PASA; C1, C2, C4 y C5 PASA; C3 NO PASA documentado |
