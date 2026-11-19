"""Pruebas del artefacto 3: codificadores JSON ↔ binario del protocolo."""
import json
import random

import pytest

from aco_gemelo.protocolo import (
    FLAG_RESCATE,
    MENSAJES,
    Contexto,
    a_binario,
    a_json,
    byte_a_celda,
    celda_a_byte,
    crear,
    de_binario,
    de_json,
    nombre_de,
)
from aco_gemelo.protocolo.codec import Pad, Rep, Res, U, _bits, _cuenta

CONTEXTOS = [Contexto(8, 8, 8), Contexto(8, 8, 4), Contexto(16, 16, 8), Contexto(5, 3, 4)]


def _campos_al_azar(campos, ctx, rng, raiz):
    msg = raiz if raiz is not None else {}
    for campo in campos:
        if isinstance(campo, U):
            msg[campo.nombre] = rng.randrange(1 << campo.bits)
        elif isinstance(campo, Rep):
            lista = []
            for _ in range(_cuenta(campo, ctx, msg if raiz is not None else {})):
                if campo.campos:
                    elemento = {}
                    for sub in campo.campos:
                        if isinstance(sub, U):
                            elemento[sub.nombre] = rng.randrange(1 << sub.bits)
                    lista.append(elemento)
                else:
                    lista.append(rng.randrange(1 << _bits(campo, ctx)))
            msg[campo.nombre] = lista
    return msg


def mensaje_al_azar(nombre, ctx, rng):
    msg = crear(nombre, src=rng.randrange(256), seq=rng.randrange(256),
                dst=rng.randrange(256), tick=rng.randrange(65536), flags=rng.randrange(256))
    return _campos_al_azar(MENSAJES[nombre].campos, ctx, rng, msg)


@pytest.mark.parametrize("ctx", CONTEXTOS)
@pytest.mark.parametrize("nombre", sorted(MENSAJES))
def test_ida_y_vuelta_binario_y_json(nombre, ctx):
    rng = random.Random(f"{nombre}-{ctx}")
    for _ in range(100):
        msg = mensaje_al_azar(nombre, ctx, rng)
        assert de_binario(a_binario(msg, ctx), ctx) == msg
        assert de_json(a_json(msg, ctx), ctx) == msg
        assert nombre_de(msg) == nombre


def test_ack():
    msg = crear("ACK", fam=2, src=0, dst=3, seq=41, tick=1000)
    datos = a_binario(msg)
    assert len(datos) == 7
    assert de_binario(datos) == msg
    assert nombre_de(msg) == "ACK"
    with pytest.raises(ValueError):
        a_binario(crear("ACK", fam=1, src=0))


def _tamano(nombre, ctx, **campos):
    return len(a_binario(crear(nombre, src=1, **campos), ctx))


def _ruta(largo):
    return dict(ruta_id=1, inicio=0, largo=largo, movs=[0] * largo)


@pytest.mark.parametrize("vecindad, percepcion, sigueme, danza14, danza60",
                         [(4, 14, 6, 14, 25), (8, 18, 6, 16, 33)])
def test_tamanos_segun_la_especificacion(vecindad, percepcion, sigueme, danza14, danza60):
    ctx = Contexto(8, 8, vecindad)
    vecina = dict(clase=0, ocupada=0, nido=0, fero=0)
    assert _tamano("PERCEPCION", ctx, pos=0, ok=1, vecinas=[vecina] * (vecindad + 1)) == percepcion
    assert _tamano("ACCION", ctx, accion=1, dir=0, deposito=1) == 9
    assert _tamano("BALIZA", ctx, pos=0, estado=0, rol=0, saltos_meta=15, fuerza=0) == 6
    assert _tamano("ALERTA", ctx, celda=0, motivo=0, ttl=0) == 5
    assert _tamano("SIGUEME", ctx, ruta_id=0, n=4, movs=[0] * 4) == sigueme
    assert _tamano("ESTADO", ctx, pos=0, estado=0, rol=0, experiencia=0, llegadas=0) == 11
    assert _tamano("FRAGMENTO", ctx, origen=0, conocidas=0, obstaculos=0) == 12
    assert _tamano("DANZA", ctx, **_ruta(14)) == danza14
    assert _tamano("RUTA", ctx, **_ruta(60)) == danza60
    assert _tamano("PIDE_RESCATE", ctx, experiencia=0, motivo=0) == 9
    assert _tamano("PIDE_RUTA", ctx, ruta_id=0) == 8
    assert _tamano("INICIO", ctx, ancho_m1=7, alto_m1=7, nido=0, vecindad=1, modo_com=0,
                   modo_madre=0, verificadora=0, semilla=0, delta_t=10, K=8) == 14
    rutas = [dict(ruta_id=i, largo=10, peso=100) for i in range(3)]
    assert _tamano("RECLUTA", ctx, n=3, rutas=rutas) == 17
    assert _tamano("RECLUTA", ctx, n=0, rutas=[]) == 8
    ceros = [0] * 64
    assert _tamano("MAPA", ctx, incluye_fero=0, conocidas=ceros, obstaculos=ceros, fero=[]) == 24
    assert _tamano("MAPA", ctx, incluye_fero=1, conocidas=ceros, obstaculos=ceros, fero=ceros) == 56
    assert _tamano("STOP", ctx, objetivo=0, motivo=0, id=0) == 9
    assert _tamano("FIN", ctx, motivo=0) == 8


def test_todo_cabe_en_un_paquete_esp_now():
    ctx = Contexto(16, 16, 8)
    unos = [1] * 256
    msg = crear("MAPA", src=0, incluye_fero=1, conocidas=unos, obstaculos=unos, fero=[15] * 256)
    assert len(a_binario(msg, ctx)) <= 250


def test_ejemplo_de_la_especificacion():
    msg = crear("BALIZA", src=3, seq=41, pos=celda_a_byte((2, 5)), estado=2, rol=1,
                saltos_meta=6, fuerza=200)
    assert a_binario(msg) == bytes([0x11, 0x03, 0x29, 0x52, 0xA6, 0xC8])
    assert json.loads(a_json(msg)) == {
        "ver": 0, "fam": 1, "tipo": 0, "corta": 1, "src": 3, "seq": 41,
        "pos": 82, "estado": 2, "rol": 1, "saltos_meta": 6, "fuerza": 200,
    }


def test_campo_de_16_bits_va_con_el_byte_alto_primero():
    datos = a_binario(crear("PIDE_RUTA", src=1, dst=0, seq=2, tick=0x1234, flags=FLAG_RESCATE,
                            ruta_id=9))
    assert datos == bytes([0b00_10_100_0, 1, 0, 2, 0x12, 0x34, FLAG_RESCATE, 9])


def test_json_y_binario_llevan_la_misma_informacion():
    rng = random.Random(1)
    for ctx in CONTEXTOS:
        for nombre in MENSAJES:
            msg = mensaje_al_azar(nombre, ctx, rng)
            por_json = de_json(a_json(msg, ctx), ctx)
            por_binario = de_binario(a_binario(msg, ctx), ctx)
            assert por_json == por_binario
            assert a_binario(por_json, ctx) == a_binario(por_binario, ctx)


def test_rechaza_mensajes_invalidos():
    base = crear("BALIZA", src=3, pos=0, estado=0, rol=0, saltos_meta=0, fuerza=0)
    with pytest.raises(ValueError):
        a_binario({**base, "saltos_meta": 16})
    with pytest.raises(ValueError):
        a_binario({**base, "fuerza": -1})
    with pytest.raises(ValueError):
        a_binario({**base, "fuerza": 1.5})
    with pytest.raises(ValueError):
        a_binario({k: v for k, v in base.items() if k != "pos"})
    with pytest.raises(ValueError):
        a_json({**base, "extra": 1})
    with pytest.raises(ValueError):
        a_binario(crear("DANZA", src=1, ruta_id=1, inicio=0, largo=3, movs=[0, 1]))
    with pytest.raises(ValueError):
        a_binario(crear("DANZA", src=1, ruta_id=1, inicio=0, largo=1, movs=[5]), Contexto(8, 8, 4))
    with pytest.raises(ValueError):
        a_binario({**base, "tipo": 5})
    with pytest.raises(ValueError):
        crear("NO_EXISTE", src=1)


def test_rechaza_binario_truncado_o_con_sobrantes():
    datos = a_binario(crear("BALIZA", src=3, pos=0, estado=0, rol=0, saltos_meta=0, fuerza=0))
    with pytest.raises(ValueError):
        de_binario(datos[:-1])
    with pytest.raises(ValueError):
        de_binario(datos + b"\x00")


def test_celda_ida_y_vuelta():
    for x in range(16):
        for y in range(16):
            assert byte_a_celda(celda_a_byte((x, y))) == (x, y)
    assert celda_a_byte((2, 5)) == 0x52
    with pytest.raises(ValueError):
        celda_a_byte((16, 0))
