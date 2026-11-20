import json, runpy, sys
import aco_gemelo.motor.simulacion as sim_mod
from aco_gemelo.canal import CanalMemoria
from aco_gemelo.protocolo import nombre_de
class CanalNeutro(CanalMemoria):
    def enviar(self, msg):
        if nombre_de(msg) == "INICIO":
            e = self._rng.getstate(); super().enviar(msg); self._rng.setstate(e); return
        super().enviar(msg)
sim_mod.CanalMemoria = CanalNeutro
runpy.run_path(sys.argv[1], run_name="__main__")
