"""El mundo y sus escenarios."""

from .escenarios import OBSTACULOS_L, PuenteDoble, mundo_aleatorio, mundo_l, puente_doble
from .mundo import DIRECCIONES, Celda, Clase, Mundo

__all__ = [
    "DIRECCIONES",
    "OBSTACULOS_L",
    "Celda",
    "Clase",
    "Mundo",
    "PuenteDoble",
    "mundo_aleatorio",
    "mundo_l",
    "puente_doble",
]
