"""Prueba del artefacto 1: el entorno tiene las versiones fijadas en environment.yml."""
import importlib
import re
import sys
from pathlib import Path

# nombre en environment.yml -> nombre del módulo al importar
MODULOS = {"pyyaml": "yaml", "pillow": "PIL"}


def _fijadas():
    texto = (Path(__file__).parent.parent / "environment.yml").read_text(encoding="utf-8")
    return dict(re.findall(r"^\s*-\s*([a-z0-9_-]+)=([0-9.]+)\s*$", texto, flags=re.M))


def test_version_de_python():
    assert ".".join(map(str, sys.version_info[:3])) == _fijadas()["python"]


def test_versiones_de_paquetes():
    fijadas = _fijadas()
    fijadas.pop("python")
    for paquete, version in fijadas.items():
        modulo = importlib.import_module(MODULOS.get(paquete, paquete))
        assert modulo.__version__ == version, f"{paquete}: {modulo.__version__} != {version}"
