"""Pruebas automatizadas del cuento ilustrado limpio y popups nativos de Elena."""

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


def test_cuento_elena_sin_ruido_visual_y_cumple_extension():
    cuento = obtener_cuento_elena()
    assert len(cuento.escenas) == 5
    assert cuento.total_palabras_relato() >= 820
    assert cuento.escenas[0].etiqueta_tiempo == "5:30 a. m. · Madrugada"
    for esc in cuento.escenas:
        assert "Escena" not in esc.etiqueta_tiempo
        assert "Azul Acero" not in esc.paleta.nombre_clima


def test_cuento_html_limpio_con_ventana_emergente():
    cuento = obtener_cuento_elena()
    html_out = exportar_cuento_html(cuento, ASSETS_DIR)
    assert "La mujer de las mil pestañas abiertas" in html_out
    assert "data:image/jpeg;base64," in html_out
    assert 'role="dialog"' in html_out
    assert "💡 Dato de salud mental" in html_out
    # Sin elementos descartados por el usuario
    assert "Mapa de Salud Mental" not in html_out
    assert "medidores-escena" not in html_out
    assert "Calma interior" not in html_out
    assert "Extensión del relato" not in html_out
    assert "Azul Acero" not in html_out


def test_cuento_pptx_7_diapositivas_con_popups_interactivos_en_la_misma_slide():
    cuento = obtener_cuento_elena()
    raw = exportar_cuento_pptx_bytes(cuento, ASSETS_DIR)
    prs = Presentation(io.BytesIO(raw))

    # 1 Portada + 5 páginas del cuento + 1 Reflexión = 7 diapositivas limpias
    assert len(prs.slides) == 7

    # La portada solo tiene el botón Comenzar lectura (sin mapa ni 5 accesos)
    textos_portada = " ".join(
        sh.text_frame.text for sh in prs.slides[0].shapes if sh.has_text_frame
    )
    assert "Comenzar lectura" in textos_portada
    assert "Mapa de Salud Mental" not in textos_portada
    assert "Extensión del relato" not in textos_portada
    assert "Modo Presentación" not in textos_portada

    # Cada una de las 5 páginas tiene animación desencadenada (<p:timing> + interactiveSeq)
    # y todos los spid referenciados en <p:spTgt> existen en la misma diapositiva
    ns = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main"}
    for slide in list(prs.slides)[1:6]:
        textos = " ".join(sh.text_frame.text for sh in slide.shapes if sh.has_text_frame)
        assert "Dato de salud mental" in textos
        assert "Carga mental:" not in textos
        assert "Calma interior:" not in textos
        assert "Escena 1" not in textos
        assert "Azul Acero" not in textos

        spids_presentes = {str(sh.shape_id) for sh in slide.shapes}
        seqs = slide._element.findall(".//p:seq/p:cTn[@nodeType='interactiveSeq']", ns)
        assert len(seqs) == 3  # Abrir popup, Cerrar con X, Cerrar tocando tarjeta
        targets = slide._element.findall(".//p:spTgt", ns)
        assert len(targets) >= 6
        for t in targets:
            assert t.get("spid") in spids_presentes


def test_endpoints_cuento_elena_funcionan():
    r_view = client.get("/cuento/elena")
    assert r_view.status_code == 200
    assert "La mujer de las mil pestañas abiertas" in r_view.text

    r_html = client.get("/api/cuento/elena/html")
    assert r_html.status_code == 200

    r_pptx = client.get("/api/cuento/elena/pptx")
    assert r_pptx.status_code == 200
    assert r_pptx.content[:2] == b"PK"
