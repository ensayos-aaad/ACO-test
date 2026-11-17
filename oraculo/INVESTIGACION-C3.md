# Investigación: ¿por qué C3 da NO PASA? (F-015)

**Fecha:** 2026-11-17 04:42 -0500 · **Por:** Claude Opus 5.5, a pedido del operador ("Investiga").
**Carácter:** exploratorio. **No cambia el producto ni los criterios** (`TOLERANCIAS.md` sigue igual).
Las variantes que tocan la percepción se hacen reemplazando funciones **solo dentro del script**.
Reproducir: `python -X utf8 oraculo/investigacion_c3.py <variante> <r> 100` (resultados en `investigacion_c3/`).

## Hipótesis (escritas antes de correr)

- **H1, resolución:** la agente ve la feromona en 16 niveles lineales de 20 depósitos; las primeras diferencias se pierden.
- **H2, pocas decisiones:** el gemelo toma 300 decisiones por ensayo (6 agentes × 50 viajes); el notebook usa 1000 hormigas.
- **H3, granularidad del estadístico:** con 6 agentes, x ≥ 0,8 exige 5 o 6 de 6.

## Resultados (100 semillas por celda; oráculo con r = 2: x ≥ 0,8 en el **0,75** de los ensayos, tráfico medio en la corta **0,82**)

| Variante | Percepción | Viajes | r = 1: extremos (C2 ≥ 0,7) | r = 2: final ≥ 0,8 (C3: 0,60–0,90) | r = 2: tráfico tardío ≥ 0,8 | r = 2: tráfico tardío medio |
|---|---|---|---|---|---|---|
| base (actual) | 16 niveles lineales, 1 nivel = 20 dep. | 50 | 0,75 | 0,48 | 0,40 | 0,62 |
| L10 | 16 lineales, 1 nivel = 10 dep. | 50 | 0,50 | 0,41 | 0,34 | 0,62 |
| L40 | 16 lineales, 1 nivel = 40 dep. | 50 | 0,68 | 0,41 | 0,37 | 0,59 |
| ideal | **exacta** (sin cuantizar; no cabe en el protocolo) | 50 | 0,75 | 0,41 | 0,35 | 0,63 |
| log | 16 niveles **logarítmicos** (mismos 4 bits) | 50 | 0,71 | 0,50 | 0,34 | 0,62 |
| base_170 | 16 lineales, 1 nivel = 20 dep. | 170 | 0,47 | 0,34 | 0,32 | 0,62 |
| ideal_170 | exacta | 170 | **0,90** | **0,65** | 0,60 | 0,69 |
| log_170 | 16 logarítmicos | 170 | **0,85** | 0,58 | 0,54 | 0,66 |
| q8_170 | **256 niveles lineales (8 bits)**, 1 nivel = 4 dep. | 170 | **0,89** | **0,62** | 0,62 | 0,66 |

(170 viajes × 6 agentes ≈ 1000 decisiones, como las 1000 hormigas del notebook.)

## Conclusiones

1. **H2 es la causa principal.** Con 300 decisiones ni siquiera la percepción exacta alcanza (0,41). Con unas 1000 decisiones, la percepción exacta llega a 0,65: estaría dentro de la tolerancia de C3 (|0,65 − 0,75| = 0,10 ≤ 0,15).
2. **H1 importa solo cuando hay muchas decisiones.** Con 1000 decisiones, 16 niveles lineales se **saturan** (base_170: 0,34, peor que con 50 viajes, y C2 también cae a 0,47). Los niveles logarítmicos resuelven el rango con los mismos 4 bits (0,58, pero no alcanzan la tolerancia por 0,02). 8 bits (0,62) se acercan a la percepción exacta.
3. **H3 se descarta.** El tráfico tardío, que no tiene el problema de granularidad, da valores parecidos o menores que la fracción final.
4. **Lo que queda de diferencia** (0,62–0,65 frente a 0,75): en r = 2 el gemelo converge con fuerza (extremos 0,94 en q8_170), pero **hacia la rama larga en ~1 de cada 3 ensayos**, contra 5 % en el oráculo. Con solo 6 agentes, las fluctuaciones del principio fijan la elección antes de que se acumule la ventaja de tiempo de la rama corta. **No se comprobó.**

## Advertencia de método

Estas variantes se eligieron por hipótesis, no barriendo valores hasta pasar. Aun así, adoptar una ahora sería
ajustar el sistema después de ver los resultados. Si el operador adopta un cambio, hay que **declararlo como
decisión** y volver a correr `oraculo/comparar.py` con las tolerancias de siempre.
