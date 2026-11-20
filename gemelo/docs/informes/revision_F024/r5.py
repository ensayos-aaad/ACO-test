# Exploratorio: efecto agregado de la semilla compartida agente/canal. Variante: canal con semilla salada (independiente).
import random, sys, statistics
import aco_gemelo.canal.canal as cm
from aco_gemelo.madre import ConfigMadre, Modo
from aco_gemelo.motor import ConfigEnsayo, Simulacion
from aco_gemelo.mundo import mundo_aleatorio
C = dict(tau0=0.0, tau_max=1.0, unidad_deposito=1/255)
def mundo(s):
    rng = random.Random(s)
    while True:
        m = mundo_aleatorio(rng, **C)
        if m.largo_optimo() >= 4: return m
orig = cm.CanalMemoria._rng_de
def salado(self, src):
    if src not in self._rngs:
        self._rngs[src] = random.Random(f"canal:{self.semilla}:{src}")
    return self._rngs[src]
for nombre, f in (("actual (misma semilla)", orig), ("independiente", salado)):
    cm.CanalMemoria._rng_de = f
    for modo in Modo:
        res = [Simulacion(mundo(s), ConfigEnsayo(semilla=s, rho=0.01, salida_cada=1, p_perdida=0.3, retardo=(0, 3),
               madre=ConfigMadre(modo=modo))).correr() for s in range(30)]
        print(f"{nombre:24s} {modo.name:15s} verificadas {sum(r.verificada for r in res):2d}/30  ticks medianos {statistics.median(r.ticks_total for r in res)}", flush=True)
