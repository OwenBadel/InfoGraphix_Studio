"""Pruebas de integración de la API FastAPI y del CLI."""

from pathlib import Path
from fastapi.testclient import TestClient

from app import app
from infographix.cli import main as cli_main
from infographix.domain.presets import obtener_preset


client = TestClient(app)


def test_endpoints_catalogo_y_portada():
    r_home = client.get("/")
    assert r_home.status_code == 200
    assert "InfoGraphix Studio" in r_home.text

    r_health = client.get("/api/health")
    assert r_health.status_code == 200
    assert r_health.json()["status"] == "ok"

    r_temas = client.get("/api/temas")
    assert r_temas.status_code == 200
    assert len(r_temas.json()) == 4

    r_presets = client.get("/api/presets")
    assert r_presets.status_code == 200
    assert len(r_presets.json()) == 3


def test_endpoints_preview_y_exportacion_dual():
    spec = obtener_preset("transformacion_ia")
    assert spec is not None
    payload = spec.model_dump()

    r_prev = client.post("/api/preview/html", json=payload)
    assert r_prev.status_code == 200
    assert "<!DOCTYPE html>" in r_prev.text

    r_html = client.post("/api/export/html", json=payload)
    assert r_html.status_code == 200
    assert "attachment;" in r_html.headers["content-disposition"]
    assert r_html.headers["content-disposition"].endswith('.html"')

    r_pptx = client.post("/api/export/pptx", json=payload)
    assert r_pptx.status_code == 200
    assert "presentationml" in r_pptx.headers["content-type"]
    # Firma ZIP de archivo OpenXML (.pptx)
    assert r_pptx.content[:2] == b"PK"


def test_cli_genera_ambos_formatos(tmp_path: Path):
    codigo = cli_main(
        [
            "--preset",
            "roadmap_producto",
            "--formato",
            "ambos",
            "--salida",
            str(tmp_path),
            "--nombre",
            "roadmap",
        ]
    )
    assert codigo == 0
    assert (tmp_path / "roadmap.html").exists()
    assert (tmp_path / "roadmap.pptx").exists()
