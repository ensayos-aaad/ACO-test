import pandas as pd, numpy as np
from pathlib import Path
from scipy.stats import fisher_exact, levene
D = Path(r"d:/experimento/ACO-test/gemelo/experimentos/datos")
def leer(p): return pd.concat([pd.read_csv(f) for f in sorted((D/p).glob("*.csv")) if f.name!="resumen.csv"], ignore_index=True)
m = leer("modos"); r = leer("rescate")
print("MODOS")
for esc in ("L","aleatorio"):
    a = m[(m.escenario==esc)&(m.modo=="ausente")]
    for modo in ("ausente","pista_de_baile","rescate","difusion"):
        c = m[(m.escenario==esc)&(m.modo==modo)]
        v=int(c.verificada.sum()); va=int(a.verificada.sum())
        pf = fisher_exact([[v,30-v],[va,30-va]]).pvalue
        pb = levene(a.ticks_asentadas.dropna(), c.ticks_asentadas.dropna(), center="median").pvalue
        print(esc, modo, f"{v}/30 pF={pf:.3f}({min(1,pf*6):.2f}) media={c.ticks_asentadas.mean():.1f} sd0={c.ticks_asentadas.std(ddof=0):.1f} sd1={c.ticks_asentadas.std(ddof=1):.1f} pBF={pb:.3f}({min(1,pb*6):.2f})",
              f"bA={c.bytes_agente_madre.mean():.1f} bM={c.bytes_madre_agente.mean():.1f} msgM={c.mensajes_madre_agente.mean():.1f}",
              "asent", int(c.asentadas.sum()), "motivos", dict(c.motivo.value_counts()),
              "recluta", c.recluta_enviados.sum(), "hered", c.rutas_heredadas.sum(), "difund", c.rutas_difundidas.sum(), c.mapas_difundidos.sum(),
              "resc", c.rescates_enviados.sum(), "memmax", c.memoria_madre_max.max(),
              "btot", int(c.bytes_totales.min()), int(c.bytes_totales.max()), round(c.bytes_totales.mean()),
              "frac0 min", round((c.bytes_mundo_agente/c.bytes_totales).min(),3),
              "msgs0", int(c.mensajes_mundo_agente.mean()), "b_madre_tot", round((c.bytes_agente_madre+c.bytes_madre_agente).mean()),
              "ticks_total_media", round(c.ticks_total.mean()), "bytes_aa", c.bytes_agente_agente.sum())
print("frac0 global min/max:", (m.bytes_mundo_agente/m.bytes_totales).min(), (m.bytes_mundo_agente/m.bytes_totales).max())
print("frac0 por condición (media):")
g = m.groupby(["escenario","modo"])[["bytes_mundo_agente","bytes_totales"]].mean(); print((g.bytes_mundo_agente/g.bytes_totales).round(3))
print("bytes_totales range (medias por cond):", m.groupby(["escenario","modo"]).bytes_totales.mean().round())
print("RESCATE")
for esc in ("L","aleatorio"):
    a = m[(m.escenario==esc)&(m.modo=="ausente")]; va=int(a.verificada.sum())
    for u in (0.5,0.8,0.95,1.0):
        c = r[(r.escenario==esc)&np.isclose(r.umbral_rescate,u)]
        v=int(c.verificada.sum()); pf=fisher_exact([[v,30-v],[va,30-va]]).pvalue
        print(esc,u,v,f"pF={pf:.3f}({min(1,pf*6):.3f}) media={c.ticks_asentadas.mean():.1f} sd0={c.ticks_asentadas.std(ddof=0):.1f} sd1={c.ticks_asentadas.std(ddof=1):.1f}",
              "env/usado/ya_tiene/ya_llego", c.rescates_enviados.sum(), c.rescate_usado.sum(), c.rescate_ya_tiene_ruta.sum(), c.rescate_ya_llego.sum(),
              "otros", c[["rescate_fallida","rescate_ocupada","rescate_no_cabe","rescate_otro_nido","rescate_verificadora","rescate_sin_clasificar"]].sum().to_dict(),
              "bM", round(c.bytes_madre_agente.mean(),1), "msgsM", round(c.mensajes_madre_agente.mean(),2), "btot", round(c.bytes_totales.mean()))
print("rescate_verificadora total r/m:", r.rescate_verificadora.sum(), m.rescate_verificadora.sum())
print("ausente sd L/al ddof0:", [round(m[(m.escenario==e)&(m.modo=='ausente')].ticks_asentadas.std(ddof=0),1) for e in ('L','aleatorio')])
