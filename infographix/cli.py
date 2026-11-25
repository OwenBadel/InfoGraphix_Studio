"""Interfaz de línea de comandos para generar infografías HTML y PowerPoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .domain.models import InfografiaSpec
from .domain.presets import PRESETS, obtener_preset
from .exporters.html_exporter import guardar_html
from .exporters.pptx_exporter import guardar_pptx


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Genera infografías interactivas en HTML y PowerPoint (.pptx)."
    )
    origen = parser.add_mutually_exclusive_group(required=True)
    origen.add_argument(
        "--preset",
        choices=sorted(PRESETS.keys()),
        help="Identificador de plantilla precargada.",
    )
    origen.add_argument(
        "--entrada-json",
        type=Path,
        help="Ruta a un archivo JSON compatible con InfografiaSpec.",
    )
    parser.add_argument(
        "--formato",
        choices=["html", "pptx", "ambos"],
        default="ambos",
        help="Formato de exportación deseado.",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        default=Path("output"),
        help="Directorio de salida para los archivos generados.",
    )
    parser.add_argument(
        "--nombre",
        default="infografia",
        help="Nombre base de los archivos generados (sin extensión).",
    )
    args = parser.parse_args(argv)

    if args.preset:
        spec = obtener_preset(args.preset)
        assert spec is not None
    else:
        datos = json.loads(args.entrada_json.read_text(encoding="utf-8"))
        spec = InfografiaSpec.model_validate(datos)

    generados: list[Path] = []
    if args.formato in ("html", "ambos"):
        generados.append(guardar_html(spec, args.salida / f"{args.nombre}.html"))
    if args.formato in ("pptx", "ambos"):
        generados.append(guardar_pptx(spec, args.salida / f"{args.nombre}.pptx"))

    for ruta in generados:
        print(f"[OK] Archivo generado: {ruta.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
