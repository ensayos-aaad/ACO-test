"""Hace importable el paquete del gemelo para las pruebas de QA (ADR-004).

Fuera de `gemelo/`, pytest no lee `gemelo/pyproject.toml` (que fija `pythonpath = ["."]`), así que no encontraría
`aco_gemelo`. Comando, desde la raíz del repositorio:

    <python> -B -I -X utf8 -m pytest .handoff/pruebas_qa -q -p no:cacheprovider -W ignore
"""
import sys
from pathlib import Path

GEMELO = Path(__file__).resolve().parents[2] / "gemelo"
if str(GEMELO) not in sys.path:
    sys.path.insert(0, str(GEMELO))
