"""Pruebas del exportador HTML5 interactivo autocontenido."""

from pathlib import Path

from infographix.domain.models import InfografiaSpec, SeccionItem
from infographix.domain.presets import obtener_preset
from infographix.exporters.html_exporter import exportar_html, guardar_html


def test_exportar_html_contiene_estructura_y_controles_interactivos():
    spec = obtener_preset("transformacion_ia")
    assert spec is not None
    html_out = exportar_html(spec)

    assert "<!DOCTYPE html>" in html_out
    assert spec.titulo in html_out
    assert 'id="selector-tema"' in html_out
    assert 'id="btn-pantalla-completa"' in html_out
    assert "construirSvgGrafico" in html_out
    assert "prefers-reduced-motion" in html_out


def test_exportar_html_escapa_inyeccion_script():
    spec = InfografiaSpec(
        titulo="Infografía <script>alert(1)</script> Segura",
        subtitulo="Subtítulo </script><img src=x onerror=alert(1)>",
        secciones=[
            SeccionItem(
                id="seg",
                titulo="Bloque <b>Seguro</b>",
                resumen="Resumen </script> controlado",
            )
        ],
    )
    html_out = exportar_html(spec)
    assert "<script>alert(1)</script>" not in html_out
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html_out
    assert "<\\/script>" in html_out


def test_guardar_html_crea_archivo(tmp_path: Path):
    spec = obtener_preset("salud_publica")
    assert spec is not None
    destino = guardar_html(spec, tmp_path / "salida" / "salud.html")
    assert destino.exists()
    assert destino.stat().st_size > 4000
