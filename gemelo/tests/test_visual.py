"""Pruebas del artefacto 11: visualización (PNG del estado final y animación)."""
import random

import pytest
from matplotlib import animation
from PIL import Image

from aco_gemelo.__main__ import main
from aco_gemelo.madre import ConfigMadre, Modo
from aco_gemelo.motor import ConfigEnsayo, Simulacion
from aco_gemelo.mundo import mundo_l
from aco_gemelo.visual import COLORES_HEX, animar, cuadros, png_final

CUADRICULA = dict(tau0=0.0, tau_max=1.0, unidad_deposito=1 / 255)


def ensayo(semilla=3, modo=Modo.PISTA_DE_BAILE, registrar=True):
    rng = random.Random(semilla)
    mundo = mundo_l(rng, **CUADRICULA)
    while mundo.largo_optimo() < 4:
        mundo = mundo_l(rng, **CUADRICULA)
    cfg = ConfigEnsayo(semilla=semilla, rho=0.0, registrar=registrar, madre=ConfigMadre(modo=modo))
    return mundo, Simulacion(mundo, cfg).correr()


def pixeles_de(imagen, color_hex, tolerancia=12):
    """Cuántos píxeles tienen (casi) ese color."""
    objetivo = tuple(int(color_hex[i:i + 2], 16) for i in (1, 3, 5))
    return sum(
        n for n, rgb in imagen.convert("RGB").getcolors(1 << 20)
        if all(abs(c - o) <= tolerancia for c, o in zip(rgb, objetivo))
    )


# ---------------------------------------------------------------- lo que se registra para dibujar


def test_la_feromona_se_registra_tick_a_tick():
    mundo, r = ensayo()
    assert len(r.feromona) == len(r.serie) == r.ticks_total
    assert len(r.feromona[0]) == mundo.ancho * mundo.alto
    final = [mundo.feromona((x, y)) for y in range(mundo.alto) for x in range(mundo.ancho)]
    assert r.feromona[-1] == pytest.approx(final)
    assert r.ruta_verificada[0] == mundo.inicio and r.ruta_verificada[-1] == mundo.meta


def test_los_cuadros_reconstruyen_el_ensayo():
    mundo, r = ensayo()
    lista = cuadros(mundo, r, 6)
    assert [c.tick for c in lista] == list(range(r.ticks_total + 1))
    assert set(lista[0].agentes.values()) == {mundo.inicio} and len(lista[0].agentes) == 6
    assert sum(lista[0].feromona) == 0
    for t, cuadro in enumerate(lista[1:]):
        assert cuadro.feromona == r.feromona[t]
    # La verificadora aparece en el cuadro siguiente al tick en que la última se asentó.
    con_verificadora = [c.tick for c in lista if c.verificadora is not None]
    assert con_verificadora[0] == r.ticks_asentadas + 1
    final = lista[-1]
    assert set(final.agentes.values()) == {mundo.meta} and final.asentadas == 6
    assert final.verificadora == mundo.meta  # llegó
    # Las posiciones coinciden con el historial del motor.
    for t, i, celda in r.historial:
        if i <= 6:
            assert lista[t + 1].agentes[i] == celda


def test_sin_registrar_no_se_puede_dibujar():
    mundo, r = ensayo(registrar=False)
    with pytest.raises(ValueError):
        cuadros(mundo, r, 6)


# ---------------------------------------------------------------- criterio 1: PNG del estado final


def test_png_del_estado_final(tmp_path):
    mundo, r = ensayo()
    ruta = png_final(mundo, r, 6, tmp_path / "sub" / "final.png")
    imagen = Image.open(ruta)
    assert imagen.format == "PNG" and imagen.size == (572, 704)
    for elemento in ("inicio", "meta", "obstaculo", "agente", "verificadora", "madre"):
        assert pixeles_de(imagen, COLORES_HEX[elemento]) > 20, elemento


def test_png_sin_madre_no_dibuja_la_madre(tmp_path):
    mundo, r = ensayo(modo=Modo.AUSENTE)
    imagen = Image.open(png_final(mundo, r, 6, tmp_path / "a.png"))
    arriba = imagen.crop((0, 0, imagen.width, 120))
    assert pixeles_de(arriba, COLORES_HEX["madre"]) == 0
    assert pixeles_de(imagen, COLORES_HEX["inicio"]) > 20


def test_png_reproducible(tmp_path):
    mundo, r = ensayo()
    a = png_final(mundo, r, 6, tmp_path / "a.png")
    mundo2, r2 = ensayo()
    b = png_final(mundo2, r2, 6, tmp_path / "b.png")
    assert list(Image.open(a).getdata()) == list(Image.open(b).getdata())


# ---------------------------------------------------------------- criterio 2: animación GIF / MP4


def test_animacion_gif_un_cuadro_por_tick(tmp_path):
    mundo, r = ensayo()
    gif = Image.open(animar(mundo, r, 6, tmp_path / "e.gif"))
    assert gif.format == "GIF" and gif.n_frames == r.ticks_total + 1


def test_animacion_gif_saltando_cuadros_conserva_el_final(tmp_path):
    mundo, r = ensayo()
    gif = Image.open(animar(mundo, r, 6, tmp_path / "e.gif", cada=10))
    assert gif.n_frames == len(range(0, r.ticks_total + 1, 10)) + (r.ticks_total % 10 != 0)


@pytest.mark.skipif(not animation.writers.is_available("ffmpeg"), reason="ffmpeg no está instalado")
def test_animacion_mp4(tmp_path):
    mundo, r = ensayo()
    ruta = animar(mundo, r, 6, tmp_path / "e.mp4", cada=5)
    datos = ruta.read_bytes()
    assert len(datos) > 1000 and datos[4:8] == b"ftyp"  # cabecera de un MP4


def test_formato_de_animacion_no_valido(tmp_path):
    mundo, r = ensayo()
    with pytest.raises(ValueError):
        animar(mundo, r, 6, tmp_path / "e.avi")


def test_la_linea_de_comandos_genera_png_y_gif(tmp_path, capsys):
    png, gif = tmp_path / "f.png", tmp_path / "e.gif"
    config = tmp_path / "c.yaml"  # un ensayo corto (1 viaje) para que la animación sea rápida
    config.write_text("ensayo: {rho: 0.0}\n", encoding="utf-8")
    assert main(["run", "--config", str(config), "--semilla", "3",
                 "--png", str(png), "--animacion", str(gif), "--fps", "12"]) == 0
    salida = capsys.readouterr().out
    assert f"PNG: {png}" in salida and f"Animación: {gif}" in salida
    assert Image.open(png).format == "PNG" and Image.open(gif).n_frames > 10
