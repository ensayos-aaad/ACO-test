"""El mundo: una cuadrícula con obstáculos, un inicio (nido), una meta y feromona por celda.

Convenciones (las mismas de PROTOCOLO.md):

- Una celda es el par ``(x, y)``: ``x`` es la columna y ``y`` la fila, ambas desde 0.
  La fila 0 es la de arriba, así que el norte es ``y - 1``.
- Direcciones: 0 = N, 1 = E, 2 = S, 3 = O, 4 = NE, 5 = SE, 6 = SO, 7 = NO.
- Vecindad de 8 celdas **sin cortar esquinas**: un movimiento diagonal solo es válido
  si las dos celdas ortogonales que toca también están libres (decisiones C2 y C2.1).
- La feromona vive en las celdas del mundo (decisiones E1 y E2).
"""

from __future__ import annotations

from collections import deque
from enum import IntEnum
from typing import Iterable

Celda = tuple[int, int]

#: Desplazamiento (dx, dy) de cada dirección, indexado por su código de protocolo.
DIRECCIONES: tuple[Celda, ...] = (
    (0, -1),  # 0 N
    (1, 0),  # 1 E
    (0, 1),  # 2 S
    (-1, 0),  # 3 O
    (1, -1),  # 4 NE
    (1, 1),  # 5 SE
    (-1, 1),  # 6 SO
    (-1, -1),  # 7 NO
)


class Clase(IntEnum):
    """Clase de una celda tal como viaja en el mensaje PERCEPCION (2 bits)."""

    LIBRE = 0
    OBSTACULO = 1
    META = 2
    FUERA = 3


class Mundo:
    """Cuadrícula de ``ancho`` × ``alto`` con obstáculos, inicio, meta y feromona.

    Args:
        ancho, alto: dimensiones, entre 1 y 16 (límite del tipo ``celda`` del protocolo).
        obstaculos: celdas bloqueadas.
        inicio: celda del nido, de donde parten los agentes.
        meta: celda objetivo.
        tau0: feromona inicial de cada celda libre.
        tau_max: tope de feromona; el depósito se satura en este valor.
    """

    def __init__(
        self,
        ancho: int,
        alto: int,
        obstaculos: Iterable[Celda],
        inicio: Celda,
        meta: Celda,
        tau0: float = 1.0,
        tau_max: float = 255.0,
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
        for nombre, celda in (("inicio", inicio), ("meta", meta)):
            if not self.es_libre(celda):
                raise ValueError(f"La celda de {nombre} {celda} no está libre")
        for celda in self.obstaculos:
            if not self.dentro(celda):
                raise ValueError(f"Obstáculo fuera de la cuadrícula: {celda}")
        self._tau: dict[Celda, float] = {c: tau0 for c in self.celdas_libres()}

    # ------------------------------------------------------------------ geometría

    def dentro(self, celda: Celda) -> bool:
        """Indica si la celda está dentro de la cuadrícula."""
        x, y = celda
        return 0 <= x < self.ancho and 0 <= y < self.alto

    def es_libre(self, celda: Celda) -> bool:
        """Indica si la celda está dentro de la cuadrícula y no es un obstáculo."""
        return self.dentro(celda) and celda not in self.obstaculos

    def clase(self, celda: Celda) -> Clase:
        """Clase de la celda para el mensaje PERCEPCION."""
        if not self.dentro(celda):
            return Clase.FUERA
        if celda in self.obstaculos:
            return Clase.OBSTACULO
        if celda == self.meta:
            return Clase.META
        return Clase.LIBRE

    def celdas_libres(self) -> list[Celda]:
        """Todas las celdas libres, en orden fijo (por filas), para que sea reproducible."""
        return [
            (x, y)
            for y in range(self.alto)
            for x in range(self.ancho)
            if (x, y) not in self.obstaculos
        ]

    def mover(self, celda: Celda, direccion: int) -> Celda | None:
        """Celda a la que se llega desde ``celda`` en ``direccion``, o ``None`` si no se puede.

        Un movimiento diagonal exige que las dos celdas ortogonales estén libres
        (no se cortan esquinas).
        """
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
        """Movimientos válidos desde ``celda``: lista de ``(direccion, destino)``."""
        salida = []
        for direccion in range(len(DIRECCIONES)):
            destino = self.mover(celda, direccion)
            if destino is not None:
                salida.append((direccion, destino))
        return salida

    def bfs(self, origen: Celda | None = None, destino: Celda | None = None) -> list[Celda] | None:
        """Ruta más corta (en número de movimientos) de ``origen`` a ``destino``.

        Por defecto va del inicio a la meta. Devuelve la lista de celdas, incluidos los
        extremos, o ``None`` si el destino no es alcanzable. Es el óptimo contra el que
        se mide la calidad de la ruta de la colonia.
        """
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
                    ruta.append(previo[ruta[-1]])  # type: ignore[arg-type]
                return ruta[::-1]
            for _, vecino in self.vecinos(actual):
                if vecino not in previo:
                    previo[vecino] = actual
                    cola.append(vecino)
        return None

    def largo_optimo(self) -> int | None:
        """Número de movimientos de la ruta óptima del inicio a la meta."""
        ruta = self.bfs()
        return None if ruta is None else len(ruta) - 1

    # ------------------------------------------------------------------ feromona

    def feromona(self, celda: Celda) -> float:
        """Feromona de la celda (0 si es obstáculo o está fuera)."""
        return self._tau.get(celda, 0.0)

    def depositar(self, celda: Celda, cantidad: float) -> None:
        """Suma feromona a una celda libre, saturando en ``tau_max``."""
        if cantidad < 0:
            raise ValueError("El depósito no puede ser negativo")
        if celda not in self._tau:
            raise ValueError(f"No se puede depositar en {celda}: no es una celda libre")
        self._tau[celda] = min(self.tau_max, self._tau[celda] + cantidad)

    def evaporar(self, rho: float) -> None:
        """Evapora la feromona de todas las celdas: ``tau ← (1 − rho) · tau``."""
        if not 0 <= rho <= 1:
            raise ValueError("rho debe estar entre 0 y 1")
        if rho:
            for celda in self._tau:
                self._tau[celda] *= 1 - rho

    def feromona_q4(self, celda: Celda) -> int:
        """Feromona cuantizada a 16 niveles (0–15), como la percibe un agente (decisión E3)."""
        return round(15 * self.feromona(celda) / self.tau_max) if self.tau_max else 0

    # ------------------------------------------------------------------ texto

    def __str__(self) -> str:
        """Dibujo en texto: ``#`` obstáculo, ``I`` inicio, ``F`` meta, ``.`` libre."""
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
