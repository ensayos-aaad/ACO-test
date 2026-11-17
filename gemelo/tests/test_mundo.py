"""Pruebas del artefacto 4: mundo, BFS y escenarios."""
import random
from fractions import Fraction

import pytest

from aco_gemelo.mundo import (
    OBSTACULOS_L,
    Clase,
    Mundo,
    mundo_aleatorio,
    mundo_l,
    puente_doble,
)

SEMILLAS = range(200)


# ---------------------------------------------------------------- criterio 1: meta alcanzable


@pytest.mark.parametrize("fabrica", [mundo_l, mundo_aleatorio])
def test_la_meta_siempre_es_alcanzable(fabrica):
    for semilla in SEMILLAS:
        mundo = fabrica(random.Random(semilla))
        assert mundo.inicio != mundo.meta
        assert mundo.es_libre(mundo.inicio) and mundo.es_libre(mundo.meta)
        assert mundo.bfs() is not None


def test_bfs_devuelve_none_si_la_meta_esta_encerrada():
    pared = [(1, y) for y in range(3)]
    mundo = Mundo(3, 3, pared, inicio=(0, 0), meta=(2, 2))
    assert mundo.bfs() is None
    assert mundo.largo_optimo() is None


def test_misma_semilla_mismo_mundo():
    for fabrica in (mundo_l, mundo_aleatorio):
        a, b = fabrica(random.Random(7)), fabrica(random.Random(7))
        assert (a.obstaculos, a.inicio, a.meta) == (b.obstaculos, b.inicio, b.meta)


# ---------------------------------------------------------------- criterio 2: BFS de 8 vecinos sin cortar esquinas


def test_diagonal_libre_cuenta_como_un_movimiento():
    mundo = Mundo(4, 4, [], inicio=(0, 0), meta=(3, 3))
    assert mundo.largo_optimo() == 3


def test_no_se_cortan_esquinas():
    mundo = Mundo(2, 2, [(1, 0)], inicio=(0, 0), meta=(1, 1))
    assert mundo.mover((0, 0), 5) is None  # SE: roza el obstáculo (1, 0)
    assert mundo.bfs() == [(0, 0), (0, 1), (1, 1)]


def test_no_se_pasa_entre_dos_obstaculos_en_diagonal():
    mundo = Mundo(2, 2, [(1, 0), (0, 1)], inicio=(0, 0), meta=(1, 1))
    assert mundo.bfs() is None


def test_la_ruta_del_bfs_es_valida_y_minima():
    for semilla in range(50):
        mundo = mundo_aleatorio(random.Random(semilla))
        ruta = mundo.bfs()
        assert ruta[0] == mundo.inicio and ruta[-1] == mundo.meta
        for a, b in zip(ruta, ruta[1:]):
            assert b in [destino for _, destino in mundo.vecinos(a)]
        # Mínima: ninguna celda de la ruta está más cerca de la meta de lo que la ruta dice.
        for i, celda in enumerate(ruta):
            assert len(mundo.bfs(celda, mundo.meta)) - 1 == len(ruta) - 1 - i


def test_los_vecinos_nunca_son_obstaculo_ni_salen_de_la_grilla():
    mundo = mundo_l(random.Random(0))
    for celda in mundo.celdas_libres():
        for direccion, destino in mundo.vecinos(celda):
            assert mundo.es_libre(destino)
            assert mundo.mover(celda, direccion) == destino


# ---------------------------------------------------------------- criterio 3: la L coincide con el plano


def test_la_l_coincide_con_el_plano():
    esperado = {(1, 1), (1, 2), (1, 3), (1, 4), (2, 5), (3, 5), (4, 5)}
    assert set(OBSTACULOS_L) == esperado
    mundo = Mundo(8, 8, OBSTACULOS_L, inicio=(0, 0), meta=(5, 7))
    dibujo = str(mundo).splitlines()
    assert dibujo == [
        "I . . . . . . .",
        ". # . . . . . .",
        ". # . . . . . .",
        ". # . . . . . .",
        ". # . . . . . .",
        ". . # # # . . .",
        ". . . . . . . .",
        ". . . . . F . .",
    ]
    assert mundo.clase((1, 1)) is Clase.OBSTACULO
    assert mundo.clase((5, 7)) is Clase.META
    assert mundo.clase((8, 0)) is Clase.FUERA
    assert mundo.clase((0, 1)) is Clase.LIBRE


# ---------------------------------------------------------------- criterio 4: puente doble parametrizado por r


@pytest.mark.parametrize(
    "r, ancho, corta, larga",
    [(1, 3, 4, 4), (2, 3, 4, 8), (2, 5, 6, 12), (Fraction(3, 2), 3, 4, 6), (3, 3, 4, 12)],
)
def test_puente_doble_longitudes(r, ancho, corta, larga):
    puente = puente_doble(r, ancho)
    assert (puente.largo_corta, puente.largo_larga) == (corta, larga)
    assert puente.r == Fraction(r)
    mundo = puente.mundo
    assert mundo.largo_optimo() == corta
    # Cada rama es un camino válido del nido a la meta.
    for rama in (puente.rama_corta, puente.rama_larga):
        assert rama[0] == mundo.inicio and rama[-1] == mundo.meta
        for a, b in zip(rama, rama[1:]):
            assert b in [destino for _, destino in mundo.vecinos(a)]
    # Las ramas solo comparten el nido y la meta, y no hay otras celdas libres.
    assert set(puente.rama_corta) & set(puente.rama_larga) == {mundo.inicio, mundo.meta}
    assert set(puente.rama_corta) | set(puente.rama_larga) == set(mundo.celdas_libres())


def test_puente_doble_sin_atajos():
    """Si se bloquea la rama corta, el único camino que queda mide lo que la rama larga."""
    puente = puente_doble(2, 3)
    mundo = puente.mundo
    bloqueada = Mundo(
        mundo.ancho, mundo.alto, mundo.obstaculos | {puente.rama_corta[2]}, mundo.inicio, mundo.meta
    )
    assert bloqueada.largo_optimo() == puente.largo_larga


def test_puente_doble_rechaza_r_imposible():
    with pytest.raises(ValueError):
        puente_doble(Fraction(5, 4), 3)


# ---------------------------------------------------------------- feromona en límites válidos


def test_feromona_en_limites_tras_deposito_y_evaporacion():
    mundo = Mundo(3, 3, [(1, 1)], inicio=(0, 0), meta=(2, 2), tau0=20, tau_max=100)
    assert mundo.feromona((0, 0)) == 20
    assert mundo.feromona((1, 1)) == 0  # obstáculo
    mundo.depositar((0, 0), 1000)
    assert mundo.feromona((0, 0)) == 100  # satura
    assert mundo.feromona_q4((0, 0)) == 15
    for _ in range(50):
        mundo.evaporar(0.5)
    for celda in mundo.celdas_libres():
        assert 0 <= mundo.feromona(celda) <= mundo.tau_max
        assert 0 <= mundo.feromona_q4(celda) <= 15
    with pytest.raises(ValueError):
        mundo.depositar((1, 1), 1)
    with pytest.raises(ValueError):
        mundo.depositar((0, 0), -1)
