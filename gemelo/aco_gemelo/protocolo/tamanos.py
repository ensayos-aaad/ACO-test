"""Tamaño de cada mensaje en binario y en JSON (C2 de ``PLAN-MEJORAS.md``, idea de Gemini).

Usa los codificadores del protocolo con un ejemplo típico de cada mensaje (mundo de 8 × 8, 8
vecinos). Sirve para decidir el transporte (B2) y el formato: un paquete ESP-NOW admite como
máximo 250 bytes.
"""

from __future__ import annotations

from .codec import ID_DIFUSION, ID_MADRE, ID_MUNDO, Contexto, a_binario, a_json, crear

LIMITE_ESP_NOW = 250


def ejemplos(ctx: Contexto = Contexto()) -> dict[str, dict]:
    """Un mensaje típico de cada tipo (valores de un ensayo normal, no los máximos)."""
    vecina = {"clase": 0, "ocupada": 0, "nido": 0, "fero": 7}
    ruta = dict(ruta_id=3, inicio=0x52, largo=14, movs=[1, 5, 2] * 4 + [1, 2])
    n = ctx.n_celdas
    return {
        "PERCEPCION": crear("PERCEPCION", src=ID_MUNDO, dst=4, tick=1234, pos=0x52, ok=1,
                            vecinas=[vecina] * ctx.n_vecinas),
        "ACCION": crear("ACCION", src=4, dst=ID_MUNDO, tick=1234, accion=2, dir=5, deposito=18),
        "BALIZA": crear("BALIZA", src=4, seq=41, pos=0x52, estado=2, rol=1, saltos_meta=6, fuerza=200),
        "ALERTA": crear("ALERTA", src=4, seq=42, celda=0x53, motivo=0, ttl=3),
        "SIGUEME": crear("SIGUEME", src=4, seq=43, ruta_id=3, n=4, movs=[1, 5, 2, 1]),
        "ESTADO": crear("ESTADO", src=4, dst=ID_MADRE, tick=1234, pos=0x52, estado=0, rol=1,
                        experiencia=37, llegadas=2),
        "FRAGMENTO": crear("FRAGMENTO", src=4, dst=ID_MADRE, tick=1234, origen=0x44,
                           conocidas=0xFFF0, obstaculos=0x0120),
        "DANZA": crear("DANZA", src=4, dst=ID_MADRE, tick=1234, **ruta),
        "PIDE_RESCATE": crear("PIDE_RESCATE", src=4, dst=ID_MADRE, tick=1234, experiencia=5, motivo=0),
        "PIDE_RUTA": crear("PIDE_RUTA", src=4, dst=ID_MADRE, tick=1234, ruta_id=3),
        "INICIO": crear("INICIO", src=ID_MADRE, dst=ID_DIFUSION, ancho_m1=7, alto_m1=7, nido=0x52,
                        vecindad=1, modo_com=0, modo_madre=1, verificadora=0, semilla=2026,
                        delta_t=10, K=64),
        "RECLUTA": crear("RECLUTA", src=ID_MADRE, dst=ID_DIFUSION, tick=1234, n=3,
                         rutas=[dict(ruta_id=i, largo=10 + i, peso=80) for i in range(3)]),
        "RUTA": crear("RUTA", src=ID_MADRE, dst=4, tick=1234, **ruta),
        "MAPA": crear("MAPA", src=ID_MADRE, dst=ID_DIFUSION, tick=1234, incluye_fero=0,
                      conocidas=[1] * n, obstaculos=[0, 1] * (n // 2), fero=[]),
        "STOP": crear("STOP", src=ID_MADRE, dst=ID_DIFUSION, tick=1234, objetivo=1, motivo=0, id=0x53),
        "FIN": crear("FIN", src=ID_MADRE, dst=ID_DIFUSION, tick=1234, motivo=0),
    }


def tamanos(ctx: Contexto = Contexto()) -> list[dict]:
    """Tamaño en bytes de cada mensaje en binario y en JSON, y si cabe en un paquete ESP-NOW."""
    filas = []
    for nombre, msg in ejemplos(ctx).items():
        binario = len(a_binario(msg, ctx))
        json_ = len(a_json(msg, ctx).encode("utf-8"))
        filas.append({"mensaje": nombre, "binario": binario, "json": json_,
                      "veces": round(json_ / binario, 1),
                      "json_cabe_en_esp_now": json_ <= LIMITE_ESP_NOW})
    return filas
