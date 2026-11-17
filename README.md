![Built with AI](https://img.shields.io/badge/Built%20with-AI-blue.svg)
![Model](https://img.shields.io/badge/Modelo-Claude%20Opus%205.5-blueviolet.svg)

# ACO-test

Ensayos sobre **optimización por colonia de hormigas (ACO)**: un **gemelo de software** de una colonia
de agentes con recursos limitados (a futuro ESP32) coordinados por una "madre" en el edge (a futuro
Raspberry Pi). Los agentes exploran un mundo en cuadrícula y se inspiran en las hormigas (feromona) y
en las abejas (danza y reclutamiento).

![Plano de ensayo](bosquejo/Plano%20de%20ensayo%20·%20ACO%20en%20edge.png)

## Estado

Sesión 0 cerrada: contexto, protocolo (borrador) y decisiones de diseño registrados. **Todavía no hay
código**. El avance de cada artefacto está en [ARTEFACTOS.md](ARTEFACTOS.md).

| Fase | Contenido | Meta |
|---|---|---|
| 1 | Gemelo en Python: mundo, agentes y madre | Diciembre de 2026 |
| 2 | Agentes y madre en Python + mundo en NetLogo (MQTT) | Demostración mínima en diciembre de 2026 |
| 3 | Agentes en ESP32 + madre en Raspberry Pi | 2027 |

## Documentos

| Archivo | Para qué |
|---|---|
| [PROMPT-ZERO.md](PROMPT-ZERO.md) | Método de trabajo (operador humano + IA) |
| [CONTEXT.md](CONTEXT.md) | Contexto: referencia, NetLogo, agentes AIMA, propuesta de enjambre, enfoque del gemelo |
| [DECISIONES-PRUEBA.md](DECISIONES-PRUEBA.md) | Decisiones de diseño, con las opciones elegidas y las descartadas |
| [PROTOCOLO.md](PROTOCOLO.md) | Mensajes madre ↔ agentes ↔ mundo (campos y bits) |
| [ARTEFACTOS.md](ARTEFACTOS.md) | Software a generar, estado y requisitos de reproducción |
| [CHECKLIST-ENTORNO.md](CHECKLIST-ENTORNO.md) | Software necesario |
| [DECISIONS.md](DECISIONS.md) · [FAILURES.md](FAILURES.md) · [ASSUMPTIONS.md](ASSUMPTIONS.md) · [CHANGELOG.md](CHANGELOG.md) | Registros del método |
| [referencia/](referencia/) | Copia de solo lectura de [UdeA-IoT/ESP-ACO](https://github.com/UdeA-IoT/ESP-ACO) (ver `PROCEDENCIA.md`) |
| [bosquejo/](bosquejo/) | Plano de ensayo (a mano y en limpio) |

## Uso de IA

Este repositorio se construye con **asistencia de IA** bajo supervisión de un operador humano, que toma
las decisiones finales (ver [PROMPT-ZERO.md](PROMPT-ZERO.md)).

| Parte | Herramienta / modelo |
|---|---|
| Documentación, contexto, protocolo, decisiones y registros de este repo | **Claude Opus 5.5** (`claude-opus-5-5`), Anthropic, mediante Claude Code |
| Plano de ensayo en limpio y prompt del simulador | Claude Design (el modelo no está registrado) |
| Material de `referencia/` | Ver el repositorio de origen; varios archivos llevan sus propias insignias o autoría de IA (por ejemplo, Claude Sonnet 4.6 en los modelos NetLogo de Holland & Melhuish) |

Los commits generados con IA llevan la línea `Co-Authored-By` del modelo.

## Licencia

[GPL v3](LICENSE). Algunos ejemplos externos citados en `CONTEXT.md` tienen otras licencias (por ejemplo,
el modelo Ants de NetLogo usa CC BY-NC-SA); no se copia su código aquí.
