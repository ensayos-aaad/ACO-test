"""Parte B de TOLERANCIAS.md: el gemelo frente al oráculo (criterios C1–C5 de PROMPT-ZERO).

Correr desde la raíz del repositorio con el Python del entorno aco-gemelo::

    python -X utf8 oraculo/comparar.py

Escribe ``oraculo/RESULTADOS.md``. Las pruebas y tolerancias están en ``TOLERANCIAS.md`` y se
declararon antes de escribir este archivo.
"""

from __future__ import annotations

import math
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI.parent / "gemelo")]

import oraculo as o  # noqa: E402
from aco_gemelo.agente import Agente, ConfigAgente  # noqa: E402
from aco_gemelo.agente.agente import Estado  # noqa: E402
from aco_gemelo.canal import CanalMemoria  # noqa: E402
from aco_gemelo.config import cargar, config_ensayo, crear_mundo  # noqa: E402
from aco_gemelo.motor import Simulacion  # noqa: E402
from aco_gemelo.mundo import puente_doble  # noqa: E402

CONFIG = AQUI.parent / "gemelo" / "configs" / "puente_doble.yaml"
N_SEMILLAS = 100


def ensayo_puente(r: int, semilla: int, n_agentes: int | None = None) -> float | None:
    """x del gemelo: fracción de agentes asentadas cuya ruta pasa por la rama corta (o de abajo).

    Devuelve ``None`` si la colonia no se asentó dentro del límite.
    """
    datos = cargar(CONFIG)
    datos["mundo"] = {**datos["mundo"], "r": r}
    config = config_ensayo(datos, semilla)
    if n_agentes is not None:
        config = replace(config, n_agentes=n_agentes)
    mundo = crear_mundo(datos, semilla)
    puente = puente_doble(r, datos["mundo"].get("ancho_puente", 3))
    sim = Simulacion(mundo, config)
    resultado = sim.correr()
    if not resultado.asentadas:
        return None
    entrada_corta = puente.rama_corta[1]
    return sum(entrada_corta in a.ruta for a in sim.agentes) / len(sim.agentes)


def serie_gemelo(r: int, n_agentes: int | None = None) -> list[float | None]:
    return [ensayo_puente(r, s, n_agentes) for s in range(N_SEMILLAS)]


def c1() -> tuple[bool, list[tuple[int, float, float, float]]]:
    """Frecuencia de elección del agente frente a ``p1`` del oráculo, delta = −15…15."""
    p1 = o.p1()
    filas = []
    ok = True
    n = 20_000
    for delta in range(-15, 16):
        puente = puente_doble(2, 3, tau0=0.0, tau_max=15.0, unidad_deposito=1.0)
        mundo, nido = puente.mundo, puente.mundo.inicio
        if delta > 0:
            mundo.depositar(puente.rama_corta[1], delta)
        elif delta < 0:
            mundo.depositar(puente.rama_larga[1], -delta)
        agente = Agente(1, CanalMemoria(), ConfigAgente(alpha=2, k=20, theta=0), semilla=2026)
        agente.pos, agente.ruta = nido, [nido]
        vecinas = mundo.percibir(nido)
        hacia_corta = agente._hacia(puente.rama_corta[1])
        frecuencia = sum(agente.elegir(vecinas) == hacia_corta for _ in range(n)) / n
        esperado = float(p1(20, 2, np.array([delta]))[0])
        sigma = math.sqrt(esperado * (1 - esperado) / n)
        ok &= abs(frecuencia - esperado) <= 4 * sigma
        filas.append((delta, esperado, frecuencia, (frecuencia - esperado) / sigma))
    return ok, filas


def extremos(xs: list[float | None]) -> list[float]:
    return [x for x in xs if x is not None and (x <= 0.2 or x >= 0.8)]


def main() -> int:
    estado = {True: "**PASA**", False: "**NO PASA**"}
    oraculo_r1 = [v / 100 for v in o.montecarlo(1.0)[0]]
    oraculo_r2 = [v / 100 for v in o.montecarlo(2.0)[0]]
    gemelo_r1, gemelo_r2 = serie_gemelo(1), serie_gemelo(2)

    ok1, filas1 = c1()

    ext = extremos(gemelo_r1)
    frac_ext = len(ext) / N_SEMILLAS
    gana_abajo = sum(x >= 0.8 for x in ext)
    p_binomial = binomtest(gana_abajo, len(ext), 0.5).pvalue if ext else float("nan")
    ok2 = frac_ext >= 0.7 and p_binomial > 0.05

    p_or = sum(x >= 0.8 for x in oraculo_r2) / len(oraculo_r2)
    p_ge = sum(x is not None and x >= 0.8 for x in gemelo_r2) / N_SEMILLAS
    ok3 = abs(p_ge - p_or) <= 0.15

    derivada = str(o.derivada_en_medio())
    medio = sum(x is not None and 0.4 <= x <= 0.6 for x in gemelo_r1) / N_SEMILLAS
    ok4 = derivada == "alpha" and medio <= 0.2

    repetido = [ensayo_puente(1, s) for s in range(5)]
    ok5 = repetido == gemelo_r1[:5] and o.montecarlo.__wrapped__(2.0) == o.montecarlo(2.0)

    no_asentadas = sum(x is None for x in gemelo_r1 + gemelo_r2)

    def histograma(xs):
        validos = [100 * x for x in xs if x is not None]
        conteos, _ = np.histogram(validos, bins=o.BINS)
        return " · ".join(f"{100 * c / len(xs):.0f} %" for c in conteos)

    info = {}
    for r in (1, 2):
        xs = serie_gemelo(r, 60)
        info[r] = (histograma(xs), sum(x is not None and (x <= 0.2 or x >= 0.8) for x in xs) / N_SEMILLAS,
                   sum(x is not None and x >= 0.8 for x in xs) / N_SEMILLAS)

    lineas = [
        "# RESULTADOS — gemelo frente al oráculo",
        "",
        "Generado por `python -X utf8 oraculo/comparar.py`. Pruebas y tolerancias: `TOLERANCIAS.md`",
        "(declaradas antes de correr). Gemelo: `gemelo/configs/puente_doble.yaml`, "
        f"{N_SEMILLAS} semillas por r.",
        "",
        "## Resumen",
        "",
        "| Criterio | Resultado | Valor medido | Umbral declarado |",
        "|---|---|---|---|",
        f"| C1 Regla de decisión | {estado[ok1]} | máx. \\|z\\| = {max(abs(f[3]) for f in filas1):.2f} en 31 casos | \\|z\\| ≤ 4 en todos |",
        f"| C2 Ruptura de simetría (r = 1) | {estado[ok2]} | extremos {frac_ext:.2f}; gana abajo {gana_abajo}/{len(ext)} (p = {p_binomial:.3f}) | extremos ≥ 0,7 y p > 0,05 |",
        f"| C3 Ramas desiguales (r = 2) | {estado[ok3]} | gemelo {p_ge:.2f} frente a oráculo {p_or:.2f} (diferencia {abs(p_ge - p_or):.2f}) | diferencia ≤ 0,15 |",
        f"| C4 Puntos fijos | {estado[ok4]} | f'(1/2) = {derivada}; ensayos con x en [0,4; 0,6]: {medio:.2f} | f'(1/2) = α y ≤ 0,2 |",
        f"| C5 Determinismo | {estado[ok5]} | gemelo y oráculo repiten con la misma semilla | igualdad exacta |",
        "| C6 Pedagógico | NO PROBADO | — | lo evalúa el operador |",
        "",
        "## Histogramas (% de ensayos por bin de tráfico en la rama corta: 0–20 · 20–40 · 40–60 · 60–80 · 80–100)",
        "",
        "| | r = 1 | r = 2 |",
        "|---|---|---|",
        f"| Oráculo (montecarlo_aco [4], 1000 hormigas, N = 1000) | {' · '.join(f'{v:.0f} %' for v in o.montecarlo(1.0)[1])} | {' · '.join(f'{v:.0f} %' for v in o.montecarlo(2.0)[1])} |",
        f"| Gemelo (6 agentes, N = {N_SEMILLAS}) | {histograma(gemelo_r1)} | {histograma(gemelo_r2)} |",
        f"| Gemelo con 60 agentes (informativo, parte C) | {info[1][0]} | {info[2][0]} |",
        "",
        f"Ensayos del gemelo que no se asentaron (6 agentes, ambos r): {no_asentadas}.",
        f"Con 60 agentes: extremos en r = 1 = {info[1][1]:.2f}; x ≥ 0,8 en r = 2 = {info[2][2]:.2f}.",
        "",
        "## C1 en detalle",
        "",
        "| delta | p1 del oráculo | frecuencia del gemelo | z |",
        "|---|---|---|---|",
        *[f"| {d} | {e:.4f} | {f:.4f} | {z:+.2f} |" for d, e, f, z in filas1],
    ]
    (AQUI / "RESULTADOS.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print("\n".join(lineas[:16]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
