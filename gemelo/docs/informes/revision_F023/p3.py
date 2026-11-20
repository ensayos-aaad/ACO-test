# P3: un ensayo abortado rompe la visualizacion.
import sys, traceback
from aco_gemelo.agente import Estado
from aco_gemelo.madre import ConfigMadre, Modo
from aco_gemelo.motor import ConfigEnsayo, Simulacion
from aco_gemelo.mundo import Mundo
from aco_gemelo.visual import png_final, animar
S = sys.argv[1]
m = Mundo(2, 1, [], inicio=(0, 0), meta=(1, 0), tau0=0.0, tau_max=1.0)  # el mismo de test_b2
sim = Simulacion(m, ConfigEnsayo(n_agentes=1, rho=0.0, registrar=True, madre=ConfigMadre(modo=Modo.AUSENTE)))
sim.agentes[0].estado = Estado.FALLIDA
r = sim.correr()
print("motivo:", r.motivo, "ticks_total:", r.ticks_total)
for nombre, f in [("png_final", lambda: png_final(m, r, 1, S + "/abortado.png")),
                  ("animar", lambda: animar(m, r, 1, S + "/abortado.gif"))]:
    try:
        print(nombre, "->", f())
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)[-1]
        print(nombre, "->", type(e).__name__, repr(e), "en", tb.filename.split("aco_gemelo")[-1], "linea", tb.lineno)
