import pandas as pd, numpy as np, glob, os
from scipy.stats import fisher_exact, levene, chi2_contingency
from statsmodels.stats.proportion import proportion_confint
R="experimentos/datos"
def load(base,pat):
    return pd.read_csv(f"{base}/{pat}.csv")
out=[]
for tag,base in (("DESPUES",R),("ANTES",R+"/_antes_F020")):
    print("=====",tag)
    rows=[];var=[]
    for esc in ("L","aleatorio"):
        aus=load(f"{base}/modos",f"escenario-{esc}__modo-ausente")
        for u in (0.8,0.95,1.0):
            r=load(f"{base}/rescate",f"escenario-{esc}__modo-rescate__umbral_rescate-{u}")
            a,b=int(r.verificada.sum()),int(aus.verificada.sum())
            p=fisher_exact([[a,30-a],[b,30-b]])[1]
            lo,hi=proportion_confint(a,30,method="wilson")
            stat,pv=levene(r.ticks_asentadas.dropna(),aus.ticks_asentadas.dropna(),center="median")
            rows.append((esc,u,a,b,round(lo,2),round(hi,2),p,min(1,p*6)))
            var.append((esc,u,round(r.ticks_asentadas.std(),1),round(aus.ticks_asentadas.std(),1),pv,min(1,pv*6)))
    print(pd.DataFrame(rows,columns="mundo umbral resc_ver aus_ver IC_lo IC_hi p p_bonf".split()).round(4).to_string())
    print(pd.DataFrame(var,columns="mundo umbral sd_resc sd_aus p p_bonf".split()).round(4).to_string())
    if tag=="DESPUES":
        print("--- mecanismos")
        cols="rescates_enviados rescate_usado rescate_ya_llego rescate_ocupada rescate_no_cabe rescate_otro_nido rescate_verificadora".split()
        for f in sorted(glob.glob(f"{base}/rescate/*.csv"))+sorted(glob.glob(f"{base}/modos/*.csv")):
            if "resumen" in f: continue
            d=pd.read_csv(f); print(os.path.basename(f)[:-4], d[cols].sum().to_dict(), "recluta",d.recluta_enviados.sum(),"heredadas",d.rutas_heredadas.sum())
