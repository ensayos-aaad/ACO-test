"""Métricas del gemelo (decisiones G1 y G2 e ideas del operador en CONTEXT.md §8).

Por ensayo:

- **Convergencia** (G1): todas las agentes asentadas en la meta y la verificadora llega
  siguiendo solo el rastro. Se mide también en cuántos ticks se asentó la última.
- **Calidad**: largo de la ruta de la verificadora dividido por el óptimo del BFS.
- **Conocimiento del mundo**: cuánto coincide el mapa de la madre con el mundo real. Solo el
  gemelo puede medirlo, porque solo él conoce la verdad.
- **Costo de red**: mensajes y bytes por familia de mensajes.

Por lote: tasas con su intervalo de confianza, y media y varianza de los tiempos.
"""

from __future__ import annotations

from statistics import mean, pvariance
from typing import Any, Iterable

from statsmodels.stats.proportion import proportion_confint

from ..madre import Madre
from ..mundo import Mundo

FAMILIAS = ("mundo_agente", "agente_agente", "agente_madre", "madre_agente")


def conocimiento_del_mundo(madre: Madre, mundo: Mundo) -> float | None:
    """Fracción de las celdas del mundo que la madre conoce **y** clasifica bien.

    Una celda cuenta si la madre la tiene como conocida y acierta si es obstáculo o libre.
    Las celdas que no conoce, o en las que se equivoca, no cuentan. Devuelve ``None`` si la
    madre no guarda mapa (modos ausente y pista de baile).
    """
    if not madre.guarda_mapa:
        return None
    aciertos = 0
    for y in range(mundo.alto):
        for x in range(mundo.ancho):
            celda = (x, y)
            if celda in madre.conocidas and (celda in madre.obstaculos) == (celda in mundo.obstaculos):
                aciertos += 1
    return aciertos / (mundo.ancho * mundo.alto)


def fila(semilla: int, escenario: str, resultado) -> dict[str, Any]:
    """Aplana el resultado de un ensayo en una fila (para un CSV o un DataFrame)."""
    salida = {
        "semilla": semilla,
        "escenario": escenario,
        "modo_madre": resultado.modo_madre,
        "motivo": resultado.motivo,
        "asentadas": int(resultado.asentadas),
        "verificada": int(resultado.verificada),
        "ticks_asentadas": resultado.ticks_asentadas,
        "ticks_total": resultado.ticks_total,
        "largo_optimo": resultado.largo_optimo,
        "largo_verificado": resultado.largo_verificado,
        "razon": None if resultado.razon is None else round(resultado.razon, 4),
        "conocimiento": None if resultado.conocimiento is None else round(resultado.conocimiento, 4),
        "bloqueadas": resultado.bloqueadas,
        "memoria_madre": resultado.memoria_madre,
        "memoria_madre_max": resultado.memoria_madre_max,
        "madre_verificacion": resultado.madre_verificacion,
    }
    salida["ticks_verificacion"] = resultado.ticks_verificacion
    for familia in FAMILIAS:
        salida[f"mensajes_{familia}"] = resultado.trafico[familia]["enviados"]
        salida[f"bytes_{familia}"] = resultado.trafico[familia]["bytes"]
    salida["bytes_totales"] = sum(resultado.trafico[f]["bytes"] for f in FAMILIAS)
    salida.update(resultado.mecanismos)  # C4: lo que realmente pasó
    return salida


def _numeros(filas: list[dict[str, Any]], clave: str) -> list[float]:
    return [float(f[clave]) for f in filas if f.get(clave) not in (None, "")]


def _tasa(exitos: int, n: int) -> dict[str, float]:
    """Proporción con su intervalo de confianza de Wilson al 95 %."""
    bajo, alto = proportion_confint(exitos, n, alpha=0.05, method="wilson")
    return {"exitos": exitos, "n": n, "tasa": exitos / n, "ic95_bajo": float(bajo),
            "ic95_alto": float(alto)}


def resumen(filas: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Resume un lote de ensayos de una misma condición.

    Acepta las filas tal como salen de ``fila()`` o leídas de un CSV (texto). Las medias de
    tiempo y calidad se calculan solo sobre los ensayos donde el dato existe.
    """
    filas = list(filas)
    n = len(filas)
    if n == 0:
        raise ValueError("No hay ensayos que resumir")
    ticks = _numeros(filas, "ticks_asentadas")
    razones = _numeros(filas, "razon")
    conocimiento = _numeros(filas, "conocimiento")
    salida: dict[str, Any] = {
        "n": n,
        "asentadas": _tasa(sum(int(f["asentadas"]) for f in filas), n),
        "verificadas": _tasa(sum(int(f["verificada"]) for f in filas), n),
        "ticks_media": mean(ticks) if ticks else None,
        "ticks_varianza": pvariance(ticks) if ticks else None,
        "ticks_min": min(ticks) if ticks else None,
        "ticks_max": max(ticks) if ticks else None,
        "razon_media": mean(razones) if razones else None,
        "conocimiento_medio": mean(conocimiento) if conocimiento else None,
    }
    for familia in FAMILIAS:
        salida[f"bytes_{familia}_media"] = mean(_numeros(filas, f"bytes_{familia}"))
    return salida
