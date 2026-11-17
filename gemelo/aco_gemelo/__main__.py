"""Línea de comandos del gemelo.

Desde la carpeta ``gemelo/``::

    python -m aco_gemelo run   --config configs/default.yaml
    python -m aco_gemelo batch --config configs/default.yaml --semillas 30
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any

from .config import cargar, config_ensayo, crear_mundo
from .motor import Resultado, Simulacion

_FAMILIAS = ("mundo_agente", "agente_agente", "agente_madre", "madre_agente")


def fila(semilla: int, datos: dict[str, Any], resultado: Resultado) -> dict[str, Any]:
    """Aplana un resultado en una fila de CSV."""
    salida = {
        "semilla": semilla,
        "escenario": (datos.get("mundo") or {}).get("escenario", "L"),
        "modo_madre": config_ensayo(datos).madre.modo.name.lower(),
        "motivo": resultado.motivo,
        "asentadas": int(resultado.asentadas),
        "verificada": int(resultado.verificada),
        "ticks_asentadas": resultado.ticks_asentadas,
        "ticks_total": resultado.ticks_total,
        "largo_optimo": resultado.largo_optimo,
        "largo_verificado": resultado.largo_verificado,
        "razon": None if resultado.razon is None else round(resultado.razon, 4),
        "bloqueadas": resultado.bloqueadas,
        "memoria_madre": resultado.memoria_madre,
    }
    for familia in _FAMILIAS:
        salida[f"mensajes_{familia}"] = resultado.trafico[familia]["enviados"]
        salida[f"bytes_{familia}"] = resultado.trafico[familia]["bytes"]
    return salida


def ejecutar(datos: dict[str, Any], semilla: int, motor: str = "determinista"):
    """Corre un ensayo. Devuelve el mundo inicial (como texto) y el resultado."""
    mundo = crear_mundo(datos, semilla)
    dibujo = str(mundo)
    return dibujo, Simulacion(mundo, config_ensayo(datos, semilla)).correr(motor)


def _run(args: argparse.Namespace) -> int:
    datos = cargar(args.config)
    semilla = datos.get("semilla", 0) if args.semilla is None else args.semilla
    dibujo, resultado = ejecutar(datos, semilla, args.motor)
    print(f"Mundo (semilla {semilla}):\n{dibujo}\n")
    for clave, valor in fila(semilla, datos, resultado).items():
        print(f"{clave:28} {'' if valor is None else valor}")
    return 0


def _batch(args: argparse.Namespace) -> int:
    datos = cargar(args.config)
    semillas = range(args.semilla_inicial, args.semilla_inicial + args.semillas)
    filas = [fila(s, datos, ejecutar(datos, s)[1]) for s in semillas]
    salida = Path(args.salida or f"resultados/{Path(args.config).stem}.csv")
    salida.parent.mkdir(parents=True, exist_ok=True)
    with open(salida, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)
    n = len(filas)
    verificadas = [f for f in filas if f["verificada"]]
    print(f"{n} ensayos → {salida}")
    print(f"asentadas:   {sum(f['asentadas'] for f in filas)}/{n}")
    print(f"verificadas: {len(verificadas)}/{n}")
    if verificadas:
        print(f"razón media (ruta verificada / óptima): "
              f"{sum(f['razon'] for f in verificadas) / len(verificadas):.2f}")
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
