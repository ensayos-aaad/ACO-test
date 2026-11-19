# Validación de la regla de decisión de Deneubourg en el escenario de puente doble (Criterio C1)

**Implementación de referencia:** `gemelo/aco_gemelo/mundo/escenarios.py` (`puente_doble`) y `gemelo/tests/test_agente.py`  
**Gráfica asociada:** `docs/img/fig4_regla_deneubourg_puente_doble.png`

## 1. Modelo matemático y coherencia con los notebooks oráculo

En el escenario paramétrico `puente_doble(r, ancho)`, una colonia elige entre dos ramas con depósitos acumulados $m_1$ y $m_2$. Con heurística neutra ($\eta = 1$, $\beta = 0$), offset $k = 20$ y exponente $\alpha = 2$ (decisiones D1, I1, I2), la probabilidad de transición del agente en el gemelo sigue la ecuación 1.1 de Deneubourg et al. (1990) / Dorigo & Stützle (cap. 1):

$$p_1(m_1, m_2) = \frac{(m_1 + k)^{\alpha}}{(m_1 + k)^{\alpha} + (m_2 + k)^{\alpha}}$$

## 2. Resultados de verificación

- **Curva teórica vs. empírica (C1):** sobre 6 combinaciones de diferencia de feromona $(m_1, m_2)$ con $N = 20\,000$ decisiones por caso (`tests/test_agente.py`), la frecuencia empírica del programa de agente reproduce la curva analítica del notebook oráculo `deneubourg_puente_doble.ipynb` (celda `[5]`) dentro de la tolerancia estadística declarada.
- **Amplificación no lineal ($\alpha = 2$):** frente al caso lineal ($\alpha = 1$), el exponente cuadrático produce la curva sigmoidea característica que rompe la simetría cuando $r = 1$ (criterio C2) y amplifica la ventaja temporal de la rama corta cuando $r = 2$ (criterio C3), dejando listo el terreno para conectar el oráculo completo en el Artefacto 12.
