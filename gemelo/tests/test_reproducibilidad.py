"""Reproducibilidad más allá de un proceso (observaciones leves de F-026, ronda 001 de QA).

1. El mismo ensayo da exactamente el mismo resultado en procesos distintos, con PYTHONHASHSEED distinto. Dentro
   de un proceso la suite ya lo comprueba; esto atrapa un generador sembrado con algo que dependa del proceso, como
   ``hash()`` de un texto (mutante ``docs/informes/revision_F025/mut_hash.py``, que pasaba las 127 pruebas de canal,
   motor, línea de comandos y experimentos).
2. Las semillas negativas se rechazan: Python siembra con el valor absoluto (``Random(-3)`` da lo mismo que
   ``Random(3)``), así que una semilla negativa repetiría el mundo de la positiva (las decisiones de las agentes no;
   F-030).
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

from aco_gemelo.config import config_ensayo, crear_mundo
from aco_gemelo.motor import ConfigEnsayo

GEMELO = Path(__file__).resolve().parents[1]

# Ensayo con todo lo que usa azar: mundo aleatorio, madre en difusión, pérdidas y retardo en el canal.
# Imprime una huella del resultado completo: el repr de la dataclass con registrar=True, que incluye el
# historial de posiciones, la serie, la feromona y el mapa de la madre tick a tick (H4, ronda 001 de QA).
GUION = """
import hashlib, sys
from dataclasses import replace
for modulo in sys.argv[1:]:
    __import__(modulo)  # para comprobar a mano con un mutante (ver la docstring de la prueba)
from aco_gemelo.config import config_ensayo, crear_mundo
from aco_gemelo.motor import Simulacion
datos = {"semilla": 7, "mundo": {"escenario": "aleatorio"}, "madre": {"modo": "difusion"},
         "canal": {"p_perdida": 0.3, "retardo": [0, 3]}, "ensayo": {"limite": 1500}}
r = Simulacion(crear_mundo(datos), replace(config_ensayo(datos), registrar=True)).correr()
print(r.motivo, r.ticks_total, hashlib.sha256(repr(r).encode()).hexdigest())
"""


def _huella(hashseed: str, *modulos: str) -> str:
    entorno = {**os.environ, "PYTHONHASHSEED": hashseed}
    salida = subprocess.run([sys.executable, "-B", "-X", "utf8", "-c", GUION, *modulos], cwd=GEMELO,
                            env=entorno, capture_output=True, text=True, timeout=300, check=True)
    return salida.stdout.strip()


def test_mismo_ensayo_en_procesos_con_pythonhashseed_distinto():
    """Para comprobar que la prueba detecta el defecto, desde ``gemelo/``:
    ``PYTHONPATH=docs/informes/revision_F025 python -X utf8 -c "<GUION>" mut_hash`` con dos PYTHONHASHSEED
    distintos debe dar huellas distintas.
    """
    huellas = {semilla: _huella(semilla) for semilla in ("0", "1", "12345")}
    assert len(set(huellas.values())) == 1, huellas
    motivo, ticks, _ = huellas["0"].split()
    assert int(ticks) > 0 and motivo in ("verificada", "verificadora_fallo", "limite", "abortado")


@pytest.mark.parametrize("semilla", [-1, -3, -2026])
def test_las_semillas_negativas_se_rechazan(semilla):
    with pytest.raises(ValueError, match="mayor o igual que 0"):
        crear_mundo({"mundo": {"escenario": "aleatorio"}}, semilla=semilla)
    with pytest.raises(ValueError, match="mayor o igual que 0"):
        config_ensayo({}, semilla=semilla)
    with pytest.raises(ValueError, match="mayor o igual que 0"):
        ConfigEnsayo(semilla=semilla)


@pytest.mark.parametrize("semilla", [1.5, "3", True])
def test_la_semilla_debe_ser_un_entero(semilla):
    with pytest.raises(ValueError):
        ConfigEnsayo(semilla=semilla)
    with pytest.raises(ValueError):
        crear_mundo({}, semilla=semilla)


def test_la_semilla_cero_y_las_positivas_siguen_valiendo():
    assert ConfigEnsayo(semilla=0).semilla == 0
    assert crear_mundo({}, semilla=0) is not None
    assert config_ensayo({"semilla": 2026}).semilla == 2026
