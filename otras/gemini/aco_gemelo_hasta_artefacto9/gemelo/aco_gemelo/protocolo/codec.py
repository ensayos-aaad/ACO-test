"""Codificadores del protocolo (PROTOCOLO.md v0.2)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable

Mensaje = dict[str, Any]

VERSION = 0

ID_MADRE = 0x00
ID_MUNDO = 0xFE
ID_DIFUSION = 0xFF

FLAG_ACK = 0x01
FLAG_RESCATE = 0x02
FLAG_ULTIMO = 0x04
FLAG_VERIFICACION = 0x08

TIPO_ACK = 7


def celda_a_byte(celda: tuple[int, int]) -> int:
    x, y = celda
    if not (0 <= x <= 15 and 0 <= y <= 15):
        raise ValueError(f"Celda fuera del rango del protocolo: {celda}")
    return (y << 4) | x


def byte_a_celda(valor: int) -> tuple[int, int]:
    return (valor & 0x0F, valor >> 4)


def celdas_a_bloque(origen: tuple[int, int], celdas) -> int:
    ox, oy = origen
    bits = 0
    for dy in range(4):
        for dx in range(4):
            if (ox + dx, oy + dy) in celdas:
                bits |= 1 << (15 - (4 * dy + dx))
    return bits


def bloque_a_celdas(origen: tuple[int, int], bits: int) -> set[tuple[int, int]]:
    ox, oy = origen
    return {
        (ox + dx, oy + dy)
        for dy in range(4)
        for dx in range(4)
        if bits >> (15 - (4 * dy + dx)) & 1
    }


@dataclass(frozen=True)
class Contexto:
    ancho: int = 8
    alto: int = 8
    vecindad: int = 8

    def __post_init__(self) -> None:
        if self.vecindad not in (4, 8):
            raise ValueError("La vecindad es 4 u 8")

    @property
    def bits_mov(self) -> int:
        return 2 if self.vecindad == 4 else 3

    @property
    def n_vecinas(self) -> int:
        return self.vecindad + 1

    @property
    def n_celdas(self) -> int:
        return self.ancho * self.alto


@dataclass(frozen=True)
class U:
    nombre: str
    bits: int


@dataclass(frozen=True)
class Res:
    bits: int


@dataclass(frozen=True)
class Pad:
    pass


@dataclass(frozen=True)
class Rep:
    nombre: str
    cuenta: int | str | Callable[[Contexto, Mensaje], int]
    bits: int | Callable[[Contexto], int] | None = None
    campos: tuple = ()


@dataclass(frozen=True)
class Definicion:
    nombre: str
    fam: int
    tipo: int
    corta: bool
    campos: tuple


_RUTA = (
    U("ruta_id", 8),
    U("inicio", 8),
    U("largo", 8),
    Rep("movs", "largo", bits=lambda ctx: ctx.bits_mov),
    Pad(),
)

_DEFINICIONES = (
    Definicion(
        "PERCEPCION", 0, 0, False,
        (
            U("pos", 8), U("ok", 1), Res(7),
            Rep(
                "vecinas", lambda ctx, m: ctx.n_vecinas,
                campos=(U("clase", 2), U("ocupada", 1), U("nido", 1), U("fero", 4)),
            ),
        ),
    ),
    Definicion("ACCION", 0, 1, False, (U("accion", 2), U("dir", 3), Res(3), U("deposito", 8))),
    Definicion(
        "BALIZA", 1, 0, True,
        (U("pos", 8), U("estado", 2), U("rol", 1), Res(1), U("saltos_meta", 4), U("fuerza", 8)),
    ),
    Definicion("ALERTA", 1, 1, True, (U("celda", 8), U("motivo", 2), U("ttl", 3), Res(3))),
    Definicion(
        "SIGUEME", 1, 2, True,
        (U("ruta_id", 8), U("n", 3), Rep("movs", "n", bits=lambda ctx: ctx.bits_mov), Pad()),
    ),
    Definicion(
        "ESTADO", 2, 0, False,
        (U("pos", 8), U("estado", 2), U("rol", 1), Res(5), U("experiencia", 8), U("llegadas", 8)),
    ),
    Definicion("FRAGMENTO", 2, 1, False, (U("origen", 8), U("conocidas", 16), U("obstaculos", 16))),
    Definicion("DANZA", 2, 2, False, _RUTA),
    Definicion("PIDE_RESCATE", 2, 3, False, (U("experiencia", 8), U("motivo", 2), Res(6))),
    Definicion("PIDE_RUTA", 2, 4, False, (U("ruta_id", 8),)),
    Definicion(
        "INICIO", 3, 0, False,
        (
            U("ancho_m1", 4), U("alto_m1", 4), U("nido", 8),
            U("vecindad", 1), U("modo_com", 1), U("modo_madre", 2), U("verificadora", 1), Res(3),
            U("semilla", 16), U("delta_t", 8), U("K", 8),
        ),
    ),
    Definicion(
        "RECLUTA", 3, 1, False,
        (
            U("n", 2), Res(6),
            Rep("rutas", "n", campos=(U("ruta_id", 8), U("largo", 8), U("peso", 8))),
        ),
    ),
    Definicion("RUTA", 3, 2, False, _RUTA),
    Definicion(
        "MAPA", 3, 3, False,
        (
            U("incluye_fero", 1), Res(7),
            Rep("conocidas", lambda ctx, m: ctx.n_celdas, bits=1), Pad(),
            Rep("obstaculos", lambda ctx, m: ctx.n_celdas, bits=1), Pad(),
            Rep("fero", lambda ctx, m: ctx.n_celdas if m["incluye_fero"] else 0, bits=4), Pad(),
        ),
    ),
    Definicion("STOP", 3, 4, False, (U("objetivo", 1), U("motivo", 2), Res(5), U("id", 8))),
    Definicion("FIN", 3, 5, False, (U("motivo", 2), Res(6))),
)

MENSAJES: dict[str, Definicion] = {d.nombre: d for d in _DEFINICIONES}
_POR_CODIGO: dict[tuple[int, int], Definicion] = {(d.fam, d.tipo): d for d in _DEFINICIONES}

_CABECERA_CORTA = (U("src", 8), U("seq", 8))
_CABECERA_LARGA = (U("src", 8), U("dst", 8), U("seq", 8), U("tick", 16), U("flags", 8))


class _Escritor:
    def __init__(self) -> None:
        self.valor = 0
        self.n = 0

    def u(self, valor: int, bits: int) -> None:
        self.valor = (self.valor << bits) | valor
        self.n += bits

    def pad(self) -> None:
        self.u(0, -self.n % 8)

    def bytes(self) -> bytes:
        self.pad()
        return self.valor.to_bytes(self.n // 8, "big")


class _Lector:
    def __init__(self, datos: bytes) -> None:
        self.valor = int.from_bytes(datos, "big")
        self.n = len(datos) * 8
        self.pos = 0

    def u(self, bits: int) -> int:
        if self.pos + bits > self.n:
            raise ValueError("Mensaje truncado")
        valor = (self.valor >> (self.n - self.pos - bits)) & ((1 << bits) - 1)
        self.pos += bits
        return valor

    def pad(self) -> None:
        self.pos += -self.pos % 8


def _cuenta(rep: Rep, ctx: Contexto, msg: Mensaje) -> int:
    if isinstance(rep.cuenta, int):
        return rep.cuenta
    if isinstance(rep.cuenta, str):
        return msg[rep.cuenta]
    return rep.cuenta(ctx, msg)


def _bits(rep: Rep, ctx: Contexto) -> int:
    return rep.bits if isinstance(rep.bits, int) else rep.bits(ctx)


def _entero(valor: Any, bits: int, nombre: str) -> int:
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ValueError(f"El campo '{nombre}' debe ser un entero, no {valor!r}")
    if not 0 <= valor < (1 << bits):
        raise ValueError(f"El campo '{nombre}' = {valor} no cabe en {bits} bits")
    return valor


def _escribir(campos: tuple, msg: Mensaje, ctx: Contexto, w: _Escritor, raiz: Mensaje) -> set[str]:
    usados = set()
    for campo in campos:
        if isinstance(campo, Res):
            w.u(0, campo.bits)
        elif isinstance(campo, Pad):
            w.pad()
        elif isinstance(campo, U):
            if campo.nombre not in msg:
                raise ValueError(f"Falta el campo '{campo.nombre}'")
            w.u(_entero(msg[campo.nombre], campo.bits, campo.nombre), campo.bits)
            usados.add(campo.nombre)
        else:
            if campo.nombre not in msg:
                raise ValueError(f"Falta el campo '{campo.nombre}'")
            lista = msg[campo.nombre]
            esperados = _cuenta(campo, ctx, raiz)
            if not isinstance(lista, list) or len(lista) != esperados:
                raise ValueError(f"'{campo.nombre}' debe ser una lista de {esperados} elementos")
            for elemento in lista:
                if campo.campos:
                    if not isinstance(elemento, dict):
                        raise ValueError(f"Los elementos de '{campo.nombre}' deben ser objetos")
                    sobran = set(elemento) - _escribir(campo.campos, elemento, ctx, w, raiz)
                    if sobran:
                        raise ValueError(f"Campos desconocidos en '{campo.nombre}': {sorted(sobran)}")
                else:
                    bits = _bits(campo, ctx)
                    w.u(_entero(elemento, bits, campo.nombre), bits)
            usados.add(campo.nombre)
    return usados


def _leer(campos: tuple, ctx: Contexto, r: _Lector, msg: Mensaje, raiz: Mensaje) -> None:
    for campo in campos:
        if isinstance(campo, Res):
            r.u(campo.bits)
        elif isinstance(campo, Pad):
            r.pad()
        elif isinstance(campo, U):
            msg[campo.nombre] = r.u(campo.bits)
        else:
            lista = []
            for _ in range(_cuenta(campo, ctx, raiz)):
                if campo.campos:
                    elemento: Mensaje = {}
                    _leer(campo.campos, ctx, r, elemento, raiz)
                    lista.append(elemento)
                else:
                    lista.append(r.u(_bits(campo, ctx)))
            msg[campo.nombre] = lista


def _definicion(fam: int, tipo: int, corta: int) -> tuple[Definicion | None, tuple]:
    if tipo == TIPO_ACK and fam != 1:
        if corta:
            raise ValueError("Un ACK lleva cabecera larga")
        return None, _CABECERA_LARGA
    definicion = _POR_CODIGO.get((fam, tipo))
    if definicion is None:
        raise ValueError(f"Tipo de mensaje desconocido: familia {fam}, tipo {tipo}")
    if bool(corta) != definicion.corta:
        raise ValueError(f"{definicion.nombre}: el bit 'corta' no corresponde")
    return definicion, _CABECERA_CORTA if definicion.corta else _CABECERA_LARGA


def nombre_de(msg: Mensaje) -> str:
    definicion, _ = _definicion(msg["fam"], msg["tipo"], msg["corta"])
    return "ACK" if definicion is None else definicion.nombre


def crear(nombre: str, *, src: int, seq: int = 0, dst: int = ID_DIFUSION, tick: int = 0,
          flags: int = 0, fam: int | None = None, **campos: Any) -> Mensaje:
    if nombre == "ACK":
        if fam is None:
            raise ValueError("Un ACK necesita la familia (fam)")
        msg: Mensaje = {"ver": VERSION, "fam": fam, "tipo": TIPO_ACK, "corta": 0}
        corta = False
    else:
        if nombre not in MENSAJES:
            raise ValueError(f"Mensaje desconocido: {nombre}")
        definicion = MENSAJES[nombre]
        corta = definicion.corta
        msg = {"ver": VERSION, "fam": definicion.fam, "tipo": definicion.tipo, "corta": int(corta)}
    msg["src"] = src
    if not corta:
        msg["dst"] = dst
    msg["seq"] = seq
    if not corta:
        msg["tick"] = tick
        msg["flags"] = flags
    msg.update(campos)
    return msg


def a_binario(msg: Mensaje, ctx: Contexto = Contexto()) -> bytes:
    for clave in ("ver", "fam", "tipo", "corta"):
        if clave not in msg:
            raise ValueError(f"Falta el campo '{clave}'")
    w = _Escritor()
    w.u(_entero(msg["ver"], 2, "ver"), 2)
    w.u(_entero(msg["fam"], 2, "fam"), 2)
    w.u(_entero(msg["tipo"], 3, "tipo"), 3)
    w.u(_entero(msg["corta"], 1, "corta"), 1)
    definicion, cabecera = _definicion(msg["fam"], msg["tipo"], msg["corta"])
    usados = {"ver", "fam", "tipo", "corta"} | _escribir(cabecera, msg, ctx, w, msg)
    if definicion is not None:
        usados |= _escribir(definicion.campos, msg, ctx, w, msg)
    sobran = set(msg) - usados
    if sobran:
        raise ValueError(f"Campos desconocidos: {sorted(sobran)}")
    return w.bytes()


def de_binario(datos: bytes, ctx: Contexto = Contexto()) -> Mensaje:
    r = _Lector(datos)
    msg: Mensaje = {"ver": r.u(2), "fam": r.u(2), "tipo": r.u(3), "corta": r.u(1)}
    definicion, cabecera = _definicion(msg["fam"], msg["tipo"], msg["corta"])
    _leer(cabecera, ctx, r, msg, msg)
    if definicion is not None:
        _leer(definicion.campos, ctx, r, msg, msg)
    r.pad()
    if r.pos != r.n:
        raise ValueError(f"Sobran {(r.n - r.pos) // 8} bytes al final del mensaje")
    return msg


def a_json(msg: Mensaje, ctx: Contexto = Contexto()) -> str:
    a_binario(msg, ctx)
    return json.dumps(msg, separators=(",", ":"))


def de_json(texto: str, ctx: Contexto = Contexto()) -> Mensaje:
    msg = json.loads(texto)
    if not isinstance(msg, dict):
        raise ValueError("El JSON de un mensaje debe ser un objeto")
    a_binario(msg, ctx)
    return msg
