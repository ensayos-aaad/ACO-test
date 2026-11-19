"""Pruebas del artefacto 8: los motores de ejecución."""
import random
from dataclasses import replace

import pytest

from apoyo import Banco

from aco_gemelo.agente import Agente, ConfigAgente, Estado
from aco_gemelo.madre import ConfigMadre, Modo
from aco_gemelo.motor import ConfigEnsayo, Simulacion
from aco_gemelo.mundo import Mundo, mundo_aleatorio, mundo_l

CUADRICULA = dict(tau0=0.0, tau_max=1.0, unidad_deposito=1 / 255)


def mundo(semilla, fabrica=mundo_l, minimo=4):
    rng = random.Random(semilla)
    while True:
        m = fabrica(rng, **CUADRICULA)
        if m.largo_optimo() >= minimo:
            return m


def ensayo(semilla, modo=Modo.AUSENTE, motor="determinista", fabrica=mundo_l, **config):
    cfg = ConfigEnsayo(semilla=semilla, rho=0.0, registrar=True, madre=ConfigMadre(modo=modo))
    return Simulacion(mundo(semilla, fabrica), replace(cfg, **config)).correr(motor)


# ---------------------------------------------------------------- criterio 1: misma semilla, mismo resultado


@pytest.mark.parametrize("modo", list(Modo))
def test_misma_semilla_mismo_resultado(modo):
    assert ensayo(3, modo) == ensayo(3, modo)
    assert ensayo(3, modo).historial != ensayo(4, modo).historial


def test_reproducible_tambien_con_perdidas_retardos_y_mundo_aleatorio():
    extra = dict(p_perdida=0.2, retardo=(0, 3), rho=0.01, fabrica=mundo_aleatorio)
    a = ensayo(8, Modo.PISTA_DE_BAILE, **extra)
    assert a == ensayo(8, Modo.PISTA_DE_BAILE, **extra)
    assert a.trafico["agente_madre"]["perdidos"] > 0


def test_coincide_con_el_banco_de_pruebas():
    """El motor da los mismos tiempos que el banco con el que se midieron F-009 y F-010."""
    for semilla in range(5):
        m = mundo(semilla)
        banco = Banco(m)
        agentes = [banco.agregar(Agente(i, banco.canal, ConfigAgente(con_madre=False), semilla))
                   for i in range(1, 7)]
        esperado = banco.correr(2000, hasta=lambda: all(a.estado is Estado.ASENTADA for a in agentes))
        assert ensayo(semilla).ticks_asentadas == esperado


# ---------------------------------------------------------------- criterio 2: el motor de hilos corre el mismo paso()


@pytest.mark.parametrize("semilla", [0, 2])
def test_hilos_sin_madre_da_exactamente_lo_mismo_que_el_determinista(semilla):
    """Sin madre, cada agente decide solo con sus percepciones: el resultado no depende del motor."""
    con_hilos = ensayo(semilla, motor="hilos")
    determinista = ensayo(semilla)
    assert sorted(con_hilos.historial) == sorted(determinista.historial)
    assert replace(con_hilos, historial=[]) == replace(determinista, historial=[])


@pytest.mark.parametrize("modo", [Modo.PISTA_DE_BAILE, Modo.RESCATE, Modo.DIFUSION])
def test_hilos_con_madre_termina_bien(modo):
    """Con madre los tiempos pueden variar entre corridas, pero el ensayo debe cerrar bien."""
    resultado = ensayo(1, modo, motor="hilos")
    assert resultado.asentadas and resultado.bloqueadas == 0
    assert resultado.motivo in ("verificada", "verificadora_fallo")
    assert resultado.trafico["madre_agente"]["enviados"] > 0
    assert resultado.memoria_madre <= 64


def test_motor_desconocido():
    with pytest.raises(ValueError):
        ensayo(0, motor="cuantico")


# ---------------------------------------------------------------- criterio 3: límite de pasos (H1, I11)


def test_el_limite_de_pasos_cierra_el_ensayo():
    resultado = ensayo(0, limite=15)
    assert resultado.motivo == "limite" and resultado.ticks_total == 15
    assert not resultado.asentadas and not resultado.verificada
    assert resultado.ticks_asentadas is None and resultado.razon is None


def test_el_limite_incluye_la_verificacion():
    completo = ensayo(0)
    justo = ensayo(0, limite=completo.ticks_asentadas + 1)
    assert justo.asentadas and justo.motivo == "limite" and justo.ticks_total == completo.ticks_asentadas + 1


def test_al_cerrar_todas_reciben_el_fin():
    sim = Simulacion(mundo(0), ConfigEnsayo(rho=0.0, limite=15))
    sim.correr()
    assert all(a.terminado for a in sim.agentes)


# ---------------------------------------------------------------- las fases del ensayo


def test_la_verificadora_sale_cuando_todas_se_asentaron():
    for semilla in range(10):
        r = ensayo(semilla)
        assert r.asentadas and r.ticks_asentadas < r.ticks_total
        de_la_verificadora = [t for t, i, _ in r.historial if i == 7]
        assert min(de_la_verificadora) == r.ticks_asentadas  # ni un tick antes
        assert r.bloqueadas == 0
        if r.verificada:
            assert r.motivo == "verificada" and r.razon >= 1
            assert r.largo_verificado >= r.largo_optimo
        else:
            assert r.motivo == "verificadora_fallo" and r.razon is None


def test_ensayo_minimo_en_un_corredor():
    """Caso que se puede seguir a mano: una agente en un corredor de 5 celdas."""
    m = Mundo(5, 1, [], inicio=(0, 0), meta=(4, 0), tau0=0.0, tau_max=15.0, unidad_deposito=1.0)
    cfg = ConfigEnsayo(n_agentes=1, rho=0.0, madre=ConfigMadre(modo=Modo.AUSENTE),
                       agente=ConfigAgente(deposito="constante"))
    r = Simulacion(m, cfg).correr()
    assert (r.motivo, r.largo_optimo, r.largo_verificado, r.razon) == ("verificada", 4, 4, 1.0)
    assert r.ticks_asentadas == 13  # 4 de ida + 1 + 4 de vuelta + 4 de nuevo a la meta
    assert r.ticks_total == 13 + 5
    assert r.trafico["agente_madre"]["enviados"] == 0  # sin madre no se le habla
    assert r.trafico["mundo_agente"]["enviados"] == 2 * 13 + 2 * 2 * 5  # percepción y acción por tick


# ---------------------------------------------------------------- salidas escalonadas (J1)


def test_salidas_escalonadas():
    """Con salida_cada = 3, la agente j (desde 0) no se mueve antes del tick 3·j."""
    r = ensayo(0, salida_cada=3)
    primero = {}
    for t, i, _ in r.historial:
        primero.setdefault(i, t)
    for i in range(1, 7):
        assert primero[i] == 3 * (i - 1)
    assert r.asentadas and r.bloqueadas == 0
    assert ensayo(0, salida_cada=3) == r  # sigue siendo reproducible


def test_salidas_escalonadas_con_hilos():
    """Sin madre, el motor de hilos da exactamente lo mismo que el determinista."""
    con_hilos = ensayo(2, motor="hilos", salida_cada=2)
    determinista = ensayo(2, salida_cada=2)
    assert sorted(con_hilos.historial) == sorted(determinista.historial)
    assert replace(con_hilos, historial=[]) == replace(determinista, historial=[])


# ---------------------------------------------------------------- bloque B de PLAN-MEJORAS (ideas de Gemini)


def test_b1_la_madre_anuncia_el_ensayo_con_inicio():
    con_madre = ensayo(0, Modo.PISTA_DE_BAILE)
    sin_madre = ensayo(0, Modo.AUSENTE)
    # INICIO (14 B) se cuenta como tráfico madre → agentes; sin madre no se envía.
    assert con_madre.trafico["madre_agente"]["enviados"] >= 1
    sim = Simulacion(mundo(0), ConfigEnsayo(rho=0.0, madre=ConfigMadre(modo=Modo.DIFUSION)))
    assert sim.canal.trafico[3].enviados == 1 and sim.canal.trafico[3].bytes == 14  # antes de correr
    assert sin_madre.trafico["madre_agente"]["enviados"] == 0


def test_b2_cierre_abortado_si_ninguna_puede_seguir():
    from aco_gemelo.mundo import Mundo

    # Una sola celda libre además del nido... y la meta encerrada no es posible (el BFS lo impide),
    # así que forzamos el caso: la agente queda FALLIDA porque no tiene a dónde moverse.
    m = Mundo(2, 1, [], inicio=(0, 0), meta=(1, 0), tau0=0.0, tau_max=1.0)
    sim = Simulacion(m, ConfigEnsayo(n_agentes=1, rho=0.0, madre=ConfigMadre(modo=Modo.AUSENTE)))
    sim.agentes[0].estado = Estado.FALLIDA
    r = sim.correr()
    assert r.motivo == "abortado" and r.ticks_total == 0 and not r.asentadas


def test_b3_memoria_maxima_de_la_madre():
    sim = Simulacion(mundo(1), ConfigEnsayo(semilla=1, rho=0.0, madre=ConfigMadre(modo=Modo.DIFUSION)))
    maxima = 0
    original = sim.madre.paso

    def espia(t):
        nonlocal maxima
        original(t)
        maxima = max(maxima, sim.madre.memoria_usada())

    sim.madre.paso = espia
    r = sim.correr()
    assert r.memoria_madre_max == maxima >= r.memoria_madre and r.memoria_madre_max <= 64


def test_b4_la_madre_registra_la_verificacion_aun_con_retardo():
    for semilla in range(4):
        r = ensayo(semilla, Modo.PISTA_DE_BAILE, retardo=(2, 4))
        if r.motivo == "verificada":
            assert r.madre_verificacion == "ok"
        elif r.motivo == "verificadora_fallo":
            assert r.madre_verificacion == "fallo"


def test_b5_acciones_en_orden_fijo():
    r = ensayo(2)
    for t in {t for t, _, _ in r.historial}:
        ids = [i for tt, i, _ in r.historial if tt == t]
        assert ids == sorted(ids)


@pytest.mark.parametrize("modo", list(Modo))
def test_b7_hilos_sincronos_dan_lo_mismo_que_el_determinista_tambien_con_madre(modo):
    sincronos = ensayo(1, modo, motor="hilos_sincronos")
    determinista = ensayo(1, modo)
    assert sincronos == determinista


def test_c3_mapa_de_la_madre_tick_a_tick():
    r = ensayo(1, Modo.DIFUSION)
    assert len(r.mapa_madre) == r.ticks_total
    conocidas = [bin(c).count("1") for c, _ in r.mapa_madre]
    assert conocidas == sorted(conocidas) and conocidas[-1] > 0  # el mapa de la madre solo crece
    ancho = 8
    final = {(i % ancho, i // ancho) for i in range(64) if r.mapa_madre[-1][0] >> i & 1}
    assert len(final) == conocidas[-1]
    sin_mapa = ensayo(1, Modo.PISTA_DE_BAILE)  # la pista de baile no guarda mapa
    assert all(c == 0 and o == 0 for c, o in sin_mapa.mapa_madre)
