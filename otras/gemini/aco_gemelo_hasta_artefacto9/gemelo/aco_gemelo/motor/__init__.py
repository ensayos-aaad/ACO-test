"""El motor: ejecución determinista y multihilo del gemelo ACO."""

from .motor import (
    ConfigMotor,
    MotivoFin,
    MotorDeterminista,
    MotorHilos,
    ResultadoEnsayo,
    simular,
)

__all__ = [
    "ConfigMotor",
    "MotivoFin",
    "MotorDeterminista",
    "MotorHilos",
    "ResultadoEnsayo",
    "simular",
]
