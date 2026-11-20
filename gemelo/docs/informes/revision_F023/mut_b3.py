# Mutante B3: memoria_max = memoria final (no el maximo durante el ensayo).
import aco_gemelo.motor.simulacion as s
orig = s.Simulacion._resultado
def _resultado(self):
    r = orig(self)
    r.memoria_madre_max = r.memoria_madre
    return r
s.Simulacion._resultado = _resultado
