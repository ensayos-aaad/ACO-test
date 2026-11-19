"""La madre: el control central en el edge (a futuro, una Raspberry Pi)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from math import ceil
from typing import Any

from ..canal import Canal
from ..protocolo import (
    FLAG_ACK,
    FLAG_RESCATE,
    FLAG_VERIFICACION,
    ID_DIFUSION,
    ID_MADRE,
    Contexto,
    bloque_a_celdas,
    byte_a_celda,
    crear,
    nombre_de,
)

Celda = tuple[int, int]


class Modo(IntEnum):
    AUSENTE = 0
    PISTA_DE_BAILE = 1
    RESCATE = 2
    DIFUSION = 3


@dataclass
class ConfigMadre:
    modo: Modo = Modo.PISTA_DE_BAILE
    delta_t: int = 10
    memoria: int = 64
    umbral_rescate: float = 0.5
    rutas_por_anuncio: int = 3


class Madre:
    def __init__(self, canal: Canal, config: ConfigMadre | None = None,
                 ctx: Contexto = Contexto()) -> None:
        self.canal = canal
        self.config = config or ConfigMadre()
        self.ctx = ctx
        self.agentes: dict[int, dict[str, int]] = {}
        self.rutas: list[dict[str, Any]] = []
        self.conocidas: set[Celda] = set()
        self.obstaculos: set[Celda] = set()
        self.rescatadas: set[int] = set()
        self.pedidos: dict[int, int] = {}
        self.descartadas = 0
        self.verificacion: str | None = None
        self.largo_verificado: int | None = None
        self.actuaciones: list[int] = []
        self._ultima: int | None = None
        self._seq = 0
        self._id_ruta = 0
        canal.registrar(ID_MADRE)

    @property
    def guarda_mapa(self) -> bool:
        return self.config.modo in (Modo.RESCATE, Modo.DIFUSION)

    def memoria_usada(self) -> int:
        n = len(self.agentes)
        total = 3 * n + ceil(n / 8) + 2 * len(self.pedidos)
        total += sum(3 + ceil(self.ctx.bits_mov * len(r["movs"]) / 8) for r in self.rutas)
        if self.guarda_mapa:
            total += 2 * ceil(self.ctx.n_celdas / 8)
        return total

    def _ajustar_memoria(self) -> None:
        while self.memoria_usada() > self.config.memoria and self.rutas:
            self.rutas.pop()
            self.descartadas += 1
        while self.memoria_usada() > self.config.memoria and self.pedidos:
            self.pedidos.popitem()

    @property
    def mejor_ruta(self) -> dict[str, Any] | None:
        return self.rutas[0] if self.rutas else None

    def paso(self, ahora: int) -> None:
        mensajes = self.canal.recibir(ID_MADRE)
        if self.config.modo is Modo.AUSENTE:
            return
        for msg in mensajes:
            self._escuchar(msg)
        self._ajustar_memoria()
        if self._ultima is not None and ahora - self._ultima < self.config.delta_t:
            return
        self._ultima = ahora
        self.actuaciones.append(ahora)
        if self.config.modo is Modo.PISTA_DE_BAILE:
            self._pista_de_baile(ahora)
        elif self.config.modo is Modo.RESCATE:
            self._rescatar(ahora)
        else:
            self._difundir(ahora)

    def _escuchar(self, msg: dict[str, Any]) -> None:
        nombre, src = nombre_de(msg), msg["src"]
        verificadora = bool(msg["flags"] & FLAG_VERIFICACION)
        if nombre == "ESTADO":
            self.agentes[src] = {"pos": msg["pos"], "experiencia": msg["experiencia"],
                                 "llegadas": msg["llegadas"]}
        elif nombre == "DANZA":
            if verificadora:
                self.verificacion, self.largo_verificado = "ok", msg["largo"]
            else:
                self._recordar_ruta(msg)
        elif nombre == "FRAGMENTO" and self.guarda_mapa:
            origen = byte_a_celda(msg["origen"])
            self.conocidas |= bloque_a_celdas(origen, msg["conocidas"])
            self.obstaculos |= bloque_a_celdas(origen, msg["obstaculos"])
        elif nombre == "PIDE_RUTA" and self.config.modo is Modo.PISTA_DE_BAILE:
            self.pedidos[src] = msg["ruta_id"]
        elif nombre == "PIDE_RESCATE" and verificadora:
            self.verificacion = "fallo"

    def _recordar_ruta(self, danza: dict[str, Any]) -> None:
        if any(r["inicio"] == danza["inicio"] and r["movs"] == danza["movs"] for r in self.rutas):
            return
        self.rutas.append({"id": self._id_ruta, "inicio": danza["inicio"], "movs": danza["movs"]})
        self._id_ruta = (self._id_ruta + 1) % 256
        self.rutas.sort(key=lambda r: (len(r["movs"]), r["id"]))

    def _pista_de_baile(self, ahora: int) -> None:
        anunciadas = self.rutas[: min(3, self.config.rutas_por_anuncio)]
        if anunciadas:
            total = sum(1 / len(r["movs"]) for r in anunciadas)
            self._enviar("RECLUTA", ID_DIFUSION, ahora, n=len(anunciadas), rutas=[
                {"ruta_id": r["id"], "largo": len(r["movs"]),
                 "peso": max(1, round(255 * (1 / len(r["movs"])) / total))}
                for r in anunciadas])
        for agente, ruta_id in sorted(self.pedidos.items()):
            ruta = next((r for r in self.rutas if r["id"] == ruta_id), self.mejor_ruta)
            if ruta is not None:
                self._enviar_ruta(ruta, agente, ahora, FLAG_ACK)
        self.pedidos.clear()

    def rezagadas(self) -> list[int]:
        if not self.agentes:
            return []
        promedio = sum(a["experiencia"] for a in self.agentes.values()) / len(self.agentes)
        return sorted(
            i for i, a in self.agentes.items()
            if a["llegadas"] == 0 and i not in self.rescatadas
            and a["experiencia"] < self.config.umbral_rescate * promedio
        )

    def _rescatar(self, ahora: int) -> None:
        if self.mejor_ruta is None:
            return
        for agente in self.rezagadas():
            self._enviar_ruta(self.mejor_ruta, agente, ahora, FLAG_ACK | FLAG_RESCATE)
            self.rescatadas.add(agente)
        self._ajustar_memoria()

    def _difundir(self, ahora: int) -> None:
        celdas = [(x, y) for y in range(self.ctx.alto) for x in range(self.ctx.ancho)]
        self._enviar("MAPA", ID_DIFUSION, ahora, incluye_fero=0,
                     conocidas=[int(c in self.conocidas) for c in celdas],
                     obstaculos=[int(c in self.obstaculos) for c in celdas], fero=[])
        if self.mejor_ruta is not None:
            self._enviar_ruta(self.mejor_ruta, ID_DIFUSION, ahora, 0)

    def _enviar_ruta(self, ruta: dict[str, Any], dst: int, ahora: int, flags: int) -> None:
        self._enviar("RUTA", dst, ahora, flags=flags, ruta_id=ruta["id"], inicio=ruta["inicio"],
                     largo=len(ruta["movs"]), movs=ruta["movs"])

    def _enviar(self, nombre: str, dst: int, ahora: int, flags: int = 0, **campos: Any) -> None:
        self.canal.enviar(crear(nombre, src=ID_MADRE, dst=dst, seq=self._seq, tick=ahora % 65536,
                                flags=flags, **campos))
        self._seq = (self._seq + 1) % 256
