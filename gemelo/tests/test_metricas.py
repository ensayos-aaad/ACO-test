"""Pruebas del artefacto 10: métricas."""
import csv
import random

import pytest

from aco_gemelo.__main__ import main
from aco_gemelo.agente import ConfigAgente
from aco_gemelo.canal import CanalMemoria
from aco_gemelo.madre import ConfigMadre, Madre, Modo
from aco_gemelo.metricas import FAMILIAS, conocimiento_del_mundo, fila, resumen
from aco_gemelo.motor import ConfigEnsayo, Simulacion
from aco_gemelo.mundo import Mundo, mundo_l

CUADRICULA = dict(tau0=0.0, tau_max=1.0, unidad_deposito=1 / 255)


def simular(semilla, modo, **config):
    rng = random.Random(semilla)
    mundo = mundo_l(rng, **CUADRICULA)
    while mundo.largo_optimo() < 4:
        mundo = mundo_l(rng, **CUADRICULA)
    cfg = ConfigEnsayo(semilla=semilla, rho=0.0, registrar=True, madre=ConfigMadre(modo=modo),
                       **config)
    sim = Simulacion(mundo, cfg)
    return sim, sim.correr()


def corredor():
    mundo = Mundo(5, 1, [], inicio=(0, 0), meta=(4, 0), tau0=0.0, tau_max=15.0, unidad_deposito=1.0)
    cfg = ConfigEnsayo(n_agentes=1, rho=0.0, registrar=True, madre=ConfigMadre(modo=Modo.AUSENTE),
                       agente=ConfigAgente(deposito="constante"))
    return Simulacion(mundo, cfg).correr()


# ---------------------------------------------------------------- criterio 1: convergencia según G1


def test_convergencia_g1_en_el_corredor():
    """G1: todas asentadas y la verificadora llega. Caso que se puede seguir a mano."""
    r = corredor()
    assert r.asentadas and r.verificada and r.motivo == "verificada"
    assert r.ticks_asentadas == 13
    f = fila(0, "corredor", r)
    assert (f["asentadas"], f["verificada"], f["ticks_asentadas"], f["ticks_total"]) == (1, 1, 13, 18)


def test_sin_verificacion_no_hay_convergencia():
    _, r = simular(0, Modo.AUSENTE, limite=15)
    f = fila(0, "L", r)
    assert (f["asentadas"], f["verificada"], f["motivo"]) == (0, 0, "limite")
    assert f["ticks_asentadas"] is None and f["razon"] is None


def test_la_serie_muestra_la_convergencia_en_el_tiempo():
    sim, r = simular(1, Modo.DIFUSION)
    assert [p["tick"] for p in r.serie] == list(range(r.ticks_total))
    for clave in ("llegaron", "asentadas", "conocimiento", "bytes_madre"):
        valores = [p[clave] for p in r.serie]
        assert valores == sorted(valores), clave  # nunca retroceden
    assert all(p["asentadas"] <= p["llegaron"] <= 6 for p in r.serie)
    assert r.serie[-1]["asentadas"] == 6
    primero_completo = next(p["tick"] for p in r.serie if p["asentadas"] == 6)
    assert primero_completo == r.ticks_asentadas - 1  # se registra al cerrar el tick anterior


def test_sin_registrar_no_se_guarda_la_serie():
    mundo = mundo_l(random.Random(0), **CUADRICULA)
    r = Simulacion(mundo, ConfigEnsayo(rho=0.0)).correr()
    assert r.serie == [] and r.historial == []


# ---------------------------------------------------------------- criterio 2: calidad frente al BFS


def test_calidad_es_largo_verificado_sobre_optimo():
    r = corredor()
    assert (r.largo_optimo, r.largo_verificado, r.razon) == (4, 4, 1.0)
    for semilla in range(8):
        _, r = simular(semilla, Modo.PISTA_DE_BAILE)
        f = fila(semilla, "L", r)
        if r.verificada:
            assert f["razon"] == round(r.largo_verificado / r.largo_optimo, 4) >= 1
        else:
            assert f["razon"] is None and f["largo_verificado"] is None


# ---------------------------------------------------------------- conocimiento del mundo de la madre


def test_conocimiento_del_mundo_caso_a_mano():
    mundo = Mundo(4, 2, [(1, 0), (2, 1)], inicio=(0, 0), meta=(3, 1))  # 8 celdas, 2 obstáculos
    madre = Madre(CanalMemoria(), ConfigMadre(modo=Modo.DIFUSION))
    assert conocimiento_del_mundo(madre, mundo) == 0  # no sabe nada
    madre.conocidas = {(0, 0), (1, 0), (2, 0)}
    madre.obstaculos = {(1, 0)}
    assert conocimiento_del_mundo(madre, mundo) == 3 / 8
    madre.conocidas |= {(2, 1)}  # la conoce, pero cree que está libre: no cuenta
    assert conocimiento_del_mundo(madre, mundo) == 3 / 8
    madre.obstaculos |= {(2, 1)}
    assert conocimiento_del_mundo(madre, mundo) == 4 / 8
    madre.conocidas = {(x, y) for x in range(4) for y in range(2)}
    assert conocimiento_del_mundo(madre, mundo) == 1
    madre.obstaculos |= {(0, 1)}  # un obstáculo inventado baja el conocimiento
    assert conocimiento_del_mundo(madre, mundo) == 7 / 8


@pytest.mark.parametrize("modo, con_mapa", [(Modo.AUSENTE, False), (Modo.PISTA_DE_BAILE, False),
                                           (Modo.RESCATE, True), (Modo.DIFUSION, True)])
def test_conocimiento_segun_el_modo(modo, con_mapa):
    sim, r = simular(2, modo)
    if con_mapa:
        assert 0 < r.conocimiento <= 1
        assert r.conocimiento == conocimiento_del_mundo(sim.madre, sim.mundo)
        assert sim.madre.obstaculos <= set(sim.mundo.obstaculos)  # no inventa obstáculos
    else:
        assert r.conocimiento is None and fila(2, "L", r)["conocimiento"] is None


# ---------------------------------------------------------------- criterio 3: bytes por familia


def test_bytes_por_familia_en_el_corredor():
    f = fila(0, "corredor", corredor())
    # 13 ticks con 1 agente y 5 con 2 (la verificadora): una PERCEPCION (18 B) y una ACCION (9 B) cada uno.
    assert f["mensajes_mundo_agente"] == 2 * (13 + 2 * 5)
    assert f["bytes_mundo_agente"] == (13 + 2 * 5) * (18 + 9)
    for familia in FAMILIAS[1:]:  # sin madre y sin mensajes entre agentes
        assert f[f"mensajes_{familia}"] == f[f"bytes_{familia}"] == 0


def test_bytes_por_familia_coinciden_con_el_canal():
    sim, r = simular(3, Modo.DIFUSION)
    f = fila(3, "L", r)
    for numero, familia in enumerate(FAMILIAS):
        assert f[f"mensajes_{familia}"] == sim.canal.trafico[numero].enviados
        assert f[f"bytes_{familia}"] == sim.canal.trafico[numero].bytes
    assert f["bytes_agente_madre"] > 0 and f["bytes_madre_agente"] > 0
    assert f["modo_madre"] == "difusion" and f["memoria_madre"] <= 64


# ---------------------------------------------------------------- resumen de un lote


def _fila(asentadas, verificada, ticks, razon, bytes_madre=100):
    base = {f"bytes_{familia}": 0 for familia in FAMILIAS}
    base.update(asentadas=asentadas, verificada=verificada, ticks_asentadas=ticks, razon=razon,
                conocimiento=None, bytes_agente_madre=bytes_madre)
    return base


def test_resumen_de_un_lote_caso_a_mano():
    filas = [_fila(1, 1, 100, 1.0), _fila(1, 1, 140, 2.0), _fila(1, 0, 120, None),
             _fila(0, 0, None, None, bytes_madre=300)]
    r = resumen(filas)
    assert r["n"] == 4
    assert (r["asentadas"]["exitos"], r["asentadas"]["tasa"]) == (3, 0.75)
    assert (r["verificadas"]["exitos"], r["verificadas"]["tasa"]) == (2, 0.5)
    assert r["ticks_media"] == 120 and r["ticks_varianza"] == pytest.approx(800 / 3)
    assert (r["ticks_min"], r["ticks_max"]) == (100, 140)
    assert r["razon_media"] == 1.5 and r["conocimiento_medio"] is None
    assert r["bytes_agente_madre_media"] == 150
    ic = r["verificadas"]
    assert 0 < ic["ic95_bajo"] < 0.5 < ic["ic95_alto"] < 1
    assert ic["ic95_bajo"] == pytest.approx(0.150, abs=0.001)  # Wilson, 2 de 4


def test_resumen_sin_datos():
    with pytest.raises(ValueError):
        resumen([])
    r = resumen([_fila(0, 0, None, None)])
    assert r["ticks_media"] is None and r["razon_media"] is None


def test_resumen_acepta_las_filas_leidas_de_un_csv(tmp_path, capsys):
    """El CSV de ``batch`` se puede volver a leer y resumir: da lo mismo que en memoria."""
    salida = tmp_path / "r.csv"
    config = tmp_path / "c.yaml"
    config.write_text("madre: {modo: difusion}\nensayo: {rho: 0.0}\n", encoding="utf-8")
    assert main(["batch", "--config", str(config), "--semillas", "5", "--salida", str(salida)]) == 0
    impreso = capsys.readouterr().out
    assert "IC 95 %" in impreso and "conocimiento del mundo de la madre" in impreso
    with open(salida, newline="", encoding="utf-8") as archivo:
        filas = list(csv.DictReader(archivo))
    assert "conocimiento" in filas[0] and len(filas) == 5
    r = resumen(filas)
    assert r["asentadas"]["tasa"] == 1 and 0 < r["conocimiento_medio"] <= 1
    assert f"{r['ticks_media']:.1f}" in impreso
