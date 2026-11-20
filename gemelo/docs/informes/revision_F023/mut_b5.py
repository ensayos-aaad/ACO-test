# Mutante B5: acciones en orden de llegada (sin ordenar), como antes de B5.
import aco_gemelo.motor.simulacion as s
from aco_gemelo.protocolo import nombre_de
def aplicar_acciones(self, ahora):
    atendidos = set()
    for msg in self.canal.recibir(s.ID_MUNDO):
        if nombre_de(msg) != "ACCION":
            continue
        i = msg["src"]
        self.pos[i], self.ok[i] = self.mundo.aplicar_accion(self.pos[i], msg["accion"], msg["dir"], msg["deposito"])
        self.bloqueadas += not self.ok[i]
        if self.registrar:
            self.historial.append((ahora, i, self.pos[i]))
        atendidos.add(i)
    return atendidos
s.ActorMundo.aplicar_acciones = aplicar_acciones
