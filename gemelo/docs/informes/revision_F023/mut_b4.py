# Mutante B4: sin la lectura final de la madre.
import aco_gemelo.madre.madre as mm, aco_gemelo.motor.simulacion as s
orig = s.Simulacion._resultado
def _resultado(self):
    leer = self.madre.leer
    self.madre.leer = lambda: None
    try:
        return orig(self)
    finally:
        self.madre.leer = leer
s.Simulacion._resultado = _resultado
