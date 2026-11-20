import random
import aco_gemelo.canal.canal as c
def _rng_de(self, src):
    if src not in self._rngs:
        self._rngs[src] = random.Random(hash(f"canal:{self.semilla}:{src}"))
    return self._rngs[src]
c.CanalMemoria._rng_de = _rng_de
