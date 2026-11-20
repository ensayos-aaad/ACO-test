import sys
from dataclasses import replace
from pathlib import Path
G = Path(sys.argv[1])
sys.path.insert(0, str(G))
from aco_gemelo.config import cargar, config_ensayo, crear_mundo
from aco_gemelo.motor import Simulacion
BASE = cargar(G / "configs" / "default.yaml")
print("semilla default.yaml:", BASE["semilla"])
def correr(modo):
    datos = {**BASE, "madre": {**BASE["madre"], "modo": modo}}
    mundo = crear_mundo(datos)
    return mundo, Simulacion(mundo, replace(config_ensayo(datos), registrar=True)).correr()
M, SIN = correr("ausente"); _, CON = correr("difusion"); _, RES = correr("rescate")
print("mundo", M.ancho, M.alto, "inicio", M.inicio, "meta", M.meta, "obst", sorted(M.obstaculos))
print("optima", M.bfs())
for n, r in (("SIN", SIN), ("CON", CON), ("RES", RES)):
    ruta = r.ruta_verificada
    print(n, r.motivo, r.ticks_asentadas, r.ticks_total, r.largo_verificado, r.largo_optimo, "razon", r.razon)
    if ruta:
        print("  ruta", ruta)
        print("  celdas repetidas:", len(ruta) - len(set(ruta)))
        f = r.feromona[-1]
        top = sorted(range(len(f)), key=lambda k: -f[k])[:6]
        print("  top feromona celdas:", [((k % M.ancho, k // M.ancho), round(f[k], 3)) for k in top])
        print("  ¿top-6 en ruta?", [((k % M.ancho, k // M.ancho) in ruta) for k in top])
    print("  len serie", len(r.serie), "len mapa", len(r.mapa_madre), "conoc final", r.conocimiento)
    print("  mecanismos", {k: v for k, v in r.mecanismos.items() if v})
c = [f["conocimiento"] for f in CON.serie]
tope = c.index(max(c)); print("tope", tope, "max", max(c), "final", c[-1], "monotona", all(b >= a for a, b in zip(c, c[1:])))
print("TICKS", [round(tope * k / 7) for k in range(8)], [round(c[round(tope*k/7)], 3) for k in range(8)])
ll = [f["llegaron"] for f in CON.serie]; print("tick en que llegan las 6 al menos una vez:", ll.index(6), "primera llegada:", ll.index(1))
# obstaculos creidos vs reales en el tope
def celdas(b): return {(k % M.ancho, k // M.ancho) for k in range(M.ancho*M.alto) if b >> k & 1}
con, obs = (celdas(b) for b in CON.mapa_madre[tope])
print("en tope: conocidas", len(con), "de", M.ancho*M.alto, "obst creidos", sorted(obs), "== reales:", obs == set(M.obstaculos))
falsos = 0
for t,(a,b) in enumerate(CON.mapa_madre):
    o = celdas(b)
    if o - set(M.obstaculos): falsos += 1
print("ticks con algún obstáculo falso:", falsos)
print("RES conocimiento final", RES.conocimiento)
# trazos: ids en historial
print("ids en historial SIN:", sorted({i for _, i, _ in SIN.historial}))
