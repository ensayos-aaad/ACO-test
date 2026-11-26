"""Pruebas del artefacto 9: configuración en YAML y línea de comandos."""
import csv
import subprocess
import sys
from dataclasses import fields
from pathlib import Path

import pytest
import yaml

from aco_gemelo.__main__ import main
from aco_gemelo.agente import ConfigAgente
from aco_gemelo.config import cargar, config_ensayo, crear_mundo
from aco_gemelo.madre import ConfigMadre, Modo
from aco_gemelo.motor import ConfigEnsayo
from aco_gemelo.mundo import OBSTACULOS_L

GEMELO = Path(__file__).parent.parent
CONFIGS = GEMELO / "configs"
ARCHIVOS = sorted(CONFIGS.glob("*.yaml"))


def escribir(tmp_path, datos, nombre="prueba.yaml"):
    ruta = tmp_path / nombre
    ruta.write_text(yaml.safe_dump(datos), encoding="utf-8")
    return ruta


# ---------------------------------------------------------------- criterio 1: toda la configuración sale del YAML


def test_hay_tres_configuraciones_de_ejemplo():
    assert [a.name for a in ARCHIVOS] == ["aleatorio.yaml", "default.yaml", "puente_doble.yaml"]


def test_default_yaml_muestra_todos_los_valores_por_defecto():
    """El archivo por defecto documenta cada parámetro y coincide con los valores del código."""
    datos = cargar(CONFIGS / "default.yaml")
    # Valores del código, salvo los tres que J7 cambia en el archivo.
    assert config_ensayo(datos) == ConfigEnsayo(semilla=2026, limite=6000, salida_cada=1,
                                                agente=ConfigAgente(viajes=10))
    assert set(datos["agente"]) == {f.name for f in fields(ConfigAgente)} - {
        "con_madre", "verificadora", "informa_mapa"}
    assert set(datos["madre"]) == {f.name for f in fields(ConfigMadre)}
    assert set(datos["canal"]) == {"radio", "p_perdida", "retardo", "formato"}


def test_cada_parametro_se_puede_cambiar_desde_el_yaml(tmp_path):
    datos = {
        "semilla": 7,
        "ensayo": {"n_agentes": 3, "limite": 99, "rho": 0.2, "registrar": True, "pausa": 0.01},
        "agente": {"alpha": 1.0, "k": 20.0, "theta": 0.0, "K": 9, "deposito": "constante",
                   "deposito_valor": 5, "delta_t": 4},
        "madre": {"modo": "difusion", "delta_t": 3, "memoria": 128, "umbral_rescate": 0.9,
                  "rutas_por_anuncio": 1},
        "canal": {"radio": 2, "p_perdida": 0.1, "retardo": [1, 4], "formato": "json"},
    }
    cfg = config_ensayo(cargar(escribir(tmp_path, datos)))
    assert cfg == ConfigEnsayo(
        semilla=7, n_agentes=3, limite=99, rho=0.2, registrar=True, pausa=0.01,
        agente=ConfigAgente(alpha=1.0, k=20.0, theta=0.0, K=9, deposito="constante",
                            deposito_valor=5, delta_t=4),
        madre=ConfigMadre(modo=Modo.DIFUSION, delta_t=3, memoria=128, umbral_rescate=0.9,
                          rutas_por_anuncio=1),
        radio=2, p_perdida=0.1, retardo=(1, 4), formato="json")
    assert config_ensayo(cargar(escribir(tmp_path, datos)), semilla=11).semilla == 11


@pytest.mark.parametrize("modo", ["ausente", "pista_de_baile", "rescate", "difusion", 2])
def test_modos_de_la_madre_por_nombre_o_numero(modo):
    assert isinstance(config_ensayo({"madre": {"modo": modo}}).madre.modo, Modo)


@pytest.mark.parametrize("datos", [
    {"mundoo": {}},
    {"agente": {"alfa": 2}},
    {"agente": {"verificadora": True}},  # la fija el motor, no el usuario
    {"madre": {"modo": "reina"}},
    {"canal": {"radios": 1}},
    {"ensayo": {"semillas": 3}},
    {"mundo": {"escenario": "laberinto"}},
    {"mundo": {"densidad_": 0.1}},
])
def test_una_clave_o_valor_desconocido_es_un_error(tmp_path, datos):
    with pytest.raises(ValueError):
        leidos = cargar(escribir(tmp_path, datos))
        config_ensayo(leidos)
        crear_mundo(leidos)


def test_un_yaml_vacio_usa_todos_los_valores_por_defecto(tmp_path):
    ruta = tmp_path / "vacio.yaml"
    ruta.write_text("", encoding="utf-8")
    datos = cargar(ruta)
    assert config_ensayo(datos) == ConfigEnsayo()
    assert crear_mundo(datos).obstaculos == OBSTACULOS_L


# ---------------------------------------------------------------- el mundo desde el YAML


def test_escenario_l_con_distancia_minima():
    for semilla in range(30):
        mundo = crear_mundo({"mundo": {"distancia_minima": 6}}, semilla)
        assert mundo.obstaculos == OBSTACULOS_L and mundo.largo_optimo() >= 6
    a, b = crear_mundo({}, 5), crear_mundo({}, 5)
    assert (a.inicio, a.meta) == (b.inicio, b.meta)
    assert (mundo.tau_max, mundo.unidad_deposito) == (1.0, 1 / 255)


def test_escenario_aleatorio_siempre_tiene_camino():
    datos = {"mundo": {"escenario": "aleatorio", "ancho": 10, "alto": 6, "densidad": 0.3}}
    vistos = set()
    for semilla in range(30):
        mundo = crear_mundo(datos, semilla)
        assert (mundo.ancho, mundo.alto) == (10, 6)
        assert mundo.bfs() is not None and mundo.largo_optimo() >= 4
        vistos.add(mundo.obstaculos)
    assert len(vistos) == 30  # cada semilla, un mundo distinto


def test_escenario_puente_doble():
    mundo = crear_mundo(cargar(CONFIGS / "puente_doble.yaml"))
    assert (mundo.ancho, mundo.alto, mundo.largo_optimo()) == (3, 5, 4)
    assert (mundo.tau_max, mundo.unidad_deposito) == (300.0, 1.0)  # J3: 1 nivel = 20 depósitos
    mundo = crear_mundo({"mundo": {"escenario": "puente_doble", "r": "3/2"}})
    assert mundo.alto == 4


def test_distancia_minima_imposible_es_un_error():
    with pytest.raises(ValueError):
        crear_mundo({"mundo": {"distancia_minima": 99}})


# ---------------------------------------------------------------- criterio 2: run y batch funcionan


@pytest.mark.parametrize("archivo", ARCHIVOS, ids=lambda a: a.stem)
def test_run_con_cada_configuracion_de_ejemplo(archivo, capsys):
    assert main(["run", "--config", str(archivo)]) == 0
    salida = capsys.readouterr().out
    assert "Mundo (semilla 2026):" in salida and "I" in salida and "F" in salida
    assert "motivo" in salida and "asentadas                    1" in salida


def test_run_con_otra_semilla_y_motor_de_hilos(capsys):
    assert main(["run", "--config", str(CONFIGS / "default.yaml"), "--semilla", "3",
                 "--motor", "hilos"]) == 0
    assert "Mundo (semilla 3):" in capsys.readouterr().out


def test_batch_guarda_un_csv_reproducible(tmp_path, capsys):
    salida = tmp_path / "sub" / "r.csv"
    orden = ["batch", "--config", str(CONFIGS / "default.yaml"), "--semillas", "4",
             "--semilla-inicial", "10", "--salida", str(salida)]
    assert main(orden) == 0
    impreso = capsys.readouterr().out
    assert "4 ensayos" in impreso and "asentadas:   4/4" in impreso
    primero = salida.read_bytes()
    with open(salida, newline="", encoding="utf-8") as archivo:
        filas = list(csv.DictReader(archivo))
    assert [f["semilla"] for f in filas] == ["10", "11", "12", "13"]
    assert {f["escenario"] for f in filas} == {"L"}
    assert {f["modo_madre"] for f in filas} == {"pista_de_baile"}
    assert all(int(f["bytes_agente_madre"]) > 0 and int(f["bloqueadas"]) == 0 for f in filas)
    assert main(orden) == 0
    assert salida.read_bytes() == primero  # misma orden, mismo archivo


def test_un_archivo_inexistente_o_invalido_da_codigo_2(tmp_path, capsys):
    assert main(["run", "--config", str(tmp_path / "no_existe.yaml")]) == 2
    assert main(["run", "--config", str(escribir(tmp_path, {"agente": {"alfa": 1}}))]) == 2
    assert "Error:" in capsys.readouterr().err


def test_python_m_aco_gemelo_desde_la_carpeta_gemelo():
    """La orden tal como la escribe una persona: ``python -m aco_gemelo run --config ...``."""
    proceso = subprocess.run(
        [sys.executable, "-X", "utf8", "-m", "aco_gemelo", "run", "--config", "configs/default.yaml"],
        cwd=GEMELO, capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert proceso.returncode == 0, proceso.stderr
    assert "motivo" in proceso.stdout


# ---------------------------------------------------------------- B6: escenario personalizado


def test_escenario_personalizado():
    datos = {"mundo": {"escenario": "personalizado", "ancho": 5, "alto": 4,
                       "obstaculos": [[1, 0], [1, 1], [1, 2], [3, 1], [3, 2], [3, 3]],
                       "inicio": [0, 0], "meta": [4, 0]}}
    mundo = crear_mundo(datos, semilla=123)
    assert mundo.obstaculos == {(1, 0), (1, 1), (1, 2), (3, 1), (3, 2), (3, 3)}
    assert (mundo.inicio, mundo.meta) == ((0, 0), (4, 0))
    assert crear_mundo(datos, semilla=7).obstaculos == mundo.obstaculos  # no depende de la semilla
    assert mundo.largo_optimo() == 10  # bordea las dos paredes; sin cortar esquinas no hay atajo


@pytest.mark.parametrize("mundo", [
    {"escenario": "personalizado", "inicio": [0, 0]},  # falta la meta
    {"escenario": "personalizado", "inicio": [0, 0], "meta": [2, 0], "obstaculos": [[1, 0], [1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [1, 7]]},  # sin camino
    {"escenario": "personalizado", "inicio": "0,0", "meta": [2, 0]},  # celda mal escrita
    {"escenario": "personalizado", "inicio": [0, 0], "meta": [1, 0], "obstaculos": [[1, 0]]},  # meta en obstáculo
    {"escenario": "personalizado", "inicio": [2, 2], "meta": [2, 2]},  # inicio = meta (F-023, 4)
    {"escenario": "personalizado", "inicio": [0, 0], "meta": [4, 0], "obstaculos": [[2, 0], [2, 0]]},  # repetido
])
def test_escenario_personalizado_invalido(mundo):
    with pytest.raises(ValueError):
        crear_mundo({"mundo": mundo})


@pytest.mark.parametrize("escenario", ["L", "aleatorio", "puente_doble"])
@pytest.mark.parametrize("clave, valor", [("obstaculos", [[0, 0]]), ("inicio", [7, 7]), ("meta", [0, 1])])
def test_claves_del_personalizado_en_otro_escenario_son_error(escenario, clave, valor):
    """F-023 (4): antes se ignoraban sin aviso."""
    with pytest.raises(ValueError, match="personalizado"):
        crear_mundo({"mundo": {"escenario": escenario, clave: valor}}, semilla=1)


def test_motor_hilos_sincronos_desde_la_linea_de_comandos(capsys):
    assert main(["run", "--config", str(CONFIGS / "default.yaml"), "--semilla", "1",
                 "--motor", "hilos_sincronos"]) == 0
    assert "motivo" in capsys.readouterr().out


def test_delta_t_fuera_de_rango_es_error_al_cargar_el_yaml():
    """F-023 (7): el error sale al leer la configuración, no a mitad del ensayo."""
    with pytest.raises(ValueError, match="INICIO"):
        config_ensayo({"madre": {"modo": "pista_de_baile", "delta_t": 256}})


@pytest.mark.parametrize("semilla_archivo", [-3, 1.5, "3", True, None])
def test_run_con_semilla_reemplaza_la_del_archivo_aunque_sea_invalida(tmp_path, capsys, semilla_archivo):
    """H1 (regresión de la ronda 001 de QA): `run --semilla 3` sobre un YAML con semilla inválida corría el
    ensayo y terminaba con error al final, sin generar el PNG."""
    config = tmp_path / "c.yaml"
    config.write_text(yaml.safe_dump({"semilla": semilla_archivo, "ensayo": {"limite": 50}}), encoding="utf-8")
    png = tmp_path / "final.png"
    assert main(["run", "--config", str(config), "--semilla", "3", "--png", str(png)]) == 0
    assert png.stat().st_size > 0
    assert "Error" not in capsys.readouterr().err
    assert main(["run", "--config", str(config)]) == 2  # sin --semilla, la del archivo sí se valida


@pytest.mark.parametrize("n", [0, -2])
def test_batch_con_cero_semillas_da_error_limpio(tmp_path, capsys, n):
    """O3 de la revisión de la ronda 002 (ya pasaba antes): `batch --semillas 0` terminaba en IndexError con traza."""
    salida = tmp_path / "sub" / "b.csv"
    assert main(["batch", "--config", str(CONFIGS / "default.yaml"), "--semillas", str(n),
                 "--salida", str(salida)]) == 2
    assert "Error: --semillas" in capsys.readouterr().err
    assert not salida.parent.exists()
