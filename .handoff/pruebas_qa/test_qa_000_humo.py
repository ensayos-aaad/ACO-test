"""Prueba de humo mínima de QA para la ronda 000 (prueba en seco, ADR-004)."""

from pathlib import Path

import aco_gemelo


def test_qa_000_importa_aco_gemelo_desde_gemelo():
    """Verifica que `aco_gemelo` se importa correctamente vía `conftest.py`."""
    assert isinstance(aco_gemelo.__version__, str)
    assert aco_gemelo.__version__.strip() != ""
    ruta_paquete = Path(aco_gemelo.__file__).resolve()
    assert ruta_paquete.parent.name == "aco_gemelo"
    assert ruta_paquete.parent.parent.name == "gemelo"
