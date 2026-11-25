"""Pruebas de modelos de dominio, temas WCAG y presets."""

import pytest
from pydantic import ValidationError

from infographix.domain.models import InfografiaSpec, SeccionItem
from infographix.domain.presets import PRESETS, listar_presets, obtener_preset
from infographix.domain.themes import TEMAS, obtener_tema


def test_presets_son_validos_y_clonables():
    resumen = listar_presets()
    assert len(resumen) == 3
    for item in resumen:
        copia = obtener_preset(item["id"])
        assert copia is not None
        assert copia.titulo == item["titulo"]
        copia.titulo = "Modificado"
        assert PRESETS[item["id"]].titulo != "Modificado"


def test_ids_duplicados_en_secciones_se_desambiguan():
    spec = InfografiaSpec(
        titulo="Prueba de IDs únicos",
        secciones=[
            SeccionItem(id="bloque", titulo="Uno", resumen="Resumen uno"),
            SeccionItem(id="bloque", titulo="Dos", resumen="Resumen dos"),
        ],
    )
    assert [s.id for s in spec.secciones] == ["bloque", "bloque-2"]


def test_falla_si_no_hay_secciones():
    with pytest.raises(ValidationError):
        InfografiaSpec(titulo="Sin secciones", secciones=[])


def test_temas_convierten_hex_a_rgb():
    assert len(TEMAS) == 4
    tema = obtener_tema("obsidian_sage")
    assert tema.hex_a_rgb(tema.bg) == (13, 15, 14)
    assert tema.es_oscuro is True
