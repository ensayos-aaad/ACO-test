# RESULTADOS — gemelo frente al oráculo

Generado por `python -X utf8 oraculo/comparar.py`. Pruebas y tolerancias: `TOLERANCIAS.md`
(declaradas antes de correr). Gemelo: `gemelo/configs/puente_doble.yaml`, 100 semillas por r: 6 agentes, 50 viajes, salida cada 1 tick(s), k = 1.0, tau_max = 300.

## Resumen

| Criterio | Resultado | Valor medido | Umbral declarado |
|---|---|---|---|
| C1 Regla de decisión | **PASA** | máx. \|z\| = 0.94 en 31 casos | \|z\| ≤ 4 en todos |
| C2 Ruptura de simetría (r = 1) | **PASA** | extremos 0.75; gana abajo 34/75 (p = 0.489) | extremos ≥ 0,7 y p > 0,05 |
| C3 Ramas desiguales (r = 2) | **NO PASA** | gemelo 0.48 frente a oráculo 0.75 (diferencia 0.27) | diferencia ≤ 0,15 |
| C4 Puntos fijos | **PASA** | f'(1/2) = alpha; ensayos con x en [0,4; 0,6]: 0.06 | f'(1/2) = α y ≤ 0,2 |
| C5 Determinismo | **PASA** | gemelo y oráculo repiten con la misma semilla | igualdad exacta |
| C6 Pedagógico | NO PROBADO | — | lo evalúa el operador |

## Histogramas (% de ensayos por bin de tráfico en la rama corta: 0–20 · 20–40 · 40–60 · 60–80 · 80–100)

| | r = 1 | r = 2 |
|---|---|---|
| Oráculo (montecarlo_aco [4], 1000 hormigas, N = 1000) | 35 % · 11 % · 8 % · 10 % · 36 % | 5 % · 5 % · 6 % · 9 % · 75 % |
| Gemelo (6 agentes, N = 100) | 41 % · 8 % · 6 % · 11 % · 34 % | 20 % · 7 % · 9 % · 16 % · 48 % |
| Gemelo con 60 agentes, 10 semillas (informativo, parte C) | 0 % · 10 % · 80 % · 10 % · 0 % | 0 % · 0 % · 80 % · 20 % · 0 % |
| Gemelo, tráfico de la 2.ª mitad de los viajes (informativo, J6) | 26 % · 21 % · 15 % · 19 % · 19 % | 12 % · 12 % · 15 % · 21 % · 40 % |

Ensayos del gemelo que no se asentaron (6 agentes, ambos r): 0.
Con 60 agentes: extremos en r = 1 = 0.00; x ≥ 0,8 en r = 2 = 0.00.

## C1 en detalle

| delta | p1 del oráculo | frecuencia del gemelo | z |
|---|---|---|---|
| -15 | 0.2462 | 0.2452 | -0.31 |
| -14 | 0.2571 | 0.2567 | -0.10 |
| -13 | 0.2686 | 0.2687 | +0.02 |
| -12 | 0.2809 | 0.2809 | +0.02 |
| -11 | 0.2939 | 0.2940 | +0.03 |
| -10 | 0.3077 | 0.3082 | +0.16 |
| -9 | 0.3223 | 0.3226 | +0.08 |
| -8 | 0.3378 | 0.3386 | +0.23 |
| -7 | 0.3543 | 0.3565 | +0.65 |
| -6 | 0.3717 | 0.3745 | +0.79 |
| -5 | 0.3902 | 0.3918 | +0.47 |
| -4 | 0.4098 | 0.4101 | +0.08 |
| -3 | 0.4306 | 0.4292 | -0.39 |
| -2 | 0.4525 | 0.4505 | -0.57 |
| -1 | 0.4756 | 0.4747 | -0.28 |
| 0 | 0.5000 | 0.4991 | -0.24 |
| 1 | 0.5244 | 0.5226 | -0.49 |
| 2 | 0.5475 | 0.5442 | -0.94 |
| 3 | 0.5694 | 0.5665 | -0.84 |
| 4 | 0.5902 | 0.5882 | -0.56 |
| 5 | 0.6098 | 0.6075 | -0.65 |
| 6 | 0.6283 | 0.6277 | -0.16 |
| 7 | 0.6457 | 0.6451 | -0.18 |
| 8 | 0.6622 | 0.6594 | -0.83 |
| 9 | 0.6777 | 0.6755 | -0.66 |
| 10 | 0.6923 | 0.6899 | -0.72 |
| 11 | 0.7061 | 0.7040 | -0.65 |
| 12 | 0.7191 | 0.7173 | -0.57 |
| 13 | 0.7314 | 0.7291 | -0.72 |
| 14 | 0.7429 | 0.7414 | -0.50 |
| 15 | 0.7538 | 0.7529 | -0.33 |
