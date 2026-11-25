# DECISIONS — registro de decisiones (formato ADR)

Estados: Propuesta · Aprobada · Rechazada · Reemplazada. Solo el operador aprueba.

## ADR-001 — Copia íntegra de ESP-ACO en referencia/
- **Fecha:** 2026-11-16
- **Estado:** Propuesta (pendiente de aprobación del operador)
- **Contexto:** PROMPT-ZERO exige `referencia/` como copia de solo lectura de `UdeA-IoT/ESP-ACO`, y la carpeta no existía.
- **Decisión:** copiar todos los archivos versionados del commit `3c48648` con `git archive`, sin `.git/` y sin filtrar, y registrar el origen en `referencia/PROCEDENCIA.md`.
- **Alternativas:** submódulo de git (fija el commit, pero complica el flujo); copiar solo `ACO/experimento_doble-puente/` (más liviano, pero pierde el antecedente de ESP32 de `simulaciones/ejemplo3`).
- **Modo de falla más probable:** el repositorio crece unos 20 MB por PDFs e imágenes ajenas al puente doble, y la copia se desactualiza si el fuente cambia.
- **Cómo se detecta:** comparar el commit de PROCEDENCIA.md con `git ls-remote` del fuente.

## ADR-002 — Unificar las instrucciones permanentes en CLAUDE.md
- **Fecha:** 2026-11-16
- **Estado:** Propuesta (pendiente de aprobación del operador)
- **Contexto:** llegó `CLAUDE (2).md` con las reglas permanentes junto a un CLAUDE.md existente.
- **Decisión:** las reglas pasan al inicio de CLAUDE.md, que importa `@PROMPT-ZERO.md`, y se elimina el duplicado.
- **Modo de falla más probable:** que Claude Code no cargue las reglas si el archivo no se llama exactamente `CLAUDE.md`.
- **Cómo se detecta:** al abrir una sesión nueva, comprobar que Claude cita las reglas no negociables.

## ADR-003 — El gemelo de software extiende PROMPT-ZERO
- **Fecha:** 2026-11-16 20:25 -0500
- **Estado:** **Aprobada** por el operador (respuesta A1 en DECISIONES-PRUEBA.md)
- **Decisión:** se mantienen el método, los registros, el oráculo y los estados PASA / NO PASA / NO PROBADO. El artefacto de PROMPT-ZERO §3 es el **gemelo de software del plano** (cuadrícula, 6 agentes, madre con 4 modos). El puente doble queda como escenario de validación contra los notebooks (C3).
- **Meta a diciembre de 2026:** fase 1 completa + demostración mínima con NetLogo (A2). Disponibilidad indefinida: se planifica por prioridad de etapas (A3).
- **Modo de falla más probable:** que la disponibilidad indefinida deje la fase 1 a medias sin un punto de corte claro.
- **Cómo se detecta:** cada etapa termina con pruebas en estado PASA / NO PASA registradas; lo que no llegue queda NO PROBADO, sin porcentajes.

## ADR-004 — Flujo de pares Desarrollo + QA con una IA externa (Gemini)
- **Fecha:** 2026-11-25 14:03 -0500
- **Estado:** **Aprobada** por el operador ("Sí", 2026-11-25), tras una propuesta de QA y una contrapropuesta de Desarrollo aceptadas por las dos IA.
- **Decisión:** Claude (orquestadora) y sus agentes son **Desarrollo**; Gemini, desde Antigravity y sobre el mismo directorio, es **QA externo** (audita el código y las pruebas, escribe pruebas nuevas). El relevo se hace por `.handoff/`, **versionada en git**: `ESTADO.md` (turno y ronda; **solo el operador cambia el turno**), `rondas/NNN-para_qa.md` (Desarrollo) y `rondas/NNN-reporte_qa.md` (solo QA), `pruebas_qa/test_qa_NNN_<tema>.py`. Reglamento completo en `.handoff/README.md`.
- **Roles:** la orquestadora implementa y decide las correcciones; el revisor verifica antes de entregar y reproduce los hallazgos de QA, sin coordinar (conserva su independencia); el experimentador sigue solo con experimentos; el divulgador cuenta solo lo que pasó QA. QA es solo lectura fuera de su carpeta y no hace commit. Ningún commit sin el operador.
- **Reglas de QA:** PASA / NO PASA / NO PROBADO; resumen de máximo 5 líneas al inicio del reporte; cada hallazgo con archivo:línea, escenario, comando y salida; ejecución sobre una copia en `%TEMP%/aco-qa/ronda-NNN/` y `git status` antes y después; un hallazgo sin evidencia reproducible cuenta como NO PROBADO (F-028).
- **Alternativas descartadas:** el experimentador implementando el código y el revisor coordinando las correcciones (propuesta inicial de QA: cambiaba el método y quitaba independencia al revisor); `.handoff/` fuera de git con un solo reporte que se sobrescribe (se perdería la memoria, como en F-023).
- **Modo de falla más probable:** colisión de escrituras si alguna de las dos IA trabaja fuera de su turno, o un reporte de QA que afirma sin evidencia.
- **Cómo se detecta:** `git status` antes y después de cada ronda en el reporte de QA; el revisor reproduce cada hallazgo antes de corregir nada.

