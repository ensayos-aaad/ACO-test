import sys, pandas as pd
d = sys.argv[1]
det = pd.read_csv(f"{d}/determinista.csv", dtype=str, keep_default_na=False)
a = pd.read_csv(f"{d}/sincronos_a.csv", dtype=str, keep_default_na=False)
b = pd.read_csv(f"{d}/sincronos_b.csv", dtype=str, keep_default_na=False)
db = pd.read_csv(f"{d}/determinista_b.csv", dtype=str, keep_default_na=False)
for c in ["ideal", "perdidas", "retardo"]:
    m = det.canal == c
    print(c, "A!=B", (a[m] != b[m]).any(axis=1).sum(), "det!=A", (det[m] != a[m]).any(axis=1).sum(), "/", m.sum())
k = ["condicion", "semilla"]
mm = det.merge(db, on=k, suffixes=("", "_b"))
cols = [c for c in det.columns if c not in k]
print("det vs det_b:", sum(any(r[c] != r[c+"_b"] for c in cols) for _, r in mm.iterrows()), "/", len(mm))
