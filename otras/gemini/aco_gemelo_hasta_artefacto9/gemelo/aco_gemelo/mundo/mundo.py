"""El mundo: una cuadrícula con obstáculos, un inicio (nido), una meta y feromona por celda."""

from __future__ import annotations

from collections import deque
from enum import IntEnum
from typing import Iterable

Celda = tuple[int, int]

DIRECCIONES: tuple[Celda, ...] = (
    (0, -1),  # 0 N
    (1, 0),   # 1 E
    (0, 1),   # 2 S
    (-1, 0),  # 3 O
    (1, -1),  # 4 NE
    (1, 1),   # 5 SE
    (-1, 1),  # 6 SO
    (-1, -1), # 7 NO
)


class Clase(IntEnum):
    LIBRE = 0
    OBSTACULO = 1
    META = 2
    FUERA = 3


class Mundo:
    def __init__(
        self,
        ancho: int,
        alto: int,
        obstaculos: Iterable[Celda],
        inicio: Celda,
        meta: Celda,
        tau0: float = 1.0,
        tau_max: float = 255.0,
        unidad_deposito: float = 1.0,
    ) -> None:
        if not (1 <= ancho <= 16 and 1 <= alto <= 16):
            raise ValueError("El protocolo admite mundos de 1×1 a 16×16")
        if not 0 <= tau0 <= tau_max:
            raise ValueError("Se requiere 0 <= tau0 <= tau_max")
        self.ancho = ancho
        self.alto = alto
        self.obstaculos: frozenset[Celda] = frozenset(obstaculos)
        self.inicio = inicio
        self.meta = meta
        self.tau0 = tau0
        self.tau_max = tau_max
        self.unidad_deposito = unidad_deposito
        for nombre, celda in (("inicio", inicio), ("meta", meta)):
            if not self.es_libre(celda):
                raise ValueError(f"La celda de {nombre} {celda} no está libre")
        for celda in self.obstaculos:
            if not self.dentro(celda):
                raise ValueError(f"Obstáculo fuera de la cuadrícula: {celda}")
        self._tau: dict[Celda, float] = {c: tau0 for c in self.celdas_libres()}

    def dentro(self, celda: Celda) -> bool:
        x, y = celda
        return 0 <= x < self.ancho and 0 <= y < self.alto

    def es_libre(self, celda: Celda) -> bool:
        return self.dentro(celda) and celda not in self.obstaculos

    def clase(self, celda: Celda) -> Clase:
        if not self.dentro(celda):
            return Clase.FUERA
        if celda in self.obstaculos:
            return Clase.OBSTACULO
        if celda == self.meta:
            return Clase.META
        return Clase.LIBRE

    def celdas_libres(self) -> list[Celda]:
        return [
            (x, y)
            for y in range(self.alto)
            for x in range(self.ancho)
            if (x, y) not in self.obstaculos
        ]

    def mover(self, celda: Celda, direccion: int) -> Celda | None:
        dx, dy = DIRECCIONES[direccion]
        x, y = celda
        destino = (x + dx, y + dy)
        if not self.es_libre(destino):
            return None
        if dx != 0 and dy != 0:
            if not (self.es_libre((x + dx, y)) and self.es_libre((x, y + dy))):
                return None
        return destino

    def vecinos(self, celda: Celda) -> list[tuple[int, Celda]]:
        salida = []
        for direccion in range(len(DIRECCIONES)):
            destino = self.mover(celda, direccion)
            if destino is not None:
                salida.append((direccion, destino))
        return salida

    def bfs(self, origen: Celda | None = None, destino: Celda | None = None) -> list[Celda] | None:
        origen = self.inicio if origen is None else origen
        destino = self.meta if destino is None else destino
        if not (self.es_libre(origen) and self.es_libre(destino)):
            return None
        previo: dict[Celda, Celda | None] = {origen: None}
        cola = deque([origen])
        while cola:
            actual = cola.popleft()
            if actual == destino:
                ruta = [actual]
                while previo[ruta[-1]] is not None:
                    ruta.append(previo[ruta[-1]])
                return ruta[::-1]
            for _, vecino in self.vecinos(actual):
                if vecino not in previo:
                    previo[vecino] = actual
                    cola.append(vecino)
        return None

    def largo_optimo(self) -> int | None:
        ruta = self.bfs()
        return None if ruta is None else len(ruta) - 1

    def feromona(self, celda: Celda) -> float:
        return self._tau.get(celda, 0.0)

    def depositar(self, celda: Celda, cantidad: float) -> None:
        if cantidad < 0:
            raise ValueError("El depósito no puede ser negativo")
        if celda not in self._tau:
            raise ValueError(f"No se puede depositar en {celda}: no es una celda libre")
        self._tau[celda] = min(self.tau_max, self._tau[celda] + cantidad)

    def evaporar(self, rho: float) -> None:
        if not 0 <= rho <= 1:
            raise ValueError("rho debe estar entre 0 y 1")
        if rho:
            for celda in self._tau:
                self._tau[celda] *= 1 - rho

    def feromona_q4(self, celda: Celda) -> int:
        return round(15 * self.feromona(celda) / self.tau_max) if self.tau_max else 0

    def percibir(self, celda: Celda, ocupadas: Iterable[Celda] = ()) -> list[dict[str, int]]:
        ocupadas = set(ocupadas)
        x, y = celda
        celdas = [celda] + [(x + dx, y + dy) for dx, dy in DIRECCIONES]
        return [
            {
                "clase": int(self.clase(c)),
                "ocupada": int(c in ocupadas),
                "nido": int(c == self.inicio),
                "fero": self.feromona_q4(c),
            }
            for c in celdas
        ]

    def aplicar_accion(
        self, celda: Celda, accion: int, direccion: int, deposito: int
    ) -> tuple[Celda, bool]:
        if accion in (2, 3) and deposito:
            self.depositar(celda, deposito * self.unidad_deposito)
        if accion in (1, 2):
            destino = self.mover(celda, direccion)
            if destino is None:
                return celda, False
            return destino, True
        return celda, True

    def __str__(self) -> str:
        simbolo = {self.inicio: "I", self.meta: "F"}
        filas = []
        for y in range(self.alto):
            filas.append(
                " ".join(
                    "#" if (x, y) in self.obstaculos else simbolo.get((x, y), ".")
                    for x in range(self.ancho)
                )
            )
        return "\n".join(filas)
