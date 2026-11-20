"""Línea base de F-023. Desde gemelo/:

    python -X utf8 -W ignore experimentos/linea_base_f023/linea_base.py [--salida DIR] [--semillas 30]

Deja en DIR (por defecto experimentos/linea_base_f023/datos):
  determinista.csv, sincronos_a.csv, sincronos_b.csv  (una fila por condición x semilla)
  diferencias.csv   (por condición: cuántos ensayos difieren entre las dos corridas de hilos_sincronos,
                     entre determinista y sincronos_a, y contra datos/modos de F-022 con canal ideal)
  determinista_b.csv (segunda corrida de una muestra, comprueba reproducibilidad)
Se puede repetir tal cual después de corregir el código y comparar con comparar.py.
"""
from __future__ import annotations

import argparse
import copy
import csv
import itertools
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]  # gemelo/
sys.path.insert(0, str(RAIZ))

from aco_gemelo.config import cargar, config_ensayo, crear_mundo  # noqa: E402
from aco_gemelo.metricas import fila  # noqa: E402
from aco_gemelo.motor import Simulacion  # noqa: E402

CANALES = {"ideal": {}, "perdidas": {"p_perdida": 0.2}, "retardo": {"retardo": [1, 3]}}
MODOS = ["ausente", "pista_de_baile", "rescate", "difusion"]
MUNDOS = ["L", "aleatorio"]
CLAVE = ["motivo", "ticks_asentadas", "ticks_total", "verificada", "conocimiento", "bytes_totales"]


def condiciones():
    base = cargar(RAIZ / "configs" / "default.yaml")
    for canal, mundo, modo in itertools.product(CANALES, MUNDOS, MODOS):
        d = copy.deepcopy(base)
        d["mundo"]["escenario"] = mundo
        d["madre"]["modo"] = modo
        d.setdefault("canal", {}).update(CANALES[canal])
        yield f"canal-{canal}__escenario-{mundo}__modo-{modo}", canal, mundo, modo, d


def ensayo(arg):
    nombre, canal, mundo, modo, datos, semilla, motor = arg
    r = Simulacion(crear_mundo(datos, semilla), config_ensayo(datos, semilla)).correr(motor)
    return {"condicion": nombre, "canal": canal, **fila(semilla, mundo, r)}


def correr(trabajos, procesos=8):
    with ProcessPoolExecutor(max_workers=procesos) as g:
        return list(g.map(ensayo, trabajos, chunksize=2))


def guardar(ruta, filas):
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)


def txt(v):
    """None se guarda como celda vacía en el CSV."""
    return "" if v is None else str(v)


def difieren(a, b):
    return sum(1 for x, y in zip(a, b) if x != y)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", default=str(Path(__file__).parent / "datos"))
    ap.add_argument("--semillas", type=int, default=30)
    a = ap.parse_args()
    out = Path(a.salida)
    out.mkdir(parents=True, exist_ok=True)
    conds = list(condiciones())
    mk = lambda motor: [(n, c, m, mo, d, s, motor) for n, c, m, mo, d in conds for s in range(a.semillas)]
    det = correr(mk("determinista"))
    guardar(out / "determinista.csv", det)
    muestra = [t for t in mk("determinista") if t[1] != "ideal"]
    det_b = correr(muestra)
    guardar(out / "determinista_b.csv", det_b)
    sa = correr(mk("hilos_sincronos"), procesos=4)
    guardar(out / "sincronos_a.csv", sa)
    sb = correr(mk("hilos_sincronos"), procesos=4)
    guardar(out / "sincronos_b.csv", sb)

    f22 = {}
    for p in (RAIZ / "experimentos" / "datos" / "modos").glob("escenario-*.csv"):
        with open(p, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                f22[(r["escenario"], r["modo_madre"], int(r["semilla"]))] = r
    filas = []
    for i, (n, c, m, mo, d) in enumerate(conds):
        s0, s1 = i * a.semillas, (i + 1) * a.semillas
        D, A, B = det[s0:s1], sa[s0:s1], sb[s0:s1]
        reg = {"condicion": n, "n": a.semillas,
               "sinc_a_vs_b": difieren(A, B),
               "sinc_a_vs_b_clave": sum(1 for x, y in zip(A, B) if any(str(x[k]) != str(y[k]) for k in CLAVE)),
               "det_vs_sinc_a": difieren(D, A)}
        if c == "ideal":
            reg["det_vs_F022"] = sum(1 for x in D if any(
                txt(x[k]) != txt(f22[(m, x["modo_madre"], x["semilla"])][k]) for k in CLAVE))
        filas.append(reg)
    # det vs det_b: det_b solo tiene los canales no ideales, en el mismo orden
    no_ideal = [(i, n) for i, (n, c, *_r) in enumerate(conds) if c != "ideal"]
    for j, (i, n) in enumerate(no_ideal):
        filas[i]["det_vs_det_b"] = difieren(det[i * a.semillas:(i + 1) * a.semillas],
                                           det_b[j * a.semillas:(j + 1) * a.semillas])
    cab = ["condicion", "n", "sinc_a_vs_b", "sinc_a_vs_b_clave", "det_vs_sinc_a", "det_vs_det_b", "det_vs_F022"]
    with open(out / "diferencias.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cab)
        w.writeheader()
        w.writerows(filas)
    for c in CANALES:
        g = [r for r in filas if r["condicion"].startswith(f"canal-{c}")]
        print(c, "sinc_a_vs_b", sum(r["sinc_a_vs_b"] for r in g), "/", sum(r["n"] for r in g),
              "| det_vs_sinc_a", sum(r["det_vs_sinc_a"] for r in g))


if __name__ == "__main__":
    main()
