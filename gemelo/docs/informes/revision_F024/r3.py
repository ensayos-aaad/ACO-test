# Nuevo: el generador del canal de la agente i y el generador de decisiones de la agente i tienen la MISMA semilla.
import random
from aco_gemelo.madre import ConfigMadre, Modo
from aco_gemelo.motor import ConfigEnsayo, Simulacion
from aco_gemelo.mundo import mundo_l
m = mundo_l(random.Random(3), tau0=0.0, tau_max=1.0, unidad_deposito=1/255)
sim = Simulacion(m, ConfigEnsayo(semilla=3, rho=0.0, p_perdida=0.5, madre=ConfigMadre(modo=Modo.DIFUSION)))
iguales = []
for a in sim.agentes:
    iguales.append(a.rng.getstate() == sim.canal._rng_de(a.id).getstate())
print("estado inicial identico (agente vs canal del mismo id):", iguales)
# registrar los valores que cada generador entrega a lo largo de un ensayo (agente 1)
a1 = sim.agentes[0]
log_ag, log_ca = [], []
class Espia(random.Random):
    pass
def envolver(rng, log):
    orig = rng.random
    def r():
        v = orig(); log.append(v); return v
    rng.random = r
envolver(a1.rng, log_ag)
envolver(sim.canal._rng_de(a1.id), log_ca)
r = sim.correr()
n = min(len(log_ag), len(log_ca))
comun = len(set(log_ag) & set(log_ca))
print(f"agente {a1.id}: valores random() usados por la agente {len(log_ag)}, por su canal {len(log_ca)}, valores identicos en ambos: {comun}")
print("primeros 5 de la agente:", [round(v, 4) for v in log_ag[:5]])
print("primeros 5 de su canal :", [round(v, 4) for v in log_ca[:5]])
# mundo (semilla 0) frente al generador de la madre en el canal (0*256+0)
print("semilla 0: generador del mundo == generador de la madre en el canal:",
      random.Random(0).getstate() == random.Random(0 * 256 + 0).getstate())
