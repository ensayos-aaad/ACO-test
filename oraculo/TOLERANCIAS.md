# TOLERANCIAS — declaradas antes de correr

**Declaradas:** 2026-11-17 03:13 -0500, **antes** de escribir o ejecutar el código del oráculo y de la comparación.
**Por:** Claude Opus 5.5, por delegación del operador ("que sea lo que Dios quiera", 2026-11-17; ver
ASSUMPTIONS.md). **No tienen aprobación explícita del operador.** No se cambian después de ver los
resultados: si alguna resulta mal planteada, se registra en FAILURES.md y se declara una nueva versión.

Fuente: `referencia/ACO/experimento_doble-puente/` (idéntica a `hormigas-artificiales/`, I10).
Los notebooks no se modifican: el oráculo ejecuta el código de sus celdas tal cual.

## Parte A — El oráculo reproduce los notebooks (criterios del artefacto 12)

| ID | Qué | Prueba | Tolerancia |
|---|---|---|---|
| A1 | `p1(k, n, delta)`, deneubourg **[5]** | Ejecutar la función de la celda y compararla con la fórmula escrita a mano `(k+m1)^n / ((k+m1)^n + (k+m2)^n)`, con m1 = max(delta, 0) y m2 = max(−delta, 0), en la malla de la celda (n = 1, 2, 4; delta = −30…30; k = 20) | Diferencia absoluta ≤ 1e-12 en todos los puntos |
| A2 | Dinámica con retardo, deneubourg **[7]** | Ejecutar la celda completa (con matplotlib sin ventana) y leer `p_s_hist`. Es determinista | (a) Dos ejecuciones dan exactamente lo mismo; (b) **p_s al final (t = T − 1) ≥ 0,9**: la celda afirma que converge a la rama corta (r = 2) |
| A3 | Histograma de Montecarlo, montecarlo_aco **[4]** | Ejecutar `experimento_individual(ratio_r, alpha=2)` (extraída de la celda sin cambios), **N = 1000** experimentos por r, semilla `numpy.random.seed(2026)`, los 5 bins de la celda | (a) Misma semilla ⇒ mismo histograma; (b) **r = 1:** bins 0–20 % + 80–100 % ≥ **70 %** de los experimentos (forma de "U"); (c) **r = 2:** bin 80–100 % ≥ **70 %** |
| A4 | f'(1/2) = α, deneubourg **[9]** | Ejecutar el cálculo simbólico de la celda | Resultado simbólico igual a α |

## Parte B — El gemelo frente al oráculo (criterios C1–C5 de PROMPT-ZERO)

Gemelo: `gemelo/configs/puente_doble.yaml` tal como está (6 agentes, sin madre, sin evaporación,
k = 20, α = 2, depósito constante, ancho 3). **N = 100 semillas** (0–99) por valor de r.

**Estadístico por ensayo, x** = fracción de las agentes asentadas cuya ruta final pasa por la rama corta
(con r = 1, la rama "corta" es la de abajo). En el oráculo, x = fracción de las hormigas 501–1000 que
eligieron la rama corta (la definición de la celda [4]). Un ensayo del gemelo que no se asienta dentro
del límite cuenta como "no converge".

| ID | Criterio | Prueba | PASA si |
|---|---|---|---|
| C1 | Regla de decisión | Frecuencia con que el agente del gemelo elige la rama corta frente a `p1` **del oráculo** (A1), en los casos de la malla con delta = −15…15 (en 16 niveles el gemelo solo ve hasta 15 depósitos por rama), N = 20 000 elecciones por caso, semilla fija | En todos los casos, \|frecuencia − p1\| ≤ 4 desviaciones estándar de una binomial |
| C2 | Ruptura de simetría (r = 1) | En el gemelo: fracción de ensayos con x ≤ 0,2 o x ≥ 0,8, y, entre esos, cuántos gana la rama de abajo | (a) Fracción ≥ **0,7** (el mismo umbral que A3-b); **y** (b) prueba binomial bilateral de "gana abajo" frente a 0,5 con p > 0,05 |
| C3 | Ramas desiguales (r = 2) | P_gemelo = fracción de ensayos con x ≥ 0,8; P_oráculo = la misma fracción en A3 | \|P_gemelo − P_oráculo\| ≤ **0,15** |
| C4 | Puntos fijos | (a) A4 (f'(1/2) = α = 2 > 1 ⇒ p = 1/2 inestable); (b) en el gemelo con r = 1, fracción de ensayos con 0,4 ≤ x ≤ 0,6 | (a) se cumple **y** (b) fracción ≤ **0,2** |
| C5 | Determinismo auditable | Misma semilla ⇒ mismo resultado, en el gemelo (con semilla registrada) y en el oráculo (A2-a, A3-a) | Se cumple en ambos |

C6 (criterio pedagógico) queda **NO PROBADO**: lo evalúa el operador.

## Parte C — Informativo (no es criterio)

Se correrá también el gemelo con **60 agentes** en el puente doble (r = 1 y r = 2) para ver si el tamaño
de la colonia cambia el resultado. Solo se reporta; no decide ningún PASA / NO PASA.
