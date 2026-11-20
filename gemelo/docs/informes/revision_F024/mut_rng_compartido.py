# Mutante 1a: un solo generador compartido por todos los emisores (vuelve el defecto de F-023 (1)).
import random
import aco_gemelo.canal.canal as c
def _rng_de(self, src):
    if not hasattr(self, "_comun"):
        self._comun = random.Random(self.semilla)
    return self._comun
c.CanalMemoria._rng_de = _rng_de
