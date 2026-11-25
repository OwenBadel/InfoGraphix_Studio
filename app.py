"""Servidor FastAPI para InfoGraphix Studio (HTML Interactivo + PowerPoint .pptx)."""

from __future__ import annotations

import re
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from infographix.domain.models import InfografiaSpec
from infographix.domain.presets import listar_presets, obtener_preset
from infographix.domain.story_elena import obtener_cuento_elena
from infographix.domain.themes import TEMAS
from infographix.exporters.html_exporter import exportar_html
from infographix.exporters.pptx_exporter import exportar_pptx_bytes
from infographix.exporters.story_html_exporter import exportar_cuento_html
from infographix.exporters.story_pptx_exporter import exportar_cuento_pptx_bytes


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
ASSETS_ELENA_DIR = BASE_DIR / "assets" / "cuento_elena"

app = FastAPI(
    title="InfoGraphix Studio",
    description="Generador dual de infografías interactivas para navegador (HTML5) y PowerPoint (.pptx).",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def _slug_archivo(texto: str) -> str:
    limpio = re.sub(r"[^a-zA-Z0-9_-]+", "_", texto.strip().lower()).strip("_")
    return (limpio or "infografia")[:60]


@app.get("/", response_class=HTMLResponse)
def inicio() -> HTMLResponse:
    """Sirve la aplicación web del estudio interactivo."""
    index_path = STATIC_DIR / "index.html"
    return HTMLResponse(content=index_path.read_text(encoding="utf-8"))


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "servicio": "InfoGraphix Studio"}


@app.get("/api/temas")
def api_temas() -> list[dict[str, object]]:
    return [
        {
            "id": t.id,
            "nombre": t.nombre,
            "descripcion": t.descripcion,
            "bg": t.bg,
            "accent": t.accent,
            "ink": t.ink,
        }
        for t in TEMAS.values()
    ]


@app.get("/api/presets")
def api_presets() -> list[dict[str, str]]:
    return listar_presets()


@app.get("/api/presets/{preset_id}")
def api_preset_detalle(preset_id: str) -> dict[str, object]:
    spec = obtener_preset(preset_id)
    if spec is None:
        raise HTTPException(status_code=404, detail=f"Plantilla '{preset_id}' no encontrada.")
    return spec.model_dump()


@app.post("/api/preview/html", response_class=HTMLResponse)
def api_preview_html(spec: InfografiaSpec) -> HTMLResponse:
    """Renderiza en vivo el HTML interactivo autocontenido para el visor."""
    return HTMLResponse(content=exportar_html(spec))


@app.post("/api/export/html")
def api_export_html(spec: InfografiaSpec) -> Response:
    """Genera y descarga la infografía interactiva en formato HTML5."""
    contenido = exportar_html(spec).encode("utf-8")
    nombre = f"{_slug_archivo(spec.titulo)}.html"
    return Response(
        content=contenido,
        media_type="text/html; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )


@app.post("/api/export/pptx")
def api_export_pptx(spec: InfografiaSpec) -> Response:
    """Genera y descarga la infografía interactiva en formato PowerPoint (.pptx)."""
    contenido = exportar_pptx_bytes(spec)
    nombre = f"{_slug_archivo(spec.titulo)}.pptx"
    return Response(
        content=contenido,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )


@app.get("/cuento/elena", response_class=HTMLResponse)
def ver_cuento_elena() -> HTMLResponse:
    """Abre en el navegador el libro-infografía interactivo de Elena."""
    return HTMLResponse(content=exportar_cuento_html(obtener_cuento_elena(), ASSETS_ELENA_DIR))


@app.get("/api/cuento/elena/html")
def descargar_cuento_elena_html() -> Response:
    """Descarga el cuento interactivo de Elena en HTML5 autocontenido."""
    contenido = exportar_cuento_html(obtener_cuento_elena(), ASSETS_ELENA_DIR).encode("utf-8")
    return Response(
        content=contenido,
        media_type="text/html; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="La_Mujer_de_las_Mil_Pestanas_Abiertas.html"'},
    )


@app.get("/api/cuento/elena/pptx")
def descargar_cuento_elena_pptx() -> Response:
    """Descarga el cuento interactivo de Elena en PowerPoint (.pptx) ilustrado."""
    contenido = exportar_cuento_pptx_bytes(obtener_cuento_elena(), ASSETS_ELENA_DIR)
    return Response(
        content=contenido,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": 'attachment; filename="La_Mujer_de_las_Mil_Pestanas_Abiertas.pptx"'},
    )


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8020, reload=False)
