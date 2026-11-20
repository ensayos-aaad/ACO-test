# P3 natural: callejon a la izquierda del nido; con 1 agente que entra al callejon -> FALLIDA -> abortado.
import sys, traceback
from aco_gemelo.config import crear_mundo
from aco_gemelo.madre import ConfigMadre, Modo
from aco_gemelo.motor import ConfigEnsayo, Simulacion
from aco_gemelo.visual import png_final
S = sys.argv[1]
datos = {"mundo": {"escenario": "personalizado", "ancho": 4, "alto": 1, "obstaculos": [],
                   "inicio": [1, 0], "meta": [3, 0]}}
for semilla in range(20):
    m = crear_mundo(datos)
    r = Simulacion(m, ConfigEnsayo(semilla=semilla, n_agentes=1, rho=0.0, registrar=True,
                                   madre=ConfigMadre(modo=Modo.AUSENTE))).correr()
    if r.motivo == "abortado":
        print("semilla", semilla, "motivo", r.motivo, "ticks_total", r.ticks_total)
        try:
            png_final(m, r, 1, S + "/abortado.png")
            print("png_final OK")
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)[-1]
            print("png_final ->", type(e).__name__, repr(e), "en visual.py linea", tb.lineno)
        break
else:
    print("ninguna semilla aborto")
