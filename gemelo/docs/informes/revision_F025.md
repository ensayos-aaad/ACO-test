# Revisión F-025 — confirmación de N1 y N2 y veredicto final del bloque B + C

**Autor:** agente `revisor` · **Fecha:** 2026-11-19 (≈ 23:30–23:38 -0500) · **Código revisado:** árbol de trabajo
sobre `693c694` · Scripts en `revision_F025/` (`indep.py`, `repro.py`, `filas.py`, `muestra_lb.py` y los mutantes
`mut_n1.py`, `mut_hash.py`).

**Veredicto global: PASA.** N1 y N2 corregidos; los 8 puntos de F-023 siguen en PASA; el arreglo no introduce defectos
que bloqueen.

| Punto | Veredicto | Evidencia |
|---|---|---|
| N1 | PASA | `canal.py` usa `Random(f"canal:{semilla}:{src}")`. Con `r3.py` ninguna agente comparte estado con su canal; la agente 1 y su canal no tienen ningún número en común |
| N2 | PASA | `indep.py`, 12 semillas (0, 1, −1, −2, 7, 255, 256, −256, 65535, 2³¹, −2³¹, 10¹²): 3000 números de cada generador del canal frente a las agentes 1–8 y el mundo: 0 valores compartidos, 0 estados iguales |
| Reproducible entre procesos | PASA | `repro.py`, PYTHONHASHSEED = 0, 1, 12345 y aleatorio: el mismo hash en las 4 corridas |
| La prueba nueva detecta el defecto | PASA | Con el mutante de la fórmula vieja falla en sus 4 semillas |
| Suites | PASA | 318 del gemelo y 7 del oráculo |
| `r1.py` | PASA | 0 de 576 diferencias entre `hilos_sincronos` y el determinista |
| Planes publicados | PASA | 18 CSV idénticos byte a byte |
| Cifras de la línea base (`datos_despues_n1/`) | PASA | Contadas por separado: coinciden con `informe.md` y F-025; 80 filas recalculadas con el código actual, 0 diferencias |

## Hallazgos (ninguno bloquea)

1. **Leve:** ninguna prueba vigila la reproducibilidad entre procesos. Un mutante que siembra con
   `hash(f"canal:{semilla}:{src}")` (depende de PYTHONHASHSEED) pasa las 127 pruebas de canal, motor, CLI y experimentos.
   Sugerencia: una prueba con dos subprocesos de PYTHONHASHSEED distinto.
2. **Leve, previo y fuera de B + C:** Python siembra con el valor absoluto, así que la semilla −3 da el mismo mundo que la 3
   (`config.py:142`). No afecta a los experimentos (semillas 0–29). El canal ya no tiene este problema.
3. **Informativo:** la última línea de `r3.py` siempre da True; por eso se usó `indep.py`.

**No comprobado:** la línea base completa (solo los CSV y una muestra de 80 filas); el motor `hilos` asíncrono con madre
más allá de la suite; una revisión a fondo de nuevo de `test_b3`, `test_b5`, `test_b7`, el personalizado y la
visualización (ya dados PASA antes).
