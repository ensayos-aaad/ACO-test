# oraculo/

Ejecuta la implementación de referencia (los notebooks de `../referencia/`) y compara el gemelo contra ella.

| Archivo | Qué hace |
|---|---|
| `TOLERANCIAS.md` | Pruebas y tolerancias, **declaradas antes de correr** (2026-11-17 03:13 -0500) |
| `oraculo.py` | Lee el código de las celdas de los notebooks **tal cual** (sin copiarlo ni modificarlo) y lo ejecuta: `p1` (deneubourg [5]), dinámica con retardo (deneubourg [7]), f'(1/2) (deneubourg [9]), `experimento_individual` (montecarlo_aco [4]) |
| `test_oraculo.py` | Parte A: el oráculo reproduce los notebooks (7 pruebas) |
| `comparar.py` | Parte B: el gemelo frente al oráculo (criterios C1–C5); escribe `RESULTADOS.md` |
| `RESULTADOS.md` | Último resultado de la comparación |

Desde la raíz del repositorio, con el Python del entorno `aco-gemelo`:

```
python -X utf8 -m pytest oraculo -q        # parte A
python -X utf8 oraculo/comparar.py         # parte B (unos minutos)
```

Reglas: nada en `../referencia/` se modifica (lo comprueba una prueba); las pruebas estocásticas fijan la
semilla (`numpy.random.seed(2026)` en el oráculo; semillas 0–99 en el gemelo).
