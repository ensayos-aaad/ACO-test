import sys, pandas as pd
from scipy.stats import fisher_exact, mannwhitneyu
a = pd.read_csv(sys.argv[1]); b = pd.read_csv(sys.argv[2])
k = ["canal", "escenario", "modo_madre", "semilla"]
m = a.merge(b, on=k, suffixes=("_antes", "_despues"))
cols = ["motivo", "ticks_asentadas", "ticks_total", "verificada", "conocimiento", "bytes_totales"]
for canal, g in m.groupby("canal"):
    dif = sum(any(str(r[c+"_antes"]) != str(r[c+"_despues"]) for c in cols) for _, r in g.iterrows())
    print(f"{canal}: {dif}/{len(g)} ensayos distintos")
print()
print("canal escenario modo | verif antes/despues (p Fisher) | ticks_total mediana antes/despues (p MW)")
for (canal, esc, modo), g in m[m.canal != "ideal"].groupby(["canal", "escenario", "modo_madre"]):
    va, vd = g.verificada_antes.sum(), g.verificada_despues.sum(); n = len(g)
    pf = fisher_exact([[va, n-va], [vd, n-vd]])[1]
    ta, td = g.ticks_total_antes, g.ticks_total_despues
    pm = mannwhitneyu(ta, td)[1] if (ta != td).any() else 1.0
    print(f"{canal:8s} {esc:9s} {modo:14s} | {va:2d}/{vd:2d} (p={pf:.2f}) | {ta.median():6.0f}/{td.median():6.0f} (p={pm:.2f})")
