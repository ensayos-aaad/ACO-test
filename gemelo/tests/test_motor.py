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
    """F-023 (5): la máxima se mide durante el ensayo, no al final.

    El espía mide la memoria después de cada lectura (también la lectura final de B4) y de cada
    paso de la madre. Al menos un ensayo debe tener máxima > final; si no, la prueba no
    distinguiría la máxima de la final.
    """
    supera = 0
    for semilla in range(4):
        sim = Simulacion(mundo(semilla), ConfigEnsayo(semilla=semilla, rho=0.0,
                                                      madre=ConfigMadre(modo=Modo.PISTA_DE_BAILE)))
        maxima = 0
        leer, paso = sim.madre.leer, sim.madre.paso

        def medir():
            nonlocal maxima
            maxima = max(maxima, sim.madre.memoria_usada())

        def espia_leer(*a, **k):
            salida = leer(*a, **k)
            medir()
            return salida

        def espia_paso(*a, **k):
            salida = paso(*a, **k)
            medir()
            return salida

        sim.madre.leer, sim.madre.paso = espia_leer, espia_paso
        r = sim.correr()
        assert r.memoria_madre_max == maxima >= r.memoria_madre
        assert r.memoria_madre_max <= sim.config.madre.memoria
        supera += r.memoria_madre_max > r.memoria_madre
    assert supera > 0


def test_b4_la_madre_registra_la_verificacion_aun_con_retardo():
    comprobados = 0
    for semilla in range(4):
        r = ensayo(semilla, Modo.PISTA_DE_BAILE, retardo=(2, 4))
        if r.motivo == "verificada":
            assert r.madre_verificacion == "ok"
            comprobados += 1
        elif r.motivo == "verificadora_fallo":
            assert r.madre_verificacion == "fallo"
            comprobados += 1
    assert comprobados > 0  # F-023 (5): si ningún ensayo llega a verificar, no se probó nada


def test_b5_acciones_en_orden_fijo():
    """F-023 (5): unas ACCION que llegan desordenadas se aplican en orden de id.

    El motor determinista ya llama a las agentes en orden, y desde F-023 (1) el canal también
    entrega por emisor, así que ni un ensayo completo ni el canal lo prueban: se le pasan al
    mundo las ACCION desordenadas a propósito, sin pasar por el canal. (Las agentes pueden
    compartir celda, por eso no hay un choque cuyo resultado dependa del orden; queda el orden
    del historial.)
    """
    from aco_gemelo.canal import CanalMemoria
    from aco_gemelo.motor.simulacion import ActorMundo
    from aco_gemelo.protocolo import ID_MUNDO, Contexto, crear

    m = Mundo(4, 4, [], inicio=(0, 0), meta=(3, 3), tau0=0.0, tau_max=1.0)
    canal = CanalMemoria(Contexto(4, 4, 8))
    actor = ActorMundo(m, canal, 0.0, True)
    for i in (1, 2, 3):
        canal.registrar(i)
        actor.agregar(i)
    desordenadas = [crear("ACCION", src=i, dst=ID_MUNDO, tick=0, accion=0, dir=0, deposito=0)
                    for i in (3, 1, 2)]
    actor.canal = type("CanalFijo", (), {"recibir": lambda self, _id: list(desordenadas)})()
    assert actor.aplicar_acciones(0) == {1, 2, 3}
    assert [i for _, i, _ in actor.historial] == [1, 2, 3]


@pytest.mark.parametrize("modo", list(Modo))
def test_b7_hilos_sincronos_dan_lo_mismo_que_el_determinista_tambien_con_madre(modo):
    sincronos = ensayo(1, modo, motor="hilos_sincronos")
    determinista = ensayo(1, modo)
    assert sincronos == determinista


@pytest.mark.parametrize("canal", [dict(p_perdida=0.2), dict(retardo=(0, 3)),
                                   dict(p_perdida=0.2, retardo=(1, 4))])
@pytest.mark.parametrize("modo", list(Modo))
def test_b7_hilos_sincronos_deterministas_con_perdidas_y_retardo(modo, canal):
    """F-023 (1): con pérdidas o retardo, repartir las agentes en hilos tampoco cambia nada."""
    for semilla in range(3):
        extra = dict(canal, rho=0.01, fabrica=mundo_aleatorio)
        determinista = ensayo(semilla, modo, **extra)
        for _ in range(2):
            assert ensayo(semilla, modo, motor="hilos_sincronos", **extra) == determinista


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


def test_b7_la_madre_lee_en_orden_de_tick_y_emisor():
    """F-023 (5): el orden propio de la madre, aparte del orden de entrega del canal.

    Desde F-023 (1) el canal ya entrega en orden fijo, así que quitar este orden no rompe el
    determinismo y ninguna prueba de motores lo nota (mutante ``mut_b7`` del revisor). Se
    prueba directo: mensajes desordenados se escuchan por (tick, emisor).
    """
    from aco_gemelo.madre import Madre

    llegada = [{"src": 3, "tick": 5}, {"src": 1, "tick": 7}, {"src": 2, "tick": 5}, {"src": 1, "tick": 5}]
    canal = type("CanalFijo", (), {"registrar": lambda self, _id: None,
                                   "recibir": lambda self, _id: list(llegada)})()
    madre = Madre(canal, ConfigMadre(modo=Modo.DIFUSION))
    escuchados = []
    madre._escuchar = escuchados.append
    madre.leer()
    assert [(m["tick"], m["src"]) for m in escuchados] == [(5, 1), (5, 2), (5, 3), (7, 1)]


@pytest.mark.parametrize("modo", [Modo.DIFUSION, Modo.RESCATE])
def test_c3_el_ultimo_cuadro_coincide_con_el_conocimiento_aun_con_retardo(modo):
    """F-023 (6): la lectura final de B4 ya no cambia `conocimiento` después del último cuadro.

    Antes, con retardo (2, 4), DIFUSION semilla 3 daba 0,671875 frente a 0,640625 del cuadro.
    """
    for semilla in range(15):
        m = mundo(semilla)
        r = ensayo(semilla, modo, retardo=(2, 4))
        conocidas, obstaculos = r.mapa_madre[-1]
        aciertos = sum(
            bool(conocidas >> (y * m.ancho + x) & 1)
            and bool(obstaculos >> (y * m.ancho + x) & 1) == ((x, y) in m.obstaculos)
            for y in range(m.alto) for x in range(m.ancho))
        assert aciertos / (m.ancho * m.alto) == r.conocimiento == r.serie[-1]["conocimiento"]


@pytest.mark.parametrize("campo, valor", [("delta_t", 256), ("delta_t", 300), ("K", 256)])
def test_inicio_valida_los_campos_de_8_bits(campo, valor):
    """F-023 (7): antes fallaba al construir INICIO, con un error del codificador."""
    agente = ConfigAgente(K=valor) if campo == "K" else ConfigAgente()
    madre = ConfigMadre(modo=Modo.PISTA_DE_BAILE, delta_t=valor if campo == "delta_t" else 10)
    with pytest.raises(ValueError, match="INICIO"):
        ConfigEnsayo(agente=agente, madre=madre)
    sin_madre = ConfigMadre(modo=Modo.AUSENTE, delta_t=madre.delta_t)
    ConfigEnsayo(agente=agente, madre=sin_madre)  # sin madre no se envía INICIO: vale
    assert ConfigEnsayo(madre=ConfigMadre(modo=Modo.PISTA_DE_BAILE, delta_t=255)).madre.delta_t == 255
