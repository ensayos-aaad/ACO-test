"""El oráculo: ejecuta el código de los notebooks de ``referencia/`` tal como está.

No se copia ni se modifica nada: el código se lee de la celda indicada del notebook (archivo y
número de celda, base 0) y se ejecuta. Así, si la referencia cambiara, el oráculo lo notaría.
Las funciones se extraen de la celda con ``ast``, para no ejecutar la parte de gráficas o widgets.

Celdas usadas (ver ``TOLERANCIAS.md``):

- ``deneubourg_puente_doble.ipynb`` [5]: ``p1(k, n, delta)``, la fórmula de elección.
- ``deneubourg_puente_doble.ipynb`` [7]: la dinámica con retardo (campo medio, determinista).
- ``deneubourg_puente_doble.ipynb`` [9]: f'(1/2) con sympy.
- ``montecarlo_aco.ipynb`` [4]: ``experimento_individual(ratio_r, alpha)`` y los bins del histograma.
"""

from __future__ import annotations

import ast
import contextlib
import io
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402

CARPETA = Path(__file__).resolve().parent.parent / "referencia" / "ACO" / "experimento_doble-puente"
DENEUBOURG = "deneubourg_puente_doble.ipynb"
MONTECARLO = "montecarlo_aco.ipynb"
#: Bins del histograma de la celda montecarlo_aco [4] (`bins = [0, 20, 40, 60, 80, 100]`).
BINS = [0, 20, 40, 60, 80, 100]


def celda(notebook: str, indice: int) -> str:
    """Código fuente de una celda de código."""
    datos = json.loads((CARPETA / notebook).read_text(encoding="utf-8"))
    c = datos["cells"][indice]
    if c["cell_type"] != "code":
        raise ValueError(f"{notebook} [{indice}] no es una celda de código")
    return "".join(c["source"])


def funcion(notebook: str, indice: int, nombre: str, globales: dict[str, Any]) -> Callable:
    """Extrae y define una función de una celda, sin ejecutar el resto de la celda."""
    arbol = ast.parse(celda(notebook, indice))
    for nodo in arbol.body:
        if isinstance(nodo, ast.FunctionDef) and nodo.name == nombre:
            modulo = ast.Module(body=[nodo], type_ignores=[])
            espacio = dict(globales)
            exec(compile(modulo, f"{notebook}[{indice}]", "exec"), espacio)  # noqa: S102
            return espacio[nombre]
    raise ValueError(f"No hay una función '{nombre}' en {notebook} [{indice}]")


def ejecutar(notebook: str, indice: int, globales: dict[str, Any]) -> dict[str, Any]:
    """Ejecuta una celda completa y devuelve sus variables (y lo que imprimió, en ``_salida``)."""
    espacio = dict(globales)
    salida = io.StringIO()
    with contextlib.redirect_stdout(salida):
        exec(compile(celda(notebook, indice), f"{notebook}[{indice}]", "exec"), espacio)  # noqa: S102
    plt.close("all")
    espacio["_salida"] = salida.getvalue()
    return espacio


# ----------------------------------------------------------------------------- A1, A2, A4


def p1() -> Callable:
    """``p1(k, n, delta)`` de deneubourg [5]."""
    return funcion(DENEUBOURG, 5, "p1", {"np": np})


def dinamica() -> dict[str, Any]:
    """Ejecuta deneubourg [7]. Devuelve ``p_s_hist``, ``phi_s``, ``phi_l`` y sus parámetros."""
    espacio = ejecutar(DENEUBOURG, 7, {"np": np, "plt": plt})
    claves = ("p_s_hist", "phi_s", "phi_l", "c", "t_s", "r", "T", "alpha", "k")
    return {clave: espacio[clave] for clave in claves}


def derivada_en_medio() -> sp.Expr:
    """f'(1/2) simbólico, calculado por deneubourg [9]."""
    return ejecutar(DENEUBOURG, 9, {"sp": sp})["f_prime_at_half"]


# ----------------------------------------------------------------------------- A3


def experimento_individual() -> Callable:
    """``experimento_individual(ratio_r, alpha)`` de montecarlo_aco [4]."""
    return funcion(MONTECARLO, 4, "experimento_individual", {"np": np})


@lru_cache(maxsize=None)
def montecarlo(ratio_r: float, alpha: float = 2.0, n: int = 1000, semilla: int = 2026):
    """N experimentos de la celda montecarlo_aco [4] con la semilla de numpy fijada.

    Devuelve ``(x, porcentajes)``: x es el % de tráfico en la rama corta de cada experimento
    (hormigas 501–1000) y porcentajes el % de experimentos en cada uno de los 5 bins.
    """
    experimento = experimento_individual()
    np.random.seed(semilla)
    x = tuple(experimento(ratio_r, alpha) for _ in range(n))
    conteos, _ = np.histogram(x, bins=BINS)  # como en la celda [4]
    return x, tuple(float(v) for v in conteos / n * 100.0)
