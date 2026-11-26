"""Pruebas de QA (ronda 003): ataques a `reproducir/comparar.py` e integridad de `gemelo/REPRODUCIR.md`.

Cubre los puntos 2, 3 y 4 de `.handoff/rondas/003-para_qa.md`:
- Que `comparar.py` detecta diferencias en texto, CSV, PNG (RGB con alfa igual, negro con alfa 255,
  alfa alterado, modo distinto, tamaño distinto) y CSV publicados con `--completo` (alterado o faltante).
- Que `gemelo/REPRODUCIR.md` no tiene enlaces relativos rotos ni dependencias externas fuera de `git clone`.
"""

from __future__ import annotations

import importlib.util
import re
import shutil
import tempfile
from pathlib import Path

import pytest
from PIL import Image

REPO = Path(__file__).resolve().parents[2]
GEMELO = REPO / "gemelo"


def _cargar_comparador():
    spec = importlib.util.spec_from_file_location("qa_comparar_reproducir", GEMELO / "reproducir" / "comparar.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _copiar_esperado(comparar, carpeta: Path) -> dict[str, Path]:
    for nombre in ("run_default.txt", "batch_default_10.csv", "final_default.png"):
        shutil.copy(comparar.ESPERADO / nombre, carpeta / nombre)
    return {
        "texto": carpeta / "run_default.txt",
        "csv": carpeta / "batch_default_10.csv",
        "png": carpeta / "final_default.png",
    }


def test_qa_003_comparador_detecta_texto_alterado(monkeypatch, capsys):
    comparar = _cargar_comparador()

    def producir(carpeta: Path):
        out = _copiar_esperado(comparar, carpeta)
        out["texto"].write_text(
            out["texto"].read_text(encoding="utf-8").replace("739", "740", 1), encoding="utf-8"
        )
        return out

    monkeypatch.setattr(comparar, "_producir", producir)
    assert comparar.main([]) == 1
    salida = capsys.readouterr().out
    assert "NO PASA  Ensayo de referencia" in salida
    assert "PASA     Lote de referencia" in salida
    assert "PASA     Imagen del estado final" in salida


def test_qa_003_comparador_detecta_csv_alterado(monkeypatch, capsys):
    comparar = _cargar_comparador()

    def producir(carpeta: Path):
        out = _copiar_esperado(comparar, carpeta)
        out["csv"].write_text(
            out["csv"].read_text(encoding="utf-8").replace("327", "328", 1), encoding="utf-8"
        )
        return out

    monkeypatch.setattr(comparar, "_producir", producir)
    assert comparar.main([]) == 1
    salida = capsys.readouterr().out
    assert "PASA     Ensayo de referencia" in salida
    assert "NO PASA  Lote de referencia" in salida
    assert "PASA     Imagen del estado final" in salida


@pytest.mark.parametrize("mutacion", ["rgb_1px", "negro_alfa255", "alfa_1px", "modo_rgb", "tamano"])
def test_qa_003_comparador_detecta_png_alterado(monkeypatch, capsys, mutacion):
    comparar = _cargar_comparador()

    def producir(carpeta: Path):
        out = _copiar_esperado(comparar, carpeta)
        ruta = out["png"]
        with Image.open(ruta) as img:
            if mutacion == "rgb_1px":
                copia = img.copy()
                r, g, b, a = copia.getpixel((5, 5))
                copia.putpixel((5, 5), ((r + 1) % 256, g, b, a))
            elif mutacion == "negro_alfa255":
                copia = Image.new("RGBA", img.size, (0, 0, 0, 255))
            elif mutacion == "alfa_1px":
                copia = img.copy()
                r, g, b, a = copia.getpixel((5, 5))
                copia.putpixel((5, 5), (r, g, b, (a - 1) % 256))
            elif mutacion == "modo_rgb":
                copia = img.convert("RGB")
            else:
                copia = img.crop((0, 0, img.size[0] - 1, img.size[1]))
            copia.save(ruta)
        return out

    monkeypatch.setattr(comparar, "_producir", producir)
    assert comparar.main([]) == 1
    salida = capsys.readouterr().out
    assert "PASA     Ensayo de referencia" in salida
    assert "PASA     Lote de referencia" in salida
    assert "NO PASA  Imagen del estado final" in salida


@pytest.mark.parametrize("tipo_falla", ["csv_modificado", "csv_faltante"])
def test_qa_003_comparador_completo_detecta_csv_publicado_alterado_o_faltante(monkeypatch, capsys, tipo_falla):
    comparar = _cargar_comparador()

    def producir_ok(carpeta: Path):
        return _copiar_esperado(comparar, carpeta)

    def gemelo_mutado(*args: str) -> str:
        plan_arg = args[args.index("--plan") + 1]
        out_dir = Path(args[args.index("--salida") + 1])
        out_dir.mkdir(parents=True, exist_ok=True)
        plan = Path(plan_arg).stem
        src_dir = comparar.GEMELO / "experimentos" / "datos" / plan
        for archivo in src_dir.glob("*.csv"):
            shutil.copy(archivo, out_dir / archivo.name)
        if plan == "modos":
            objetivo = out_dir / "resumen.csv"
            if tipo_falla == "csv_modificado":
                objetivo.write_text(
                    objetivo.read_text(encoding="utf-8").replace("21", "22", 1), encoding="utf-8"
                )
            else:
                objetivo.unlink()
        return ""

    monkeypatch.setattr(comparar, "_producir", producir_ok)
    monkeypatch.setattr(comparar, "_gemelo", gemelo_mutado)
    assert comparar.main(["--completo"]) == 1
    salida = capsys.readouterr().out
    assert "NO PASA  Experimento publicado `modos` (8/9 CSV iguales)" in salida
    assert "PASA     Experimento publicado `rescate` (9/9 CSV iguales)" in salida
    ultima = Path(tempfile.gettempdir()) / "aco-reproducir-ultima"
    assert ultima.is_dir()


def test_qa_003_guia_enlaces_relativos_y_autocontenida():
    guia = GEMELO / "REPRODUCIR.md"
    texto = guia.read_text(encoding="utf-8")
    enlaces = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", texto)
    assert len(enlaces) >= 30
    rotos = []
    externos = []
    for etiqueta, destino in enlaces:
        if destino.startswith(("http://", "https://")):
            externos.append((etiqueta, destino))
        else:
            if not (guia.parent / destino).resolve().exists():
                rotos.append((etiqueta, destino))
    assert rotos == [], f"Enlaces relativos rotos: {rotos}"
    assert externos == [], f"Enlaces externos en markdown: {externos}"
    urls = re.findall(r"https?://[^\s\)>\]`\"]+", texto)
    assert urls == ["https://github.com/ensayos-aaad/ACO-test.git"], f"URLs inesperadas: {urls}"


def test_qa_003_salida_esperada_coincide_con_tabla_de_la_guia():
    guia = (GEMELO / "REPRODUCIR.md").read_text(encoding="utf-8")
    esperado_txt = (GEMELO / "reproducir" / "esperado" / "run_default.txt").read_text(encoding="utf-8")
    for linea in (
        "semilla                      2026",
        "escenario                    L",
        "modo_madre                   pista_de_baile",
        "motivo                       verificada",
        "asentadas                    1",
        "verificada                   1",
        "ticks_asentadas              739",
        "ticks_total                  760",
        "largo_optimo                 8",
        "largo_verificado             20",
        "razon                        2.5",
    ):
        assert linea in guia
        assert linea in esperado_txt
