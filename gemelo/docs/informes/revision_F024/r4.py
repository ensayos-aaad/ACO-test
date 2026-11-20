from aco_gemelo.config import crear_mundo, config_ensayo
from aco_gemelo.motor import Simulacion
base = {"escenario": "personalizado", "ancho": 5, "alto": 4, "obstaculos": [[2, 0], [2, 1], [2, 2]], "inicio": [0, 0], "meta": [4, 0]}
d = {"mundo": base, "madre": {"modo": "pista_de_baile"}}
m = crear_mundo(d); r = Simulacion(m, config_ensayo(d)).correr()
print("ejemplo de default.yaml: optima", m.largo_optimo(), "motivo", r.motivo)
for caso in ({"escenario": "L", "inicio": [7, 7]}, {"escenario": "L", "obstaculos": []},
             {**base, "inicio": [2, 2], "meta": [2, 2]}, {**base, "inicio": [0, 0], "meta": [0, 0], "obstaculos": []},
             {**base, "inicio": [9, 9]}):
    try:
        crear_mundo({"mundo": caso}, semilla=1); print(caso, "-> aceptado")
    except Exception as e:
        print({k: caso[k] for k in caso if k in ("escenario","inicio","meta","obstaculos")}, "->", type(e).__name__, e)
