"""Pruebas de QA (ronda 002): casos borde de `run`, planes `experimentos` y `batch`.

Cubre los grupos 1, 2 y 3 de `.handoff/rondas/002-para_qa.md` directamente vía `main()`
para mantener la ejecución rápida y sin efectos sobre el repositorio.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from aco_gemelo.__main__ import main


@pytest.mark.parametrize("motor", ["determinista", "hilos_sincronos", "hilos"])
@pytest.mark.parametrize("semilla_cli", ["0", "3"])
def test_qa_002_run_semilla_reemplaza_yaml_invalido_en_todos_los_motores(
    tmp_path, capsys, motor, semilla_cli
):
    cfg = tmp_path / "invalido.yaml"
    cfg.write_text('semilla: "3"\nensayo:\n  limite: 40\n', encoding="utf-8")
    rc = main(["run", "--config", str(cfg), "--semilla", semilla_cli, "--motor", motor])
    captura = capsys.readouterr()
    assert rc == 0, captura.err
    assert f"Mundo (semilla {semilla_cli}):" in captura.out
    assert captura.err == ""


def test_qa_002_run_semilla_con_png_y_animacion_sobre_yaml_invalido(tmp_path, capsys):
    cfg = tmp_path / "invalido.yaml"
    cfg.write_text("semilla: true\nensayo:\n  limite: 30\n", encoding="utf-8")
    png = tmp_path / "final.png"
    gif = tmp_path / "ensayo.gif"
    rc = main([
        "run", "--config", str(cfg), "--semilla", "3",
        "--png", str(png), "--animacion", str(gif),
    ])
    captura = capsys.readouterr()
    assert rc == 0, captura.err
    assert png.is_file() and png.stat().st_size > 0
    assert gif.is_file() and gif.stat().st_size > 0
    # Sin --semilla, la semilla inválida del YAML sí debe rechazarse
    assert main(["run", "--config", str(cfg)]) == 2


@pytest.mark.parametrize(
    "linea_semillas, esperadas",
    [
        ("semillas: [0, 0, 1]", ["0", "0", "1"]),
        (f"semillas: [{2**31}, {10**12}, {2**64}]", [str(2**31), str(10**12), str(2**64)]),
        ("semillas: [5]", ["5"]),
        ("", [str(i) for i in range(30)]),
    ],
    ids=["repetidas", "enormes", "un_elemento", "ausente_30"],
)
def test_qa_002_planes_validos_borde_con_base_de_semilla_invalida(
    tmp_path, linea_semillas, esperadas
):
    base = tmp_path / "base.yaml"
    base.write_text("semilla: -99\nensayo:\n  limite: 25\n", encoding="utf-8")
    plan = tmp_path / "plan.yaml"
    cuerpo = f"nombre: borde\nbase: {base.name}\n"
    if linea_semillas:
        cuerpo += f"{linea_semillas}\n"
    cuerpo += "factores:\n  madre.modo: [ausente]\n"
    plan.write_text(cuerpo, encoding="utf-8")
    salida = tmp_path / "out"
    rc = main(["experimentos", "--plan", str(plan), "--salida", str(salida), "--procesos", "1"])
    assert rc == 0
    with (salida / "modo-ausente.csv").open(newline="", encoding="utf-8") as f:
        semillas = [fila["semilla"] for fila in csv.DictReader(f)]
    assert semillas == esperadas


@pytest.mark.parametrize(
    "semillas_yaml",
    ["[]", "{a: 1}", "null", "-3", "0", '"3"', "[0, -1]", "[0, true]", "[0, false]", "[0, 1.5]", "[0, null]"],
)
def test_qa_002_planes_invalidos_no_crean_carpeta(tmp_path, capsys, semillas_yaml):
    base = tmp_path / "base.yaml"
    base.write_text("semilla: 0\nensayo:\n  limite: 25\n", encoding="utf-8")
    plan = tmp_path / "plan.yaml"
    plan.write_text(
        f"nombre: malo\nbase: {base.name}\nsemillas: {semillas_yaml}\n"
        "factores:\n  madre.modo: [ausente]\n",
        encoding="utf-8",
    )
    salida = tmp_path / "out_no_crear"
    rc = main(["experimentos", "--plan", str(plan), "--salida", str(salida), "--procesos", "1"])
    assert rc == 2
    assert "Error:" in capsys.readouterr().err
    assert not salida.exists()


@pytest.mark.parametrize(
    "extra_args",
    [
        ["--semillas", "0"],
        ["--semillas", "-2"],
        ["--semillas", "3", "--semilla-inicial", "-2"],
        ["--semillas", "1", "--semilla-inicial", "-1"],
    ],
)
def test_qa_002_batch_invalido_no_deja_carpeta_ni_csv(tmp_path, capsys, extra_args):
    base = tmp_path / "base.yaml"
    base.write_text("semilla: -99\nensayo:\n  limite: 25\n", encoding="utf-8")
    salida = tmp_path / "sub_no_crear" / "res.csv"
    rc = main(["batch", "--config", str(base), "--salida", str(salida), *extra_args])
    assert rc == 2
    assert "Error:" in capsys.readouterr().err
    assert not salida.exists()
    assert not salida.parent.exists()


def test_qa_002_batch_una_semilla_sobre_yaml_con_semilla_invalida(tmp_path):
    base = tmp_path / "base.yaml"
    base.write_text("semilla: -99\nensayo:\n  limite: 25\n", encoding="utf-8")
    salida = tmp_path / "sub_ok" / "res.csv"
    rc = main(["batch", "--config", str(base), "--semillas", "1", "--salida", str(salida)])
    assert rc == 0
    assert salida.is_file()
    with salida.open(newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    assert [fila["semilla"] for fila in filas] == ["0"]
