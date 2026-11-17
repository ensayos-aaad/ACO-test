# experimentos/

Planes de experimentos del gemelo. Cada plan es un YAML con una configuración base, los factores que se
varían y las semillas (ver la documentación de `aco_gemelo/experimentos.py`).

| Plan | Pregunta |
|---|---|
| `modos.yaml` | ¿Qué hace cada modo de la madre (ausente, pista de baile, rescate, difusión) en el mundo L y en mundos aleatorios? |
| `rescate.yaml` | ¿Reduce el rescate la varianza del tiempo de convergencia (hipótesis de `referencia/resumen.pdf`) si el umbral permite que se dispare? |

Correr (desde `gemelo/`, con el Python del entorno `aco-gemelo`):

```
python -X utf8 -m aco_gemelo experimentos --plan experimentos/modos.yaml
python -X utf8 -m aco_gemelo experimentos --plan experimentos/rescate.yaml
```

Cada plan deja en `datos/<nombre>/` un CSV por condición (una fila por semilla) y `resumen.csv` (una fila
por condición, con tasas e intervalos de confianza de Wilson al 95 %). Los resultados no dependen del número
de procesos: cada ensayo es determinista con su semilla.
