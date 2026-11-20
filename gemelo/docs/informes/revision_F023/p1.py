# P1: hilos_sincronos frente a determinista con perdidas/retardo.
import random, sys
from dataclasses import replace
from aco_gemelo.madre import ConfigMadre, Modo
from aco_gemelo.motor import ConfigEnsayo, Simulacion
from aco_gemelo.mundo import mundo_l
C = dict(tau0=0.0, tau_max=1.0, unidad_deposito=1/255)
def mundo(s):
    rng = random.Random(s)
    while True:
        m = mundo_l(rng, **C)
        if m.largo_optimo() >= 4: return m
def ensayo(s, modo, motor, **kw):
    cfg = ConfigEnsayo(semilla=s, rho=0.0, registrar=True, madre=ConfigMadre(modo=modo), **kw)
    return Simulacion(mundo(s), cfg).correr(motor)
canal = [("defecto", {}), ("p=0.2", dict(p_perdida=0.2)), ("ret(0,3)", dict(retardo=(0,3))),
         ("p=0.2+ret(0,3)", dict(p_perdida=0.2, retardo=(0,3)))]
for nombre, kw in canal:
    dist = tot = 0
    for modo in Modo:
        for s in range(5):
            tot += 1
            a = ensayo(s, modo, "hilos_sincronos", **kw); b = ensayo(s, modo, "determinista", **kw)
            dist += a != b
    print(f"{nombre:16s} distintos {dist}/{tot}")
# tambien: hilos_sincronos contra si mismo (no determinista entre corridas)
kw = dict(p_perdida=0.2, retardo=(0,3))
rs = [ensayo(1, Modo.PISTA_DE_BAILE, "hilos_sincronos", **kw) for _ in range(5)]
print("hilos_sincronos s=1 PISTA p=0.2 ret(0,3), 5 corridas -> ticks_total:", [r.ticks_total for r in rs],
      "| resultados distintos entre si:", len({repr(r) for r in rs}))
print("determinista mismo caso, 3 corridas ->", [ensayo(1, Modo.PISTA_DE_BAILE, "determinista", **kw).ticks_total for _ in range(3)])
