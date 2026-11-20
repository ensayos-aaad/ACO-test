# Novedades: un equipo en el laboratorio

*Qué cambió desde [«La colonia y la madre»](01_la_colonia_y_la_madre.md) y qué viene.*

## 1. Un segundo par de ojos

Quien escribe una carta suele ser el último en ver sus erratas: lee lo que quiso decir, no lo que dijo. Con el código
pasa algo parecido. Durante dos días, el registro afirmó que el rescate de la madre no se disparaba. Lo concluyó el
mismo que la había programado, porque el resultado no cambiaba y sin contar los envíos: una falla de método (F-021).

Desde entonces trabaja un equipo de agentes de inteligencia artificial, cada uno con su papel escrito en un archivo:

- **Quien construye** (el orquestador) escribe el código, reparte los encargos y verifica lo que entregan los demás.
- **El revisor** comprueba cada cambio sin conocer el razonamiento de quien lo hizo: no confía en lo que diga el encargo,
  lo comprueba. Solo lee y ejecuta pruebas; no puede modificar nada.
- **El experimentador** corre los ensayos y escribe, con la hora, qué pruebas estadísticas aplicará antes de mirar los
  datos. Lo que se le ocurra después lo marca como exploratorio.
- **El divulgador**, autor de este texto, debe citar la fuente de cada afirmación.

Por encima hay un operador humano: decide si se sigue o se para, y ningún cambio entra al historial del proyecto (un
*commit*) sin su aprobación.

¿Por qué separar? Porque cada papel le quita a alguien una manera de engañarse. Quien no conoce el razonamiento no se
contagia de él. Quien declara la prueba antes no puede elegirla después según le convenga. Y quien no puede tocar el
código no puede "arreglar" un dato para que cuadre.

## 2. El error del rescate, cerrado

El defecto: la madre tomaba por rezagada a la **verificadora**, la agente que sale al final a comprobar el camino, y le
enviaba rescates que ella ignoraba (F-020). La corrección: la verificadora marca sus mensajes de estado con una bandera
y la madre deja de contarla. Además, cada ensayo ahora **cuenta sus mecanismos**: rescates enviados, usados y
descartados, reclutamientos y rutas heredadas.

Lo interesante es cómo se comprobó. El revisor volvió a introducir el defecto a propósito, sin modificar ningún archivo,
y las pruebas lo detectaron. Una prueba que nunca falla podría no estar mirando nada; esta demostró que mira. En 320
ensayos con mensajes perdidos, retardos y el motor de hilos, ningún rescate fue a la verificadora. Dio PASA con cuatro
observaciones, todas atendidas.

El experimentador repitió los 480 ensayos de los modos de la madre, con sus preguntas escritas antes de correr (18 de
noviembre, 22:59). Las respuestas:

- **Ningún rescate** llegó a la verificadora en los 480 ensayos.
- **Ningún resultado de convergencia ni de tiempo cambió**: las 480 filas salieron idénticas. Esos rescates se
  ignoraban; quitarlos no movió nada.
- **Cambió la explicación.** Con umbral 0,5 el rescate solo llegaba a la verificadora; ahora no se envía ninguno y ese
  modo equivale a la madre ausente. Con umbral 0,8 o mayor, la madre envía entre 79 y 129 rescates por cada 30 ensayos
  a rezagadas reales; se usan entre el 71 % y el 83 %, y el resto llega tarde (la agente ya había llegado a la meta).
- **Las conclusiones previas se sostienen.** La mejora en el mundo aleatorio (27 de 30 frente a 18 de 30) sigue sin ser
  significativa tras corregir por comparaciones múltiples (p = 0,09), y el rescate no reduce la variación del tiempo
  (p corregido = 1,00).

Los registros viejos no se borraron: llevan una nota de corrección ("se disparaba hacia la verificadora"). Hoy hay 264
pruebas del gemelo en PASA. *(Al 20 de noviembre son 318.)*

## 3. Lo que viene

> **Actualización (2026-11-20).** Esta sección quedó vieja. Los bloques B + C (motor y métricas) y D (notebook más
> explicable) ya se hicieron. B + C pasó la revisión después de dos NO PASA. En D, lo técnico pasó desde la primera
> revisión y los tres NO PASA fueron por textos; la última corrección usó la redacción del revisor y, por decisión del
> operador, no tuvo una cuarta pasada. Las dos figuras que aquí "no existen todavía" ya existen: los fotogramas del
> mapa de la madre y los mapas de feromona con trazos. El orden que sigue lo aprobó el operador el 18 de noviembre a
> las 23:46, pero aquí no quedó escrito completo: primero la guía de reproducción, luego los registros y después la
> demostración con NetLogo. Todo eso se cuenta en [«Repetir el azar, mirar por dentro»](03_repetir_el_azar.md). Lo de
> abajo se deja como estaba escrito el 18 de noviembre.

Hay un plan por bloques. El primero, corregir el rescate, está hecho; los demás esperan la decisión del operador. Sigue
mejorar el motor y medir más, entre otras cosas lo que la madre sabe del mundo en cada instante.

La madre no ve el mundo: solo sabe lo que las agentes le cuentan en sus fragmentos de mapa. El plan propone
**fotogramas de su conocimiento**: de 6 a 8 cuadros que muestren, junto al mundo real, qué celdas conoce y cuáles cree
obstáculo, y cómo ese mapa interior se va llenando.
La otra figura son **mapas de color de la feromona** con los trazos de las exploradoras, la ruta de la verificadora y la
ruta óptima, sin madre y con madre, en el mismo mundo y con la misma semilla. **Ninguna de las dos existe todavía.**

Después viene la demostración con NetLogo, un programa para simular agentes: el mundo en NetLogo y las agentes en
Python, hablándose por el protocolo. Los mensajes saldrán por primera vez de la memoria de un solo programa.

El hardware (ESP32 y Raspberry Pi) tiene seis bloqueantes: protocolo sin aprobar; transporte sin decidir entre MQTT y
ESP-NOW (la Raspberry Pi no habla ESP-NOW, y en JSON la percepción no cabe en un paquete de ESP-NOW); lenguaje,
MicroPython o C++; inventario de piezas sin verificar; cuántos niveles de feromona distingue una agente; y la
demostración con NetLogo.

## Lo que aprendimos

- Separar a quien construye de quien revisa y de quien experimenta le quita al equipo maneras de engañarse.
- Una prueba gana confianza cuando se la ve fallar: con el defecto de vuelta, las pruebas lo detectaron.
- Un defecto puede no cambiar ningún resultado y aun así cambiar la explicación. Por eso ahora los mecanismos se cuentan.

## Lo que todavía no sabemos

- Si la madre mejora de verdad la convergencia: falta un experimento confirmatorio, con unas 100 semillas por condición.
- Cómo afectan a la convergencia la pérdida y el retardo de mensajes de una radio real: no se ha medido. *(Al 20 de noviembre sigue sin medirse. Los ensayos con pérdidas y retardo simulados que existen, los de este texto y los del texto 03, se hicieron para comprobar otras cosas —que el rescate no va a la verificadora y que los resultados se repiten—, no para medir ese efecto.)*
- Si lo que funciona en el gemelo funcionará en los micros: antes hay que cerrar los seis bloqueantes.

## Fuentes

- Equipo y roles: `.claude/agents/revisor.md`, `.claude/agents/experimentador.md`, `.claude/agents/divulgador.md`;
  `CLAUDE.md` (reglas, "Para retomar" e historial del 2026-11-18).
- Falla de método: `FAILURES.md` (F-021).
- Defecto, corrección y verificación: `FAILURES.md` (F-020, F-022), `PLAN-MEJORAS.md` (A1–A3, C4).
- Repetición de los 480 ensayos: `gemelo/docs/informes/rescate_tras_F020.md`.
- Plan: `PLAN-MEJORAS.md` (bloques B–E, en especial C3, D2 y D3).
- Actualizaciones del 2026-11-20: `FAILURES.md` (F-024 a F-028), `gemelo/docs/informes/rescate_tras_F020.md` (tabla de
  mecanismos: 71,1 % a 83,2 % usados), `gemelo/docs/informes/experimento_rescate.md`,
  `gemelo/docs/informes/experimento_reproducibilidad_canal.md`, `CLAUDE.md` ("Para retomar": 318 pruebas, orden de trabajo).
- NetLogo y hardware: `ESTADO-PREHARDWARE.md` (artefacto 16, bloqueantes B1–B6, exploraciones X1 y X2); `CLAUDE.md`
  ("Abierto o pendiente": JSON y ESP-NOW).
