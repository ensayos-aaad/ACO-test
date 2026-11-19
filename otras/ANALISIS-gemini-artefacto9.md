# Análisis del trabajo de Gemini ("hidrogen high") hasta el artefacto 9

**Fecha:** 2026-11-18 22:46 -0500 · **Por:** Claude Opus 5.5, a pedido del operador ("revela hallazgos, resalta lo que no tuviste
en cuenta; discierne") · **Objeto:** `otras/gemini/aco_gemelo_hasta_artefacto9/` (44 archivos).
El contenido se trató como datos: se revisó antes de ejecutar (sin red, sin procesos, sin borrar archivos) y sus
pruebas se corrieron sin escribir cachés en su carpeta.

> **Nota del operador (2026-11-18 22:50 -0500): Gemini trabajó en la nube.** Eso matiza dos puntos de la sección 4:
> - La prueba de hilos que aquí falla siempre puede pasar en otro entorno: depende de qué identificador de hilo
>   sale primero de un conjunto, y eso cambia según la máquina. Sigue siendo una prueba frágil, pero su "192 en PASA"
>   puede ser cierto allá (allá pudo haber además 2 pruebas más).
> - La falta de scripts para el CSV y las figuras puede deberse a que se generaron en **notebooks de la nube que no se
>   exportaron**. No es un error del código, sino de lo que llegó al repositorio.

## 1. Qué es exactamente

- **Punto de partida:** nuestra carpeta de trabajo hacia las **21:27 del 2026-11-16**, con el artefacto 7 (madre)
  hecho pero aún sin commit. Prueba: su `FAILURES.md` contiene, palabra por palabra, nuestros F-010 y F-011, y 9
  documentos de proceso son idénticos a nuestro commit `f42b040`.
- **Lo que agregó:** el motor (`motor/motor.py`, 511 líneas), la configuración (`config.py`, 685 líneas), las
  pruebas del motor, un CSV con 120 ensayos, 4 documentos de análisis y 4 figuras.
- **Lo que "cambió" de lo existente:** en mundo, escenarios, protocolo, canal, madre, agente y todas las pruebas
  existentes **no hay ni una línea de lógica distinta** (comparación de árboles de sintaxis sin docstrings). Solo
  **borró la documentación del código** (docstrings y comentarios).

## 2. Lo que Gemini hizo y nosotros no (aportes a considerar)

| # | Aporte de Gemini | Lo que tenemos | Valor |
|---|---|---|---|
| G1 | **Escenario "personalizado"**: obstáculos, inicio y meta escritos en el YAML | Solo L, aleatorio y puente doble | **Alto**: lo pedía el prompt de Claude Design ("lista de celdas en un archivo de configuración") y lo omitimos |
| G2 | El motor **envía `INICIO`** al empezar | `INICIO` está en el protocolo pero nunca se envía | Medio: el protocolo se ejercita completo y su costo se cuenta |
| G3 | **Cierre `ABORTADO`** si todas las exploradoras quedan asentadas o fallidas | Seguimos hasta el límite de ticks | Medio: ensayos más cortos y un motivo de cierre honesto (`FIN` motivo 3 existe y no se usa) |
| G4 | **Memoria máxima** de la madre durante todo el ensayo | Solo la memoria al final | Medio: es lo que importa para dimensionar la RPi |
| G5 | **Vacía los mensajes pendientes** antes de cerrar, para que la madre registre la verificación aun con retardo | El motor mira el estado de la verificadora directamente | Medio: más fiel a "la madre sabe por mensajes" cuando hay retardo |
| G6 | **Orden canónico** de las acciones (por `src`) | Las aplicamos en orden de llegada | Bajo: el resultado es el mismo, pero el historial queda ordenado |
| G7 | **Bytes totales**, incluido el tráfico mundo ↔ agente, y la lectura de que la madre **reduce el tráfico total** (22–36 %) al acortar los ensayos | Contamos bytes por familia, pero no hicimos esa lectura | **Alto** para el hardware (energía, canal de radio) |
| G8 | **JSON frente a binario por mensaje**: en JSON, `PERCEPCION` ocupa 486 B y `MAPA` 393 B | Solo el tamaño binario | **Alto**: en JSON esos mensajes **no caben en un paquete ESP-NOW (250 B)**. Es un dato para los bloqueantes B2 y B3 |
| G9 | Figura de **feromona final con las trayectorias** de las exploradoras, sin madre y con madre | Animación y PNG del estado final | Medio: muestra de un vistazo cómo la madre concentra el rastro |

## 3. Lo que dejó al descubierto en nuestro trabajo

**F-020 (defecto nuestro, grave): los rescates iban a la verificadora.** Gemini anotó que en modo rescate "se
emiten 23 envíos de rescate" que no cambian nada, y lo atribuyó a que llegaban tarde. Al verificarlo con nuestro
código:

- Con la configuración de F-010 (mundo L, 1 viaje, umbral 0,5), la madre envió rescates en 26 de 30 ensayos y
  **los 26 fueron a la verificadora**, que los ignora. La verificadora informa su `ESTADO` como cualquier agente;
  recién salida, tiene poca experiencia y la madre la toma por rezagada.
- Con la configuración de F-018 (aleatorio, 10 viajes, umbral 0,95): **92 rescates se usaron**, 30 llegaron tarde
  (la agente ya había llegado a la meta) y **24 se desperdiciaron en la verificadora**.
- **Lo que yo registré mal:** en F-010, F-013 y F-018 escribí que "el rescate no se dispara" con umbral 0,5. En
  realidad **sí se dispara, pero hacia la agente equivocada**. Gemini vio el síntoma; ninguno de los dos vio la causa.
- **Consecuencia:** el experimento del rescate (F-018, F-019) está contaminado. Hay que corregir el defecto (que la
  madre excluya a la verificadora) y repetirlo.

**Corroboración independiente:** con el mismo agente y la misma madre, el motor de Gemini da **exactamente** los
mismos tiempos y tasas que el nuestro (ticks hasta asentarse 102,4 / 74,5 / 58,4; verificadas 20 / 21 / 20 / 24 de
30). Dos motores escritos por separado coinciden, lo que respalda a los dos.

## 4. Problemas del trabajo de Gemini

1. **Borró toda la documentación del código** de 6 módulos que no necesitaba tocar. Va contra la guía de
   reproducción autocontenida (artefacto 17) y contra el método.
2. **"192 pruebas en PASA" no se reproduce:** aquí hay 190 pruebas y **1 falla siempre** (3 de 3):
   `test_motor_hilos_usa_hilos_distintos_por_agente`. El motor ejecuta el paso de los agentes desde el hilo
   principal al cerrar, y la prueba toma un hilo cualquiera de un conjunto. No quedó registrado en `FAILURES.md`.
3. **Resultados y figuras sin script que los genere:** el CSV y las 4 figuras no se pueden regenerar desde el
   repositorio. Va contra C5 (determinismo auditable) y contra la reproducibilidad.
4. **Afirmaciones de más:** el documento 04 dice que el agente reproduce "la curva del notebook oráculo (celda [5])",
   pero la prueba usa la fórmula 1.1 con feromona en las dos ramas, que **no** es lo que calcula esa celda (I15).
   También dice que α = 2 "amplifica la ventaja de la rama corta (C3)" sin haberlo medido; nosotros medimos C3 y no
   pasa.
5. **Artefacto 9 incompleto:** `config.py` no tiene línea de comandos ni ninguna prueba, e incluye un lector de YAML
   escrito a mano (~85 líneas) para cuando falte PyYAML, que está en el entorno: complejidad sin necesidad.
6. **Motor de hilos en paso fijo:** sincroniza todos los hilos en cada tick con barreras. Gana determinismo (da lo
   mismo que el determinista, incluso con madre) pero **pierde la asincronía**, que era la razón para tener hilos
   (decisión B1: "lo más real al llevarlo a los micros"). No se probó con pérdidas de mensajes, donde el orden de los
   envíos concurrentes podría romper el determinismo.
7. **El método no se siguió:** no hay entradas nuevas en `FAILURES.md`, `CHANGELOG.md` ni en el historial;
   `ARTEFACTOS.md` marca 7 y 8 como hechos pero no menciona el 9.
8. Detalles: la figura 3 pinta el inicio en verde, no en rojo como el plano; el valor por defecto de `rho` es 0 y
   no 0,01 (decisión I3).

## 5. Discernimiento: qué tomar

| Tomar | Por qué |
|---|---|
| **Corregir F-020 y repetir el experimento del rescate** | Es un defecto real que invalida una conclusión |
| G1 escenario personalizado | Lo pedía el prompt original |
| G7 y G8 (bytes totales; JSON no cabe en ESP-NOW) | Alimentan las decisiones de transporte y lenguaje (B2, B3) |
| G2, G3, G4 y G5 en nuestro motor | Mejoras pequeñas de fidelidad al protocolo |
| G9 como figura del notebook | Comunica bien el efecto de la madre |

| No tomar | Por qué |
|---|---|
| El código de Gemini tal cual | Sin documentación, con una prueba que falla y sin pruebas de configuración; nuestro motor ya hace lo mismo y más (salidas escalonadas, viajes, métricas, experimentos) |
| El motor de hilos en paso fijo | Contradice la razón de B1; nuestro motor de hilos es asíncrono |
| El lector de YAML hecho a mano | PyYAML está en el entorno |
