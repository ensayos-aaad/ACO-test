"""Pruebas del artefacto 15: el notebook de análisis se ejecuta completo y responde sus preguntas.

Desde el bloque D (PLAN-MEJORAS.md) también explica cómo funciona un ensayo, con figuras que salen del código y
los datos del repositorio (D7).
"""
from pathlib import Path

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

CARPETA = Path(__file__).parent.parent / "notebooks"
FIGURAS = ["f1_convergencia_por_modo.png", "f2_tiempo_por_modo.png", "f3_costo_de_red.png",
           "f4_umbral_de_rescate.png",
           # bloque D
           "f5_un_ensayo.png", "f6_feromona_y_trazos.png", "f7_conocimiento_de_la_madre.png",
           "f7_conocimiento_de_la_madre.gif", "f8_tamano_de_mensajes.png", "f9_trafico_por_familia.png"]


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
    for figura in FIGURAS:  # se borran para comprobar que el notebook las vuelve a generar
        (CARPETA / "figuras" / figura).unlink(missing_ok=True)
    ExecutePreprocessor(timeout=600, kernel_name="python3").preprocess(nb, {"metadata": {"path": str(CARPETA)}})
    texto = _salidas(nb)
    # criterio 1: gráficas comparativas (y, desde el bloque D, las que explican un ensayo)
    for figura in FIGURAS:
        assert (CARPETA / "figuras" / figura).stat().st_size > 10_000, figura
    assert sum("image/png" in s.get("data", {}) for c in nb.cells for s in c.get("outputs", [])) == 9
    # criterio 2: prueba estadística de la varianza con y sin rescate
    assert "p_varianza" in texto and "p_varianza_bonferroni" in texto
    assert "Hipótesis de resumen.pdf" in texto
    assert ("APOYADA" in texto) != ("NO apoyada" in texto)  # una sola conclusión
    assert "modos: 240 ensayos · rescate: 240 ensayos" in texto
    # bloque D: un ensayo comentado, el mapa de la madre y el costo de red
    assert "Sin madre:" in texto and "Con madre (difusión):" in texto and "fase colonia" in texto
    assert "Conocimiento final" in texto
    assert "no caben en un paquete ESP-NOW" in texto
    # D6: cada figura lleva su "Qué mirar", y hay glosario
    fuentes = [c.source for c in nb.cells]
    assert sum(f.startswith("**Qué mirar.**") for f in fuentes) == 9
    assert any("### Glosario" in f for f in fuentes)
