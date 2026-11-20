# P6: con retardo, la lectura final (B4) cambia 'conocimiento' y el ultimo cuadro de mapa_madre no la refleja.
import random
from aco_gemelo.madre import ConfigMadre, Modo
from aco_gemelo.motor import ConfigEnsayo, Simulacion
from aco_gemelo.mundo import mundo_l
C = dict(tau0=0.0, tau_max=1.0, unidad_deposito=1/255)
def mundo(s):
    rng = random.Random(s)
    while True:
        m = mundo_l(rng, **C)
        if m.largo_optimo() >= 4: return m
def desde_cuadro(m, cuadro):
    con, obs = cuadro
    ok = 0
    for y in range(m.alto):
        for x in range(m.ancho):
            b = 1 << (y * m.ancho + x)
            ok += bool(con & b) and bool(obs & b) == ((x, y) in m.obstaculos)
    return ok / (m.ancho * m.alto)
tot = desal = 0; ej = None
for modo in (Modo.DIFUSION, Modo.RESCATE):
    for s in range(15):
        m = mundo(s)
        sim = Simulacion(m, ConfigEnsayo(semilla=s, rho=0.0, registrar=True, retardo=(2, 4), madre=ConfigMadre(modo=modo)))
        r = sim.correr()
        ult = desde_cuadro(m, r.mapa_madre[-1])
        tot += 1
        if round(ult, 4) != round(r.conocimiento, 4):
            desal += 1
            ej = ej or (modo.name, s, r.conocimiento, ult, bin(r.mapa_madre[-1][0]).count("1"), len(sim.madre.conocidas))
print(f"ensayos con conocimiento != ultimo cuadro de mapa_madre: {desal}/{tot}")
print("ejemplo (modo, semilla, conocimiento, conocimiento_ultimo_cuadro, celdas_ultimo_cuadro, celdas_madre_al_cerrar):", ej)
# sin retardo: control
r = Simulacion(mundo(0), ConfigEnsayo(semilla=0, rho=0.0, registrar=True, madre=ConfigMadre(modo=Modo.DIFUSION))).correr()
print("control sin retardo (DIFUSION s=0): igual =", round(desde_cuadro(mundo(0), r.mapa_madre[-1]), 4) == round(r.conocimiento, 4))
