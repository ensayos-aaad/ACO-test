"""Pruebas de QA (ronda 001): hallazgos reproducibles en CLI `run` y planes `experimentos`.

Reproducen los hallazgos H1 y H2 reportados en `.handoff/rondas/001-reporte_qa.md`.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

GEMELO = Path(__file__).resolve().parents[2] / "gemelo"


def _ejecutar_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", "-X", "utf8", "-m", "aco_gemelo", *args],
        cwd=GEMELO,
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_qa_001_h1_cli_run_semilla_reemplaza_semilla_invalida_del_yaml(tmp_path):
    """H1: `--semilla 3` debe reemplazar `semilla: -3` del YAML sin fallar al final en `_run`."""
    cfg = tmp_path / "semilla_negativa.yaml"
    cfg.write_text("semilla: -3\nensayo:\n  limite: 80\n", encoding="utf-8")
    png = tmp_path / "final.png"
    res = _ejecutar_cli("run", "--config", str(cfg), "--semilla", "3", "--png", str(png))
    assert res.returncode == 0, f"stderr={res.stderr!r}"
    assert png.exists()


@pytest.mark.parametrize("semillas_yaml", ["true", "false", "1.5"])
def test_qa_001_h2_plan_experimentos_rechaza_semillas_booleana_o_flotante(tmp_path, semillas_yaml):
    """H2: en un plan YAML, `semillas: true/false/1.5` debe dar error limpio (código 2, sin CSV)."""
    base = tmp_path / "base.yaml"
    base.write_text("semilla: 0\nensayo:\n  limite: 50\n", encoding="utf-8")
    plan = tmp_path / "plan.yaml"
    plan.write_text(
        f"nombre: mal_plan\nbase: {base.name}\nsemillas: {semillas_yaml}\n"
        "factores:\n  madre.modo: [ausente]\n",
        encoding="utf-8",
    )
    salida = tmp_path / "out"
    res = _ejecutar_cli("experimentos", "--plan", str(plan), "--salida", str(salida), "--procesos", "1")
    assert res.returncode == 2, f"returncode={res.returncode}, stderr={res.stderr!r}"
    assert res.stderr.startswith("Error:"), f"stderr={res.stderr!r}"
    assert not list(salida.glob("*.csv")) if salida.exists() else True
