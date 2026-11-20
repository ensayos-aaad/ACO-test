# Mutante 6: conocimiento medido despues de la lectura final de B4 (como antes).
import aco_gemelo.motor.simulacion as s
orig = s.Simulacion._resultado
def _resultado(self):
    r = orig(self)
    r.conocimiento = self._conocimiento()
    return r
s.Simulacion._resultado = _resultado
