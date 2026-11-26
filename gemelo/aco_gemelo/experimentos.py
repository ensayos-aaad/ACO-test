"""Experimentos en lote: varias condiciones × varias semillas → un CSV por condición y un resumen.

Un **plan** es un YAML con una configuración base, los factores que se varían y las semillas::

    nombre: modos
    base: ../configs/default.yaml        # relativo al archivo del plan
    semillas: 30                         # semillas 0..29 (o una lista)
    factores:                            # se corren todas las combinaciones
      mundo.escenario: [L, aleatorio]
      madre.modo: [ausente, pista_de_baile, rescate, difusion]

Cada ensayo es determinista con su semilla; los ensayos se reparten entre procesos y luego se ordenan,
así que el resultado no depende de cuántos procesos se usen.
"""

from __future__ import annotations

import copy
import csv
import itertools
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import yaml

from .config import cargar, config_ensayo, crear_mundo
from .metricas import fila, resumen
from .motor import Simulacion

_PLAN = ("nombre", "base", "semillas", "factores")


def cargar_plan(ruta: str | Path) -> dict[str, Any]:
    """Lee un plan y resuelve la ruta de su configuración base."""
    ruta = Path(ruta)
    with open(ruta, encoding="utf-8") as archivo:
        plan = yaml.safe_load(archivo) or {}
    sobran = set(plan) - set(_PLAN)
    if sobran:
        raise ValueError(f"Claves desconocidas en el plan: {sorted(sobran)}. Válidas: {list(_PLAN)}")
    for clave in ("base", "factores"):
        if clave not in plan:
            raise ValueError(f"Al plan le falta '{clave}'")
    plan.setdefault("nombre", ruta.stem)
    plan["base"] = (ruta.parent / plan["base"]).resolve()
    plan["semillas"] = _semillas(plan.get("semillas", 30))
    for clave, valores in plan["factores"].items():
        if "." not in clave or not isinstance(valores, list) or not valores:
            raise ValueError(f"Factor mal escrito: '{clave}' debe ser 'seccion.clave' con una lista de valores")
    return plan


def _entero(valor: Any) -> bool:
    return isinstance(valor, int) and not isinstance(valor, bool)  # en Python, True es un int


def _semillas(valor: Any) -> list[int]:
    """``semillas`` del plan: un entero n ≥ 1 (las semillas 0 … n−1) o una lista no vacía de enteros ≥ 0.

    Se valida al leer el plan, antes de crear la carpeta de salida o correr nada (H2 y H3, ronda 001 de QA): antes,
    ``true`` se tomaba como ``[0]`` y ``1.5``, ``false``, ``0`` o ``-3`` terminaban en una traza sin controlar.
    """
    if _entero(valor):
        if valor < 1:
            raise ValueError(f"semillas = {valor}: si es un número, debe ser al menos 1")
        return list(range(valor))
    if isinstance(valor, list) and valor:
        malas = [s for s in valor if not _entero(s) or s < 0]
        if malas:  # el mismo texto que en ConfigEnsayo y crear_mundo, para los demás puntos de entrada
            raise ValueError(f"semilla = {malas[0]!r} (en 'semillas' del plan): debe ser un entero mayor o "
                             "igual que 0")
        return list(valor)
    raise ValueError(f"semillas = {valor!r}: debe ser un entero ≥ 1 o una lista no vacía de enteros ≥ 0")


def _poner(datos: dict[str, Any], clave: str, valor: Any) -> None:
    seccion, nombre = clave.split(".", 1)
    datos.setdefault(seccion, {})
    if datos[seccion] is None:
        datos[seccion] = {}
    datos[seccion][nombre] = valor


def condiciones(plan: dict[str, Any]) -> list[tuple[str, dict[str, Any], dict[str, Any]]]:
    """Todas las combinaciones de factores: ``(nombre, datos de configuración, valores)``."""
    base = cargar(plan["base"])
    claves = list(plan["factores"])
    salida = []
    for combinacion in itertools.product(*(plan["factores"][c] for c in claves)):
        datos = copy.deepcopy(base)
        valores = dict(zip(claves, combinacion))
        for clave, valor in valores.items():
            _poner(datos, clave, valor)
        # Valida la configuración antes de correr nada, con una semilla del plan: la del archivo base no se usa
        # (H3, ronda 001 de QA).
        config_ensayo(datos, plan["semillas"][0])
        crear_mundo(datos, plan["semillas"][0])
        nombre = "__".join(f"{c.split('.')[-1]}-{v}" for c, v in valores.items())
        salida.append((nombre, datos, valores))
    return salida


def _ensayo(argumentos: tuple[dict[str, Any], int, dict[str, Any]]) -> dict[str, Any]:
    """Un ensayo (en un proceso aparte). Devuelve su fila con los valores de los factores."""
    datos, semilla, valores = argumentos
    resultado = Simulacion(crear_mundo(datos, semilla), config_ensayo(datos, semilla)).correr()
    escenario = (datos.get("mundo") or {}).get("escenario", "L")
    return {**{c.split(".")[-1]: v for c, v in valores.items()}, **fila(semilla, escenario, resultado)}


def _guardar(ruta: Path, filas: list[dict[str, Any]]) -> None:
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)


def _plano(r: dict[str, Any]) -> dict[str, Any]:
    """Aplana el resumen de una condición para el CSV de resumen."""
    salida = {"n": r["n"]}
    for nombre in ("asentadas", "verificadas"):
        t = r[nombre]
        salida.update({f"{nombre}": t["exitos"], f"{nombre}_tasa": round(t["tasa"], 4),
                       f"{nombre}_ic95_bajo": round(t["ic95_bajo"], 4),
                       f"{nombre}_ic95_alto": round(t["ic95_alto"], 4)})
    for clave in ("ticks_media", "ticks_varianza", "ticks_min", "ticks_max", "razon_media",
                  "conocimiento_medio", "bytes_agente_madre_media", "bytes_madre_agente_media"):
        valor = r[clave]
        salida[clave] = None if valor is None else round(valor, 4)
    return salida


def correr_plan(ruta_plan: str | Path, salida: str | Path | None = None,
                procesos: int | None = None) -> Path:
    """Corre un plan completo. Devuelve la carpeta con los CSV.

    Deja ``<condicion>.csv`` (una fila por semilla) y ``resumen.csv`` (una fila por condición).
    """
    plan = cargar_plan(ruta_plan)
    carpeta = Path(salida) if salida else Path(ruta_plan).parent / "datos" / plan["nombre"]
    lista = condiciones(plan)  # valida todo antes de crear la carpeta (H3, ronda 001 de QA)
    carpeta.mkdir(parents=True, exist_ok=True)
    trabajos = [(datos, s, valores) for _, datos, valores in lista for s in plan["semillas"]]
    if procesos == 1:
        filas = [_ensayo(t) for t in trabajos]
    else:
        with ProcessPoolExecutor(max_workers=procesos) as grupo:
            filas = list(grupo.map(_ensayo, trabajos, chunksize=4))
    n = len(plan["semillas"])
    resumenes = []
    for i, (nombre, _, valores) in enumerate(lista):
        de_esta = filas[i * n:(i + 1) * n]
        _guardar(carpeta / f"{nombre}.csv", de_esta)
        resumenes.append({"condicion": nombre, **{c.split(".")[-1]: v for c, v in valores.items()},
                          **_plano(resumen(de_esta))})
    _guardar(carpeta / "resumen.csv", resumenes)
    return carpeta
