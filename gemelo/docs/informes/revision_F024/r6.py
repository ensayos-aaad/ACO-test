# Punto 2: cuanto cambia INICIO por si solo (ahora solo gasta el generador de la madre).
import random
import aco_gemelo.motor.simulacion as sim_mod
from aco_gemelo.canal import CanalMemoria
from aco_gemelo.madre import ConfigMadre, Modo
from aco_gemelo.motor import ConfigEnsayo, Simulacion
from aco_gemelo.mundo import mundo_l
from aco_gemelo.protocolo import nombre_de
C = dict(tau0=0.0, tau_max=1.0, unidad_deposito=1/255)
def mundo(s):
    rng = random.Random(s)
    while True:
        m = mundo_l(rng, **C)
        if m.largo_optimo() >= 4: return m
class CanalNeutro(CanalMemoria):
    def enviar(self, msg):
        if nombre_de(msg) == "INICIO":
            g = self._rng_de(msg["src"]); e = g.getstate(); super().enviar(msg); g.setstate(e); return
        super().enviar(msg)
def correr(s, modo, neutro, **kw):
    sim_mod.CanalMemoria = CanalNeutro if neutro else CanalMemoria
    try:
        return Simulacion(mundo(s), ConfigEnsayo(semilla=s, rho=0.0, madre=ConfigMadre(modo=modo), **kw)).correr()
    finally:
        sim_mod.CanalMemoria = CanalMemoria
for nombre, kw in [("defecto", {}), ("p=0.2", dict(p_perdida=0.2)), ("p=0.2,ret(0,3)", dict(p_perdida=0.2, retardo=(0, 3)))]:
    tot = dt = dm = 0
    for modo in (Modo.PISTA_DE_BAILE, Modo.RESCATE, Modo.DIFUSION):
        for sem in range(10):
            a = correr(sem, modo, False, **kw); b = correr(sem, modo, True, **kw)
            tot += 1; dt += a.ticks_total != b.ticks_total; dm += a.motivo != b.motivo
    print(f"{nombre:15s} INICIO normal vs neutro: ticks_total distintos {dt}/{tot}, motivo {dm}/{tot}")
