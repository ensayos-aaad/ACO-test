# Mutante 3: sin texto para abortado.
import aco_gemelo.visual.visual as v
orig = v._texto
def _texto(resultado, cuadro, final):
    if final and resultado.motivo == "abortado":
        raise KeyError("abortado")
    return orig(resultado, cuadro, final)
v._texto = _texto
