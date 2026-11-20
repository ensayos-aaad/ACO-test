# Punto 1: hilos_sincronos (3 corridas) frente al determinista, canales agresivos, mundos L y aleatorio.
import random, sys
from aco_gemelo.madre import ConfigMadre, Modo
from aco_gemelo.motor import ConfigEnsayo, Simulacion
from aco_gemelo.mundo import mundo_l, mundo_aleatorio
C = dict(tau0=0.0, tau_max=1.0, unidad_deposito=1/255)
def mundo(f, s):
    rng = random.Random(s)
    while True:
        m = f(rng, **C)
        if m.largo_optimo() >= 4: return m
canales = [("p0.2", dict(p_perdida=0.2)), ("ret0-3", dict(retardo=(0, 3))),
           ("p0.5+ret0-5", dict(p_perdida=0.5, retardo=(0, 5))),
           ("p0.2+ret1-4+json", dict(p_perdida=0.2, retardo=(1, 4), formato="json"))]
tot = dist = 0
for nombre, kw in canales:
    d0 = 0
    for f in (mundo_l, mundo_aleatorio):
        for modo in Modo:
            for s in range(6):
                cfg = ConfigEnsayo(semilla=s, rho=0.01, registrar=True, madre=ConfigMadre(modo=modo), salida_cada=1, **kw)
                det = Simulacion(mundo(f, s), cfg).correr("determinista")
                for _ in range(3):
                    tot += 1
                    h = Simulacion(mundo(f, s), cfg).correr("hilos_sincronos")
                    d0 += h != det
    dist += d0
    print(f"{nombre:18s} hilos_sincronos != determinista: {d0}/{2*4*6*3}", flush=True)
print("total", dist, "/", tot)
