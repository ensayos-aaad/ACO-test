# P2: INICIO gasta numeros del generador del canal.
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

# (a) evidencia directa: estado del generador antes/despues de construir la Simulacion
cfg = ConfigEnsayo(semilla=5, rho=0.0, madre=ConfigMadre(modo=Modo.DIFUSION))
s = Simulacion(mundo(5), cfg)
print("(a) rng del canal tras __init__ == random.Random(semilla):",
      s.canal._rng.getstate() == random.Random(5).getstate())

# (b) mismo codigo, INICIO enviado pero devolviendo el generador a su estado previo
class CanalNeutro(CanalMemoria):
    def enviar(self, msg):
        if nombre_de(msg) == "INICIO":
            estado = self._rng.getstate(); super().enviar(msg); self._rng.setstate(estado); return
        super().enviar(msg)
def correr(s, modo, neutro, **kw):
    sim_mod.CanalMemoria = CanalNeutro if neutro else CanalMemoria
    try:
        return Simulacion(mundo(s), ConfigEnsayo(semilla=s, rho=0.0, madre=ConfigMadre(modo=modo), **kw)).correr()
    finally:
        sim_mod.CanalMemoria = CanalMemoria
for nombre, kw in [("defecto", {}), ("p=0.2,ret(0,3)", dict(p_perdida=0.2, retardo=(0, 3)))]:
    tot = dif_t = dif_m = 0
    for modo in (Modo.PISTA_DE_BAILE, Modo.RESCATE, Modo.DIFUSION):
        for sem in range(10):
            a = correr(sem, modo, False, **kw); b = correr(sem, modo, True, **kw)
            tot += 1; dif_t += a.ticks_total != b.ticks_total; dif_m += a.motivo != b.motivo
    print(f"(b) {nombre:15s} con INICIO vs INICIO neutro: ticks_total distintos {dif_t}/{tot}, motivo distinto {dif_m}/{tot}")
