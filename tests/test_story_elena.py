"""Pruebas automatizadas del libro-infografía interactivo de Elena."""

import io
from pathlib import Path
from fastapi.testclient import TestClient
from pptx import Presentation

from app import app
from infographix.domain.story_elena import obtener_cuento_elena
from infographix.exporters.story_html_exporter import exportar_cuento_html
from infographix.exporters.story_pptx_exporter import exportar_cuento_pptx_bytes


ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "cuento_elena"
client = TestClient(app)


def test_cuento_elena_cumple_rubrica_palabras_y_progresion_cromatica():
    cuento = obtener_cuento_elena()
    assert len(cuento.escenas) == 5
    # Rúbrica: mínimo 800 palabras
    assert cuento.total_palabras_relato() >= 820
    # Transición cromática real: escena 1 oscura/fría -> escena 5 clara/cálida
    assert cuento.escenas[0].paleta.es_oscura is True
    assert cuento.escenas[-1].paleta.es_oscura is False
    # Progresión emocional coherente
    assert cuento.escenas[0].nivel_carga_mental > cuento.escenas[-1].nivel_carga_mental
    assert cuento.escenas[-1].nivel_calma > cuento.escenas[0].nivel_calma


def test_cuento_html_embebe_imagenes_y_controles_interactivos():
    cuento = obtener_cuento_elena()
    html_out = exportar_cuento_html(cuento, ASSETS_DIR)
    assert "La mujer de las mil pestañas abiertas" in html_out
    assert "data:image/jpeg;base64," in html_out
    assert "speechSynthesis" in html_out
    assert "Ver dato sobre salud mental" in html_out
    assert "respiración 4–4–6" in html_out


def test_cuento_pptx_genera_13_slides_con_imagenes_enlaces_y_grafico():
    cuento = obtener_cuento_elena()
    raw = exportar_cuento_pptx_bytes(cuento, ASSETS_DIR)
    prs = Presentation(io.BytesIO(raw))

    # 1 Portada + 5 Escenas + 1 Reflexión + 1 Infografía + 5 Cápsulas de Salud Mental = 13 slides
    assert len(prs.slides) == 13
    # Portada tiene enlaces interactivos a escenas e infografía
    enlaces_portada = sum(
        1 for sh in prs.slides[0].shapes if getattr(getattr(sh, "click_action", None), "target_slide", None) is not None
    )
    assert enlaces_portada >= 7
    # Slide 8 (índice 7) es la infografía de cierre con gráfico nativo editable
    assert any(getattr(sh, "has_chart", False) for sh in prs.slides[7].shapes)


def test_endpoints_cuento_elena_funcionan():
    r_view = client.get("/cuento/elena")
    assert r_view.status_code == 200
    assert "La mujer de las mil pestañas abiertas" in r_view.text

    r_html = client.get("/api/cuento/elena/html")
    assert r_html.status_code == 200
    assert "La_Mujer_de_las_Mil_Pestanas_Abiertas.html" in r_html.headers["content-disposition"]

    r_pptx = client.get("/api/cuento/elena/pptx")
    assert r_pptx.status_code == 200
    assert r_pptx.content[:2] == b"PK"
