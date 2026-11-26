"""Comprueba que esta máquina reproduce la salida de referencia del gemelo (artefacto 17, `gemelo/REPRODUCIR.md`).

Uso, desde `gemelo/` y con el Python del entorno `aco-gemelo`:

    python -X utf8 reproducir/comparar.py              # escenario L, semilla 2026 (≈ 30 s)
    python -X utf8 reproducir/comparar.py --completo   # además, los 18 CSV de los experimentos publicados (≈ 3–4 min en total)

Corre los mismos comandos que la guía, por la línea de comandos del gemelo, en una carpeta temporal (no escribe nada en
el repositorio) y compara con `reproducir/esperado/`. Imprime PASA o NO PASA por punto y termina con código 0 solo si
todo pasa. `--generar` rehace `esperado/` (solo para Desarrollo, cuando un cambio de código cambia la salida a
propósito: el cambio debe quedar explicado en `FAILURES.md` o en `CHANGELOG.md`).
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

GEMELO = Path(__file__).resolve().parents[1]
ESPERADO = Path(__file__).resolve().parent / "esperado"
CONFIG = "configs/default.yaml"  # escenario L del plano, semilla 2026
N_SEMILLAS = 10  # lote corto: semillas 0 a 9
PLANES = ("modos", "rescate")


def _gemelo(*argumentos: str) -> str:
    """Corre `python -m aco_gemelo ...` con este mismo intérprete y devuelve la salida estándar."""
    salida = subprocess.run([sys.executable, "-X", "utf8", "-W", "ignore", "-m", "aco_gemelo", *argumentos],
                            cwd=GEMELO, capture_output=True, text=True, encoding="utf-8")
    if salida.returncode != 0:
        raise RuntimeError(f"Falló: aco_gemelo {' '.join(argumentos)}\n{salida.stderr}")
    return salida.stdout


def _lineas(texto: str) -> list[str]:
    """Líneas sin el salto de línea (Git puede guardar LF o CRLF según el sistema; el contenido es lo que cuenta)."""
    return texto.splitlines()


def _sin_ruta_png(texto: str) -> str:
    """La línea `PNG: <ruta>` depende de la carpeta temporal; no forma parte del resultado."""
    return "\n".join(l for l in _lineas(texto) if not l.startswith("PNG:")) + "\n"


def _mismos_pixeles(a: Path, b: Path) -> bool:
    from PIL import Image

    # Se comparan los bytes de todos los canales. (`ImageChops.difference(...).getbbox()` no sirve: con imágenes RGBA,
    # Pillow solo mira el canal alfa y una imagen de otro color "pasaba"; hallazgo H1 de la revisión de la ronda 003.)
    with Image.open(a) as x, Image.open(b) as y:
        return x.size == y.size and x.mode == y.mode and x.tobytes() == y.tobytes()


def _producir(carpeta: Path) -> dict[str, Path]:
    """Corre el ensayo y el lote de referencia en `carpeta`. Devuelve los archivos producidos."""
    png, csv = carpeta / "final_default.png", carpeta / f"batch_default_{N_SEMILLAS}.csv"
    texto = _gemelo("run", "--config", CONFIG, "--png", str(png))
    (carpeta / "run_default.txt").write_text(_sin_ruta_png(texto), encoding="utf-8")
    _gemelo("batch", "--config", CONFIG, "--semillas", str(N_SEMILLAS), "--salida", str(csv))
    return {"texto": carpeta / "run_default.txt", "csv": csv, "png": png}


def _comparar_texto(a: Path, b: Path) -> bool:
    return _lineas(a.read_text(encoding="utf-8")) == _lineas(b.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compara la salida de esta máquina con la de referencia.")
    parser.add_argument("--completo", action="store_true", help="también los 18 CSV de los experimentos publicados")
    parser.add_argument("--generar", action="store_true", help="rehace reproducir/esperado/ (solo Desarrollo)")
    args = parser.parse_args(argv)
    print(f"Python: {sys.executable}  ({sys.version.split()[0]})")

    if args.generar:
        ESPERADO.mkdir(exist_ok=True)
        for ruta in _producir(ESPERADO).values():
            print(f"generado: {ruta.relative_to(GEMELO)}")
        return 0

    resultados: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory(prefix="aco-reproducir-") as tmp:
        carpeta = Path(tmp)
        producidos = _producir(carpeta)
        resultados.append(("Ensayo de referencia (texto de `run`, semilla 2026)",
                           _comparar_texto(producidos["texto"], ESPERADO / "run_default.txt")))
        resultados.append((f"Lote de referencia ({N_SEMILLAS} semillas, CSV)",
                           _comparar_texto(producidos["csv"], ESPERADO / f"batch_default_{N_SEMILLAS}.csv")))
        resultados.append(("Imagen del estado final (PNG, píxel a píxel)",
                           _mismos_pixeles(producidos["png"], ESPERADO / "final_default.png")))
        if args.completo:
            for plan in PLANES:
                salida = carpeta / plan
                _gemelo("experimentos", "--plan", f"experimentos/{plan}.yaml", "--salida", str(salida))
                publicados = sorted((GEMELO / "experimentos" / "datos" / plan).glob("*.csv"))
                iguales = [p.name for p in publicados if (salida / p.name).exists()
                           and _comparar_texto(p, salida / p.name)]
                resultados.append((f"Experimento publicado `{plan}` ({len(iguales)}/{len(publicados)} CSV iguales)",
                                   len(iguales) == len(publicados) > 0))
        if not all(ok for _, ok in resultados):
            guardar = Path(tempfile.gettempdir()) / "aco-reproducir-ultima"
            shutil.rmtree(guardar, ignore_errors=True)
            shutil.copytree(carpeta, guardar)
    for nombre, ok in resultados:
        print(f"{'PASA   ' if ok else 'NO PASA'}  {nombre}")
    if all(ok for _, ok in resultados):
        print("Resultado: PASA. Esta máquina reproduce la salida de referencia.")
        return 0
    print(f"Resultado: NO PASA. Lo producido quedó en {guardar} para compararlo con reproducir/esperado/.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
