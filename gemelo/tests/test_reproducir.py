"""Pruebas del artefacto 17: la salida de referencia de la guía (`REPRODUCIR.md`, `reproducir/esperado/`) sigue vigente.

Si un cambio de código cambia la salida del escenario de referencia, esta prueba falla: hay que regenerar
`reproducir/esperado/` a propósito (`python -X utf8 reproducir/comparar.py --generar`) y explicar el cambio.
"""
import importlib.util
import shutil
from pathlib import Path

GEMELO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("comparar_reproducir", GEMELO / "reproducir" / "comparar.py")
comparar = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(comparar)


def test_la_salida_de_referencia_se_reproduce(capsys):
    assert comparar.main([]) == 0
    salida = capsys.readouterr().out
    assert salida.count("PASA     ") == 3 and "NO PASA" not in salida


def test_el_comparador_detecta_una_diferencia(tmp_path, monkeypatch, capsys):
    """Sin simular: se "produce" una copia de la referencia con una cifra cambiada en el CSV."""
    def producir_alterado(carpeta):
        for nombre in ("run_default.txt", "batch_default_10.csv", "final_default.png"):
            shutil.copy(comparar.ESPERADO / nombre, carpeta / nombre)
        csv = carpeta / "batch_default_10.csv"
        lineas = csv.read_text(encoding="utf-8").splitlines()
        lineas[1] = lineas[1].replace("2026", "2025", 1) if "2026" in lineas[1] else lineas[1] + "0"
        csv.write_text("\n".join(lineas) + "\n", encoding="utf-8")
        return {"texto": carpeta / "run_default.txt", "csv": csv, "png": carpeta / "final_default.png"}

    monkeypatch.setattr(comparar, "_producir", producir_alterado)
    assert comparar.main([]) == 1
    salida = capsys.readouterr().out
    assert "NO PASA  Lote de referencia" in salida and "PASA     Ensayo de referencia" in salida


def test_el_comparador_detecta_un_pixel_distinto(tmp_path):
    """H1 de la revisión de la ronda 003: la comparación anterior solo miraba el canal alfa y una imagen de otro color
    pasaba. Aquí cambia un solo píxel, conservando el alfa."""
    from PIL import Image

    original = comparar.ESPERADO / "final_default.png"
    assert comparar._mismos_pixeles(original, original)
    with Image.open(original) as imagen:
        alterada = imagen.copy()
    r, g, b, *alfa = alterada.getpixel((10, 10))
    alterada.putpixel((10, 10), ((r + 1) % 256, g, b, *alfa))
    ruta = tmp_path / "alterada.png"
    alterada.save(ruta)
    assert not comparar._mismos_pixeles(original, ruta)
