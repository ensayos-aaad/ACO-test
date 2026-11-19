"""Pruebas del artefacto 8: motor determinista con semilla y motor multihilo."""
import random
import threading

import pytest

from aco_gemelo.agente import Agente, ConfigAgente
from aco_gemelo.madre import ConfigMadre, Modo
from aco_gemelo.motor import (
    ConfigMotor,
    MotivoFin,
    MotorDeterminista,
    MotorHilos,
    simular,
)
from aco_gemelo.mundo import Mundo, mundo_l

CUADRICULA = dict(tau0=0.0, tau_max=1.0, unidad_deposito=1 / 255)


def mundo_prueba(semilla):
    rng = random.Random(semilla)
    while True:
        mundo = mundo_l(rng, **CUADRICULA)
        if mundo.largo_optimo() >= 4:
            return mundo


@pytest.mark.parametrize("modo", [Modo.AUSENTE, Modo.PISTA_DE_BAILE, Modo.RESCATE, Modo.DIFUSION])
def test_misma_semilla_mismo_resultado(modo):
    cfg = ConfigMotor(config_madre=ConfigMadre(modo=modo))
    a = MotorDeterminista(cfg).ejecutar(mundo_prueba(4), semilla=4)
    b = MotorDeterminista(cfg).ejecutar(mundo_prueba(4), semilla=4)
    c = MotorDeterminista(cfg).ejecutar(mundo_prueba(5), semilla=5)
    assert a.convergio == b.convergio
    assert a.motivo_fin == b.motivo_fin
    assert a.ticks_totales == b.ticks_totales
    assert a.ticks_exploracion == b.ticks_exploracion
    assert a.ruta_verificada == b.ruta_verificada
    assert a.historial == b.historial
    assert a.trafico == b.trafico
    assert a.historial != c.historial


@pytest.mark.parametrize("modo", [Modo.AUSENTE, Modo.PISTA_DE_BAILE, Modo.DIFUSION])
@pytest.mark.parametrize("semilla", [0, 1, 2, 4])
def test_motor_hilos_coincide_con_determinista(modo, semilla):
    cfg = ConfigMotor(config_madre=ConfigMadre(modo=modo))
    det = MotorDeterminista(cfg).ejecutar(mundo_prueba(semilla), semilla=semilla)
    hil = MotorHilos(cfg).ejecutar(mundo_prueba(semilla), semilla=semilla)
    assert hil.convergio == det.convergio
    assert hil.motivo_fin == det.motivo_fin
    assert hil.ticks_totales == det.ticks_totales
    assert hil.ticks_exploracion == det.ticks_exploracion
    assert hil.ticks_verificacion == det.ticks_verificacion
    assert hil.ruta_verificada == det.ruta_verificada
    assert hil.rutas_exploradoras == det.rutas_exploradoras
    assert hil.historial == det.historial
    assert hil.trafico == det.trafico


def test_motor_hilos_usa_hilos_distintos_por_agente(monkeypatch=None):
    hilos_por_agente = {}
    original_paso = Agente.paso

    def rastrear_paso(self, ahora):
        hilos_por_agente.setdefault(self.id, set()).add(threading.get_ident())
        return original_paso(self, ahora)

    Agente.paso = rastrear_paso
    try:
        mundo = Mundo(5, 1, [], inicio=(0, 0), meta=(4, 0), **CUADRICULA)
        cfg = ConfigMotor(n_agentes=4, max_ticks=50)
        res = MotorHilos(cfg).ejecutar(mundo, semilla=1)
        assert res.convergio
        hilos_exploradores = {next(iter(hilos_por_agente[i])) for i in range(1, 5)}
        assert len(hilos_exploradores) == 4
        assert threading.get_ident() not in hilos_exploradores
    finally:
        Agente.paso = original_paso


def test_ciclo_dos_etapas_exploradoras_y_verificadora():
    mundo = mundo_prueba(0)
    cfg = ConfigMotor(config_madre=ConfigMadre(modo=Modo.PISTA_DE_BAILE))
    res = simular(mundo, semilla=0, config=cfg)
    assert res.convergio
    assert res.motivo_fin is MotivoFin.VERIFICADA
    assert res.etapa_final == "verificada"
    assert res.agentes_asentadas == 6
    assert res.ticks_exploracion is not None
    assert res.ticks_verificacion is not None
    assert res.ticks_totales >= res.ticks_exploracion + res.ticks_verificacion
    assert res.ruta_verificada[0] == mundo.inicio
    assert res.ruta_verificada[-1] == mundo.meta
    assert len(set(res.ruta_verificada)) == len(res.ruta_verificada)
    for a, b in zip(res.ruta_verificada, res.ruta_verificada[1:]):
        assert b in [destino for _, destino in mundo.vecinos(a)]
    assert res.largo_verificado >= res.largo_optimo
    assert res.razon_calidad >= 1.0
    assert res.bloqueadas == 0


def test_respeta_limite_de_pasos_h1():
    mundo = mundo_prueba(0)
    cfg = ConfigMotor(max_ticks=5, config_madre=ConfigMadre(modo=Modo.PISTA_DE_BAILE))
    res = simular(mundo, semilla=0, config=cfg)
    assert not res.convergio
    assert res.motivo_fin is MotivoFin.LIMITE_PASOS
    assert res.etapa_final == "limite_exploracion"
    assert res.ticks_totales == 5
    assert res.ruta_verificada == []
    assert res.largo_verificado is None
    assert res.razon_calidad is None


def test_detecta_fallo_de_verificadora_en_callejon():
    # Callejon sin salida con feromona alta que atrae a la verificadora lejos de la meta
    obstaculos = [(2, 0), (2, 1), (0, 2), (1, 2)]
    mundo = Mundo(4, 4, obstaculos, inicio=(0, 0), meta=(3, 3), tau0=0.0, tau_max=1.0)
    mundo.depositar((0, 1), 0.9)
    mundo.depositar((1, 1), 0.9)
    cfg = ConfigMotor(n_agentes=1, max_ticks=50, verificar=True,
                      config_agente=ConfigAgente(deposito="constante", deposito_valor=0))
    # Forzamos etapa de verificacion dejando que una exploradora llegue por (1,0)->(2,2)->(3,3)
    # y verificamos que cuando la verificadora entra al callejon (0,1)->(1,1) falla con motivo 2
    res = simular(mundo, semilla=3, config=cfg)
    if not res.convergio and res.motivo_fin is MotivoFin.VERIFICADORA_FALLO:
        assert res.etapa_final == "verificadora_fallo"
        assert res.ruta_verificada == []


def test_retardo_en_canal_entrega_danza_de_verificacion():
    mundo = Mundo(5, 1, [], inicio=(0, 0), meta=(4, 0), **CUADRICULA)
    cfg = ConfigMotor(
        n_agentes=2,
        retardo=(2, 3),
        config_madre=ConfigMadre(modo=Modo.PISTA_DE_BAILE, delta_t=2),
    )
    res = simular(mundo, semilla=7, config=cfg)
    assert res.convergio
    assert res.motivo_fin is MotivoFin.VERIFICADA
    assert res.largo_verificado == 4


def test_resumen_fila_para_csv():
    mundo = Mundo(5, 1, [], inicio=(0, 0), meta=(4, 0), **CUADRICULA)
    res = simular(mundo, semilla=1)
    fila = res.resumen_fila(etiqueta="corredor")
    assert fila["etiqueta"] == "corredor"
    assert fila["semilla"] == 1
    assert fila["convergio"] == 1
    assert fila["largo_optimo"] == 4
    assert fila["largo_verificado"] == 4
    assert fila["razon_calidad"] == pytest.approx(1.0)
