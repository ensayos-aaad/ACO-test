import random, sys, json
from aco_gemelo.madre import ConfigMadre, Modo
from aco_gemelo.motor import ConfigEnsayo, Simulacion
from aco_gemelo.mundo import mundo_l
C = dict(tau0=0.0, tau_max=1.0, unidad_deposito=1/255)
def mundo(s):
    rng = random.Random(s)
    while True:
        m = mundo_l(rng, **C)
        if m.largo_optimo() >= 4: return m
out = []
for nombre, kw in [("defecto", {}), ("perd", dict(p_perdida=0.2, retardo=(0, 3)))]:
    for modo in (Modo.PISTA_DE_BAILE, Modo.RESCATE, Modo.DIFUSION):
        for s in range(10):
            r = Simulacion(mundo(s), ConfigEnsayo(semilla=s, rho=0.0, madre=ConfigMadre(modo=modo), **kw)).correr()
            out.append([nombre, modo.name, s, r.motivo, r.ticks_total])
print(json.dumps(out))
