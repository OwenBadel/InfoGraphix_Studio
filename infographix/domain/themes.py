"""Sistema de temas visuales WCAG AA compartidos entre HTML y PowerPoint."""

from __future__ import annotations

from dataclasses import dataclass
from .models import TemaId


@dataclass(frozen=True)
class TemaVisual:
    """Paleta tipográfica y cromática verificada para HTML y PPTX."""

    id: TemaId
    nombre: str
    descripcion: str
    es_oscuro: bool
    bg: str
    surface: str
    surface_alt: str
    ink: str
    muted: str
    border: str
    accent: str
    accent_ink: str
    accent_soft: str
    secondary: str
    success: str
    warning: str
    chart_palette: tuple[str, ...]
    font_display_html: str
    font_body_html: str
    font_mono_html: str
    font_display_pptx: str
    font_body_pptx: str

    def hex_a_rgb(self, color_hex: str) -> tuple[int, int, int]:
        """Convierte un color hexadecimal #RRGGBB a tupla (R, G, B)."""
        limpio = color_hex.lstrip("#")
        return (int(limpio[0:2], 16), int(limpio[2:4], 16), int(limpio[4:6], 16))


TEMAS: dict[TemaId, TemaVisual] = {
    "swiss_cobalt": TemaVisual(
        id="swiss_cobalt",
        nombre="Swiss Cobalt",
        descripcion="Grilla suiza de alta precisión en fondo claro con acento azul cobalto.",
        es_oscuro=False,
        bg="#f8fafc",
        surface="#ffffff",
        surface_alt="#eef2f7",
        ink="#0f172a",
        muted="#475569",
        border="#cbd5e1",
        accent="#1d4ed8",
        accent_ink="#ffffff",
        accent_soft="#dbeafe",
        secondary="#0f766e",
        success="#15803d",
        warning="#b45309",
        chart_palette=("#1d4ed8", "#0f766e", "#0369a1", "#4338ca", "#047857", "#b45309"),
        font_display_html="'Plus Jakarta Sans', 'Segoe UI', system-ui, sans-serif",
        font_body_html="'Plus Jakarta Sans', 'Segoe UI', system-ui, sans-serif",
        font_mono_html="'IBM Plex Mono', Consolas, monospace",
        font_display_pptx="Segoe UI Semibold",
        font_body_pptx="Segoe UI",
    ),
    "editorial_papel": TemaVisual(
        id="editorial_papel",
        nombre="Editorial Papel y Tinta",
        descripcion="Estética documental de revista en tono marfil con acento terracota oscuro.",
        es_oscuro=False,
        bg="#faf8f5",
        surface="#ffffff",
        surface_alt="#f3eee6",
        ink="#1c1917",
        muted="#57534e",
        border="#d6cfc4",
        accent="#9a3412",
        accent_ink="#ffffff",
        accent_soft="#ffedd5",
        secondary="#1e3a5f",
        success="#166534",
        warning="#a16207",
        chart_palette=("#9a3412", "#1e3a5f", "#166534", "#92400e", "#374151", "#7c2d12"),
        font_display_html="'Newsreader', Georgia, serif",
        font_body_html="'Plus Jakarta Sans', 'Segoe UI', system-ui, sans-serif",
        font_mono_html="'JetBrains Mono', Consolas, monospace",
        font_display_pptx="Georgia",
        font_body_pptx="Calibri",
    ),
    "obsidian_sage": TemaVisual(
        id="obsidian_sage",
        nombre="Obsidian & Sage",
        descripcion="Modo oscuro editorial en carbón profundo con acento verde salvia y ámbar.",
        es_oscuro=True,
        bg="#0d0f0e",
        surface="#161a18",
        surface_alt="#1f2522",
        ink="#eceee9",
        muted="#a3b1a8",
        border="#2c3530",
        accent="#6b9e7a",
        accent_ink="#0b110d",
        accent_soft="#1f3125",
        secondary="#d4a359",
        success="#74b886",
        warning="#e0a952",
        chart_palette=("#6b9e7a", "#d4a359", "#5c9ead", "#9ab87a", "#c97b63", "#8ea4d2"),
        font_display_html="'Fraunces', Georgia, serif",
        font_body_html="'DM Sans', 'Segoe UI', system-ui, sans-serif",
        font_mono_html="'JetBrains Mono', Consolas, monospace",
        font_display_pptx="Georgia",
        font_body_pptx="Segoe UI",
    ),
    "terracota_estudio": TemaVisual(
        id="terracota_estudio",
        nombre="Estudio Botánico",
        descripcion="Superficie arena cálida con contraste bosque profundo y cobre.",
        es_oscuro=False,
        bg="#f6f4ee",
        surface="#ffffff",
        surface_alt="#ebe6da",
        ink="#14231d",
        muted="#455950",
        border="#cfc7b6",
        accent="#14532d",
        accent_ink="#ffffff",
        accent_soft="#dcfce7",
        secondary="#b45309",
        success="#15803d",
        warning="#b45309",
        chart_palette=("#14532d", "#b45309", "#0f766e", "#7c2d12", "#3f6212", "#1e3a8a"),
        font_display_html="'Fraunces', Georgia, serif",
        font_body_html="'DM Sans', 'Segoe UI', system-ui, sans-serif",
        font_mono_html="'IBM Plex Mono', Consolas, monospace",
        font_display_pptx="Georgia",
        font_body_pptx="Segoe UI",
    ),
}


def obtener_tema(tema_id: TemaId) -> TemaVisual:
    """Obtiene un tema visual por identificador, con respaldo seguro."""
    return TEMAS.get(tema_id, TEMAS["swiss_cobalt"])
