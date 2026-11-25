# Ronda NNN — reporte de QA

<!-- Lo escribe solo QA (Gemini). Desarrollo no lo edita. -->

## Resumen (máximo 5 líneas)

- **Veredicto global:** PASA / NO PASA / NO PROBADO
- **Conteo:** N PASA · N NO PASA · N NO PROBADO
- **Bloqueantes:** H1 ..., H2 ... (o "ninguno")

---

- **Fecha y hora:** AAAA-MM-DD HH:MM -0500
- **Commit base revisado:** `xxxxxxx`
- **Entrega revisada:** `rondas/NNN-para_qa.md`
- **Carpeta de trabajo:** `%TEMP%/aco-qa/ronda-NNN/`

## `git status --short` antes de la ronda

```
(salida)
```

## Veredicto por punto

| # | Punto revisado | Estado | Evidencia (comando o archivo) |
|---|---|---|---|
| 1 | ... | PASA / NO PASA / NO PROBADO | ... |

## Hallazgos (del más grave al más leve)

### H1 — título corto

- **Gravedad:** bloquea / no bloquea
- **Dónde:** `archivo:línea`
- **Escenario que lo demuestra:** ...
- **Comando exacto:**
  ```
  ...
  ```
- **Salida:**
  ```
  ...
  ```
- **Qué debería dar:** ...

## Pruebas nuevas en `pruebas_qa/`

| Archivo | Qué prueba | Resultado con el código actual |
|---|---|---|
| `test_qa_NNN_<tema>.py` | ... | PASA / NO PASA |

Comando: `<python> -B -I -X utf8 -m pytest .handoff/pruebas_qa -q -p no:cacheprovider -W ignore` (desde la raíz).

## Lo que no se pudo comprobar

- ...

## `git status --short` después de la ronda

```
(salida: solo pueden aparecer este reporte y pruebas_qa/)
```
