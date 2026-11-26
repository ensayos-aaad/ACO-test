# Ronda 003 — reporte de QA

<!-- Lo escribe solo QA (Gemini). Desarrollo no lo edita. -->

## Resumen (máximo 5 líneas)

- **Veredicto global:** PASA
- **Conteo:** 12 PASA · 0 NO PASA · 2 NO PROBADO
- **Bloqueantes:** ninguno (reproducción verificada de punta a punta desde un clon limpio y con `conda env create -f gemelo/environment.yml` real: 350 + 7 pruebas, `comparar.py` y `--completo` 18/18 CSV, `analisis.ipynb` solo marcas de tiempo, `oraculo/RESULTADOS.md` sin cambios, criterios 17.1–17.4 en PASA; solo 2 observaciones cosméticas no bloqueantes H1–H2).

---

- **Fecha y hora:** 2026-11-25 23:06 -0500
- **Commit base revisado:** `815e629` (cambios de la ronda 003 sin commit en el árbol de trabajo; más revisión de los dos cambios de solo texto de F-030 en `815e629`)
- **Entrega revisada:** `rondas/003-para_qa.md`
- **Carpeta de trabajo:** `%TEMP%/aco-qa/ronda-003/` (`C:\Users\Usuario\AppData\Local\Temp\aco-qa\ronda-003\`) y entorno conda nuevo en `%TEMP%/aco-qa/ronda-003-env/`

## `git status --short` antes de la ronda

```
 M .handoff/ESTADO.md
 M ARTEFACTOS.md
 M CLAUDE.md
 M FAILURES.md
 M IDEAS.md
?? .handoff/rondas/003-para_qa.md
?? gemelo/REPRODUCIR.md
?? gemelo/docs/informes/revision_r003.md
?? gemelo/reproducir/
?? gemelo/tests/test_reproducir.py
```

## Veredicto por punto

| # | Punto revisado | Estado | Evidencia (comando o archivo) |
|---|---|---|---|
| 1 | Paso 2.1: clonar desde GitHub | NO PROBADO | Los cambios aún no están publicados en GitHub; se clonó `d:/experimento/ACO-test` en `%TEMP%/aco-qa/ronda-003/` aplicando `git diff 815e629` y los archivos sin seguimiento, como indica `003-para_qa.md` |
| 2 | Paso 2.2: crear entorno real con `conda env create -f gemelo/environment.yml` y validar dentro de él | PASA | `conda env create -f gemelo/environment.yml -p %TEMP%/aco-qa/ronda-003-env --yes` (`conda 25.1.1`): `CONDA_CREATE_EXIT=0` (396,7 s); Python `3.12.7` y los 13 paquetes coinciden exactamente con `environment.yml`; `comparar.py` dentro del entorno nuevo dio 3 `PASA` y `EXIT=0` |
| 3 | Paso 2.3: correr pruebas del gemelo y del oráculo | PASA | En el clon: `pytest -q` en `gemelo/` → `350 passed in 347.00s (0:05:47)`; `pytest oraculo -q` → `7 passed in 11.63s`; `git diff --stat -- gemelo/notebooks/figuras` vacío |
| 4 | Paso 2.4: escenario de referencia (`run --config configs/default.yaml --png resultados/final.png`) | PASA | `RUN_EXIT=0` (10,53 s); tabla coincide con `REPRODUCIR.md:87-97` (`semilla 2026`, `ticks_asentadas 739`, `ticks_total 760`, `largo_optimo 8`, `largo_verificado 20`, `razon 2.5`); `resultados/final.png` creado y `git status` del clon sin archivos extra |
| 5 | Paso 2.5: `reproducir/comparar.py` y `--completo` | PASA | `comparar.py`: 3 líneas `PASA`, `Resultado: PASA` (`EXIT=0`, 27,61 s), coincide con `REPRODUCIR.md:116-120`; `--completo`: además `modos` (9/9) y `rescate` (9/9) (`EXIT=0`, 252,92 s); `git status` del clon idéntico antes y después |
| 6 | Paso 2.6: regenerar `analisis.ipynb` y `oraculo/comparar.py` | PASA | `nbconvert --to notebook --execute --inplace analisis.ipynb`: `EXIT=0` (51 s), `NON_TIMESTAMP_DIFF_LINES=0` (solo marcas `iopub.*` / `shell.execute_reply`) y 0 cambios en `notebooks/figuras/`; `oraculo/comparar.py`: `EXIT=0` (732,3 s ≈ 12,2 min), `git diff -- oraculo/RESULTADOS.md` vacío (`0` bytes) |
| 7 | Ataques a `reproducir/comparar.py` (texto, CSV, PNG con y sin cambio de alfa, CSV publicado con `--completo`) | PASA | `test_qa_003_comparador_y_guia.py` (`11 passed in 3.42s`): detecta texto alterado, CSV alterado, PNG alterado (1 px RGB igual alfa, negro alfa 255, 1 px alfa, modo `RGB`, tamaño) y CSV publicado alterado o faltante en `--completo`, guardando `%TEMP%/aco-reproducir-ultima` |
| 8 | Revisión de cambios de solo texto de F-030 (`815e629`) | PASA | `git show 815e629 -- gemelo/aco_gemelo/motor/simulacion.py gemelo/tests/test_reproducibilidad.py`: solo comentario en `ConfigEnsayo.__post_init__` y docstring en `test_reproducibilidad.py`; sin cambios de lógica y coherentes con F-030 |
| 9 | Verificación de afirmaciones y enlaces relativos en `gemelo/REPRODUCIR.md` | PASA | 35/35 enlaces relativos existen; cifras, versiones (`CHECKLIST-ENTORNO.md`, `environment.yml`), fallas (`FAILURES.md` F-002/005/007/019/023–027/029–030), `referencia/` (`PROCEDENCIA.md`, `CONTEXT.md`, `ejemplo4`/`ejemplo5`/`ejemplo6`) y resultados (`RESULTADOS.md`, informes) coinciden con sus fuentes |
| 10 | Criterio 17.1 (`ARTEFACTOS.md`): prerrequisitos con versiones; hardware de fases 2–3 aparte | PASA | `REPRODUCIR.md` §1 tabla de fase 1 (versiones exactas confirmadas con `conda env create`) y subsección aparte para fases 2–3 fiel a `CHECKLIST-ENTORNO.md` y `ESTADO-PREHARDWARE.md` |
| 11 | Criterio 17.2 (`ARTEFACTOS.md`): desde cero reproduce la salida esperada y resultados publicados (revisor + QA) | PASA | QA reprodujo texto, CSV, PNG, 18 CSV publicados, notebook y `oraculo/RESULTADOS.md` desde un clon limpio y un entorno conda recién creado |
| 12 | Criterio 17.3 (`ARTEFACTOS.md`): explica el porqué e incorpora experimentos previos de la referencia con fuentes | PASA | `REPRODUCIR.md` §3 explica cada paso con enlaces; §4 cubre los 4 bloques de `referencia/` exigidos en `ARTEFACTOS.md` req. 4 y §5 las trampas de Windows (F-002, F-005, F-027) |
| 13 | Criterio 17.4 (`ARTEFACTOS.md`): autocontenida (sin enlaces externos fuera de clonar y crear el entorno) | PASA | `test_qa_003_guia_enlaces_relativos_y_autocontenida`: 0 enlaces externos en Markdown; única URL en el archivo es `https://github.com/ensayos-aaad/ACO-test.git` (paso 2.1) |
| 14 | Otra plataforma, otra máquina u otro usuario de Windows | NO PROBADO | Solo probado en esta máquina Windows con Python 3.12.7 (la guía lo declara explícitamente en la cabecera y §6) |

## Hallazgos (del más grave al más leve)

Sin hallazgos bloqueantes. Dos observaciones muy leves (cosméticas):

### H1 — Importación sin usar `ImageChops` en `gemelo/reproducir/comparar.py`

- **Gravedad:** no bloquea
- **Dónde:** `gemelo/reproducir/comparar.py:49`
- **Escenario que lo demuestra:** Tras corregir H1 de `revision_r003.md` cambiando `ImageChops.difference(...).getbbox()` por comparación de `tobytes()`, la línea 49 conservó `ImageChops` en el `import`, que ya no se usa en la función.
- **Comando exacto:**
  ```powershell
  Select-String -Path gemelo/reproducir/comparar.py -Pattern "ImageChops"
  ```
- **Salida:**
  ```
  gemelo/reproducir/comparar.py:49:    from PIL import Image, ImageChops
  gemelo/reproducir/comparar.py:51:    # Se comparan los bytes de todos los canales. (`ImageChops.difference(...).getbbox()` no sirve: con imágenes RGBA,
  ```
- **Qué debería dar:** `from PIL import Image` (sin importar `ImageChops`).

### H2 — Ligera diferencia en el tiempo estimado de `--completo` dentro de la guía

- **Gravedad:** no bloquea
- **Dónde:** `gemelo/REPRODUCIR.md:8`, `gemelo/REPRODUCIR.md:129` y `gemelo/reproducir/comparar.py:6`
- **Escenario que lo demuestra:** La cabecera (`REPRODUCIR.md:8`) indica `la comparación completa, ≈ 5 min más` (y `comparar.py:6` dice `≈ 5 min`), mientras que §2.5 (`REPRODUCIR.md:129`) dice `tarda ≈ 3 min más`. En la medición de QA, `comparar.py` tardó `27,6 s` y `comparar.py --completo` tardó `252,9 s` en total (`≈ 4,2 min` totales; `≈ 3,8 min` adicionales).
- **Comando exacto:**
  ```powershell
  # Desde %TEMP%\aco-qa\ronda-003\gemelo
  Measure-Command { C:/Users/Usuario/anaconda3/envs/aco-gemelo/python.exe -X utf8 reproducir/comparar.py --completo }
  ```
- **Salida:**
  ```
  CMP_FULL_EXIT=0 ELAPSED_S=252.92
  ```
- **Qué debería dar:** Alinear opcionalmente el rango estimado (p. ej. `≈ 3–5 min más` en los tres sitios).

## Pruebas nuevas en `pruebas_qa/`

| Archivo | Qué prueba | Resultado con el código actual |
|---|---|---|
| `test_qa_003_comparador_y_guia.py` | 11 pruebas: ataques a `reproducir/comparar.py` (texto alterado, CSV alterado, 5 mutaciones de PNG incluyendo RGB 1 px y negro con alfa 255, CSV publicado alterado y faltante con `--completo` + carpeta `aco-reproducir-ultima`), auditoría de los 35 enlaces relativos y ausencia de URLs externas en `gemelo/REPRODUCIR.md`, y coincidencia de la tabla §2.4 con `reproducir/esperado/run_default.txt` | PASA (11 passed) |

Comando ejecutado en el clon (`%TEMP%/aco-qa/ronda-003/`, desde la raíz):
```
C:/Users/Usuario/anaconda3/envs/aco-gemelo/python.exe -B -I -X utf8 -m pytest .handoff/pruebas_qa/test_qa_003_comparador_y_guia.py -q -p no:cacheprovider -W ignore
# 11 passed in 3.42s
```

## Lo que no se pudo comprobar

- El paso 2.1 (`git clone https://github.com/ensayos-aaad/ACO-test.git`) directamente contra GitHub, porque los cambios de esta entrega aún no están publicados en el remoto.
- Otra máquina, otro usuario de Windows u otro sistema operativo (Linux/macOS): solo se probó en esta máquina Windows con Anaconda3 (`conda 25.1.1`) y Python 3.12.7.

## `git status --short` después de la ronda

```
 M .handoff/ESTADO.md
 M ARTEFACTOS.md
 M CLAUDE.md
 M FAILURES.md
 M IDEAS.md
?? .handoff/pruebas_qa/test_qa_003_comparador_y_guia.py
?? .handoff/rondas/003-para_qa.md
?? .handoff/rondas/003-reporte_qa.md
?? gemelo/REPRODUCIR.md
?? gemelo/docs/informes/revision_r003.md
?? gemelo/reproducir/
?? gemelo/tests/test_reproducir.py
```
