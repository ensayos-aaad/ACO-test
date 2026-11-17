"""Investigación de por qué C3 da NO PASA (F-015). Exploratorio: NO cambia el producto ni los criterios.

Cada variante corre el puente doble del gemelo (``gemelo/configs/puente_doble.yaml``) cambiando una
sola cosa. Las variantes que tocan cómo percibe el agente se hacen **reemplazando funciones solo dentro
de este script** (no se toca ``gemelo/``).

Uso (desde la raíz, con el Python de aco-gemelo):
    python -X utf8 oraculo/investigacion_c3.py <variante> <r> <n_semillas>
Escribe ``oraculo/investigacion_c3/<variante>_r<r>.json``.
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import replace
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI.parent / "gemelo")]

from aco_gemelo.agente import Agente  # noqa: E402
from aco_gemelo.agente.agente import DIRECCIONES  # noqa: E402
from aco_gemelo.config import cargar, config_ensayo, crear_mundo  # noqa: E402
from aco_gemelo.motor import Simulacion  # noqa: E402
from aco_gemelo.mundo import Mundo, puente_doble  # noqa: E402
from aco_gemelo.protocolo import byte_a_celda  # noqa: E402

CONFIG = AQUI.parent / "gemelo" / "configs" / "puente_doble.yaml"
_decidir_original = Agente.decidir
_q4_original = Mundo.feromona_q4


def _escala(L: float) -> dict:
    """1 nivel = L depósitos; k = 20 depósitos de Deneubourg = 20/L niveles."""
    return {"mundo": {"tau_max": 15 * L}, "agente": {"k": 20 / L}}


def _percepcion_ideal(mundo_actual: list) -> None:
    """El agente ve la feromona exacta (en depósitos), sin cuantizar. k = 20 depósitos."""
    def decidir(self, percepto, ahora=0):
        mundo = mundo_actual[0]
        x, y = byte_a_celda(percepto["pos"])
        celdas = [(x, y)] + [(x + dx, y + dy) for dx, dy in DIRECCIONES]
        for vecina, celda in zip(percepto["vecinas"], celdas):
            vecina["fero"] = mundo.feromona(celda)
        return _decidir_original(self, percepto, ahora)
    Agente.decidir = decidir


def _percepcion_log() -> None:
    """16 niveles **logarítmicos**: nivel = round(log2(1 + depósitos)); el agente estima
    m = 2^nivel − 1 depósitos y pesa (20 + m)^2. Cabe en los mismos 4 bits."""
    Mundo.feromona_q4 = lambda self, celda: min(15, round(math.log2(1 + self.feromona(celda))))

    def decidir(self, percepto, ahora=0):
        # decidir() se llama a sí misma al cambiar de estado: convertir una sola vez.
        if not percepto.get("_convertido"):
            for vecina in percepto["vecinas"]:
                vecina["fero"] = 2 ** vecina["fero"] - 1
            percepto["_convertido"] = True
        return _decidir_original(self, percepto, ahora)
    Agente.decidir = decidir


def _percepcion_q8(mundo_actual: list) -> None:
    """256 niveles lineales (8 bits): 1 nivel = 4 depósitos (rango 1020); k = 20/4 = 5 niveles.
    Simula un campo ``fero`` de 8 bits en PERCEPCION (no cabe en el protocolo actual, que usa 4)."""
    def decidir(self, percepto, ahora=0):
        mundo = mundo_actual[0]
        x, y = byte_a_celda(percepto["pos"])
        celdas = [(x, y)] + [(x + dx, y + dy) for dx, dy in DIRECCIONES]
        for vecina, celda in zip(percepto["vecinas"], celdas):
            vecina["fero"] = min(255, round(mundo.feromona(celda) / 4))
        return _decidir_original(self, percepto, ahora)
    Agente.decidir = decidir


VARIANTES = {
    # nombre: (cambios al YAML, viajes, función que reemplaza la percepción o None)
    "base": ({}, 50, None),
    "L10": (_escala(10), 50, None),
    "L40": (_escala(40), 50, None),
    "ideal": ({"mundo": {"tau_max": 1e9}, "agente": {"k": 20.0}}, 50, "ideal"),
    "log": ({"mundo": {"tau_max": 1e9}, "agente": {"k": 20.0}}, 50, "log"),
    "base_170": ({}, 170, None),
    "ideal_170": ({"mundo": {"tau_max": 1e9}, "agente": {"k": 20.0}}, 170, "ideal"),
    "log_170": ({"mundo": {"tau_max": 1e9}, "agente": {"k": 20.0}}, 170, "log"),
    "q8_170": ({"mundo": {"tau_max": 1e9}, "agente": {"k": 5.0}}, 170, "q8"),
}


def correr(variante: str, r: int, n: int) -> dict:
    cambios, viajes, percepcion = VARIANTES[variante]
    mundo_actual: list = [None]
    if percepcion == "ideal":
        _percepcion_ideal(mundo_actual)
    elif percepcion == "log":
        _percepcion_log()
    elif percepcion == "q8":
        _percepcion_q8(mundo_actual)
    finales, tardios = [], []
    for semilla in range(n):
        datos = cargar(CONFIG)
        datos["mundo"] = {**datos["mundo"], **cambios.get("mundo", {}), "r": r}
        datos["agente"] = {**datos["agente"], **cambios.get("agente", {}), "viajes": viajes}
        config = replace(config_ensayo(datos, semilla), limite=20_000)
        mundo = crear_mundo(datos, semilla)
        mundo_actual[0] = mundo
        sim = Simulacion(mundo, config)
        resultado = sim.correr()
        entrada = puente_doble(r, 3).rama_corta[1]
        if not resultado.asentadas:
            finales.append(None)
            tardios.append(None)
            continue
        finales.append(sum(entrada in a.ruta for a in sim.agentes) / len(sim.agentes))
        tarde = [e for a in sim.agentes for e in a.entradas[len(a.entradas) // 2:]]
        tardios.append(sum(e == entrada for e in tarde) / len(tarde))
    validos = [x for x in finales if x is not None]
    return {
        "variante": variante, "r": r, "n": n,
        "no_asentadas": finales.count(None),
        "final_ge_08": sum(x >= 0.8 for x in validos) / n,
        "final_extremos": sum(x <= 0.2 or x >= 0.8 for x in validos) / n,
        "final_medio": sum(0.4 <= x <= 0.6 for x in validos) / n,
        "tardio_ge_08": sum(x is not None and x >= 0.8 for x in tardios) / n,
        "tardio_medio": sum(x for x in tardios if x is not None) / max(1, len(validos)),
        "finales": finales, "tardios": tardios,
    }


if __name__ == "__main__":
    variante, r, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    salida = AQUI / "investigacion_c3" / f"{variante}_r{r}.json"
    salida.parent.mkdir(exist_ok=True)
    salida.write_text(json.dumps(correr(variante, r, n), indent=1), encoding="utf-8")
    print(salida)
