"""Escenarios del mundo: la "L" del plano, mundos aleatorios y el puente doble."""

from __future__ import annotations

import random
from dataclasses import dataclass
from fractions import Fraction

from .mundo import Celda, Mundo

OBSTACULOS_L: frozenset[Celda] = frozenset(
    [(1, y) for y in range(1, 5)] + [(x, 5) for x in range(2, 5)]
)

_MAX_INTENTOS = 1000


def _con_extremos_al_azar(
    ancho: int, alto: int, obstaculos: frozenset[Celda], rng: random.Random, **kwargs
) -> Mundo | None:
    libres = [(x, y) for y in range(alto) for x in range(ancho) if (x, y) not in obstaculos]
    if len(libres) < 2:
        return None
    inicio, meta = rng.sample(libres, 2)
    mundo = Mundo(ancho, alto, obstaculos, inicio, meta, **kwargs)
    return mundo if mundo.bfs() is not None else None


def mundo_l(rng: random.Random, **kwargs) -> Mundo:
    for _ in range(_MAX_INTENTOS):
        mundo = _con_extremos_al_azar(8, 8, OBSTACULOS_L, rng, **kwargs)
        if mundo is not None:
            return mundo
    raise RuntimeError("No se encontró un par inicio-meta alcanzable")


def mundo_aleatorio(
    rng: random.Random, ancho: int = 8, alto: int = 8, densidad: float = 0.2, **kwargs
) -> Mundo:
    if not 0 <= densidad < 1:
        raise ValueError("La densidad debe estar en [0, 1)")
    for _ in range(_MAX_INTENTOS):
        obstaculos = frozenset(
            (x, y) for y in range(alto) for x in range(ancho) if rng.random() < densidad
        )
        mundo = _con_extremos_al_azar(ancho, alto, obstaculos, rng, **kwargs)
        if mundo is not None:
            return mundo
    raise RuntimeError("No se pudo generar un mundo con meta alcanzable; baje la densidad")


@dataclass(frozen=True)
class PuenteDoble:
    mundo: Mundo
    rama_corta: tuple[Celda, ...]
    rama_larga: tuple[Celda, ...]

    @property
    def largo_corta(self) -> int:
        return len(self.rama_corta) - 1

    @property
    def largo_larga(self) -> int:
        return len(self.rama_larga) - 1

    @property
    def r(self) -> Fraction:
        return Fraction(self.largo_larga, self.largo_corta)


def puente_doble(r: int | Fraction = 2, ancho: int = 3, **kwargs) -> PuenteDoble:
    if ancho < 3:
        raise ValueError("El ancho mínimo es 3")
    r = Fraction(r)
    if r < 1:
        raise ValueError("r debe ser >= 1")
    corta = ancho + 1
    doble_d = r * corta - (ancho - 1)
    if doble_d.denominator != 1 or doble_d.numerator % 2:
        raise ValueError(f"Con r = {r} y ancho = {ancho} la rama larga no cabe en la cuadrícula")
    d = doble_d.numerator // 2
    alto = d + 2
    fila = d
    obstaculos = frozenset((x, y) for x in range(1, ancho - 1) for y in range(1, fila + 1))
    inicio, meta = (0, fila), (ancho - 1, fila)
    mundo = Mundo(ancho, alto, obstaculos, inicio, meta, **kwargs)
    rama_corta = (inicio, *[(x, fila + 1) for x in range(ancho)], meta)
    rama_larga = (
        *[(0, y) for y in range(fila, -1, -1)],
        *[(x, 0) for x in range(1, ancho - 1)],
        *[(ancho - 1, y) for y in range(0, fila + 1)],
    )
    return PuenteDoble(mundo, rama_corta, rama_larga)
