# Revisión interna previa — ronda 003 de QA (artefacto 17, guía de reproducción)

**Autor:** agente `revisor` · **Fecha:** 2026-11-25 (≈ 21:45–22:15 -0500) · **Montaje:** clon de `d:/experimento/ACO-test`
(`815e629`) más los cambios sin commit (`git diff HEAD` y los archivos sin seguimiento), igual al árbol de trabajo. El
paso 2.1 (clonar desde GitHub) no se probó tal cual: la guía aún no está publicada.

**Veredicto: NO PASA** por H1 y H2, más textos (H6–H9). En esta máquina la reproducción sí sale completa.

| Paso | Resultado |
|---|---|
| 2.2 | Entorno `aco-gemelo` existente: Python 3.12.7 y los 13 paquetes coinciden con `environment.yml`; un `conda create --dry-run` resuelve los mismos 179 paquetes salvo `conpty` y `tornado`. No se creó un entorno nuevo |
| 2.3 | Gemelo **349 passed** (286 s), no 347; oráculo 7 passed (10,5 s); figuras sin cambios |
| 2.4 | Texto igual al esperado; PNG igual byte a byte; deja `gemelo/final.png` sin seguimiento (H3) |
| 2.5 | PASA (22 s); `--completo` PASA con 9/9 y 9/9 CSV (185 s en total) |
| 2.6 | Notebook 83 s (máquina cargada), salidas idénticas; `oraculo/comparar.py` 731 s, `git diff` de `RESULTADOS.md` vacío |

Mutantes: texto, CSV y un CSV publicado alterados → NO PASA, código 1. **PNG alterado → PASA (H1).** `test_reproducir.py`
no falla con `_mismos_pixeles` forzado a verdadero.

## Hallazgos

- **H1 (grave):** `comparar.py:54`, `ImageChops.difference(x, y).getbbox() is None`: con RGBA, Pillow 10.4 solo mira el alfa;
  una imagen negra o invertida da True. Falsas "PNG, píxel a píxel" (`REPRODUCIR.md:122`, `:173`) y la parte PNG del
  criterio 17.2.
- **H2 (medio):** la guía y `ARTEFACTOS.md` decían 347; salen 349 (347 + 2 de `test_reproducir.py`).
- **H3 (leve):** `--png final.png` deja un archivo suelto; usar `resultados/final.png` (ignorado por git).
- **H4 (leve):** tras `nbconvert`, `analisis.ipynb` aparece modificado solo por marcas de tiempo de ejecución.
- **H5 (leve):** el bloque de salida de `comparar.py` omitía la primera línea (`Python: ...`).
- **H6 (leve):** prerrequisitos de fases 2–3: pyserial está en Anaconda *base*, no en `aco-gemelo`; se callaba lo que el
  checklist marca sin probar (`py:setup` → `serial`, par COM1 ↔ COM2, Wokwi, toolchain).
- **H7 (leve):** la hipótesis es que *el rescate* reduce la varianza (no "la madre"), y F-019 la limita a la configuración
  actual, con pruebas exploratorias.
- **H8 (leve):** `list-ports.py` solo está en `ejemplo4/`; el 5 trae el código en su README.
- **H9 (leve):** F-023 dice "pérdidas o retardo"; la regresión de F-029 no fue de reproducibilidad.
- Muy leves: `--completo` tarda ≈ 2,7 min más (no 5); `environment.yml` fija solo dependencias directas; `comparar.py`
  escribe `__pycache__` (ignorado) y deja `%TEMP%\aco-reproducir-ultima` cuando da NO PASA.

Los 30 enlaces relativos existen; el resto de las afirmaciones coincide con su fuente.

| Criterio | Estado |
|---|---|
| 17.1 | PASA (con H6) |
| 17.2 | NO PASA por H1 y H2 (la reproducción en sí PASA aquí; QA, NO PROBADO) |
| 17.3 | NO PASA solo por textos (H6–H9) |
| 17.4 | PASA |

**No comprobado:** 2.1 desde GitHub; `conda env create` real; otra máquina u otro sistema; el "≈ 30 s" del notebook; que los
criterios se declararan antes de escribir la guía (solo la hora de `ARTEFACTOS.md`).

**Atendido por la orquestadora antes de entregar (2026-11-25 22:28):** H1 (comparación de bytes de todos los canales y una
prueba que altera un píxel; la función vieja daba True con un píxel cambiado y con una imagen negra, la nueva da False),
H2 (la cifra medida tras la prueba nueva es **350**), H3–H9 y las observaciones de tiempo y de `environment.yml`, con la
redacción del revisor donde la dio. F-031.
