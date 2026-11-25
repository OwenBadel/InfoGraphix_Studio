"""Pruebas del exportador PowerPoint (.pptx) interactivo nativo."""

import io
from pathlib import Path

from pptx import Presentation

from infographix.domain.presets import obtener_preset
from infographix.exporters.pptx_exporter import exportar_pptx_bytes, guardar_pptx


def _contar_hipervinculos_internos(slide) -> int:
    total = 0
    for shape in slide.shapes:
        try:
            if shape.click_action.target_slide is not None:
                total += 1
        except Exception:
            continue
    return total


def test_exportar_pptx_genera_diapositivas_y_navegacion_interactiva():
    spec = obtener_preset("transformacion_ia")
    assert spec is not None
    raw = exportar_pptx_bytes(spec)
    prs = Presentation(io.BytesIO(raw))

    # 1 Hub + 1 Gráfico + 1 Hitos + 4 Secciones = 7 diapositivas
    assert len(prs.slides) == 1 + 1 + 1 + len(spec.secciones)
    assert round(prs.slide_width.inches, 2) == 13.33
    assert round(prs.slide_height.inches, 2) == 7.5

    # El Hub debe tener enlaces interactivos hacia las secciones y hacia gráfico/hitos
    enlaces_hub = _contar_hipervinculos_internos(prs.slides[0])
    assert enlaces_hub >= len(spec.secciones) + 2

    # La diapositiva 2 debe contener un gráfico nativo editable
    tiene_grafico = any(getattr(s, "has_chart", False) for s in prs.slides[1].shapes)
    assert tiene_grafico is True

    # Cada ficha de sección debe tener al menos botón "Volver al Tablero"
    for slide_sec in list(prs.slides)[3:]:
        assert _contar_hipervinculos_internos(slide_sec) >= 2


def test_exportar_pptx_soporta_todos_los_presets_y_tipos_de_grafico(tmp_path: Path):
    for preset_id in ("transformacion_ia", "salud_publica", "roadmap_producto"):
        spec = obtener_preset(preset_id)
        assert spec is not None
        ruta = guardar_pptx(spec, tmp_path / f"{preset_id}.pptx")
        assert ruta.exists()
        prs = Presentation(str(ruta))
        assert len(prs.slides) >= 4
        assert any(getattr(s, "has_chart", False) for s in prs.slides[1].shapes)
