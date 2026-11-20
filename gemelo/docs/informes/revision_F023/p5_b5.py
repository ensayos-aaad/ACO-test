# Prueba propuesta para B5: ACCION que llegan desordenadas (3, 1, 2) se aplican en orden de id.
import sys
if len(sys.argv) > 1: import mut_b5  # noqa: aplica el mutante
from aco_gemelo.canal import CanalMemoria
from aco_gemelo.motor.simulacion import ActorMundo
from aco_gemelo.mundo import Mundo
from aco_gemelo.protocolo import ID_MUNDO, Contexto, crear
m = Mundo(4, 4, [], inicio=(0, 0), meta=(3, 3), tau0=0.0, tau_max=1.0)
canal = CanalMemoria(Contexto(4, 4, 8))
mundo = ActorMundo(m, canal, 0.0, True)
for i in (1, 2, 3):
    canal.registrar(i); mundo.agregar(i)
for i in (3, 1, 2):
    canal.enviar(crear("ACCION", src=i, dst=ID_MUNDO, tick=0, accion=0, dir=0, deposito=0))
mundo.aplicar_acciones(0)
print("orden aplicado:", [i for _, i, _ in mundo.historial])
