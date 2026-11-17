"""Línea de comandos del gemelo.

Desde la carpeta ``gemelo/``::

    python -m aco_gemelo run   --config configs/default.yaml
    python -m aco_gemelo run   --config configs/default.yaml --png final.png --animacion ensayo.gif
    python -m aco_gemelo batch --config configs/default.yaml --semillas 30
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any

from .config import cargar, config_ensayo, crear_mundo
from .metricas import fila, resumen
from .motor import Simulacion


def _escenario(datos: dict[str, Any]) -> str:
    return (datos.get("mundo") or {}).get("escenario", "L")


def ejecutar(datos: dict[str, Any], semilla: int, motor: str = "determinista",
             registrar: bool = False):
    """Corre un ensayo. Devuelve el mundo (al terminar), su dibujo inicial y el resultado."""
    mundo = crear_mundo(datos, semilla)
    dibujo = str(mundo)
    config = config_ensayo(datos, semilla)
    if registrar:
        config.registrar = True
    return mundo, dibujo, Simulacion(mundo, config).correr(motor)


def _run(args: argparse.Namespace) -> int:
    datos = cargar(args.config)
    semilla = datos.get("semilla", 0) if args.semilla is None else args.semilla
    imagenes = bool(args.png or args.animacion)
    mundo, dibujo, resultado = ejecutar(datos, semilla, args.motor, registrar=imagenes)
    print(f"Mundo (semilla {semilla}):\n{dibujo}\n")
    for clave, valor in fila(semilla, _escenario(datos), resultado).items():
        print(f"{clave:28} {'' if valor is None else valor}")
    n_agentes = config_ensayo(datos).n_agentes
    if args.png:
        from .visual import png_final

        print(f"PNG: {png_final(mundo, resultado, n_agentes, args.png)}")
    if args.animacion:
        from .visual import animar

        print(f"Animación: {animar(mundo, resultado, n_agentes, args.animacion, fps=args.fps)}")
    return 0


def _batch(args: argparse.Namespace) -> int:
    datos = cargar(args.config)
    semillas = range(args.semilla_inicial, args.semilla_inicial + args.semillas)
    filas = [fila(s, _escenario(datos), ejecutar(datos, s)[2]) for s in semillas]
    salida = Path(args.salida or f"resultados/{Path(args.config).stem}.csv")
    salida.parent.mkdir(parents=True, exist_ok=True)
    with open(salida, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)
    r = resumen(filas)
    print(f"{r['n']} ensayos → {salida}")
    for nombre in ("asentadas", "verificadas"):
        t = r[nombre]
        print(f"{nombre + ':':12} {t['exitos']}/{t['n']}"
              f"  (IC 95 %: {t['ic95_bajo']:.0%} a {t['ic95_alto']:.0%})")
    if r["ticks_media"] is not None:
        print(f"ticks hasta asentarse: media {r['ticks_media']:.1f}, "
              f"varianza {r['ticks_varianza']:.1f}, máximo {r['ticks_max']:.0f}")
    if r["razon_media"] is not None:
        print(f"razón media (ruta verificada / óptima): {r['razon_media']:.2f}")
    if r["conocimiento_medio"] is not None:
        print(f"conocimiento del mundo de la madre: {r['conocimiento_medio']:.0%}")
    print(f"bytes madre ↔ agentes por ensayo: "
          f"{r['bytes_agente_madre_media'] + r['bytes_madre_agente_media']:.0f}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada. Devuelve el código de salida."""
    parser = argparse.ArgumentParser(prog="python -m aco_gemelo",
                                     description="Gemelo de software de una colonia ACO.")
    sub = parser.add_subparsers(dest="orden", required=True)
    run = sub.add_parser("run", help="corre un ensayo y muestra el resultado")
    run.add_argument("--config", required=True, help="archivo YAML de configuración")
    run.add_argument("--semilla", type=int, help="reemplaza la semilla del archivo")
    run.add_argument("--motor", choices=("determinista", "hilos"), default="determinista")
    run.add_argument("--png", help="guarda una imagen del estado final (por ejemplo final.png)")
    run.add_argument("--animacion", help="guarda la animación del ensayo (.gif o .mp4)")
    run.add_argument("--fps", type=int, default=8, help="cuadros por segundo de la animación")
    run.set_defaults(func=_run)
    batch = sub.add_parser("batch", help="corre varios ensayos y guarda un CSV")
    batch.add_argument("--config", required=True, help="archivo YAML de configuración")
    batch.add_argument("--semillas", type=int, default=30, help="cuántas semillas (30 por defecto)")
    batch.add_argument("--semilla-inicial", type=int, default=0)
    batch.add_argument("--salida", help="CSV de salida (por defecto resultados/<config>.csv)")
    batch.set_defaults(func=_batch)
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
