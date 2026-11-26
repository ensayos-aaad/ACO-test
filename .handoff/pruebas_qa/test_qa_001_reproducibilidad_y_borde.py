"""Pruebas de QA (ronda 001): casos borde de semillas y reproducibilidad entre procesos y motores.

Cubre los grupos 1, 2 y 3 de `.handoff/rondas/001-para_qa.md` que pasan sobre el código actual.
"""

from __future__ import annotations

import dataclasses
import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

from aco_gemelo.config import config_ensayo, crear_mundo
from aco_gemelo.motor import ConfigEnsayo, Simulacion

GEMELO = Path(__file__).resolve().parents[2] / "gemelo"

_GUION_HUELLA = """
import hashlib, sys
from dataclasses import replace
from aco_gemelo.config import config_ensayo, crear_mundo
from aco_gemelo.motor import Simulacion

motor = sys.argv[1]
semilla = int(sys.argv[2])
datos = {
    "semilla": semilla,
    "mundo": {"escenario": "aleatorio"},
    "madre": {"modo": "difusion"},
    "canal": {"p_perdida": 0.3, "retardo": [0, 3]},
    "ensayo": {"limite": 1500},
}
r = Simulacion(crear_mundo(datos), replace(config_ensayo(datos), registrar=True)).correr(motor)
print(r.motivo, r.ticks_total, hashlib.sha256(repr(r).encode()).hexdigest())
"""


def _ejecutar_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", "-X", "utf8", "-m", "aco_gemelo", *args],
        cwd=GEMELO,
        capture_output=True,
        text=True,
        timeout=120,
    )


def _huella_proceso(motor: str, semilla: int, hashseed: str) -> str:
    entorno = {**os.environ, "PYTHONHASHSEED": hashseed}
    proc = subprocess.run(
        [sys.executable, "-B", "-X", "utf8", "-c", _GUION_HUELLA, motor, str(semilla)],
        cwd=GEMELO,
        env=entorno,
        capture_output=True,
        text=True,
        timeout=180,
        check=True,
    )
    return proc.stdout.strip()


@pytest.mark.parametrize("semilla", [-1, -3, 1.5, 3.0, "3", True, False, None])
def test_qa_001_replace_rechaza_semillas_invalidas(semilla):
    with pytest.raises(ValueError, match="mayor o igual que 0"):
        dataclasses.replace(ConfigEnsayo(), semilla=semilla)


@pytest.mark.parametrize(
    "datos",
    [
        {"mundo": {"escenario": "L"}},
        {"mundo": {"escenario": "aleatorio"}},
        {"mundo": {"escenario": "puente_doble"}},
        {
            "mundo": {
                "escenario": "personalizado",
                "ancho": 4,
                "alto": 4,
                "inicio": [0, 0],
                "meta": [3, 3],
                "obstaculos": [],
            }
        },
    ],
)
@pytest.mark.parametrize("semilla", [-3, 1.5, 3.0, "3", True, False])
def test_qa_001_crear_mundo_rechaza_semilla_invalida_en_todos_los_escenarios(datos, semilla):
    with pytest.raises(ValueError, match="mayor o igual que 0"):
        crear_mundo(datos, semilla=semilla)


def test_qa_001_crear_mundo_rechaza_semilla_null_en_datos():
    with pytest.raises(ValueError, match="mayor o igual que 0"):
        crear_mundo({"semilla": None, "mundo": {"escenario": "L"}})


@pytest.mark.parametrize("valor_yaml", ["-3", "1.5", "3.0", '"3"', "true", "false", "null"])
def test_qa_001_yaml_semilla_invalida_rechazada_por_cli(tmp_path, valor_yaml):
    cfg = tmp_path / "invalido.yaml"
    cfg.write_text(f"semilla: {valor_yaml}\nensayo:\n  limite: 50\n", encoding="utf-8")
    res = _ejecutar_cli("run", "--config", str(cfg))
    assert res.returncode == 2
    assert "Error: semilla =" in res.stderr


def test_qa_001_cli_semilla_negativa_con_hilos_sincronos():
    res = _ejecutar_cli(
        "run", "--config", "configs/default.yaml", "--semilla", "-3", "--motor", "hilos_sincronos"
    )
    assert res.returncode == 2
    assert "Error: semilla = -3" in res.stderr


@pytest.mark.parametrize("semillas_yaml", ["[0, -1]", "[-1, 0]", "[0, 1.5]", '[0, "3"]', "[0, true]"])
def test_qa_001_plan_lista_con_semilla_invalida_falla_sin_csv(tmp_path, semillas_yaml):
    base = tmp_path / "base.yaml"
    base.write_text("semilla: 0\nensayo:\n  limite: 50\n", encoding="utf-8")
    plan = tmp_path / "plan.yaml"
    plan.write_text(
        f"nombre: invalido\nbase: {base.name}\nsemillas: {semillas_yaml}\n"
        "factores:\n  madre.modo: [ausente]\n",
        encoding="utf-8",
    )
    salida = tmp_path / "out"
    res = _ejecutar_cli("experimentos", "--plan", str(plan), "--salida", str(salida), "--procesos", "1")
    assert res.returncode == 2
    assert "Error: semilla =" in res.stderr
    assert not list(salida.glob("*.csv")) if salida.exists() else True


@pytest.mark.parametrize("semilla", [0, 2**31, 10**12, 2**64])
def test_qa_001_semilla_cero_y_grandes_funcionan_y_son_reproducibles(semilla):
    datos = {
        "semilla": semilla,
        "mundo": {"escenario": "aleatorio"},
        "madre": {"modo": "difusion"},
        "canal": {"p_perdida": 0.2, "retardo": [0, 2]},
        "ensayo": {"limite": 400},
    }
    r1 = Simulacion(crear_mundo(datos), config_ensayo(datos)).correr()
    r2 = Simulacion(crear_mundo(datos), config_ensayo(datos)).correr()
    assert repr(r1) == repr(r2)
    assert r1.ticks_total > 0


def test_qa_001_semillas_que_difieren_en_bits_altos_no_colisionan():
    datos_a = {"semilla": 3, "mundo": {"escenario": "aleatorio"}, "ensayo": {"limite": 400}}
    datos_b = {"semilla": 3 + 65536, "mundo": {"escenario": "aleatorio"}, "ensayo": {"limite": 400}}
    ra = Simulacion(crear_mundo(datos_a), config_ensayo(datos_a)).correr()
    rb = Simulacion(crear_mundo(datos_b), config_ensayo(datos_b)).correr()
    assert repr(ra) != repr(rb)


def test_qa_001_huella_entre_procesos_random_y_hilos_sincronos_coinciden():
    huellas = [
        _huella_proceso(motor, 7, hs)
        for motor in ("determinista", "hilos_sincronos")
        for hs in ("0", "random", "random", "4294967295")
    ]
    assert len(set(huellas)) == 1, huellas


@pytest.mark.parametrize("semilla", [0, 2**31, 10**12])
def test_qa_001_semillas_grandes_reproducibles_entre_procesos(semilla):
    h_cero = _huella_proceso("determinista", semilla, "0")
    h_azar = _huella_proceso("determinista", semilla, "random")
    assert h_cero == h_azar
