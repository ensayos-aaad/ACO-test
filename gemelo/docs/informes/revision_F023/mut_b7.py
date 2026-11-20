# Mutante B7: la madre procesa en orden de llegada (sin el sorted de Madre.leer).
import aco_gemelo.madre.madre as mm
def leer(self):
    mensajes = self.canal.recibir(mm.ID_MADRE)
    if self.config.modo is mm.Modo.AUSENTE:
        return
    for msg in mensajes:
        self._escuchar(msg)
    self._ajustar_memoria()
    self.memoria_max = max(self.memoria_max, self.memoria_usada())
mm.Madre.leer = leer
