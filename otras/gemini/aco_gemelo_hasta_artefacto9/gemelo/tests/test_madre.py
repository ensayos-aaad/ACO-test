"""Pruebas del artefacto 7: la madre y lo que el agente hace con ella."""
import random
import statistics

import pytest

from apoyo import Banco

from aco_gemelo.agente import Agente, ConfigAgente, Estado
from aco_gemelo.canal import CanalMemoria
from aco_gemelo.madre import ConfigMadre, Madre, Modo
from aco_gemelo.mundo import Mundo, mundo_l
from aco_gemelo.protocolo import (
    FLAG_RESCATE,
    FLAG_VERIFICACION,
    ID_MADRE,
    bloque_a_celdas,
    celda_a_byte,
    celdas_a_bloque,
    crear,
    nombre_de,
)

CUADRICULA = dict(tau0=0.0, tau_max=1.0, unidad_deposito=1 / 255)
AGENTES = (1, 2, 3, 4)


def madre_sola(modo, **config):
    canal = CanalMemoria()
    for i in AGENTES:
        canal.registrar(i)
    return canal, Madre(canal, ConfigMadre(modo=modo, **config))


def estado(src, experiencia, llegadas=0):
    return crear("ESTADO", src=src, dst=ID_MADRE, pos=0, estado=0, rol=0,
                 experiencia=experiencia, llegadas=llegadas)


def danza(src, movs, flags=0):
    return crear("DANZA", src=src, dst=ID_MADRE, flags=flags, ruta_id=1, inicio=0,
                 largo=len(movs), movs=movs)


def recibido(canal):
    return {i: [nombre_de(m) for m in canal.recibir(i)] for i in AGENTES}


def test_modo_ausente_no_envia_ni_recuerda():
    canal, madre = madre_sola(Modo.AUSENTE)
    canal.enviar(danza(1, [1, 1, 2]))
    for t in range(30):
        canal.avanzar(t)
        madre.paso(t)
    assert canal.trafico[3].enviados == 0 and madre.rutas == [] and madre.actuaciones == []


def test_modo_pista_de_baile_anuncia_y_entrega_la_ruta_pedida():
    canal, madre = madre_sola(Modo.PISTA_DE_BAILE)
    canal.enviar(danza(1, [1, 1, 2, 2, 1, 1]))
    canal.enviar(danza(2, [5, 5, 1]))
    madre.paso(0)
    anuncios = {i: canal.recibir(i) for i in AGENTES}
    for i in AGENTES:
        (recluta,) = anuncios[i]
        assert nombre_de(recluta) == "RECLUTA" and recluta["n"] == 2
        corta, larga = recluta["rutas"]
        assert (corta["largo"], larga["largo"]) == (3, 6)
        assert corta["peso"] == 2 * larga["peso"] == 170
    canal.enviar(crear("PIDE_RUTA", src=3, dst=ID_MADRE, ruta_id=corta["ruta_id"]))
    canal.avanzar(10)
    madre.paso(10)
    ruta = [m for m in canal.recibir(3) if nombre_de(m) == "RUTA"]
    assert len(ruta) == 1 and ruta[0]["movs"] == [5, 5, 1]
    assert all("RUTA" not in nombres for i, nombres in recibido(canal).items() if i != 3)
    assert madre.pedidos == {}


def test_modo_rescate_solo_ayuda_a_la_rezagada_y_una_sola_vez():
    canal, madre = madre_sola(Modo.RESCATE)
    canal.enviar(danza(1, [1, 1, 2]))
    for src, experiencia, llegadas in [(1, 40, 1), (2, 40, 0), (3, 40, 0), (4, 10, 0)]:
        canal.enviar(estado(src, experiencia, llegadas))
    madre.paso(0)
    assert madre.rescatadas == {4}
    buzones = {i: canal.recibir(i) for i in AGENTES}
    assert [len(buzones[i]) for i in AGENTES] == [0, 0, 0, 1]
    (ruta,) = buzones[4]
    assert nombre_de(ruta) == "RUTA" and ruta["flags"] & FLAG_RESCATE and ruta["movs"] == [1, 1, 2]
    canal.avanzar(10)
    madre.paso(10)
    assert recibido(canal) == {i: [] for i in AGENTES}


def test_modo_difusion_envia_mapa_y_mejor_ruta_a_todos():
    canal, madre = madre_sola(Modo.DIFUSION)
    conocidas = {(0, 0), (1, 0), (1, 1), (5, 6)}
    for origen in [(0, 0), (4, 4)]:
        canal.enviar(crear("FRAGMENTO", src=1, dst=ID_MADRE, origen=celda_a_byte(origen),
                           conocidas=celdas_a_bloque(origen, conocidas),
                           obstaculos=celdas_a_bloque(origen, {(1, 1)})))
    canal.enviar(danza(2, [1, 2]))
    madre.paso(0)
    assert madre.conocidas == conocidas and madre.obstaculos == {(1, 1)}
    for i in AGENTES:
        mapa, ruta = canal.recibir(i)
        assert nombre_de(mapa) == "MAPA" and nombre_de(ruta) == "RUTA"
        assert {(n % 8, n // 8) for n, bit in enumerate(mapa["conocidas"]) if bit} == conocidas
        assert sum(mapa["obstaculos"]) == 1 and mapa["obstaculos"][1 * 8 + 1] == 1


def test_bloques_de_fragmento_ida_y_vuelta():
    celdas = {(4, 4), (7, 4), (5, 6), (7, 7)}
    assert bloque_a_celdas((4, 4), celdas_a_bloque((4, 4), celdas | {(0, 0)})) == celdas
    assert celdas_a_bloque((0, 0), {(0, 0)}) == 0x8000


@pytest.mark.parametrize("modo", [Modo.PISTA_DE_BAILE, Modo.RESCATE, Modo.DIFUSION])
@pytest.mark.parametrize("delta_t", [1, 7, 10])
def test_actua_solo_cada_delta_t(modo, delta_t):
    canal, madre = madre_sola(modo, delta_t=delta_t)
    ticks_con_envio = []
    for t in range(100):
        canal.avanzar(t)
        canal.enviar(danza(1, [1] * (1 + t % 5)))
        canal.enviar(estado(2, 1 + t % 3))
        antes = canal.trafico[3].enviados
        madre.paso(t)
        if canal.trafico[3].enviados > antes:
            ticks_con_envio.append(t)
    assert madre.actuaciones == list(range(0, 100, delta_t))
    assert set(ticks_con_envio) <= set(madre.actuaciones)


@pytest.mark.parametrize("modo", [Modo.PISTA_DE_BAILE, Modo.RESCATE, Modo.DIFUSION])
@pytest.mark.parametrize("memoria", [32, 64])
def test_nunca_supera_su_presupuesto_de_memoria(modo, memoria):
    canal, madre = madre_sola(modo, memoria=memoria)
    rng = random.Random(1)
    for t in range(200):
        canal.avanzar(t)
        canal.enviar(danza(1 + t % 4, [rng.randrange(8) for _ in range(rng.randint(3, 40))]))
        canal.enviar(estado(1 + t % 4, rng.randrange(60)))
        canal.enviar(crear("PIDE_RUTA", src=1 + t % 4, dst=ID_MADRE, ruta_id=rng.randrange(9)))
        madre.paso(t)
        assert madre.memoria_usada() <= memoria
    assert madre.descartadas > 0
    largos = [len(r["movs"]) for r in madre.rutas]
    assert largos == sorted(largos)
    if memoria == 64:
        assert largos and largos[0] <= 6


def test_no_guarda_rutas_repetidas():
    canal, madre = madre_sola(Modo.PISTA_DE_BAILE)
    for src in (1, 2, 3):
        canal.enviar(danza(src, [1, 1, 2]))
    madre.paso(0)
    assert len(madre.rutas) == 1


@pytest.mark.parametrize("umbral, esperadas", [(0.5, [4]), (0.9, [3, 4]), (0.2, [])])
def test_detecta_a_la_rezagada_por_umbral(umbral, esperadas):
    canal, madre = madre_sola(Modo.RESCATE, umbral_rescate=umbral)
    for src, experiencia in [(1, 50), (2, 40), (3, 28), (4, 10)]:
        canal.enviar(estado(src, experiencia))
    madre.paso(0)
    assert madre.rezagadas() == esperadas


def test_la_que_ya_llego_no_es_rezagada():
    canal, madre = madre_sola(Modo.RESCATE)
    canal.enviar(estado(1, 50))
    canal.enviar(estado(2, 50))
    canal.enviar(estado(3, 5, llegadas=1))
    madre.paso(0)
    assert madre.rezagadas() == []


def test_registra_el_resultado_de_la_verificadora():
    canal, madre = madre_sola(Modo.PISTA_DE_BAILE)
    canal.enviar(danza(9, [1, 1, 2, 2], flags=FLAG_VERIFICACION))
    madre.paso(0)
    assert (madre.verificacion, madre.largo_verificado) == ("ok", 4)
    assert madre.rutas == []
    canal, madre = madre_sola(Modo.PISTA_DE_BAILE)
    canal.enviar(crear("PIDE_RESCATE", src=9, dst=ID_MADRE, flags=FLAG_VERIFICACION,
                       experiencia=3, motivo=1))
    madre.paso(0)
    assert madre.verificacion == "fallo"


def colonia(mundo, semilla, modo, n=6, **config):
    banco = Banco(mundo)
    if modo is not Modo.AUSENTE:
        banco.madre = Madre(banco.canal, ConfigMadre(modo=modo))
    config = dict(con_madre=modo is not Modo.AUSENTE,
                  informa_mapa=modo in (Modo.RESCATE, Modo.DIFUSION), **config)
    agentes = [banco.agregar(Agente(i, banco.canal, ConfigAgente(**config), semilla))
               for i in range(1, n + 1)]
    return banco, agentes


def asentadas(agentes):
    return lambda: all(a.estado is Estado.ASENTADA for a in agentes)


def test_la_agente_reclutada_pide_la_ruta_la_recorre_la_refuerza_y_se_asienta():
    mundo = Mundo(5, 3, [(x, 1) for x in range(1, 4)], inicio=(0, 1), meta=(4, 1),
                  tau0=0.0, tau_max=15.0, unidad_deposito=1.0)
    banco = Banco(mundo)
    banco.madre = Madre(banco.canal, ConfigMadre(modo=Modo.PISTA_DE_BAILE, delta_t=2))
    arriba = [0, 1, 1, 1, 1, 2]
    banco.canal.enviar(crear("DANZA", src=7, dst=ID_MADRE, ruta_id=1,
                             inicio=celda_a_byte(mundo.inicio), largo=6, movs=arriba))
    a = banco.agregar(Agente(1, banco.canal, ConfigAgente(deposito="constante", delta_t=2)))
    banco.correr(200, hasta=asentadas([a]))
    assert a.estado is Estado.ASENTADA and a.pos == mundo.meta and a.llegadas == 2
    celdas_arriba = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)]
    assert a.ruta == [mundo.inicio, *celdas_arriba, mundo.meta]
    assert [mundo.feromona(c) for c in celdas_arriba] == [1] * 5
    assert all(mundo.feromona((x, 2)) == 0 for x in range(5))
    assert banco.bloqueadas == 0


def test_la_agente_rescatada_informa_el_estado_3():
    mundo = Mundo(5, 1, [], inicio=(0, 0), meta=(4, 0), tau0=0.0, tau_max=15.0)
    banco = Banco(mundo)
    a = banco.agregar(Agente(1, banco.canal, ConfigAgente(delta_t=1)))
    banco.correr(1)
    banco.canal.enviar(crear("RUTA", src=ID_MADRE, dst=1, flags=FLAG_RESCATE, ruta_id=0,
                             inicio=0, largo=4, movs=[1, 1, 1, 1]))
    banco.correr(3)
    assert a.rescatada and a.codigo_estado == 3
    assert [m["estado"] for m in banco.a_madre if nombre_de(m) == "ESTADO"][-1] == 3


def test_la_agente_que_ya_llego_ignora_la_ayuda():
    mundo = Mundo(5, 1, [], inicio=(0, 0), meta=(4, 0), tau0=0.0, tau_max=15.0)
    banco = Banco(mundo)
    a = banco.agregar(Agente(1, banco.canal, ConfigAgente()))
    banco.correr(6)
    assert a.estado is Estado.VOLVIENDO
    banco.canal.enviar(crear("RUTA", src=ID_MADRE, dst=1, ruta_id=0, inicio=0, largo=1, movs=[1]))
    banco.correr(30, hasta=asentadas([a]))
    assert a.estado is Estado.ASENTADA and len(a.ruta) == 5 and not a.rescatada


def test_si_la_ruta_pedida_no_llega_vuelve_a_explorar():
    mundo = Mundo(6, 6, [], inicio=(0, 0), meta=(5, 5), **CUADRICULA)
    banco = Banco(mundo)
    a = banco.agregar(Agente(1, banco.canal, ConfigAgente(delta_t=3)))
    banco.canal.enviar(crear("RECLUTA", src=ID_MADRE, dst=1, n=1,
                             rutas=[dict(ruta_id=4, largo=5, peso=255)]))
    banco.correr(2)
    assert a.estado is Estado.ESPERANDO
    assert [m["ruta_id"] for m in banco.a_madre if nombre_de(m) == "PIDE_RUTA"] == [4]
    banco.correr(15)
    assert a.estado is not Estado.ESPERANDO


def test_con_el_mapa_de_la_colonia_explora_lo_desconocido():
    mundo = Mundo(3, 3, [], inicio=(1, 1), meta=(2, 2), **CUADRICULA)
    agente = Agente(1, CanalMemoria(), ConfigAgente())
    agente.pos, agente.ruta = (1, 1), [(1, 1)]
    vecinas = mundo.percibir((1, 1))
    vecinas[1 + 5]["clase"] = 0
    agente.mapa_colonia = {c for c in mundo.celdas_libres() if c != (0, 2)}
    assert {agente.elegir(vecinas) for _ in range(50)} == {6}


def test_el_mapa_de_la_madre_coincide_con_lo_que_vieron_las_agentes():
    mundo = mundo_l(random.Random(4), **CUADRICULA)
    banco, agentes = colonia(mundo, 4, Modo.DIFUSION, delta_t=2)
    banco.madre.config.delta_t = 2
    banco.correr(400)
    visto = set().union(*(a.conocidas for a in agentes))
    assert banco.madre.conocidas == visto
    assert banco.madre.obstaculos == set().union(*(a.obstaculos for a in agentes))
    assert banco.madre.obstaculos <= set(mundo.obstaculos)
    assert banco.madre.conocidas - banco.madre.obstaculos <= set(mundo.celdas_libres())


def _ticks_por_modo(modo, semillas):
    ticks = []
    for semilla in semillas:
        rng = random.Random(semilla)
        mundo = mundo_l(rng, **CUADRICULA)
        while mundo.largo_optimo() < 4:
            mundo = mundo_l(rng, **CUADRICULA)
        banco, agentes = colonia(mundo, semilla, modo)
        ticks.append(banco.correr(2000, hasta=asentadas(agentes)))
        assert asentadas(agentes)(), f"modo {modo.name}, semilla {semilla}"
        assert banco.bloqueadas == 0
        if banco.madre is not None:
            assert banco.madre.memoria_usada() <= banco.madre.config.memoria
    return ticks


def test_con_cualquier_modo_la_colonia_se_asienta_y_la_madre_acelera():
    semillas = range(20)
    base = _ticks_por_modo(Modo.AUSENTE, semillas)
    for modo in (Modo.PISTA_DE_BAILE, Modo.DIFUSION):
        ticks = _ticks_por_modo(modo, semillas)
        assert statistics.mean(ticks) < statistics.mean(base)
        assert statistics.pstdev(ticks) < statistics.pstdev(base)
    _ticks_por_modo(Modo.RESCATE, semillas)
