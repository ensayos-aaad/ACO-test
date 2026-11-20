# Independencia de generadores: canal por emisor vs agentes, mundo y otros emisores.
import random
from aco_gemelo.canal.canal import CanalMemoria
from aco_gemelo.protocolo.codec import ID_MADRE, ID_MUNDO
N = 3000
semillas = [0, 1, -1, -2, 7, 255, 256, -256, 65535, 2**31, -(2**31), 10**12]
fallos = 0
for s in semillas:
    canal = CanalMemoria(semilla=s)
    gens = {}
    for src in (ID_MADRE, *range(1, 9), ID_MUNDO, 0xFF):
        r = canal._rng_de(src); gens[f"canal{src}"] = [r.random() for _ in range(N)]
    for i in range(1, 9):
        r = random.Random(s * 256 + i); gens[f"agente{i}"] = [r.random() for _ in range(N)]
    r = random.Random(s); gens["mundo"] = [r.random() for _ in range(N)]
    nombres = list(gens); conj = {k: set(v) for k, v in gens.items()}
    for a in range(len(nombres)):
        for b in range(a + 1, len(nombres)):
            comun = conj[nombres[a]] & conj[nombres[b]]
            if comun and (nombres[a].startswith("canal") or nombres[b].startswith("canal")):
                fallos += 1; print("COMPARTEN", s, nombres[a], nombres[b], len(comun))
    # estado inicial idéntico entre canal y agente/mundo
    for src in range(0, 9):
        st = CanalMemoria(semilla=s)._rng_de(src).getstate()
        if st == random.Random(s * 256 + src).getstate() or st == random.Random(s).getstate():
            fallos += 1; print("ESTADO IGUAL", s, src)
print("semillas", semillas, "-> pares canal-otro que comparten valores (3000 draws c/u):", fallos)
# Además: canal entre semillas distintas de un mismo emisor (p.ej. -1 vs 1, abs igual)
a = CanalMemoria(semilla=1)._rng_de(1).random(); b = CanalMemoria(semilla=-1)._rng_de(1).random()
print("canal semilla 1 vs -1, emisor 1, distintos:", a != b)
print("contraste (preexistente, fuera del canal): Random(-3)==Random(3):", random.Random(-3).random()==random.Random(3).random())
