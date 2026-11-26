![Built with AI](https://img.shields.io/badge/Built%20with-AI-blue.svg)
![Model](https://img.shields.io/badge/Modelo-Claude%20Opus%205.5-blueviolet.svg)
![QA](https://img.shields.io/badge/QA%20externo-Gemini%20(Antigravity)-orange.svg)

# ACO-test

Ensayos sobre **optimización por colonia de hormigas (ACO)**: un **gemelo de software** de una colonia
de agentes con recursos limitados (a futuro ESP32) coordinados por una "madre" en el edge (a futuro
Raspberry Pi). Los agentes exploran un mundo en cuadrícula y se inspiran en las hormigas (feromona) y
en las abejas (danza y reclutamiento).

![Plano de ensayo](bosquejo/Plano%20de%20ensayo%20·%20ACO%20en%20edge.png)

## Estado

Fase 1 casi completa: el gemelo en [gemelo/](gemelo/) (agentes, madre, motores, métricas, visualización, experimentos y
un notebook que explica un ensayo y analiza los resultados) y el oráculo en [oraculo/](oraculo/). **350 pruebas del gemelo
y 7 del oráculo** pasan, más 98 pruebas escritas por el QA externo en [.handoff/pruebas_qa/](.handoff/pruebas_qa/). Frente a
los notebooks de referencia, los criterios C1, C2, C4 y C5 pasan y C3 no (causa documentada). **Para reproducirlo desde
cero:** [gemelo/REPRODUCIR.md](gemelo/REPRODUCIR.md). Falta la demostración con NetLogo. El avance de cada artefacto está en
[ARTEFACTOS.md](ARTEFACTOS.md).

| Fase | Contenido | Meta |
|---|---|---|
| 1 | Gemelo en Python: mundo, agentes y madre | Diciembre de 2026 |
| 2 | Agentes y madre en Python + mundo en NetLogo (MQTT) | Demostración mínima en diciembre de 2026 |
| 3 | Agentes en ESP32 + madre en Raspberry Pi | 2027 |

## Cómo se trabaja

Un operador humano decide; la IA construye y se verifica a sí misma con un método escrito ([PROMPT-ZERO.md](PROMPT-ZERO.md)):
criterios y tolerancias declarados antes de medir, estados PASA / NO PASA / NO PROBADO y un registro de fallas que no se
borra ([FAILURES.md](FAILURES.md)).

| Quién | Papel |
|---|---|
| Operador humano | Decide, aprueba cada commit y **es el único que cambia el turno** entre Desarrollo y QA |
| **Desarrollo:** Claude (orquestadora) | Implementa, reparte el trabajo y lleva los registros |
| **Desarrollo:** agentes de Claude ([.claude/agents/](.claude/agents/)) | *revisor* (verifica sin conocer el razonamiento, con mutantes), *experimentador* (experimentos con pruebas declaradas antes), *divulgador* (textos para no especialistas) |
| **QA externo:** Gemini, desde Antigravity | Desde el 2026-11-25 audita cada entrega de código sobre una copia del repositorio y escribe pruebas propias, sin tocar el resto ([ADR-004](DECISIONS.md)) |

El relevo entre Desarrollo y QA es por rondas en [.handoff/](.handoff/README.md): Desarrollo entrega
(`rondas/NNN-para_qa.md`), el operador pasa el turno, QA reporta (`rondas/NNN-reporte_qa.md`), el revisor reproduce los
hallazgos y se corrige o se cierra con PASA. En la ronda 001, QA atrapó una regresión que la revisión interna no había
visto ([F-029](FAILURES.md)).

## Documentos

| Archivo | Para qué |
|---|---|
| [PROMPT-ZERO.md](PROMPT-ZERO.md) | Método de trabajo (operador humano + IA) |
| [USO-DEL-PROTOCOLO.md](USO-DEL-PROTOCOLO.md) | Evaluación del método en este proyecto: qué guió, qué evitó, qué salió mal, agentes, QA externo y costo en tokens |
| [.handoff/](.handoff/README.md) | Relevo Desarrollo ↔ QA: reglamento, turno, entregas, reportes y pruebas de QA |
| [CONTEXT.md](CONTEXT.md) | Contexto: referencia, NetLogo, agentes AIMA, propuesta de enjambre, enfoque del gemelo |
| [DECISIONES-PRUEBA.md](DECISIONES-PRUEBA.md) | Decisiones de diseño, con las opciones elegidas y las descartadas |
| [PROTOCOLO.md](PROTOCOLO.md) | Mensajes madre ↔ agentes ↔ mundo (campos y bits) |
| [ESTADO-PREHARDWARE.md](ESTADO-PREHARDWARE.md) | **Estado antes de pasar al hardware:** avance, checklist de hallazgos, bloqueantes y cosas por explorar |
| [ARTEFACTOS.md](ARTEFACTOS.md) · [PLAN-MEJORAS.md](PLAN-MEJORAS.md) | Software a generar, su estado, el orden de trabajo y los requisitos de reproducción |
| [gemelo/notebooks/analisis.ipynb](gemelo/notebooks/analisis.ipynb) | Un ensayo explicado y el análisis de los experimentos |
| [gemelo/docs/informes/](gemelo/docs/informes/) · [gemelo/docs/divulgacion/](gemelo/docs/divulgacion/) | Informes por experimento y de cada revisión; textos para no especialistas |
| [CHECKLIST-ENTORNO.md](CHECKLIST-ENTORNO.md) | Software necesario |
| [DECISIONS.md](DECISIONS.md) · [FAILURES.md](FAILURES.md) · [ASSUMPTIONS.md](ASSUMPTIONS.md) · [CHANGELOG.md](CHANGELOG.md) | Registros del método |
| [IDEAS.md](IDEAS.md) | Cuaderno de asociación libre del operador |
| [referencia/](referencia/) | Copia de solo lectura de [UdeA-IoT/ESP-ACO](https://github.com/UdeA-IoT/ESP-ACO) (ver `PROCEDENCIA.md`) |
| [bosquejo/](bosquejo/) | Plano de ensayo (a mano y en limpio) |

## Uso de IA

Este repositorio se construye con **asistencia de IA** bajo supervisión de un operador humano, que toma
las decisiones finales (ver [PROMPT-ZERO.md](PROMPT-ZERO.md)).

| Parte | Herramienta / modelo |
|---|---|
| Documentación, contexto, protocolo, decisiones y registros | **Claude Opus 5.5** (`claude-opus-5-5`), Anthropic, mediante Claude Code |
| Código del gemelo | **Claude Fable 5.2** (artefactos 1 a 9 y la mayor parte del 10) y **Claude Opus 5.5** (cierre del 10 y desde el 11), mediante Claude Code |
| Revisión, experimentos y divulgación | Agentes de Claude Code con rol fijo ([.claude/agents/](.claude/agents/)) |
| QA externo (desde el 2026-11-25): auditoría de las entregas y pruebas en `.handoff/pruebas_qa/` | **Gemini**, de Google, mediante Antigravity (la versión del modelo no está registrada) |
| Trabajo anterior hasta el artefacto 9, analizado y no incorporado tal cual | Gemini, en la nube ([otras/](otras/)) |
| Plano de ensayo en limpio y prompt del simulador | Claude Design (el modelo no está registrado) |
| Material de `referencia/` | Ver el repositorio de origen; varios archivos llevan sus propias insignias o autoría de IA (por ejemplo, Claude Sonnet 4.6 en los modelos NetLogo de Holland & Melhuish) |

Los commits generados con IA llevan la línea `Co-Authored-By` del modelo. QA no hace commit: sus reportes y pruebas
entran al repositorio en los commits que aprueba el operador.

## Licencia

[GPL v3](LICENSE). Algunos ejemplos externos citados en `CONTEXT.md` tienen otras licencias (por ejemplo,
el modelo Ants de NetLogo usa CC BY-NC-SA); no se copia su código aquí.
