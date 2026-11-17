"""Pruebas del artefacto 6: el agente (hormiga) y la verificadora."""
import math
import random

import pytest

from apoyo import Banco

from aco_gemelo.agente import Agente, ConfigAgente, Estado, prob_explotar
from aco_gemelo.canal import CanalMemoria
from aco_gemelo.mundo import DIRECCIONES, Mundo, mundo_aleatorio, mundo_l, puente_doble
from aco_gemelo.protocolo import FLAG_VERIFICACION, byte_a_celda, nombre_de

CUADRICULA = dict(tau0=0.0, tau_max=1.0, unidad_deposito=1 / 255)
PUENTE = dict(tau0=0.0, tau_max=15.0, unidad_deposito=1.0)


def mundo_con_distancia(fabrica, semilla, minimo=4):
    """Mundo con ruta óptima de al menos ``minimo`` movimientos (decisión I13)."""
    rng = random.Random(semilla)
    while True:
        mundo = fabrica(rng, **CUADRICULA)
        if mundo.largo_optimo() >= minimo:
            return mundo


def colonia(mundo, semilla, n=6, rho=0.0, **config):
    banco = Banco(mundo, rho=rho)
    agentes = [banco.agregar(Agente(i, banco.canal, ConfigAgente(**config), semilla))
               for i in range(1, n + 1)]
    return banco, agentes


def todas_asentadas(agentes):
    return lambda: all(a.estado is Estado.ASENTADA for a in agentes)


def ruta_de(danza):
    """Reconstruye las celdas de la ruta que anuncia un mensaje DANZA."""
    celdas = [byte_a_celda(danza["inicio"])]
    for d in danza["movs"]:
        celdas.append((celdas[-1][0] + DIRECCIONES[d][0], celdas[-1][1] + DIRECCIONES[d][1]))
    return celdas


# ---------------------------------------------------------------- criterio 1: nunca entra en un obstáculo ni sale


@pytest.mark.parametrize("fabrica", [mundo_l, mundo_aleatorio])
def test_nunca_entra_en_un_obstaculo_ni_sale_de_la_grilla(fabrica):
    for semilla in range(10):
        mundo = mundo_con_distancia(fabrica, semilla)
        banco, agentes = colonia(mundo, semilla)
        banco.correr(400)
        assert banco.historial
        assert all(mundo.es_libre(celda) for _, _, celda in banco.historial)
        assert banco.bloqueadas == 0  # ni siquiera lo intenta: decide bien con lo que percibe


def test_misma_semilla_mismo_recorrido():
    def recorrido(semilla):
        banco, _ = colonia(mundo_con_distancia(mundo_l, 3), semilla)
        banco.correr(300)
        return banco.historial

    assert recorrido(5) == recorrido(5)
    assert recorrido(5) != recorrido(6)


# ---------------------------------------------------------------- criterio 2: la memoria K se respeta


def test_la_memoria_k_se_respeta_y_al_llenarse_vuelve_al_nido():
    mundo = Mundo(16, 16, [], inicio=(0, 0), meta=(15, 15), **CUADRICULA)
    banco, (agente,) = colonia(mundo, semilla=1, n=1, K=6)
    volvio_al_nido = False
    for _ in range(600):
        banco.correr(1)
        assert len(agente.ruta) - 1 <= 6
        assert len(set(agente.ruta)) == len(agente.ruta)  # sin bucles
        assert agente.ruta[0] == mundo.inicio
        volvio_al_nido |= agente.reinicios > 0 and agente.pos == mundo.inicio
    assert agente.reinicios > 0 and volvio_al_nido
    assert all(mundo.feromona(c) == 0 for c in mundo.celdas_libres())  # el retroceso no deposita


# ---------------------------------------------------------------- criterio 3: cambia de rol por umbral


def test_probabilidad_de_explotar():
    assert prob_explotar(0, 8) == 0
    assert prob_explotar(8, 8) == 0.5
    assert prob_explotar(15, 8) == pytest.approx(225 / 289)
    assert prob_explotar(0, 0) == prob_explotar(7, 0) == 1  # con θ = 0 siempre explota


@pytest.mark.parametrize("nivel", [0, 4, 8, 15])
def test_el_rol_sigue_el_umbral_de_respuesta(nivel):
    """Tolerancia declarada antes de correr: 4 desviaciones estándar de una binomial, N = 4000."""
    mundo = Mundo(3, 3, [], inicio=(1, 1), meta=(2, 2), tau0=nivel / 15, tau_max=1.0)
    agente = Agente(1, CanalMemoria(), ConfigAgente(theta=8), semilla=nivel)
    agente.pos, agente.ruta = (1, 1), [(1, 1)]
    vecinas = mundo.percibir((1, 1))
    vecinas[1 + 5]["clase"] = 0  # oculta la meta para que tenga que elegir
    n, explota = 4000, 0
    for _ in range(n):
        agente.elegir(vecinas)
        explota += agente.rol
    p = prob_explotar(nivel, 8)
    assert abs(explota / n - p) <= 4 * math.sqrt(p * (1 - p) / n) + 1e-9


# ---------------------------------------------------------------- criterio 4: la verificadora


def mundo_con_rastro(rastro):
    mundo = Mundo(5, 5, [], inicio=(0, 0), meta=(4, 4), tau0=0.0, tau_max=1.0)
    for i, celda in enumerate(rastro):
        mundo.depositar(celda, 0.3 + 0.1 * i)
    return mundo


RASTRO = [(1, 0), (2, 0), (3, 1), (3, 2), (3, 3)]


@pytest.mark.parametrize("semilla", range(5))
def test_la_verificadora_sigue_el_rastro_y_avisa(semilla):
    banco = Banco(mundo_con_rastro(RASTRO))
    v = banco.agregar(Agente(9, banco.canal, ConfigAgente(verificadora=True), semilla))
    banco.correr(50, hasta=lambda: v.estado is not Estado.IDA)
    assert v.estado is Estado.ASENTADA
    assert v.ruta == [(0, 0), *RASTRO, (4, 4)]  # sin azar: igual con cualquier semilla
    (danza,) = [m for m in banco.a_madre if nombre_de(m) == "DANZA"]
    assert danza["flags"] & FLAG_VERIFICACION
    assert ruta_de(danza) == v.ruta
    assert all(banco.mundo.feromona(c) <= 0.71 for c in RASTRO)  # la verificadora no deposita


def test_la_verificadora_falla_si_el_rastro_se_corta_y_no_vuelve_sobre_sus_pasos():
    banco = Banco(mundo_con_rastro([(1, 0), (2, 0), (3, 3)]))
    v = banco.agregar(Agente(9, banco.canal, ConfigAgente(verificadora=True)))
    banco.correr(50, hasta=lambda: v.estado is not Estado.IDA)
    assert v.estado is Estado.FALLIDA
    assert v.ruta == [(0, 0), (1, 0), (2, 0)]
    assert len(set(v.ruta)) == len(v.ruta)
    (aviso,) = [m for m in banco.a_madre if nombre_de(m) == "PIDE_RESCATE"]
    assert aviso["flags"] & FLAG_VERIFICACION
    celdas = [c for _, _, c in banco.historial]
    banco.correr(10)
    assert [c for _, _, c in banco.historial][len(celdas):] == [(2, 0)] * 10  # se queda quieta


def test_la_verificadora_falla_sin_rastro():
    banco = Banco(mundo_con_rastro([]))
    v = banco.agregar(Agente(9, banco.canal, ConfigAgente(verificadora=True)))
    banco.correr(5)
    assert v.estado is Estado.FALLIDA and v.ruta == [(0, 0)]


# ---------------------------------------------------------------- ciclo de vida (D3, I4, I5)


def test_ciclo_de_vida_en_un_corredor():
    """Ida sin depositar → DANZA → vuelta depositando → de nuevo a la meta → asentada."""
    mundo = Mundo(5, 1, [], inicio=(0, 0), meta=(4, 0), **PUENTE)
    banco = Banco(mundo)
    a = banco.agregar(Agente(1, banco.canal, ConfigAgente(deposito="constante", delta_t=5)))
    banco.correr(5)  # 4 movimientos de ida y el tick en que percibe la meta
    assert a.estado is Estado.VOLVIENDO and a.llegadas == 1
    assert sum(mundo.feromona(c) for c in mundo.celdas_libres()) == 1  # a la ida no depositó
    (danza,) = [m for m in banco.a_madre if nombre_de(m) == "DANZA"]
    assert danza["largo"] == 4 and danza["movs"] == [1, 1, 1, 1]
    assert not danza["flags"] & FLAG_VERIFICACION
    banco.correr(50, hasta=lambda: a.estado is Estado.ASENTADA)
    assert a.estado is Estado.ASENTADA and a.llegadas == 2 and a.pos == mundo.meta
    assert [mundo.feromona((x, 0)) for x in range(5)] == [0, 1, 1, 1, 1]  # el nido no se marca
    estados = [m for m in banco.a_madre if nombre_de(m) == "ESTADO"]
    assert len(estados) == math.ceil(banco.tick / 5)
    assert estados[-1]["llegadas"] >= 1


def test_deposito_segun_la_calidad_de_la_ruta():
    corto = Agente(1, CanalMemoria(), ConfigAgente(deposito="calidad"))
    corto.ruta = [(x, 0) for x in range(5)]  # 4 movimientos
    largo = Agente(2, CanalMemoria(), ConfigAgente(deposito="calidad"))
    largo.ruta = [(x, 0) for x in range(16)]  # 15 movimientos
    assert corto._deposito() == round(255 / 4) > largo._deposito() == 17


def test_la_colonia_completa_se_asienta_y_anuncia_rutas_validas():
    """20 semillas en el mundo L: las 6 agentes se asientan dentro del límite de 2000 ticks (I11)."""
    for semilla in range(20):
        mundo = mundo_con_distancia(mundo_l, semilla)
        banco, agentes = colonia(mundo, semilla)
        banco.correr(2000, hasta=todas_asentadas(agentes))
        assert todas_asentadas(agentes)(), f"semilla {semilla}"
        assert all(a.pos == mundo.meta for a in agentes)
        danzas = [m for m in banco.a_madre if nombre_de(m) == "DANZA"]
        assert len(danzas) == 6
        for danza in danzas:
            ruta = ruta_de(danza)
            assert ruta[0] == mundo.inicio and ruta[-1] == mundo.meta
            assert len(set(ruta)) == len(ruta)  # sin bucles
            for a, b in zip(ruta, ruta[1:]):
                assert b in [destino for _, destino in mundo.vecinos(a)]
            assert len(ruta) - 1 >= mundo.largo_optimo()


# ---------------------------------------------------------------- C1: la regla de decisión contra Deneubourg


@pytest.mark.parametrize("m_corta, m_larga", [(0, 0), (5, 0), (0, 5), (10, 3), (15, 15), (15, 0)])
def test_la_regla_de_decision_reproduce_la_formula_de_deneubourg(m_corta, m_larga):
    """Criterio C1 de PROMPT-ZERO, a nivel del programa de agente.

    Con k = 20 y α = 2, la frecuencia con que la hormiga elige la rama corta debe coincidir con
    p = (m₁ + k)² / [(m₁ + k)² + (m₂ + k)²] (fórmula 1.1; notebook deneubourg, celda [5]).
    Declarado antes de correr: N = 20 000 elecciones, semilla fija, tolerancia de 4 desviaciones
    estándar de una binomial.
    """
    puente = puente_doble(2, 3, **PUENTE)
    mundo, nido = puente.mundo, puente.mundo.inicio
    mundo.depositar(puente.rama_corta[1], m_corta)
    mundo.depositar(puente.rama_larga[1], m_larga)
    agente = Agente(1, CanalMemoria(), ConfigAgente(alpha=2, k=20, theta=0), semilla=2026)
    agente.pos, agente.ruta = nido, [nido]
    vecinas = mundo.percibir(nido)
    hacia_corta = agente._hacia(puente.rama_corta[1])
    assert sorted(agente.movimientos_validos(vecinas)) == sorted(
        [hacia_corta, agente._hacia(puente.rama_larga[1])])
    n = 20_000
    corta = sum(agente.elegir(vecinas) == hacia_corta for _ in range(n))
    p = (m_corta + 20) ** 2 / ((m_corta + 20) ** 2 + (m_larga + 20) ** 2)
    assert abs(corta / n - p) <= 4 * math.sqrt(p * (1 - p) / n)
