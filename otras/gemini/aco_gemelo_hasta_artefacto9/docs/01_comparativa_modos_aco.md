# Comparativa de los 4 modos de coordinación de la madre (30 semillas)

**Archivo de datos:** `resultados/experimento_30_semillas.csv`  
**Gráfica asociada:** `docs/img/fig1_comparativa_modos_aco.png`

## 1. Objetivo y configuración experimental

Evaluar el impacto de los cuatro modos de la madre (`AUSENTE`, `PISTA_DE_BAILE`, `RESCATE` y `DIFUSION`) sobre el tiempo de asentamiento, la tasa de verificación (criterio G1) y la calidad de ruta respecto al óptimo BFS en el escenario de cuadrícula en **L** ($8 \times 8$, 8-vecindad sin corte de esquinas, distancia óptima $\ge 4$, 6 agentes exploradores, $K = 64$, radio de comunicación $r = 1$, $\Delta t = 10$ ticks, evaporación $\rho = 0.0$, límite $2000$ ticks, semillas $0\dots 29$).

## 2. Resumen cuantitativo (30 semillas por modo)

| Modo de madre | Tasa de convergencia (G1) | Ticks totales (media ± DE) | Ticks exploración (media ± DE) | Calidad de ruta $L_{\text{verif}}/L_{\text{BFS}}$ (media ± DE) | Hallazgo principal |
|---|---|---|---|---|---|
| `AUSENTE` | 20/30 (66.7 %) | 112.6 ± 42.8 | 102.4 ± 43.8 | 1.78 ± 1.20 | Línea base estigmérgica sin coordinación central |
| `PISTA_DE_BAILE` | 21/30 (70.0 %) | 84.0 ± 25.3 | 74.5 ± 23.3 | 1.34 ± 0.50 | `DANZA` → `RECLUTA` → `RUTA` acelera el reclutamiento y acorta rutas |
| `RESCATE` | 20/30 (66.7 %) | 112.6 ± 42.8 | 102.4 ± 43.8 | 1.78 ± 1.20 | Aunque se emiten 23 envíos de rescate, el umbral $<50\%$ (I14) no altera las trayectorias finales |
| `DIFUSION` | 24/30 (80.0 %) | 68.8 ± 28.0 | 58.4 ± 23.3 | 1.47 ± 0.91 | Difusión periódica de `MAPA` logra el menor tiempo medio y la mayor tasa de verificación |

## 3. Diagnóstico técnico

1. **Efecto del reclutamiento y la difusión:** tanto `PISTA_DE_BAILE` como `DIFUSION` reducen de forma sustancial la media y la dispersión de `ticks_exploracion` (de $102.4$ ticks a $74.5$ y $58.4$ ticks respectivamente) y mejoran la calidad media de ruta respecto a `AUSENTE` ($1.34$ y $1.47$ frente a $1.78$).
2. **Cuello de botella de la verificadora (F-009 / F-010):** en el 100 % de las corridas (120/120), las 6 exploradoras alcanzan `Estado.ASENTADA` dentro del límite de 2000 ticks. Todos los casos no convergentes (`MotivoFin.VERIFICADORA_FALLO`) ocurren en la etapa de verificación, cuando la verificadora entra en un callejón formado por rastros cruzados y no puede retroceder (regla I12).
3. **Calibración pendiente del modo rescate:** con el umbral por defecto de experiencia $< 50\%$ del promedio de la colonia (I14), los rescates ocurren tarde en la exploración sin modificar el desempeño agregado respecto a `AUSENTE`, dejando la hipótesis de `resumen.pdf` lista para barrido paramétrico en el Artefacto 14.
