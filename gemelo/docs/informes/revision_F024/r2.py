# Punto 2: INICIO solo toca el generador de la madre.
import random
from aco_gemelo.madre import ConfigMadre, Modo
from aco_gemelo.motor import ConfigEnsayo, Simulacion
from aco_gemelo.mundo import mundo_l
from aco_gemelo.protocolo import ID_MADRE
m = mundo_l(random.Random(5), tau0=0.0, tau_max=1.0, unidad_deposito=1/255)
for kw in ({}, dict(p_perdida=0.2, retardo=(0, 3))):
    sim = Simulacion(m, ConfigEnsayo(semilla=5, rho=0.0, madre=ConfigMadre(modo=Modo.DIFUSION), **kw))
    c = sim.canal
    print(kw, "generadores creados tras __init__:", sorted(c._rngs), "(ID_MADRE =", ID_MADRE, ")",
          "| madre avanzo:", c._rngs[ID_MADRE].getstate() != random.Random(5 * 256 + ID_MADRE).getstate())
# semilla negativa / grande: colision de generadores entre emisores?
from aco_gemelo.canal import CanalMemoria
c = CanalMemoria(semilla=-1)
print("semilla -1, src 1 ->", [c._rng_de(1).random() for _ in range(2)], "| semilla 0 src 255 ->",
      [random.Random(255).random() for _ in range(2)])
