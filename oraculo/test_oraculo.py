"""Parte A de TOLERANCIAS.md: el oráculo reproduce los notebooks (criterios del artefacto 12).

Correr desde la raíz del repositorio con el Python del entorno aco-gemelo:
``python -X utf8 -m pytest oraculo -q``
"""
import numpy as np
import pytest
import sympy as sp

import oraculo as o


def test_el_oraculo_lee_la_referencia_sin_modificarla():
    antes = (o.CARPETA / o.DENEUBOURG).read_bytes()
    o.dinamica()
    assert (o.CARPETA / o.DENEUBOURG).read_bytes() == antes
    assert "def p1(k, n, delta):" in o.celda(o.DENEUBOURG, 5)
    assert "def experimento_individual(ratio_r, alpha):" in o.celda(o.MONTECARLO, 4)
    with pytest.raises(ValueError):
        o.celda(o.DENEUBOURG, 4)  # es Markdown


def test_a1_p1_reproduce_la_formula():
    p1 = o.p1()
    k = 20
    delta = np.arange(-30, 31, 1)  # la malla de la celda [5]
    m1 = np.maximum(delta, 0)
    m2 = np.maximum(-delta, 0)
    for n in (1, 2, 4):
        a_mano = (k + m1) ** n / ((k + m1) ** n + (k + m2) ** n)
        assert np.max(np.abs(p1(k, n, delta) - a_mano)) <= 1e-12


def test_a2_dinamica_determinista_y_converge_a_la_rama_corta():
    a, b = o.dinamica(), o.dinamica()
    assert np.array_equal(a["p_s_hist"], b["p_s_hist"])  # (a)
    assert (a["r"], a["T"], a["alpha"], a["k"], a["t_s"]) == (2, 200, 2, 5.0, 5)
    assert a["p_s_hist"][a["T"] - 1] >= 0.9  # (b)


def test_a3_montecarlo_reproducible():
    experimento = o.experimento_individual()
    np.random.seed(7)
    primero = [experimento(2.0, 2.0) for _ in range(5)]
    np.random.seed(7)
    assert [experimento(2.0, 2.0) for _ in range(5)] == primero  # (a)


def test_a3_r1_forma_de_u():
    _, porcentajes = o.montecarlo(1.0)
    assert porcentajes[0] + porcentajes[4] >= 70  # (b)


def test_a3_r2_la_rama_corta_gana():
    _, porcentajes = o.montecarlo(2.0)
    assert porcentajes[4] >= 70  # (c)


def test_a4_derivada_en_un_medio_es_alfa():
    resultado = o.derivada_en_medio()
    assert sp.simplify(resultado - sp.Symbol("alpha", positive=True)) == 0
