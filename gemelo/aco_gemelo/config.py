"""Configuración de un ensayo desde un archivo YAML.

Todo lo que define un ensayo sale del YAML: el mundo (escenario y escalas de feromona), la
colonia, las agentes, la madre y el canal. Una clave desconocida es un error, para que un
nombre mal escrito no pase en silencio. Los archivos de ejemplo están en ``gemelo/configs/``.
"""

from __future__ import annotations

import random
from dataclasses import fields
from fractions import Fraction
from pathlib import Path
from typing import Any

import yaml

from .agente import ConfigAgente
from .madre import ConfigMadre, Modo
from .motor import ConfigEnsayo
from .mundo import Mundo, mundo_aleatorio, mundo_l, puente_doble

ESCENARIOS = ("L", "aleatorio", "puente_doble", "personalizado")

_MUNDO = {"escenario": "L", "ancho": 8, "alto": 8, "densidad": 0.2, "distancia_minima": 4,
          "r": 2, "ancho_puente": 3, "tau_max": 1.0, "unidad_deposito": "1/255",
          "obstaculos": [], "inicio": None, "meta": None}
_SECCIONES = ("semilla", "mundo", "ensayo", "agente", "madre", "canal")
_CANAL = ("radio", "p_perdida", "retardo", "formato")
_DERIVADOS = ("con_madre", "verificadora", "informa_mapa")  # los fija el motor según el modo
_MAX_INTENTOS = 10_000


def _numero(valor: Any) -> float:
    """Acepta números y fracciones escritas como texto (por ejemplo ``"1/255"``)."""
    return float(Fraction(valor)) if isinstance(valor, str) else float(valor)


def _revisar(seccion: str, dado: dict[str, Any], validas) -> None:
    if not isinstance(dado, dict):
        raise ValueError(f"La sección '{seccion}' debe ser un mapa de clave: valor")
    sobran = set(dado) - set(validas)
    if sobran:
        raise ValueError(f"Claves desconocidas en '{seccion}': {sorted(sobran)}. "
                         f"Válidas: {sorted(validas)}")


def cargar(ruta: str | Path) -> dict[str, Any]:
    """Lee un YAML de configuración y comprueba sus secciones."""
    with open(ruta, encoding="utf-8") as archivo:
        datos = yaml.safe_load(archivo) or {}
    _revisar("(raíz)", datos, _SECCIONES)
    return datos


def _modo(valor: Any) -> Modo:
    if isinstance(valor, str):
        try:
            return Modo[valor.upper()]
        except KeyError:
            raise ValueError(f"Modo de madre desconocido: {valor!r}. "
                             f"Válidos: {[m.name.lower() for m in Modo]}") from None
    return Modo(valor)


def config_ensayo(datos: dict[str, Any], semilla: int | None = None) -> ConfigEnsayo:
    """Arma la configuración del ensayo. ``semilla`` reemplaza a la del archivo."""
    agente = dict(datos.get("agente") or {})
    _revisar("agente", agente, [f.name for f in fields(ConfigAgente) if f.name not in _DERIVADOS])
    madre = dict(datos.get("madre") or {})
    _revisar("madre", madre, [f.name for f in fields(ConfigMadre)])
    if "modo" in madre:
        madre["modo"] = _modo(madre["modo"])
    canal = dict(datos.get("canal") or {})
    _revisar("canal", canal, _CANAL)
    if "retardo" in canal:
        canal["retardo"] = tuple(canal["retardo"])
    ensayo = dict(datos.get("ensayo") or {})
    _revisar("ensayo", ensayo, ("n_agentes", "limite", "rho", "registrar", "pausa", "salida_cada"))
    return ConfigEnsayo(
        semilla=datos.get("semilla", 0) if semilla is None else semilla,
        agente=ConfigAgente(**agente), madre=ConfigMadre(**madre), **ensayo, **canal)


def _celda(valor: Any, nombre: str) -> tuple[int, int]:
    if not (isinstance(valor, (list, tuple)) and len(valor) == 2
            and all(isinstance(v, int) and not isinstance(v, bool) for v in valor)):
        raise ValueError(f"'{nombre}' debe ser una celda [x, y] con dos enteros, no {valor!r}")
    return (valor[0], valor[1])


def _mundo_personalizado(mundo: dict[str, Any], escalas: dict[str, float]) -> Mundo:
    """Mundo escrito a mano en el YAML: obstáculos, inicio y meta fijos (B6, idea de Gemini).

    No usa la semilla ni ``distancia_minima``: el mundo es exactamente el que se escribe. Debe
    haber camino entre el inicio y la meta, y no pueden coincidir (F-023, punto 4: con inicio =
    meta el ensayo es trivial y la pista de baile dividía por cero). Un obstáculo repetido es
    un error, porque suele ser una celda mal copiada.
    """
    if mundo["inicio"] is None or mundo["meta"] is None:
        raise ValueError("El escenario personalizado necesita 'inicio' y 'meta'")
    if not isinstance(mundo["obstaculos"], list):
        raise ValueError("'obstaculos' debe ser una lista de celdas [x, y]")
    obstaculos = [_celda(c, "obstaculos") for c in mundo["obstaculos"]]
    repetidos = sorted({c for c in obstaculos if obstaculos.count(c) > 1})
    if repetidos:
        raise ValueError(f"Obstáculos repetidos en el escenario personalizado: {repetidos}")
    if _celda(mundo["inicio"], "inicio") == _celda(mundo["meta"], "meta"):
        raise ValueError("En el escenario personalizado el inicio y la meta no pueden coincidir")
    resultado = Mundo(mundo["ancho"], mundo["alto"], obstaculos, _celda(mundo["inicio"], "inicio"),
                      _celda(mundo["meta"], "meta"), **escalas)
    if resultado.bfs() is None:
        raise ValueError("En el escenario personalizado no hay camino entre el inicio y la meta")
    return resultado


def crear_mundo(datos: dict[str, Any], semilla: int | None = None) -> Mundo:
    """Crea el mundo del ensayo. La misma semilla da siempre el mismo mundo.

    En los escenarios con azar se regenera hasta que la ruta óptima entre el inicio y la meta
    mida al menos ``distancia_minima`` movimientos (decisión I13). El escenario
    ``personalizado`` toma ``obstaculos``, ``inicio`` y ``meta`` del YAML (B6); en los demás
    escenarios esas claves son un error, porque se ignorarían sin aviso (F-023, punto 4).
    """
    mundo = {**_MUNDO, **(datos.get("mundo") or {})}
    _revisar("mundo", mundo, _MUNDO)
    semilla = datos.get("semilla", 0) if semilla is None else semilla
    if not isinstance(semilla, int) or isinstance(semilla, bool) or semilla < 0:
        # Random(-3) == Random(3): una semilla negativa repetiría el mundo de la positiva (F-026).
        raise ValueError(f"semilla = {semilla!r}: debe ser un entero mayor o igual que 0")
    escalas = dict(tau0=0.0, tau_max=_numero(mundo["tau_max"]),
                   unidad_deposito=_numero(mundo["unidad_deposito"]))
    escenario = mundo["escenario"]
    if escenario != "personalizado":
        dadas = [c for c in ("obstaculos", "inicio", "meta") if mundo[c] != _MUNDO[c]]
        if dadas:
            raise ValueError(f"Las claves {dadas} solo valen con escenario: personalizado "
                             f"(el escenario {escenario!r} las ignoraría)")
    if escenario == "personalizado":
        return _mundo_personalizado(mundo, escalas)
    if escenario == "puente_doble":
        return puente_doble(Fraction(str(mundo["r"])), mundo["ancho_puente"], **escalas).mundo
    if escenario not in ESCENARIOS:
        raise ValueError(f"Escenario desconocido: {escenario!r}. Válidos: {list(ESCENARIOS)}")
    rng = random.Random(semilla)
    for _ in range(_MAX_INTENTOS):
        if escenario == "L":
            candidato = mundo_l(rng, **escalas)
        else:
            candidato = mundo_aleatorio(rng, mundo["ancho"], mundo["alto"], mundo["densidad"],
                                        **escalas)
        if candidato.largo_optimo() >= mundo["distancia_minima"]:
            return candidato
    raise ValueError("No se encontró un mundo con esa distancia mínima entre inicio y meta")
