"""Pruebas del artefacto 14: experimentos en lote."""
import csv
from pathlib import Path

import pytest
import yaml

from aco_gemelo.__main__ import main
from aco_gemelo.experimentos import cargar_plan, condiciones, correr_plan

GEMELO = Path(__file__).parent.parent


def plan_pequeno(tmp_path, **cambios):
    base = tmp_path / "base.yaml"
    base.write_text(yaml.safe_dump({"ensayo": {"rho": 0.0}, "agente": {"viajes": 1}}), encoding="utf-8")
    plan = {"nombre": "prueba", "base": "base.yaml", "semillas": 3,
            "factores": {"mundo.escenario": ["L", "aleatorio"], "madre.modo": ["ausente", "difusion"]}}
    plan.update(cambios)
    ruta = tmp_path / "plan.yaml"
    ruta.write_text(yaml.safe_dump(plan, sort_keys=False), encoding="utf-8")
    return ruta


def leer(ruta):
    with open(ruta, newline="", encoding="utf-8") as archivo:
        return list(csv.DictReader(archivo))


# ---------------------------------------------------------------- criterio 1: un CSV por condición


def test_un_csv_por_condicion_y_un_resumen(tmp_path):
    carpeta = correr_plan(plan_pequeno(tmp_path), tmp_path / "salida", procesos=1)
    archivos = sorted(p.name for p in carpeta.glob("*.csv"))
    assert archivos == sorted([
        "escenario-L__modo-ausente.csv", "escenario-L__modo-difusion.csv",
        "escenario-aleatorio__modo-ausente.csv", "escenario-aleatorio__modo-difusion.csv",
        "resumen.csv"])
    filas = leer(carpeta / "escenario-aleatorio__modo-difusion.csv")
    assert [f["semilla"] for f in filas] == ["0", "1", "2"]
    assert {f["escenario"] for f in filas} == {"aleatorio"} and {f["modo"] for f in filas} == {"difusion"}
    assert all(f["modo_madre"] == "difusion" for f in filas)
    resumen = leer(carpeta / "resumen.csv")
    assert len(resumen) == 4 and {r["n"] for r in resumen} == {"3"}
    sin_madre = next(r for r in resumen if r["condicion"] == "escenario-L__modo-ausente")
    assert float(sin_madre["bytes_madre_agente_media"]) == 0
    assert all(0 <= float(r["verificadas_ic95_bajo"]) <= float(r["verificadas_tasa"])
               <= float(r["verificadas_ic95_alto"]) <= 1 for r in resumen)


def test_los_factores_cambian_la_configuracion(tmp_path):
    lista = condiciones(cargar_plan(plan_pequeno(tmp_path)))
    assert len(lista) == 4
    nombre, datos, valores = lista[-1]
    assert valores == {"mundo.escenario": "aleatorio", "madre.modo": "difusion"}
    assert datos["mundo"]["escenario"] == "aleatorio" and datos["madre"]["modo"] == "difusion"
    assert datos["agente"]["viajes"] == 1  # lo demás sale de la base


# ---------------------------------------------------------------- criterio 2: reproducible con la semilla


def test_reproducible_y_no_depende_del_numero_de_procesos(tmp_path):
    a = correr_plan(plan_pequeno(tmp_path), tmp_path / "a", procesos=1)
    b = correr_plan(plan_pequeno(tmp_path), tmp_path / "b", procesos=2)
    for archivo in a.glob("*.csv"):
        assert archivo.read_bytes() == (b / archivo.name).read_bytes(), archivo.name


def test_semillas_como_lista(tmp_path):
    carpeta = correr_plan(plan_pequeno(tmp_path, semillas=[7, 11]), tmp_path / "s", procesos=1)
    assert [f["semilla"] for f in leer(carpeta / "escenario-L__modo-ausente.csv")] == ["7", "11"]


# ---------------------------------------------------------------- planes inválidos y línea de comandos


@pytest.mark.parametrize("cambios", [
    {"factores": {"modo": ["ausente"]}},  # sin sección
    {"factores": {"madre.modo": []}},  # sin valores
    {"factores": {"madre.modo": ["reina"]}},  # valor inválido
    {"factores": {"agente.alfa": [1]}},  # clave inválida
])
def test_plan_invalido(tmp_path, cambios):
    with pytest.raises(ValueError):
        condiciones(cargar_plan(plan_pequeno(tmp_path, **cambios)))


def test_clave_desconocida_en_el_plan(tmp_path):
    ruta = plan_pequeno(tmp_path)
    datos = yaml.safe_load(ruta.read_text(encoding="utf-8"))
    datos["semilas"] = 3
    ruta.write_text(yaml.safe_dump(datos, sort_keys=False), encoding="utf-8")
    with pytest.raises(ValueError):
        cargar_plan(ruta)


def test_los_planes_del_repositorio_son_validos():
    for ruta in sorted((GEMELO / "experimentos").glob("*.yaml")):
        plan = cargar_plan(ruta)
        assert len(condiciones(plan)) == 8 and len(plan["semillas"]) == 30, ruta.name


def test_linea_de_comandos(tmp_path, capsys):
    assert main(["experimentos", "--plan", str(plan_pequeno(tmp_path)), "--salida",
                 str(tmp_path / "cli"), "--procesos", "1"]) == 0
    salida = capsys.readouterr().out
    assert "escenario-aleatorio__modo-difusion" in salida and "verificadas" in salida
