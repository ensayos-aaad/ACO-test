"""Canal de comunicación: la única vía por la que los actores se hablan.

``Canal`` es la interfaz; ``CanalMemoria`` la implementa dentro del mismo proceso, simulando
lo que hará la red real: alcance limitado, retardos y pérdidas. En la fase 2 se agregará una
implementación sobre MQTT con la misma interfaz, sin tocar agentes ni madre.

Reglas de entrega (PROTOCOLO.md):

- **Familia 1** (agente ↔ agente, cabecera corta): difusión a los agentes que estén a
  distancia ≤ ``radio`` del emisor. Puede perderse.
- **Cabecera larga con destino**: va solo a ``dst``; con ``dst = ID_DIFUSION`` va a todos
  los demás.
- **Familia 0** (mundo ↔ agente): es el sensor y el actuador simulados; no se pierde ni
  se retrasa.
- Un mensaje con ``FLAG_ACK`` es de entrega garantizada: no se pierde (el tráfico de las
  confirmaciones no se modela todavía).
"""

from __future__ import annotations

import heapq
import random
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable

from ..protocolo import (
    FLAG_ACK,
    ID_DIFUSION,
    Contexto,
    a_binario,
    a_json,
    byte_a_celda,
    de_binario,
    de_json,
)
from ..protocolo.codec import Mensaje

Celda = tuple[int, int]


@dataclass
class Trafico:
    """Contadores de tráfico de una familia de mensajes."""

    enviados: int = 0  #: transmisiones (una difusión cuenta una vez)
    bytes: int = 0  #: bytes transmitidos
    entregados: int = 0  #: copias que llegaron a un buzón
    perdidos: int = 0  #: copias que se perdieron en el camino


class Canal(ABC):
    """Interfaz de comunicación entre actores."""

    @abstractmethod
    def registrar(self, id_actor: int) -> None:
        """Da de alta a un actor para que pueda recibir mensajes."""

    @abstractmethod
    def enviar(self, msg: Mensaje) -> None:
        """Envía un mensaje; el destino se deduce de su cabecera."""

    @abstractmethod
    def recibir(self, id_actor: int) -> list[Mensaje]:
        """Devuelve, sin bloquear, los mensajes que ya llegaron al actor, y los retira."""


def _distancia(a: Celda, b: Celda) -> int:
    """Distancia en celdas con 8 vecinos (Chebyshev)."""
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


class CanalMemoria(Canal):
    """Canal dentro del proceso, con alcance, retardo y pérdida simulados y reproducibles.

    Args:
        ctx: contexto del protocolo (tamaño del mundo y vecindad).
        posicion: función ``id -> celda`` (o ``None`` si el actor no está en el mundo, como
            la madre). La usa la difusión por radio. Si no se da, la posición del emisor se
            toma del campo ``pos`` o ``celda`` del mensaje y nadie más tiene posición.
        radio: alcance de la familia 1, en celdas.
        p_perdida: probabilidad de que se pierda cada copia no garantizada.
        retardo: ``(mínimo, máximo)`` en ticks, ambos incluidos; se sortea por copia.
        semilla: semilla de las pérdidas y los retardos.
        formato: ``"binario"`` o ``"json"``; define cómo viaja y cuántos bytes se cuentan.
    """

    def __init__(
        self,
        ctx: Contexto = Contexto(),
        posicion: Callable[[int], Celda | None] | None = None,
        radio: int = 1,
        p_perdida: float = 0.0,
        retardo: tuple[int, int] = (0, 0),
        semilla: int = 0,
        formato: str = "binario",
    ) -> None:
        if not 0 <= p_perdida <= 1:
            raise ValueError("p_perdida debe estar entre 0 y 1")
        if not 0 <= retardo[0] <= retardo[1]:
            raise ValueError("Se requiere 0 <= retardo mínimo <= retardo máximo")
        if formato not in ("binario", "json"):
            raise ValueError("El formato es 'binario' o 'json'")
        self.ctx = ctx
        self.posicion = posicion
        self.radio = radio
        self.p_perdida = p_perdida
        self.retardo = retardo
        self.formato = formato
        self.ahora = 0
        self.trafico: dict[int, Trafico] = {fam: Trafico() for fam in range(4)}
        self._rng = random.Random(semilla)
        self._buzones: dict[int, list[tuple[int, int, bytes | str]]] = {}
        self._orden = 0
        self._candado = threading.Lock()

    # ------------------------------------------------------------------ interfaz

    def registrar(self, id_actor: int) -> None:
        with self._candado:
            self._buzones.setdefault(id_actor, [])

    def avanzar(self, ahora: int) -> None:
        """Fija el tick actual; los mensajes con entrega ≤ ``ahora`` quedan disponibles."""
        if ahora < self.ahora:
            raise ValueError("El tiempo no retrocede")
        self.ahora = ahora

    def enviar(self, msg: Mensaje) -> None:
        if self.formato == "binario":
            datos: bytes | str = a_binario(msg, self.ctx)
            tamano = len(datos)
        else:
            datos = a_json(msg, self.ctx)
            tamano = len(datos.encode("utf-8"))
        fam = msg["fam"]
        with self._candado:
            destinos = self._destinos(msg)
            trafico = self.trafico[fam]
            trafico.enviados += 1
            trafico.bytes += tamano
            garantizado = fam == 0 or bool(msg.get("flags", 0) & FLAG_ACK)
            for destino in destinos:
                if not garantizado and self._rng.random() < self.p_perdida:
                    trafico.perdidos += 1
                    continue
                espera = 0 if fam == 0 else self._rng.randint(*self.retardo)
                self._orden += 1
                heapq.heappush(self._buzones[destino], (self.ahora + espera, self._orden, datos))
                trafico.entregados += 1

    def recibir(self, id_actor: int) -> list[Mensaje]:
        with self._candado:
            if id_actor not in self._buzones:
                raise ValueError(f"El actor {id_actor} no está registrado")
            buzon = self._buzones[id_actor]
            listos = []
            while buzon and buzon[0][0] <= self.ahora:
                listos.append(heapq.heappop(buzon)[2])
        decodificar = de_binario if self.formato == "binario" else de_json
        return [decodificar(datos, self.ctx) for datos in listos]  # type: ignore[arg-type]

    # ------------------------------------------------------------------ métricas

    def pendientes(self) -> int:
        """Mensajes que siguen en camino o sin leer."""
        with self._candado:
            return sum(len(b) for b in self._buzones.values())

    def resumen(self) -> dict[str, dict[str, int]]:
        """Tráfico por familia, listo para volcar a un CSV."""
        nombres = {0: "mundo_agente", 1: "agente_agente", 2: "agente_madre", 3: "madre_agente"}
        return {nombres[fam]: vars(t).copy() for fam, t in self.trafico.items()}

    # ------------------------------------------------------------------ interno

    def _destinos(self, msg: Mensaje) -> list[int]:
        src = msg["src"]
        if msg["corta"]:
            origen = self._posicion_emisor(msg)
            if origen is None or self.posicion is None:
                return []
            vecinos = []
            for id_actor in sorted(self._buzones):
                if id_actor == src:
                    continue
                celda = self.posicion(id_actor)
                if celda is not None and _distancia(origen, celda) <= self.radio:
                    vecinos.append(id_actor)
            return vecinos
        dst = msg["dst"]
        if dst == ID_DIFUSION:
            return [id_actor for id_actor in sorted(self._buzones) if id_actor != src]
        if dst not in self._buzones:
            raise ValueError(f"Destino no registrado: {dst}")
        return [dst]

    def _posicion_emisor(self, msg: Mensaje) -> Celda | None:
        if self.posicion is not None:
            celda = self.posicion(msg["src"])
            if celda is not None:
                return celda
        for campo in ("pos", "celda"):
            if campo in msg:
                return byte_a_celda(msg[campo])
        return None
