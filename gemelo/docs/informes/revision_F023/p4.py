# P4: escenario personalizado con inicio = meta.
import traceback
from aco_gemelo.config import crear_mundo, config_ensayo
from aco_gemelo.madre import ConfigMadre, Modo
from aco_gemelo.motor import Simulacion
datos = {"mundo": {"escenario": "personalizado", "ancho": 5, "alto": 5, "obstaculos": [],
                   "inicio": [2, 2], "meta": [2, 2]}}
try:
    m = crear_mundo(datos)
    print("crear_mundo acepta inicio = meta; largo_optimo =", m.largo_optimo())
except ValueError as e:
    print("crear_mundo rechaza:", e); raise SystemExit
for modo in ("ausente", "pista_de_baile", "rescate", "difusion"):
    d = dict(datos, madre={"modo": modo})
    try:
        r = Simulacion(crear_mundo(d), config_ensayo(d)).correr()
        print(modo, "-> motivo", r.motivo, "ticks_total", r.ticks_total, "largo_verificado", r.largo_verificado)
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)[-1]
        print(modo, "->", type(e).__name__, e, "en", tb.filename.split("aco_gemelo")[-1], "linea", tb.lineno)
# otros escenarios: claves de personalizado se ignoran sin aviso
d = {"mundo": {"escenario": "L", "obstaculos": [[0, 0]], "inicio": [7, 7], "meta": [0, 1]}}
m = crear_mundo(d, semilla=1)
print("escenario L con obstaculos/inicio/meta dados -> sin error; inicio", m.inicio, "meta", m.meta, "(0,0) obstaculo?", (0, 0) in m.obstaculos)
