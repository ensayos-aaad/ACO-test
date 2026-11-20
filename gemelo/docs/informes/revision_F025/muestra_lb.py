import sys, csv, io
sys.path.insert(0, r"D:\experimento\ACO-test\gemelo\experimentos\linea_base_f023")
import linea_base as lb
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
if __name__ == "__main__":
    conds = [c for c in lb.condiciones() if c[1] != "ideal"]
    trab = [(n, c, m, mo, d, s, "determinista") for n, c, m, mo, d in conds for s in (0, 7, 13, 22, 29)]
    with ProcessPoolExecutor(4) as g:
        filas = list(g.map(lb.ensayo, trab))
    buf = io.StringIO(); w = csv.DictWriter(buf, fieldnames=list(filas[0])); w.writeheader(); w.writerows(filas)
    nuevo = pd.read_csv(io.StringIO(buf.getvalue()), dtype=str, keep_default_na=False)
    pub = pd.read_csv(r"D:\experimento\ACO-test\gemelo\experimentos\linea_base_f023\datos_despues_n1\determinista.csv", dtype=str, keep_default_na=False)
    m = nuevo.merge(pub, on=["condicion", "semilla"], suffixes=("", "_p"))
    cols = [c for c in nuevo.columns if c not in ("condicion", "semilla")]
    print("filas recalculadas", len(m), "distintas de datos_despues_n1:", sum(any(r[c] != r[c+"_p"] for c in cols) for _, r in m.iterrows()))
