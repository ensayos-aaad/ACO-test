"""Apoyo para las pruebas: un bucle mínimo que hace de mundo (lo reemplazará el motor)."""
from aco_gemelo.canal import CanalMemoria
from aco_gemelo.protocolo import ID_MADRE, ID_MUNDO, celda_a_byte, crear, nombre_de


class Banco:
    """Conecta agentes con un mundo: envía percepciones, aplica acciones y lleva la cuenta."""

    def __init__(self, mundo, rho=0.0, **canal_kwargs):
        self.mundo = mundo
        self.rho = rho
        self.pos = {}
        self.ok = {}
        self.bloqueadas = 0  # acciones que el mundo rechazó
        self.historial = []  # (tick, id, celda)
        self.a_madre = []  # mensajes que recibió la madre
        self.canal = CanalMemoria(posicion=self.pos.get, **canal_kwargs)
        self.canal.registrar(ID_MUNDO)
        self.canal.registrar(ID_MADRE)
        self.agentes = []
        self.tick = 0

    def agregar(self, agente):
        self.agentes.append(agente)
        self.pos[agente.id] = self.mundo.inicio
        self.ok[agente.id] = True
        return agente

    def correr(self, ticks, hasta=None):
        """Avanza ``ticks`` ticks, o hasta que ``hasta()`` sea verdadero. Devuelve el tick final."""
        for _ in range(ticks):
            if hasta is not None and hasta():
                break
            t = self.tick
            self.canal.avanzar(t)
            for a in self.agentes:
                otras = [c for i, c in self.pos.items() if i != a.id]
                self.canal.enviar(crear(
                    "PERCEPCION", src=ID_MUNDO, dst=a.id, tick=t % 65536,
                    pos=celda_a_byte(self.pos[a.id]), ok=int(self.ok[a.id]),
                    vecinas=self.mundo.percibir(self.pos[a.id], otras)))
            for a in self.agentes:
                a.paso(t)
            for msg in self.canal.recibir(ID_MUNDO):
                assert nombre_de(msg) == "ACCION"
                i = msg["src"]
                self.pos[i], self.ok[i] = self.mundo.aplicar_accion(
                    self.pos[i], msg["accion"], msg["dir"], msg["deposito"])
                self.bloqueadas += not self.ok[i]
                self.historial.append((t, i, self.pos[i]))
            self.a_madre.extend(self.canal.recibir(ID_MADRE))
            self.mundo.evaporar(self.rho)
            self.tick += 1
        return self.tick
