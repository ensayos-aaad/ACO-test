# CHANGELOG

## [Sesión 1] — 2026-11-16 (Claude Fable 5.2)
### Añadido
- `gemelo/`: entorno conda `aco-gemelo` (artefacto 1), protocolo con codificadores JSON y binario (3), mundo con BFS y escenarios (4), canal en memoria (5) y agente con verificadora (6). 137 pruebas en PASA.
- `DECISIONES-PRUEBA.md`: ronda 2 (I1–I15), parámetros delegados según la literatura.
- `PROTOCOLO.md` v0.2.
### Hallazgos
- C1 en PASA a nivel del programa de agente. F-009: línea base sin madre (la verificadora llega en el 60–80 % de las semillas).

## [Sesión 0] — 2026-11-16
### Añadido
- `referencia/`: copia de solo lectura de `UdeA-IoT/ESP-ACO` @ `3c48648`, con `PROCEDENCIA.md`.
- `CONTEXT.md`: inventario de la referencia, parámetros del modelo con su celda de origen, partes que sirven como oráculo, y vacíos e inconsistencias.
- `DECISIONS.md` (ADR-001, ADR-002), `FAILURES.md`, `ASSUMPTIONS.md`, `CHANGELOG.md`.
- `oraculo/README.md`: carpeta reservada para el oráculo; todavía sin código.
- `CHECKLIST-ENTORNO.md`: software necesario (Anaconda, NetLogo, PlatformIO/ESP32, Wokwi, serial, git).
- `PROTOCOLO.md`: borrador v0.1 del protocolo de mensajes del gemelo.
- `DECISIONES-PRUEBA.md`: registro ejecutivo de las decisiones de diseño (ronda 1 completa); `DECISIONS.md` ADR-003 aprobada.
- `CONTEXT.md` §5 (hormigas y NetLogo: referencia y ejemplos de internet) y §6 (agentes según AIMA cap. 2 y su aplicación al puente doble).
- `PROMPT-ZERO.md`: método de trabajo.
- `bosquejo/`: plano de ensayo (a mano y en limpio).
- `ARTEFACTOS.md`: tabla de artefactos de software y requisitos de reproducción.
### Cambiado
- `CLAUDE.md`: incorpora las instrucciones permanentes (antes en `CLAUDE (2).md`, que se eliminó).

## 2026-11-16 — `8410704`
- `CLAUDE.md` inicial con el historial de cambios con marcas de tiempo.

## 2026-11-16 — `485a86a`
- Commit inicial: `README.md`, `LICENSE` (GPL v3).
