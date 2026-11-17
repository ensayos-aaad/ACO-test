"""Pruebas del artefacto 15: el notebook de análisis se ejecuta completo y responde sus preguntas."""
from pathlib import Path

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

CARPETA = Path(__file__).parent.parent / "notebooks"
FIGURAS = ["f1_convergencia_por_modo.png", "f2_tiempo_por_modo.png", "f3_costo_de_red.png",
           "f4_umbral_de_rescate.png"]


def _salidas(nb):
    textos = []
    for celda in nb.cells:
        for salida in celda.get("outputs", []):
            if salida.get("output_type") == "stream":
                textos.append(salida["text"])
            elif "data" in salida and "text/plain" in salida["data"]:
                textos.append(salida["data"]["text/plain"])
    return "\n".join(textos)


def test_el_notebook_se_ejecuta_y_responde():
    nb = nbformat.read(CARPETA / "analisis.ipynb", as_version=4)
    ExecutePreprocessor(timeout=300, kernel_name="python3").preprocess(nb, {"metadata": {"path": str(CARPETA)}})
    texto = _salidas(nb)
    # criterio 1: gráficas comparativas
    for figura in FIGURAS:
        assert (CARPETA / "figuras" / figura).stat().st_size > 10_000, figura
    assert sum("image/png" in s.get("data", {}) for c in nb.cells for s in c.get("outputs", [])) == 4
    # criterio 2: prueba estadística de la varianza con y sin rescate
    assert "p_varianza" in texto and "p_varianza_bonferroni" in texto
    assert "Hipótesis de resumen.pdf" in texto
    assert ("APOYADA" in texto) != ("NO apoyada" in texto)  # una sola conclusión
    assert "modos: 240 ensayos · rescate: 240 ensayos" in texto
