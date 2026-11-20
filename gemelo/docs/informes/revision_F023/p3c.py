# P3: abortado con cuadros registrados (la agente queda FALLIDA en el tick 2) -> png_final.
import sys, traceback
from aco_gemelo.agente import Estado
from aco_gemelo.madre import ConfigMadre, Modo
from aco_gemelo.motor import ConfigEnsayo, Simulacion
from aco_gemelo.mundo import mundo_l
from aco_gemelo.visual import png_final
import random
S = sys.argv[1]
m = mundo_l(random.Random(0), tau0=0.0, tau_max=1.0, unidad_deposito=1/255)
sim = Simulacion(m, ConfigEnsayo(semilla=0, n_agentes=1, rho=0.0, registrar=True, madre=ConfigMadre(modo=Modo.AUSENTE)))
a = sim.agentes[0]; original = a.paso
def paso(t):
    if t >= 2: a.estado = Estado.FALLIDA
    return original(t)
a.paso = paso
r = sim.correr()
print("motivo:", r.motivo, "ticks_total:", r.ticks_total, "cuadros de feromona:", len(r.feromona))
try:
    print("png_final ->", png_final(m, r, 1, S + "/abortado.png"))
except Exception as e:
    tb = traceback.extract_tb(e.__traceback__)[-1]
    print("png_final ->", type(e).__name__, repr(e), "en visual.py linea", tb.lineno)
