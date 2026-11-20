# P7: delta_t > 255 con madre.
import traceback
from aco_gemelo.config import crear_mundo, config_ensayo
from aco_gemelo.motor import Simulacion
for modo in ("ausente", "pista_de_baile"):
    for dt in (255, 256, 300):
        d = {"semilla": 1, "madre": {"modo": modo, "delta_t": dt}}
        try:
            cfg = config_ensayo(d)
        except Exception as e:
            print(modo, dt, "config_ensayo ->", type(e).__name__, e); continue
        try:
            r = Simulacion(crear_mundo(d), cfg).correr()
            print(modo, dt, "-> OK motivo", r.motivo)
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            loc = [f"{f.filename.split('aco_gemelo')[-1]}:{f.lineno}" for f in tb if "aco_gemelo" in f.filename]
            print(modo, dt, "->", type(e).__name__, e, "|", " <- ".join(reversed(loc[-3:])))
