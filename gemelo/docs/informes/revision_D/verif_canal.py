import pandas as pd
from pathlib import Path
B = Path(r"d:/experimento/ACO-test/gemelo/experimentos/linea_base_f023")
for v in ("datos", "datos_despues_n1"):
    d = pd.read_csv(B/v/"diferencias.csv")
    d["canal"] = d.condicion.str.extract(r"canal-(\w+)__")
    d["modo"] = d.condicion.str.extract(r"modo-(\w+)$")
    print(v); print(d.groupby("canal")[["sinc_a_vs_b","det_vs_sinc_a","det_vs_det_b","det_vs_F022"]].sum(min_count=1))
    if v == "datos": print(d[d.canal!="ideal"].groupby(["canal","modo"])["sinc_a_vs_b"].sum())
a = pd.read_csv(B/"datos"/"determinista.csv"); b = pd.read_csv(B/"datos_despues_n1"/"determinista.csv")
k = ["canal","escenario","modo_madre","semilla"]
m = a.merge(b, on=k, suffixes=("_a","_d"))
cols = ["motivo","ticks_asentadas","ticks_total","verificada","conocimiento","bytes_totales"]
for canal, g in m.groupby("canal"):
    dif = sum(any(str(r[c+"_a"]) != str(r[c+"_d"]) for c in cols) for _, r in g.iterrows())
    print(canal, len(g), "verif", g.verificada_a.sum(), "->", g.verificada_d.sum(), "ticks", round(g.ticks_total_a.mean(),1), "->", round(g.ticks_total_d.mean(),1),
          "bytes", round(g.bytes_totales_a.mean()), "->", round(g.bytes_totales_d.mean()), "cambian", dif)
