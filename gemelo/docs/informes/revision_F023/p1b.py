# P1 minimo: un caso, campos que difieren
import random
from dataclasses import fields
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
    cfg = ConfigEnsayo(semilla=s, rho=0.0, madre=ConfigMadre(modo=modo), **kw)
    return Simulacion(mundo(s), cfg).correr(motor)
kw = dict(retardo=(0, 3))
d = ensayo(0, Modo.DIFUSION, "determinista", **kw)
for k in range(4):
    h = ensayo(0, Modo.DIFUSION, "hilos_sincronos", **kw)
    print("corrida", k, "igual al determinista:", h == d,
          "| campos distintos:", [f.name for f in fields(d) if getattr(d, f.name) != getattr(h, f.name)][:6],
          "| ticks_total det/hilos:", d.ticks_total, h.ticks_total)
