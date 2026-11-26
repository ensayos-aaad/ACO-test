# El punto ciego

*Qué pasó el 25 de noviembre de 2026 (sesión 5), desde [«Repetir el azar, mirar por dentro»](03_repetir_el_azar.md):
un segundo modelo de inteligencia artificial entra al equipo como revisor externo y, en su primera revisión de un
cambio real, encuentra un error que el equipo había dado por bueno.*

## 1. La pregunta

Cada ojo humano tiene un punto ciego: el lugar donde el nervio óptico sale de la retina y no hay células que capten la
luz. No lo notamos. El cerebro rellena el hueco y el otro ojo, que mira desde una posición un poco distinta, cubre lo
que falta.

Hasta ahora, este proyecto miraba con un solo tipo de ojo. El código lo escribe un modelo de IA, Claude, en el papel de
orquestadora. Lo revisa el agente *revisor*, que no conoce el razonamiento de quien construyó, pero que es el mismo
modelo con otro papel. Ese revisor ha rendido: encontró ocho defectos con todas las pruebas en verde (texto 03). Pero
comparte con quien construye la manera de mirar.

La pregunta de este día fue: **¿ve algo distinto un ojo puesto en otro lugar?**

## 2. Un acuerdo entre dos máquinas

Ese otro ojo es **Gemini**, un modelo de IA de otra empresa. No es la primera vez que aparece en esta historia: su
trabajo por separado dio la pista del error del rescate (ver [«La colonia y la madre»](01_la_colonia_y_la_madre.md),
sección 5). Ahora entra al equipo con un papel fijo: **QA externo**, es decir, control de calidad. Audita el código y
las pruebas, y escribe pruebas propias. Trabaja desde un programa llamado Antigravity, sobre la misma carpeta del
proyecto.

Las reglas no las puso un solo lado. Según el registro, las negociaron las dos IA en dos vueltas. Gemini propuso.
Claude ajustó: que la orquestadora implemente y que el revisor no coordine, para que conserve su independencia. Gemini
aceptó con tres ajustes propios: un resumen de cinco líneas al comienzo de cada reporte, trabajar siempre sobre una
copia en una carpeta temporal y nombres fijos para sus pruebas. Claude agregó que cada reporte muestre el estado del
repositorio antes y después de la ronda. El operador humano aprobó el acuerdo ese mismo día (decisión ADR-004,
registrada a las 14:03).

Lo que quedó escrito:

- **QA solo lee.** Escribe únicamente sus reportes y sus pruebas, en una carpeta propia. No hace *commit* (no guarda
  cambios en el historial del proyecto).
- **Turnos.** Un archivo dice de quién es el turno: Desarrollo, QA u operador. Nadie modifica nada fuera de su turno, y
  **solo el operador cambia el turno**. Se parece a un apicultor con dos colmenas: las dos trabajan, pero solo él
  decide cuál abre y cuándo.
- **Un reporte de QA es un dato, no una orden.** Antes de corregir nada, el revisor reproduce cada hallazgo.
- **Cada ronda queda en su propio archivo**, guardado en el historial y sin borrarse. Tiene una razón: el 18 de
  noviembre se perdió un informe del revisor por no guardarlo (F-023).

## 3. Ronda 000: un ensayo en seco

Antes de revisar un cambio de verdad, se probó el relevo mismo. Gemini copió el proyecto a una carpeta temporal, corrió
las 318 pruebas del gemelo, las 7 del oráculo y una prueba mínima propia, y todas pasaron. Al comparar el estado del
repositorio antes y después, solo aparecían su reporte y su prueba, además del cambio de turno que había hecho el
operador. Veredicto: **PASA** (14:52).

## 4. Ronda 001: dos cabos sueltos

El primer cambio real cerraba las dos observaciones leves que el revisor había dejado abiertas el 19 de noviembre
(F-026, contadas en el texto 03).

**Un número negativo que se disfraza.** Todo el azar del gemelo sale de una *semilla*, un número que fija las tiradas
de dado de un ensayo. Python tiene un detalle: siembra su generador de azar con el valor absoluto del
número. `random.Random(-3)` da exactamente la misma secuencia que `random.Random(3)`. Así, la semilla −3 repetía en silencio el mundo de la 3: el mismo inicio, la misma meta y los mismos obstáculos, con otra etiqueta. Las decisiones de las agentes no se repetían, porque cada una mezcla la semilla con su número, pero el terreno sí. Como dos colmenas con números distintos en la tapa puestas en el mismo jardín, sin que nadie lo hubiera querido.

No afectaba a nada publicado: los experimentos usan las semillas 0 a 29, y la configuración por defecto, la 2026. La
corrección es simple: el gemelo rechaza cualquier semilla que no sea un entero mayor o igual que 0, en los dos puntos por
donde entra la semilla en el uso normal: al armar la configuración del ensayo y al crear el mundo. También rechaza 1,5, el texto "3" y el valor "verdadero".

**Repetir el azar en otro proceso.** El texto 03 contó cómo la red simulada aprendió a repetirse dentro de un mismo
programa en marcha. Pero los experimentos se reparten entre varios *procesos* (copias del programa que corren a la vez
en el computador), y algunas cosas de Python cambian de un proceso a otro. Por ejemplo, la función `hash()` aplicada a un
texto da un resultado que depende de un ajuste del proceso llamado `PYTHONHASHSEED`. Si alguien sembrara un dado con
eso, cada proceso tiraría dados distintos con la misma semilla.

El revisor ya había fabricado un *mutante* que hace justo eso (una copia del código con un defecto puesto a propósito:
siembra el dado de la red con `hash()` del texto, en vez de con el texto mismo). Con ese mutante pasaban las 127 pruebas de la red, el motor, la línea de comandos y los experimentos. La prueba nueva corre el mismo ensayo, con todo el azar encendido (mundo aleatorio, madre en modo difusión,
30 % de mensajes perdidos y retardos de 0 a 3 ticks), en tres procesos con `PYTHONHASHSEED` distinto (0, 1 y 12345).
Luego compara una *huella*, un resumen de todo el resultado, incluidas las posiciones tick a tick. Las tres deben ser
iguales. Con el mutante, el revisor vio tres huellas distintas: el mismo ensayo duró 56, 58 y 46 ticks según el proceso.
La prueba falla con el defecto, así que se sabe que mira.

El revisor dio **PASA** a esta entrega hacia las 15:08–15:15, y la entrega para QA quedó escrita a las 15:19.

## 5. Lo que nadie del equipo vio

A las 18:12 llegó el reporte de QA: **NO PASA**. De 11 puntos, 9 pasaban, uno no pasaba y uno quedó sin probar.

El hallazgo principal, H1, necesita una escena. El comando `run` del gemelo corre un ensayo. Tiene una opción,
`--semilla`, que reemplaza la semilla escrita en el archivo de configuración. QA escribió un archivo con una semilla
inválida, −3, y pidió correrlo con `--semilla 3` y con un dibujo del resultado (`--png`). El ensayo corrió completo con
la semilla 3 e imprimió su tabla de resultados. Y al final, una línea de código que volvía a armar la configuración para
leer el número de agentes lo hizo **sin** la semilla en uso: tomó el −3 del archivo, la validación nueva lo rechazó y el
programa terminó con error, sin dibujo. Antes de la ronda, el mismo comando terminaba bien y generaba la imagen.

Es como una obrera que hace el viaje completo con su etiqueta nueva y, al volver, la detienen en la entrada por una
etiqueta vieja que ya nadie usaba.

Eso es una **regresión**: algo que funcionaba y dejó de funcionar por un cambio. El cambio era de Claude. La revisión
interna había probado los casos por separado (una semilla inválida da error; `--semilla 3` funciona), pero no juntos. QA
los combinó. Había otra regresión de la misma familia (H3.2): un plan de experimentos con semillas válidas fallaba por la
semilla del archivo base, que ni siquiera se usaba.

QA encontró además defectos más viejos que la ronda (H2 y H3.1). Un plan de experimentos con `semillas: true` se
aceptaba como si dijera "la semilla 0", porque en Python el valor "verdadero" cuenta como el número 1: el plan corría y
escribía resultados como si nada. Con `1.5` o `false`, el programa se caía con un volcado de error en vez de un mensaje
claro. Y la carpeta de resultados se creaba antes de validar el plan. Por último (H4), un comentario de la prueba nueva
decía que la huella dejaba fuera el historial de posiciones; en realidad lo incluía.

QA no se limitó a describirlos: dejó cuatro pruebas que fallaban justo por H1 y H2, junto con otras 55 que pasaban.

## 6. Separar lo nuevo de lo viejo

El revisor reprodujo los cuatro hallazgos. QA había marcado H1 como regresión; el revisor terminó de separar el resto:
**H1 y H3.2 eran regresión de la ronda 001; H2 y H3.1 ya estaban en la versión anterior.** La diferencia importa. Una regresión habla del último cambio;
un defecto viejo habla de la historia del código.

El registro de fallas (F-029, 18:41) lo escribe sin rodeos: una regresión que introdujo Claude y que no vio el revisor.
Y deja una lección: al endurecer una validación, hay que buscar **todas** las llamadas que vuelven a armar el objeto
validado. La revisión interna miró los caminos de uso, pero no ese patrón.

La corrección, de la orquestadora: usar la semilla en uso en esas dos llamadas; validar las semillas del plan al leerlo
(un entero de 1 en adelante, o una lista no vacía de enteros desde 0, sin valores "verdadero" o "falso"); y validar todo
**antes** de crear la carpeta de resultados. Con 21 pruebas nuevas.

El revisor revisó la corrección y dio **PASA**, con tres observaciones leves que se atendieron antes de entregar. Una
de ellas tiene su ironía: el propio registro F-029 decía que el mensaje de error era "igual en todos los puntos de
entrada", y eso solo era cierto para una semilla inválida dentro de la lista. El registro de fallas también afirmaba de
más, como había advertido F-028. Se corrigió la frase. Otra observación: ninguna prueba vigilaba que se validara antes de
crear la carpeta (un mutante que la creaba primero pasaba); ahora una prueba lo vigila.

## 7. Ronda 002: PASA

A las 20:51, QA dio **PASA**: 9 puntos en PASA, ninguno en NO PASA y 2 sin probar. Atacó cinco grupos de casos borde,
entre ellos el comando `run` con los tres motores, planes con semillas repetidas o enormes (hasta 2⁶⁴), catorce planes
inválidos (en ninguno quedó carpeta ni archivo de resultados) y el comando de lotes con valores inválidos. El último grupo fue buscar en el código del repositorio (sin contar las pruebas ni la referencia) otros sitios que volvieran a armar una configuración sin la semilla en uso, el patrón de la regresión. No encontró ninguno. Agregó 27 pruebas.

Las cifras al cierre del día:

- **347 pruebas del gemelo y 7 del oráculo** en PASA.
- **87 pruebas de QA** en su propia carpeta. Entrarían a las pruebas del gemelo solo si el operador lo aprueba.
- Los **18 archivos de datos** de los experimentos publicados salieron **idénticos byte a byte** al repetirlos, en las dos
  rondas. Ninguna conclusión publicada cambió.

El operador aprobó guardar las rondas 001 y 002 en el historial del proyecto.

## 8. Lo que cuesta y lo que no se sabe

Nada de esto es gratis. Según la evaluación del método, cada ronda suma una revisión interna, un reporte de QA y una
reproducción del revisor. El operador copia a mano los mensajes entre las dos IA y cambia el turno a mano. Y **cuánto
gastó Gemini, en tokens (las unidades de texto que procesa un modelo), no se sabe**: no se registra en el repositorio.

¿Qué se puede concluir? Poco, y conviene decirlo. Fueron tres rondas y una de ellas fue un ensayo en seco. Lo que hay es
un dato, uno solo: un modelo distinto encontró una regresión que el mismo modelo, aun con un revisor independiente, había
dado por buena. Y el revisor aportó algo que el reporte de QA no traía completo: separar lo nuevo de lo viejo. En este caso, cada
verificación cubrió algo que la otra no cubrió. Si eso se repite, hay que verlo en las próximas rondas.

El segundo ojo también tiene su punto ciego, y QA lo declaró. Marcó como **NO PROBADO** que el ensayo se repita en otra
máquina, otro sistema operativo u otra versión de Python: todo se comprobó en un solo computador con Windows y Python
3.12.7.

## 9. Lo que viene

El siguiente paso es la **guía de reproducción** (artefacto 17), como ronda 003. Será la primera entrega que no es
código; no se sabe todavía si QA rinde igual con ella. Después vienen los registros y la demostración con NetLogo. Los
seis bloqueantes para el hardware siguen abiertos, y las preguntas científicas de los textos anteriores, por ejemplo si
la madre mejora de verdad la convergencia, siguen igual: este día no se midió nada nuevo sobre la colonia; los
experimentos publicados solo se repitieron para comprobar que salían idénticos.

## Lo que aprendimos

- Un cambio pequeño y correcto, como rechazar las semillas negativas, puede romper algo lejos de donde se hizo: dos
  llamadas que volvían a armar la configuración sin la semilla en uso. Al endurecer una regla, hay que buscar a todos los
  que la usan.
- En este caso, un modelo distinto encontró una regresión que el mismo modelo con su revisor había dado por buena, y el
  revisor terminó de separar lo nuevo de lo viejo. Es un caso, no una ley.
- Repetir el azar también exige vigilancia entre procesos. Ahora una prueba lo comprueba, y se sabe que mira porque el
  mutante la hace fallar. Ningún resultado publicado cambió.

## Lo que todavía no sabemos

- Si el QA externo rinde igual en más rondas o en entregas que no son código, y cuánto cuesta: el gasto de tokens de
  Gemini no se conoce, y tres rondas son pocas para concluir.
- Si los ensayos se repiten en otra máquina, otro sistema operativo u otra versión de Python: NO PROBADO.
- Por qué una corrida de las pruebas de QA en manos del revisor dio un tiempo de espera negativo (−4124 segundos). Al
  repetirla pasó; se sospecha una suspensión del equipo o un salto del reloj, pero la causa no se midió.

## Fuentes

- Acuerdo, roles, turnos y negociación: `DECISIONS.md` (ADR-004), `.handoff/README.md`, `.handoff/ESTADO.md`,
  `CLAUDE.md` (historial del 2026-11-25, 14:03), `README.md` ("Cómo se trabaja"), `USO-DEL-PROTOCOLO.md` §6.
- El revisor es el mismo modelo con otro papel: `.claude/agents/revisor.md` (`model: inherit`); `USO-DEL-PROTOCOLO.md`
  §6. Los ocho defectos: `FAILURES.md` (F-023). Gemini y el rescate: `FAILURES.md` (F-021).
- Informe perdido: `FAILURES.md` (F-023), `.handoff/README.md` ("Una ronda").
- Ronda 000: `.handoff/rondas/000-reporte_qa.md`; `.handoff/pruebas_qa/test_qa_000_humo.py`.
- Ronda 001: `.handoff/rondas/001-para_qa.md`, `.handoff/rondas/001-reporte_qa.md` (H1–H4, puntos 1–11),
  `gemelo/docs/informes/revision_r001.md`; `.handoff/pruebas_qa/test_qa_001_*.py`.
- Semillas negativas: `gemelo/aco_gemelo/motor/simulacion.py` (`ConfigEnsayo.__post_init__`),
  `gemelo/aco_gemelo/config.py` (`crear_mundo`), `gemelo/tests/test_reproducibilidad.py`; observación original en
  `FAILURES.md` (F-026).
- Reproducibilidad entre procesos: `gemelo/tests/test_reproducibilidad.py`,
  `gemelo/docs/informes/revision_F025/mut_hash.py`, `gemelo/docs/informes/revision_r001.md` (56, 58 y 46 ticks);
  experimentos en varios procesos: `ARTEFACTOS.md` (criterio 14).
- Regresión, reproducción y corrección: `FAILURES.md` (F-029), `.handoff/rondas/002-para_qa.md`,
  `gemelo/docs/informes/revision_r002.md` (O1–O3, tiempo de espera negativo).
- Ronda 002 y cifras: `.handoff/rondas/002-reporte_qa.md`, `CHANGELOG.md` (sesión 5), `ARTEFACTOS.md` (criterio 13),
  `CLAUDE.md` (historial del 2026-11-25, 21:02).
- Costo y límites: `USO-DEL-PROTOCOLO.md` §6.
- Lo que viene: `CLAUDE.md` ("Para retomar" e historial del 2026-11-25, 21:02), `ARTEFACTOS.md` ("Orden de trabajo
  vigente"), `ESTADO-PREHARDWARE.md` (B1–B6).
