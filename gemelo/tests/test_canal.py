"""Pruebas del artefacto 5: canal en memoria."""
import pytest

from aco_gemelo.canal import Canal, CanalMemoria
from aco_gemelo.protocolo import (
    FLAG_ACK,
    ID_DIFUSION,
    ID_MADRE,
    ID_MUNDO,
    Contexto,
    a_binario,
    a_json,
    celda_a_byte,
    crear,
)

# Agentes 1..5 en fila; la madre (0) no tiene posición en el mundo.
POSICIONES = {1: (0, 0), 2: (1, 0), 3: (2, 0), 4: (1, 1), 5: (5, 5)}


def canal_con_agentes(**kwargs):
    canal = CanalMemoria(posicion=POSICIONES.get, **kwargs)
    for id_actor in (ID_MADRE, *POSICIONES):
        canal.registrar(id_actor)
    return canal


def baliza(src, seq=0):
    return crear("BALIZA", src=src, seq=seq, pos=celda_a_byte(POSICIONES[src]), estado=0, rol=0,
                 saltos_meta=15, fuerza=100)


def estado(src, seq=0, flags=0):
    return crear("ESTADO", src=src, dst=ID_MADRE, seq=seq, flags=flags, pos=0, estado=0, rol=0,
                 experiencia=1, llegadas=0)


def quien_recibio(canal):
    return {id_actor for id_actor in (ID_MADRE, *POSICIONES) if canal.recibir(id_actor)}


# ---------------------------------------------------------------- criterio 1: entrega dentro del radio r


def test_es_un_canal():
    assert isinstance(CanalMemoria(), Canal)


@pytest.mark.parametrize("radio, esperados", [(0, set()), (1, {2, 4}), (2, {2, 3, 4}), (5, {2, 3, 4, 5})])
def test_la_baliza_solo_llega_dentro_del_radio(radio, esperados):
    canal = canal_con_agentes(radio=radio)
    canal.enviar(baliza(1))
    assert quien_recibio(canal) == esperados  # ni el emisor ni la madre


def test_mensaje_con_destino_llega_solo_al_destino():
    canal = canal_con_agentes()
    canal.enviar(estado(5))
    assert quien_recibio(canal) == {ID_MADRE}


def test_difusion_de_la_madre_llega_a_todos_los_demas():
    canal = canal_con_agentes()
    canal.enviar(crear("FIN", src=ID_MADRE, dst=ID_DIFUSION, motivo=0))
    assert quien_recibio(canal) == set(POSICIONES)


def test_destino_no_registrado_es_un_error():
    canal = canal_con_agentes()
    with pytest.raises(ValueError):
        canal.enviar(crear("FIN", src=ID_MADRE, dst=99, motivo=0))
    with pytest.raises(ValueError):
        canal.recibir(99)


def test_cada_receptor_recibe_su_propia_copia():
    canal = canal_con_agentes()
    original = baliza(1)
    canal.enviar(original)
    copia_2, copia_4 = canal.recibir(2)[0], canal.recibir(4)[0]
    assert copia_2 == copia_4 == original
    copia_2["fuerza"] = 0
    assert copia_4["fuerza"] == 100 and original["fuerza"] == 100
    assert canal.recibir(2) == []  # recibir retira los mensajes


# ---------------------------------------------------------------- criterio 2: pérdidas y retardos reproducibles


def _traza(semilla):
    canal = canal_con_agentes(p_perdida=0.3, retardo=(0, 4), semilla=semilla, radio=2)
    traza = []
    for tick in range(60):
        canal.avanzar(tick)
        canal.enviar(baliza(1 + tick % 4, seq=tick))
        canal.enviar(estado(1 + tick % 5, seq=tick))
        for id_actor in (ID_MADRE, *POSICIONES):
            for msg in canal.recibir(id_actor):
                traza.append((tick, id_actor, msg["src"], msg["seq"]))
    return traza, canal.resumen()


def test_misma_semilla_misma_traza():
    assert _traza(11) == _traza(11)
    assert _traza(11) != _traza(12)


def test_el_retardo_se_respeta():
    canal = canal_con_agentes(retardo=(3, 3))
    canal.enviar(estado(1))
    for tick in range(3):
        canal.avanzar(tick)
        assert canal.recibir(ID_MADRE) == []
    assert canal.pendientes() == 1
    canal.avanzar(3)
    assert len(canal.recibir(ID_MADRE)) == 1
    with pytest.raises(ValueError):
        canal.avanzar(1)  # el tiempo no retrocede


def test_se_entregan_en_orden_de_llegada():
    canal = canal_con_agentes()
    for seq in range(10):
        canal.enviar(estado(1, seq=seq))
    assert [m["seq"] for m in canal.recibir(ID_MADRE)] == list(range(10))


def test_el_orden_de_los_envios_concurrentes_no_cambia_nada():
    """F-023 (1): cada emisor tiene su propio azar, y en un mismo tick se entrega por emisor.

    Dos emisores envían a la vez (como en el motor de hilos): sea cual sea el orden en que
    sus envíos llegan al canal, las pérdidas, los retardos y el orden de entrega son los mismos.
    """
    def recibido(orden):
        canal = canal_con_agentes(p_perdida=0.3, retardo=(0, 3), semilla=7)
        for t in range(6):
            canal.avanzar(t)
            for src, seq in orden(t):
                canal.enviar(estado(src, seq=seq))
        canal.avanzar(10)
        return [(m["src"], m["seq"]) for m in canal.recibir(ID_MADRE)]

    envios = lambda t: [(1, t * 10 + k) for k in range(5)] + [(2, t * 10 + k) for k in range(5)]
    alternados = lambda t: [e for par in zip(envios(t)[5:], envios(t)[:5]) for e in par]
    invertidos = lambda t: envios(t)[5:] + envios(t)[:5]
    base = recibido(envios)
    assert 0 < len(base) < 60  # hubo pérdidas, pero no todas
    assert recibido(alternados) == base
    assert recibido(invertidos) == base


@pytest.mark.parametrize("semilla", [0, 3, 2026, -1])
def test_el_azar_del_canal_es_independiente_del_de_las_agentes_y_del_mundo(semilla):
    """Revisión de F-024 (N1, N2): el generador del canal de cada emisor no repite el de la
    agente con el mismo id (agente.py), ni el del mundo (config.py), ni el de otro emisor."""
    import random

    canal = CanalMemoria(semilla=semilla)
    primeros = lambda rng: [rng.random() for _ in range(8)]
    del_canal = {src: primeros(canal._rng_de(src)) for src in (ID_MADRE, *range(1, 8), 255)}
    for src in range(1, 8):
        assert del_canal[src] != primeros(random.Random(semilla * 256 + src))  # la agente src
    assert del_canal[ID_MADRE] != primeros(random.Random(semilla))  # el mundo
    assert len({tuple(v) for v in del_canal.values()}) == len(del_canal)  # emisores distintos
    assert primeros(CanalMemoria(semilla=semilla)._rng_de(1)) == del_canal[1]  # reproducible


def test_perdida_total_salvo_los_garantizados():
    canal = canal_con_agentes(p_perdida=1.0)
    canal.enviar(baliza(1))  # se pierde
    canal.enviar(estado(1))  # se pierde
    canal.enviar(estado(2, flags=FLAG_ACK))  # garantizado
    canal.registrar(ID_MUNDO)
    canal.enviar(crear("ACCION", src=3, dst=ID_MUNDO, accion=1, dir=0, deposito=1))  # familia 0
    assert [m["src"] for m in canal.recibir(ID_MADRE)] == [2]
    assert len(canal.recibir(ID_MUNDO)) == 1
    assert canal.trafico[1].perdidos == 2 and canal.trafico[1].entregados == 0
    assert canal.trafico[2].perdidos == 1 and canal.trafico[2].entregados == 1


def test_la_familia_0_no_se_retrasa():
    canal = canal_con_agentes(retardo=(5, 5))
    canal.registrar(ID_MUNDO)
    canal.enviar(crear("ACCION", src=1, dst=ID_MUNDO, accion=0, dir=0, deposito=0))
    assert len(canal.recibir(ID_MUNDO)) == 1


# ---------------------------------------------------------------- criterio 3: cuenta mensajes y bytes


def test_cuenta_mensajes_y_bytes_por_familia():
    canal = canal_con_agentes()
    b, e = baliza(1), estado(1)
    for _ in range(3):
        canal.enviar(b)
    canal.enviar(e)
    assert canal.trafico[1].enviados == 3
    assert canal.trafico[1].bytes == 3 * len(a_binario(b)) == 18
    assert canal.trafico[1].entregados == 6  # 2 vecinos por difusión
    assert canal.trafico[2].enviados == 1 and canal.trafico[2].bytes == 11
    resumen = canal.resumen()
    assert resumen["agente_agente"] == {"enviados": 3, "bytes": 18, "entregados": 6, "perdidos": 0}
    assert set(resumen) == {"mundo_agente", "agente_agente", "agente_madre", "madre_agente"}


def test_formato_json_cuenta_los_bytes_del_json_y_entrega_lo_mismo():
    binario, en_json = canal_con_agentes(), canal_con_agentes(formato="json")
    msg = baliza(1)
    binario.enviar(msg)
    en_json.enviar(msg)
    assert en_json.trafico[1].bytes == len(a_json(msg).encode()) > binario.trafico[1].bytes
    assert en_json.recibir(2) == binario.recibir(2) == [msg]


def test_el_canal_valida_los_mensajes():
    canal = canal_con_agentes()
    with pytest.raises(ValueError):
        canal.enviar({**baliza(1), "fuerza": 999})


def test_respeta_el_contexto_del_protocolo():
    ctx = Contexto(8, 8, 4)
    canal = CanalMemoria(ctx)
    canal.registrar(ID_MADRE)
    msg = crear("DANZA", src=1, dst=ID_MADRE, ruta_id=1, inicio=0, largo=3, movs=[0, 1, 3])
    canal.enviar(msg)
    assert canal.recibir(ID_MADRE) == [msg]
    assert canal.trafico[2].bytes == len(a_binario(msg, ctx))
