# PLAN — correcciones y mejoras antes del artefacto 16

**Fecha:** 2026-11-18 · **Origen:** el análisis del trabajo de Gemini (`otras/ANALISIS-gemini-artefacto9.md`) y
el pedido del operador de mejorar la explicabilidad del notebook, en particular con fotogramas del conocimiento de la
madre. Estado: **propuesta, sin aprobar**. Se marca `[x]` al terminar cada punto.

Actualizado 2026-11-18 22:51 -0500 con lo que Gemini hizo mejor (G10, G11, C4).

Notación: **(G#)** = idea tomada de Gemini · ⚠ = toca el comportamiento del gemelo y cambia resultados.

## A. Corregir primero

- [x] **A1 ⚠ F-020:** que la madre **no rescate a la verificadora**. Propuesta: la verificadora marca su `ESTADO`
      con `FLAG_VERIFICACION` (la flag ya existe en el protocolo v0.2) y la madre la excluye. Prueba de regresión.
- [x] **A2** Repetir los planes `modos` y `rescate` (30 semillas) con la corrección; dejar el antes y el después en
      `FAILURES.md`. El notebook actualiza sus conclusiones solo.
- [x] **A3** Agregar una nota de corrección a F-010, F-013 y F-018 (no se borran) y revisar la conclusión de F-019.

## B. Mejoras del motor (tomadas de Gemini)

- [ ] **B1** Enviar `INICIO` al empezar el ensayo **(G2)**. El mensaje ya existe; ahora se ejercita y su costo se cuenta.
- [ ] **B2** Cerrar como **abortado** (`FIN` motivo 3) cuando ninguna agente puede seguir **(G3)**.
- [ ] **B3** Registrar la **memoria máxima** de la madre durante el ensayo, no solo la final **(G4)**.
- [ ] **B4** Vaciar los mensajes pendientes antes de cerrar, para que la madre registre la verificación aunque haya retardo **(G5)**.
- [ ] **B5** Aplicar las acciones en orden canónico (por agente) **(G6)**.
- [ ] **B7** Modo de hilos **en paso fijo** (sincronizados por tick) como tercer motor, solo para probar que con madre da lo mismo que el determinista **(G10)**. El motor de hilos asíncrono se conserva para la demostración.
- [ ] **B6** Escenario **personalizado** en el YAML (obstáculos, inicio y meta escritos a mano) **(G1)**, con su prueba.

## C. Métricas nuevas

- [ ] **C1** **Bytes totales** por ensayo, incluido el tráfico mundo ↔ agente, en el CSV y en el resumen **(G7)**.
- [ ] **C2** Tabla de tamaño de **JSON frente a binario** por mensaje, calculada con nuestros codificadores **(G8)**.
- [x] **C4** **Medir los mecanismos, no solo el resultado** (lección de F-020/F-021): en el CSV, rescates enviados, usados e ignorados (y por qué), reclutamientos, rutas pedidas y heredadas, y ticks por fase (exploración y verificación).
- [ ] **C3** Con `registrar`, guardar tick a tick **lo que la madre sabe del mundo** (celdas conocidas y obstáculos).
      Es la base de los fotogramas de D3.

## D. Notebook: explicabilidad

- [ ] **D1** Sección inicial **"Cómo funciona un ensayo"**: una corrida comentada con semilla fija (mundo, ruta óptima,
      fases colonia → verificadora → cierre), antes de las estadísticas.
- [ ] **D2** **Mapas de color de la feromona final con los trazos** de las exploradoras, la ruta verificada y la óptima;
      sin madre frente a con madre, en el mismo mundo y semilla **(G9)**.
- [ ] **D3** **Fotogramas del conocimiento global de la madre:** 6 a 8 cuadros en el tiempo que muestran qué celdas
      conoce la madre (y cuáles cree obstáculo) frente al mundo real, a medida que le llegan los `FRAGMENTO`, más la
      curva de conocimiento en el tiempo. También como GIF en `notebooks/figuras/`.
- [ ] **D4** Tamaño por mensaje, binario frente a JSON, con la línea del límite de ESP-NOW (250 B) **(G8)**.
- [ ] **D5** Tráfico total apilado por familia y por modo de la madre **(G7)**.
- [ ] **D6** Bajo cada figura, **"qué mirar"** en dos líneas, y un glosario corto (convergencia, verificadora, rezagada, Δt).
- [ ] **D8** **Informes cortos por experimento** (objetivo, configuración, tabla, diagnóstico), al estilo de `docs/01–04` de Gemini, pensados para el experto en sistemas embebidos **(G11)**.
- [ ] **D7** Todo regenerable desde el repositorio: cada figura sale de código o datos del repo (lo que no llegó del
      trabajo de Gemini). Mantener la prueba `tests/test_notebook.py` al día.

## E. Registros

- [ ] **E1** `DECISIONES-PRUEBA.md`, ronda 4: qué se toma de Gemini y qué no, con el porqué.
- [ ] **E2** `ESTADO-PREHARDWARE.md`: sumar el dato de JSON (no cabe en ESP-NOW) a los bloqueantes B2 y B3, y el nuevo
      experimento del rescate a X1.
- [ ] **E3** Si el operador tiene los **notebooks de Gemini en la nube**, agregarlos a `otras/gemini/` para citarlos
      con su autoría.
- [ ] **E4** Sincronizar al final de cada bloque (A, B + C, D, E), con aprobación.

## Orden propuesto

**A → B + C → D → artefacto 17 → E → artefacto 16.** A va primero porque cambia resultados que el notebook muestra;
C3 debe existir antes que D3; D va antes del 17 porque la guía muestra las figuras del notebook.

**Cambio de orden aprobado por el operador (2026-11-18 23:46 -0500):** la guía de reproducción (artefacto 17) va **antes** de la
demostración con NetLogo (16). El 17 no depende del 16 (documenta la fase 1, que ya existe), cierra la fase 1 con algo
entregable y el revisor puede verificarla siguiéndola desde cero. Al hacer el 16 se le agrega su sección a la guía.
