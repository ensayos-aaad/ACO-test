import hashlib, random
from aco_gemelo.madre import ConfigMadre, Modo
from aco_gemelo.motor import ConfigEnsayo, Simulacion
from aco_gemelo.mundo import mundo_aleatorio
from aco_gemelo.canal.canal import CanalMemoria
C = dict(tau0=0.0, tau_max=1.0, unidad_deposito=1/255)
def mundo(s):
    rng = random.Random(s)
    while True:
        m = mundo_aleatorio(rng, **C)
        if m.largo_optimo() >= 4: return m
h = hashlib.sha256()
for s in (0, -1, 5, -7, 123):
    for modo in Modo:
        r = Simulacion(mundo(s), ConfigEnsayo(semilla=s, rho=0.01, salida_cada=1, p_perdida=0.3, retardo=(0, 3), registrar=True,
                       madre=ConfigMadre(modo=modo))).correr()
        h.update(repr((r.motivo, r.ticks_total, r.verificada, r.largo_verificado, r.trafico, r.memoria_madre, r.conocimiento, r.serie)).encode())
    h.update(repr([CanalMemoria(semilla=s)._rng_de(i).random() for i in range(10)]).encode())
print(h.hexdigest())
