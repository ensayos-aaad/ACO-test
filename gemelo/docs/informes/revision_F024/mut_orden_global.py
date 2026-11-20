# Mutante 1b: generador por emisor, pero desempate por orden global de llegada al canal (como antes).
import heapq, itertools
import aco_gemelo.canal.canal as c
from aco_gemelo.protocolo import FLAG_ACK, a_binario, a_json
_cont = itertools.count()
orig = c.CanalMemoria.enviar
def enviar(self, msg):
    datos = a_binario(msg, self.ctx) if self.formato == "binario" else a_json(msg, self.ctx)
    tam = len(datos) if self.formato == "binario" else len(datos.encode("utf-8"))
    fam = msg["fam"]
    with self._candado:
        destinos = self._destinos(msg); t = self.trafico[fam]; t.enviados += 1; t.bytes += tam
        g = fam == 0 or bool(msg.get("flags", 0) & FLAG_ACK); rng = self._rng_de(msg["src"])
        for d in destinos:
            if not g and rng.random() < self.p_perdida:
                t.perdidos += 1; continue
            e = 0 if fam == 0 else rng.randint(*self.retardo)
            heapq.heappush(self._buzones[d], (self.ahora + e, next(_cont), 0, 0, datos)); t.entregados += 1
c.CanalMemoria.enviar = enviar
