"""Imágenes y animaciones de un ensayo, con el mismo lenguaje visual del plano de ensayo
(``bosquejo/Plano de ensayo · ACO en edge.png``):

- obstáculos sombreados oscuros; celdas libres blancas;
- inicio: círculo rojo con "I"; meta: círculo morado con "F";
- agentes: pastillas verdes con tres puntos (un número si hay varias en la celda);
- verificadora: pastilla ámbar;
- feromona: verde, más intenso cuanto más feromona;
- madre: recuadro azul arriba, con el ojo, unido al mundo por un enlace punteado
  (solo si el modo no es "ausente").

Las imágenes se arman a partir del ``Resultado`` de un ensayo corrido con ``registrar: true``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # sin ventana: sirve en cualquier máquina y en las pruebas

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import animation  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle  # noqa: E402

from ..mundo import Mundo  # noqa: E402
from ..mundo.mundo import Celda  # noqa: E402

COLORES = {
    "fondo": "#f7f8fa",
    "rejilla": "#d5dbe3",
    "borde": "#2f3b4c",
    "obstaculo": "#334155",
    "inicio": "#dc2626",
    "meta": "#6d28d9",
    "agente": "#15803d",
    "verificadora": "#d97706",
    "feromona": "#16a34a",
    "madre": "#2563eb",
    "texto": "#1f2937",
    "suave": "#64748b",
}
_FEROMONA = LinearSegmentedColormap.from_list("feromona", ["#ffffff", "#bbf7d0", COLORES["feromona"]])


@dataclass
class Cuadro:
    """Estado del ensayo al empezar un tick."""

    tick: int
    agentes: dict[int, Celda]  #: posición de cada agente (sin la verificadora)
    verificadora: Celda | None
    feromona: list[float]  #: por filas
    asentadas: int


def cuadros(mundo: Mundo, resultado, n_agentes: int) -> list[Cuadro]:
    """Reconstruye el estado tick a tick a partir del historial y la feromona registrados.

    El cuadro ``t`` muestra el mundo al empezar el tick ``t``: el cuadro 0 es el inicio y el
    último es el estado final.
    """
    if not resultado.feromona:
        raise ValueError("El ensayo no se corrió con 'registrar': no hay nada que dibujar")
    id_verificadora = n_agentes + 1
    pos: dict[int, Celda] = {i: mundo.inicio for i in range(1, n_agentes + 1)}
    por_tick: dict[int, list[tuple[int, Celda]]] = {}
    for tick, i, celda in resultado.historial:
        por_tick.setdefault(tick, []).append((i, celda))
    vacia = [0.0] * (mundo.ancho * mundo.alto)
    salida = [Cuadro(0, dict(pos), None, vacia, 0)]
    for t in range(resultado.ticks_total):
        for i, celda in por_tick.get(t, []):
            pos[i] = celda
        asentadas = resultado.serie[t]["asentadas"] if t < len(resultado.serie) else 0
        salida.append(Cuadro(
            t + 1,
            {i: c for i, c in pos.items() if i != id_verificadora},
            pos.get(id_verificadora),
            resultado.feromona[t],
            asentadas,
        ))
    return salida


# ----------------------------------------------------------------------------- dibujo


def _pastilla(ax, celda: Celda, color: str, etiqueta: str | None, altura: float = 0.5) -> None:
    """Pastilla de agente centrada a ``altura`` dentro de la celda (0 arriba, 1 abajo)."""
    x, y = celda
    centro = y + altura
    ax.add_patch(FancyBboxPatch((x + 0.16, centro - 0.13), 0.68, 0.26,
                                boxstyle="round,pad=0,rounding_size=0.13",
                                facecolor="white", edgecolor=color, linewidth=1.6, zorder=6))
    for dx in (0.33, 0.5, 0.67):
        ax.add_patch(Circle((x + dx, centro), 0.05, color=color, zorder=7))
    if etiqueta:
        ax.text(x + 0.9, centro, etiqueta, fontsize=7, fontweight="bold", color=color,
                ha="center", va="center", zorder=8,
                bbox=dict(boxstyle="round,pad=0.12", facecolor="white", edgecolor="none"))


def _marca(ax, celda: Celda, color: str, letra: str) -> None:
    x, y = celda
    ax.add_patch(Circle((x + 0.5, y + 0.5), 0.26, color=color, zorder=4))
    ax.text(x + 0.5, y + 0.5, letra, color="white", fontsize=9, fontweight="bold",
            ha="center", va="center", zorder=5)


def _madre(fig, ax_mundo, modo: str) -> None:
    """Recuadro azul de la madre sobre el mundo, con el enlace punteado."""
    caja = fig.add_axes([0.28, 0.865, 0.44, 0.09])
    caja.set_axis_off()
    caja.set_xlim(0, 1)
    caja.set_ylim(0, 1)
    caja.add_patch(FancyBboxPatch((0.01, 0.05), 0.98, 0.9, boxstyle="round,pad=0,rounding_size=0.12",
                                  facecolor="white", edgecolor=COLORES["madre"], linewidth=1.5))
    caja.add_patch(Polygon([(0.06, 0.2), (0.18, 0.2), (0.12, 0.82)], closed=True, fill=False,
                           edgecolor=COLORES["madre"], linewidth=1.5))
    caja.add_patch(Circle((0.12, 0.38), 0.035, color=COLORES["madre"]))
    caja.text(0.24, 0.62, "Madre · control central", color=COLORES["madre"], fontsize=9,
              fontweight="bold", va="center")
    caja.text(0.24, 0.3, f"edge (RPi_server) · modo: {modo.replace('_', ' ')}",
              color=COLORES["texto"], fontsize=7.5, va="center")
    for x, texto in ((0.42, "actualiza cada Δt"), (0.58, "observa la colonia")):
        fig.add_artist(plt.Line2D([x, x], [0.865, 0.81], transform=fig.transFigure,
                                  color=COLORES["madre"], linestyle="--", linewidth=1.1))
    fig.text(0.41, 0.835, "actualiza cada Δt", color=COLORES["madre"], fontsize=6.5, ha="right")
    fig.text(0.59, 0.835, "observa la colonia", color=COLORES["madre"], fontsize=6.5, ha="left")


def _dibujar(fig, ax, mundo: Mundo, cuadro: Cuadro, fero_max: float, ruta: list[Celda] | None,
             texto: str) -> None:
    ax.clear()
    ax.set_xlim(0, mundo.ancho)
    ax.set_ylim(mundo.alto, 0)  # la fila 0 arriba, como en el plano
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for borde in ax.spines.values():
        borde.set_color(COLORES["borde"])
        borde.set_linewidth(1.8)
    valores = [[cuadro.feromona[y * mundo.ancho + x] / fero_max if fero_max else 0.0
                for x in range(mundo.ancho)] for y in range(mundo.alto)]
    ax.imshow(valores, cmap=_FEROMONA, vmin=0, vmax=1, extent=(0, mundo.ancho, mundo.alto, 0),
              interpolation="nearest", zorder=1)
    for x in range(mundo.ancho + 1):
        ax.axvline(x, color=COLORES["rejilla"], linewidth=0.8, zorder=2)
    for y in range(mundo.alto + 1):
        ax.axhline(y, color=COLORES["rejilla"], linewidth=0.8, zorder=2)
    for x, y in mundo.obstaculos:
        ax.add_patch(Rectangle((x, y), 1, 1, facecolor=COLORES["obstaculo"], hatch="///",
                               edgecolor="#64748b", linewidth=0, zorder=3))
    if ruta:
        xs = [c[0] + 0.5 for c in ruta]
        ys = [c[1] + 0.5 for c in ruta]
        ax.plot(xs, ys, color=COLORES["agente"], linestyle="--", linewidth=2.6, zorder=3.5)
    marcas = {mundo.inicio, mundo.meta}
    _marca(ax, mundo.inicio, COLORES["inicio"], "I")
    _marca(ax, mundo.meta, COLORES["meta"], "F")
    por_celda: dict[Celda, int] = {}
    for celda in cuadro.agentes.values():
        por_celda[celda] = por_celda.get(celda, 0) + 1
    v = cuadro.verificadora
    for celda, n in sorted(por_celda.items()):
        # En la celda del inicio o la meta, la pastilla baja para no tapar la letra;
        # si la verificadora comparte celda, cada una ocupa una mitad.
        altura = 0.82 if celda in marcas else (0.3 if celda == v else 0.5)
        _pastilla(ax, celda, COLORES["agente"], str(n) if n > 1 else None, altura)
    if v is not None:
        altura = 0.18 if v in marcas else (0.72 if v in por_celda else 0.5)
        _pastilla(ax, v, COLORES["verificadora"], "V", altura)
    ax.set_title(texto, fontsize=8.5, color=COLORES["texto"], pad=6)


def _leyenda(fig) -> None:
    elementos = [
        (Rectangle((0, 0), 1, 1, facecolor=COLORES["obstaculo"], hatch="///", edgecolor="#64748b"), "obstáculo"),
        (Circle((0, 0), 1, color=COLORES["inicio"]), "inicio (I)"),
        (Circle((0, 0), 1, color=COLORES["meta"]), "meta (F)"),
        (Rectangle((0, 0), 1, 1, facecolor="white", edgecolor=COLORES["agente"], linewidth=1.6), "agente"),
        (Rectangle((0, 0), 1, 1, facecolor="white", edgecolor=COLORES["verificadora"], linewidth=1.6), "verificadora"),
        (Rectangle((0, 0), 1, 1, facecolor=COLORES["feromona"]), "feromona"),
    ]
    fig.legend([e[0] for e in elementos], [e[1] for e in elementos], loc="lower center", ncol=3,
               fontsize=7.5, frameon=False, bbox_to_anchor=(0.5, 0.0))


def _figura(mundo: Mundo, modo: str):
    fig = plt.figure(figsize=(5.2, 6.4), dpi=110, facecolor=COLORES["fondo"])
    con_madre = modo != "ausente"
    alto = 0.66 if con_madre else 0.74
    ax = fig.add_axes([0.1, 0.12, 0.8, alto])
    if con_madre:
        _madre(fig, ax, modo)
    _leyenda(fig)
    return fig, ax


def _texto(resultado, cuadro: Cuadro, final: bool) -> str:
    if final:
        estado = {"verificada": "camino verificado", "verificadora_fallo": "la verificadora falló",
                  "limite": "se agotó el límite",
                  "abortado": "abortado: ninguna agente puede seguir"}[resultado.motivo]
        extra = f" · ruta {resultado.largo_verificado} / óptima {resultado.largo_optimo}" \
            if resultado.verificada else f" · óptima {resultado.largo_optimo}"
        return f"tick {cuadro.tick} · {estado}{extra}"
    return f"tick {cuadro.tick} · asentadas {cuadro.asentadas}"


def png_final(mundo: Mundo, resultado, n_agentes: int, ruta_png: str | Path) -> Path:
    """Guarda un PNG con el estado final y, si la hubo, la ruta de la verificadora."""
    lista = cuadros(mundo, resultado, n_agentes)
    fero_max = max(max(f) for f in resultado.feromona) or 1.0
    fig, ax = _figura(mundo, resultado.modo_madre)
    _dibujar(fig, ax, mundo, lista[-1], fero_max, resultado.ruta_verificada,
             _texto(resultado, lista[-1], final=True))
    ruta_png = Path(ruta_png)
    ruta_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta_png, facecolor=fig.get_facecolor())
    plt.close(fig)
    return ruta_png


def animar(mundo: Mundo, resultado, n_agentes: int, ruta_salida: str | Path, fps: int = 8,
           cada: int = 1) -> Path:
    """Guarda la animación del ensayo como GIF o MP4 (según la extensión).

    ``cada`` toma un cuadro de cada tantos ticks (el último siempre se incluye). El MP4
    necesita ffmpeg instalado; el GIF no necesita nada más.
    """
    ruta_salida = Path(ruta_salida)
    sufijo = ruta_salida.suffix.lower()
    if sufijo not in (".gif", ".mp4"):
        raise ValueError("La animación se guarda como .gif o .mp4")
    if sufijo == ".mp4" and not animation.writers.is_available("ffmpeg"):
        raise ValueError("Para MP4 hace falta ffmpeg; use .gif")
    lista = cuadros(mundo, resultado, n_agentes)
    elegidos = lista[::cada]
    if elegidos[-1] is not lista[-1]:
        elegidos.append(lista[-1])
    fero_max = max(max(f) for f in resultado.feromona) or 1.0
    fig, ax = _figura(mundo, resultado.modo_madre)

    def cuadro_n(n: int):
        final = n == len(elegidos) - 1
        _dibujar(fig, ax, mundo, elegidos[n], fero_max,
                 resultado.ruta_verificada if final else None,
                 _texto(resultado, elegidos[n], final))
        return []

    anim = animation.FuncAnimation(fig, cuadro_n, frames=len(elegidos), blit=False)
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    escritor = animation.PillowWriter(fps=fps) if sufijo == ".gif" else animation.FFMpegWriter(fps=fps)
    anim.save(ruta_salida, writer=escritor, savefig_kwargs={"facecolor": fig.get_facecolor()})
    plt.close(fig)
    return ruta_salida
