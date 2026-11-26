# Ronda 003 — entrega de Desarrollo a QA

- **Fecha y hora:** 2026-11-25 22:28 -0500
- **Commit base:** `815e629`. Los cambios de esta entrega están **sin commit**, en el árbol de trabajo (`git diff 815e629` y
  los archivos sin seguimiento de `git status`).
- **Quién entrega:** Claude (orquestadora)
- **Revisión interna previa:** NO PASA → corregida antes de entregar (`gemelo/docs/informes/revision_r003.md`, F-031). El
  revisor siguió la guía desde un clon; sus hallazgos están atendidos, pero **la versión corregida no tuvo otra pasada del
  revisor**: esta ronda es esa comprobación.

## Objetivo del cambio

**Artefacto 17: la guía de reproducción** (`gemelo/REPRODUCIR.md`), para que cualquiera con los recursos reproduzca el gemelo
desde cero sin preguntar nada. Criterios declarados antes de escribirla, en `ARTEFACTOS.md` (punto 17):

- **17.1** Prerrequisitos con versiones, con el hardware de las fases 2 y 3 aparte.
- **17.2** Desde cero reproduce la salida esperada (texto, CSV y PNG del escenario L con la semilla de referencia, y los
  resultados publicados); lo comprueban el revisor y **QA, cada uno por su cuenta**.
- **17.3** Explica el porqué de cada paso e incorpora los experimentos previos de la referencia, cada afirmación con su fuente.
- **17.4** Autocontenida: fuera de clonar y crear el entorno, sin enlaces externos.

## Archivos

| Archivo | Qué es |
|---|---|
| `gemelo/REPRODUCIR.md` (nuevo) | La guía |
| `gemelo/reproducir/comparar.py` (nuevo) | Corre el escenario de referencia y un lote de 10 semillas en una carpeta temporal y compara con `esperado/`; `--completo` también los 18 CSV publicados; código 0 solo si todo pasa |
| `gemelo/reproducir/esperado/` (nuevo) | Salida de referencia: `run_default.txt`, `batch_default_10.csv`, `final_default.png` (generados con `comparar.py --generar`) |
| `gemelo/tests/test_reproducir.py` (nuevo) | 3 pruebas: la referencia se reproduce; el comparador detecta un CSV alterado; detecta un píxel alterado |
| `ARTEFACTOS.md` | Criterios 17.1–17.4; última corrida de pruebas |
| `FAILURES.md` | F-031 |
| `IDEAS.md` | Una idea del operador (MLflow). **No es parte de la revisión** |

**Pendiente de la ronda anterior (sin efecto en el comportamiento):** por F-030, en el commit `815e629` cambiaron solo textos
dentro de dos archivos de código: un comentario en `gemelo/aco_gemelo/motor/simulacion.py` (`ConfigEnsayo.__post_init__`) y la
docstring de `gemelo/tests/test_reproducibilidad.py`. Se anotan aquí para que QA los vea, como se acordó con el operador.

## Cómo probarlo

**Sigue la guía `gemelo/REPRODUCIR.md` tal como está escrita**, como alguien que no la escribió, en un clon nuevo en
`%TEMP%/aco-qa/ronda-003/`. Como la guía todavía no está en GitHub, el paso 2.1 no se puede hacer tal cual: clona
`d:/experimento/ACO-test` y aplica los cambios sin commit (`git -C d:/experimento/ACO-test diff 815e629 | git apply`, más los
archivos sin seguimiento). Si crear un entorno conda nuevo es viable, hazlo con `conda env create -f gemelo/environment.yml`
(eso es lo que la revisión interna no probó); si no, usa `C:/Users/Usuario/anaconda3/envs/aco-gemelo/python.exe` y dilo.

## Casos borde que QA debería validar

1. Que cada comando de la guía funcione **tal cual**, y que cada "Debe dar" coincida con lo que sale.
2. Que `comparar.py` detecte de verdad una diferencia en cada uno de sus puntos (texto, CSV, PNG —incluido un cambio de
   color que conserve el alfa— y un CSV publicado con `--completo`), y que no escriba nada en el repositorio.
3. Que la guía no prometa nada falso: cifras, tiempos, versiones, rutas y enlaces relativos (deben existir), lo que se dice de
   cada experimento de la referencia y las fallas citadas.
4. Los criterios 17.1–17.4: PASA / NO PASA / NO PROBADO cada uno, con evidencia.
5. Si puedes, otra plataforma u otro usuario de Windows: la guía dice que solo se probó en la máquina de desarrollo.

## Lo que Desarrollo no probó

- El paso 2.1 desde GitHub y `conda env create` real (la revisión interna hizo un `--dry-run`, que resolvió los mismos paquetes
  salvo `conpty` y `tornado`).
- Otra máquina u otro sistema operativo.
- La versión corregida de la guía no tuvo otra pasada del revisor.

## Resultados esperados

- Paso 2.3: **350 passed** (gemelo) y **7 passed** (oráculo).
- Paso 2.5: tres líneas `PASA` y `Resultado: PASA`; con `--completo`, además `modos` 9/9 y `rescate` 9/9.
- Paso 2.6: `git diff` vacío en `oraculo/RESULTADOS.md` (≈ 13 min) y el notebook modificado solo en marcas de tiempo.
- `git status --short` del repositorio real, antes y después: solo los archivos de esta entrega, este archivo y (al final) tu
  reporte y `pruebas_qa/`.
