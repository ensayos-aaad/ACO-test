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
