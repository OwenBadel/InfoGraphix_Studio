"""Exportador PowerPoint (.pptx) 16:9 interactivo e ilustrado para Cuentos-Infografía."""

from __future__ import annotations

import io
from pathlib import Path

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

from ..domain.story_models import CuentoInfografiaSpec, EscenaCuento, PaletaEscena


SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
FONT_DISPLAY = "Georgia"
FONT_BODY = "Segoe UI"


def _rgb(pal: PaletaEscena, hex_color: str) -> RGBColor:
    r, g, b = pal.hex_a_rgb(hex_color)
    return RGBColor(r, g, b)


def _pintar_fondo(slide, pal: PaletaEscena) -> None:
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = _rgb(pal, pal.bg)


def _rect(
    slide,
    left,
    top,
    width,
    height,
    fill_rgb: RGBColor,
    border_rgb: RGBColor | None = None,
    shape_type=MSO_SHAPE.ROUNDED_RECTANGLE,
):
    sh = slide.shapes.add_shape(shape_type, left, top, width, height)
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill_rgb
    if border_rgb is not None:
        sh.line.color.rgb = border_rgb
        sh.line.width = Pt(1)
    else:
        sh.line.fill.background()
    sh.text_frame.word_wrap = True
    return sh


def _texto(
    slide,
    left,
    top,
    width,
    height,
    contenido: str,
    font_name: str,
    size_pt: int,
    color: RGBColor,
    bold: bool = False,
    italic: bool = False,
    align=PP_ALIGN.LEFT,
):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.04)
    tf.margin_right = Inches(0.04)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = contenido
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return tb


def _boton(
    slide,
    left,
    top,
    width,
    height,
    etiqueta: str,
    fill_rgb: RGBColor,
    text_rgb: RGBColor,
    border_rgb: RGBColor | None = None,
    font_size: int = 10,
    target_slide=None,
):
    sh = _rect(slide, left, top, width, height, fill_rgb, border_rgb)
    tf = sh.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(0.08)
    tf.margin_right = Inches(0.08)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = etiqueta
    r.font.name = FONT_BODY
    r.font.size = Pt(font_size)
    r.font.bold = True
    r.font.color.rgb = text_rgb
    if target_slide is not None:
        sh.click_action.target_slide = target_slide
    return sh


def _barra_navegacion_libro(
    slide,
    pal: PaletaEscena,
    slide_portada,
    slides_escenas: list,
    slide_reflexion,
    slide_infografia,
    activa: str,
) -> None:
    """Barra inferior interactiva de navegación no lineal (Modo Presentación F5)."""
    _rect(
        slide,
        Inches(0),
        Inches(6.82),
        SLIDE_W,
        Inches(0.68),
        _rgb(pal, pal.surface),
        _rgb(pal, pal.border),
        shape_type=MSO_SHAPE.RECTANGLE,
    )

    items: list[tuple[str, str, object]] = [("portada", "Portada", slide_portada)]
    for idx, sl in enumerate(slides_escenas, start=1):
        items.append((f"esc-{idx}", f"Escena {idx}", sl))
    items.append(("reflexion", "Reflexión", slide_reflexion))
    items.append(("infografia", "Mapa Salud", slide_infografia))

    x = Inches(0.45)
    for clave, label, destino in items:
        es_act = clave == activa
        ancho = Inches(1.42 if clave in ("portada", "reflexion", "infografia") else 1.24)
        _boton(
            slide,
            x,
            Inches(6.95),
            ancho,
            Inches(0.4),
            label,
            _rgb(pal, pal.accent if es_act else pal.surface_alt),
            _rgb(pal, pal.accent_ink if es_act else pal.ink),
            _rgb(pal, pal.accent if es_act else pal.border),
            font_size=10,
            target_slide=None if es_act else destino,
        )
        x += ancho + Inches(0.14)


def _construir_portada(
    slide,
    spec: CuentoInfografiaSpec,
    assets_dir: Path,
    slides_escenas: list,
    slide_reflexion,
    slide_infografia,
) -> None:
    pal = spec.escenas[0].paleta
    _pintar_fondo(slide, pal)

    # Franja de progresión cromática superior (5 colores frío -> cálido)
    ancho_franja = 13.333 / len(spec.escenas)
    for idx, esc in enumerate(spec.escenas):
        _rect(
            slide,
            Inches(idx * ancho_franja),
            Inches(0),
            Inches(ancho_franja + 0.02),
            Inches(0.16),
            _rgb(esc.paleta, esc.paleta.accent),
            shape_type=MSO_SHAPE.RECTANGLE,
        )

    # Columna izquierda: identidad editorial
    _boton(
        slide,
        Inches(0.6),
        Inches(0.55),
        Inches(4.3),
        Inches(0.36),
        spec.etiqueta_coleccion.upper(),
        _rgb(pal, pal.accent_soft),
        _rgb(pal, pal.accent),
        font_size=9,
    )

    _texto(
        slide,
        Inches(0.6),
        Inches(1.08),
        Inches(6.2),
        Inches(1.5),
        spec.titulo,
        FONT_DISPLAY,
        34,
        _rgb(pal, pal.ink),
        bold=True,
    )
    _texto(
        slide,
        Inches(0.6),
        Inches(2.58),
        Inches(6.1),
        Inches(1.05),
        spec.subtitulo,
        FONT_BODY,
        13,
        _rgb(pal, pal.muted),
    )

    # Ficha de extensión (rúbrica)
    _texto(
        slide,
        Inches(0.6),
        Inches(3.75),
        Inches(6.1),
        Inches(0.35),
        f"Extensión del relato: {spec.total_palabras_relato()} palabras  ·  5 escenas ilustradas  ·  5 datos de salud mental",
        FONT_BODY,
        10,
        _rgb(pal, pal.accent),
        bold=True,
    )

    # Botón CTA principal
    _boton(
        slide,
        Inches(0.6),
        Inches(4.25),
        Inches(2.9),
        Inches(0.56),
        "Comenzar lectura →",
        _rgb(pal, pal.accent),
        _rgb(pal, pal.accent_ink),
        font_size=13,
        target_slide=slides_escenas[0],
    )
    _boton(
        slide,
        Inches(3.7),
        Inches(4.25),
        Inches(2.7),
        Inches(0.56),
        "Mapa de Salud Mental",
        _rgb(pal, pal.surface),
        _rgb(pal, pal.ink),
        _rgb(pal, pal.border),
        font_size=12,
        target_slide=slide_infografia,
    )

    # Mosaico ilustrativo derecha (Escena 1 arriba + Escena 5 abajo mostrando el viaje frío -> cálido)
    img1 = assets_dir / spec.escenas[0].imagen_archivo
    img5 = assets_dir / spec.escenas[-1].imagen_archivo
    if img1.exists():
        slide.shapes.add_picture(str(img1), Inches(7.15), Inches(0.55), width=Inches(5.55), height=Inches(3.12))
    if img5.exists():
        slide.shapes.add_picture(str(img5), Inches(7.15), Inches(3.88), width=Inches(5.55), height=Inches(3.12))

    # Accesos directos a las 5 escenas en el pie izquierdo
    _texto(
        slide,
        Inches(0.6),
        Inches(5.05),
        Inches(6.1),
        Inches(0.28),
        "Explorar directamente una escena (Modo Presentación F5):",
        FONT_BODY,
        10,
        _rgb(pal, pal.muted),
        bold=True,
    )
    for idx, esc in enumerate(spec.escenas):
        col = idx % 3
        row = idx // 3
        bx = Inches(0.6 + col * 2.08)
        by = Inches(5.4 + row * 0.62)
        _boton(
            slide,
            bx,
            by,
            Inches(1.96),
            Inches(0.48),
            f"0{esc.numero}. {esc.titulo[:18]}",
            _rgb(esc.paleta, esc.paleta.surface),
            _rgb(esc.paleta, esc.paleta.ink),
            _rgb(esc.paleta, esc.paleta.accent),
            font_size=9,
            target_slide=slides_escenas[idx],
        )

    slide.notes_slide.notes_text_frame.text = (
        f"Portada: {spec.titulo}. Relato ilustrado de {spec.total_palabras_relato()} palabras "
        f"organizado en 5 escenas con transición cromática de tonos fríos a cálidos."
    )


def _construir_slide_escena(
    slide,
    esc: EscenaCuento,
    spec: CuentoInfografiaSpec,
    assets_dir: Path,
    slide_portada,
    slides_escenas: list,
    slide_dato,
    slide_reflexion,
    slide_infografia,
) -> None:
    pal = esc.paleta
    _pintar_fondo(slide, pal)

    # Franja superior cromática
    _rect(
        slide,
        Inches(0),
        Inches(0),
        SLIDE_W,
        Inches(0.12),
        _rgb(pal, pal.accent),
        shape_type=MSO_SHAPE.RECTANGLE,
    )

    # Cabecera izquierda-derecha
    _texto(
        slide,
        Inches(0.55),
        Inches(0.28),
        Inches(8.5),
        Inches(0.32),
        f"{esc.etiqueta_tiempo.upper()}   ·   {pal.nombre_clima.upper()}",
        FONT_BODY,
        10,
        _rgb(pal, pal.accent),
        bold=True,
    )
    _texto(
        slide,
        Inches(0.55),
        Inches(0.58),
        Inches(8.6),
        Inches(0.58),
        esc.titulo,
        FONT_DISPLAY,
        24,
        _rgb(pal, pal.ink),
        bold=True,
    )

    # Botón interactivo hacia la ficha de Salud Mental de esta escena
    _boton(
        slide,
        Inches(9.35),
        Inches(0.42),
        Inches(3.43),
        Inches(0.56),
        "💡 Dato sobre Salud Mental →",
        _rgb(pal, pal.accent),
        _rgb(pal, pal.accent_ink),
        font_size=11,
        target_slide=slide_dato,
    )

    # Columna izquierda: ilustración + cita + medidores
    img_path = assets_dir / esc.imagen_archivo
    if img_path.exists():
        slide.shapes.add_picture(str(img_path), Inches(0.55), Inches(1.28), width=Inches(5.85), height=Inches(3.29))
    else:
        _rect(slide, Inches(0.55), Inches(1.28), Inches(5.85), Inches(3.29), _rgb(pal, pal.surface), _rgb(pal, pal.border))

    cita_box = _rect(
        slide,
        Inches(0.55),
        Inches(4.72),
        Inches(5.85),
        Inches(1.1),
        _rgb(pal, pal.surface),
        _rgb(pal, pal.accent),
    )
    tf_c = cita_box.text_frame
    tf_c.margin_left = Inches(0.18)
    tf_c.margin_right = Inches(0.18)
    tf_c.vertical_anchor = MSO_ANCHOR.MIDDLE
    pc = tf_c.paragraphs[0]
    rc = pc.add_run()
    rc.text = f"“{esc.cita_destacada}”"
    rc.font.name = FONT_DISPLAY
    rc.font.size = Pt(11)
    rc.font.italic = True
    rc.font.color.rgb = _rgb(pal, pal.ink)

    # Medidores visuales Carga Mental vs Calma
    _texto(
        slide,
        Inches(0.55),
        Inches(5.96),
        Inches(2.8),
        Inches(0.24),
        f"Carga mental: {esc.nivel_carga_mental}%",
        FONT_BODY,
        9,
        _rgb(pal, pal.muted),
        bold=True,
    )
    _rect(slide, Inches(0.55), Inches(6.24), Inches(2.75), Inches(0.14), _rgb(pal, pal.border), shape_type=MSO_SHAPE.RECTANGLE)
    _rect(
        slide,
        Inches(0.55),
        Inches(6.24),
        Inches(2.75 * esc.nivel_carga_mental / 100.0),
        Inches(0.14),
        _rgb(pal, pal.accent),
        shape_type=MSO_SHAPE.RECTANGLE,
    )

    _texto(
        slide,
        Inches(3.65),
        Inches(5.96),
        Inches(2.75),
        Inches(0.24),
        f"Calma interior: {esc.nivel_calma}%",
        FONT_BODY,
        9,
        _rgb(pal, pal.muted),
        bold=True,
    )
    _rect(slide, Inches(3.65), Inches(6.24), Inches(2.75), Inches(0.14), _rgb(pal, pal.border), shape_type=MSO_SHAPE.RECTANGLE)
    _rect(
        slide,
        Inches(3.65),
        Inches(6.24),
        Inches(2.75 * esc.nivel_calma / 100.0),
        Inches(0.14),
        _rgb(pal, pal.accent),
        shape_type=MSO_SHAPE.RECTANGLE,
    )

    # Columna derecha: Relato narrativo completo de la escena
    tarjeta_texto = _rect(
        slide,
        Inches(6.68),
        Inches(1.28),
        Inches(6.1),
        Inches(5.26),
        _rgb(pal, pal.surface),
        _rgb(pal, pal.border),
    )
    tf = tarjeta_texto.text_frame
    tf.margin_left = Inches(0.26)
    tf.margin_right = Inches(0.26)
    tf.margin_top = Inches(0.2)
    tf.margin_bottom = Inches(0.16)

    total_chars = sum(len(p) for p in esc.parrafos)
    size_cuerpo = 11 if total_chars > 950 else 12

    for idx_p, parrafo in enumerate(esc.parrafos):
        p = tf.paragraphs[0] if idx_p == 0 else tf.add_paragraph()
        p.space_after = Pt(10)
        r = p.add_run()
        r.text = parrafo
        r.font.name = FONT_BODY
        r.font.size = Pt(size_cuerpo)
        r.font.color.rgb = _rgb(pal, pal.ink)

    _barra_navegacion_libro(
        slide,
        pal,
        slide_portada,
        slides_escenas,
        slide_reflexion,
        slide_infografia,
        f"esc-{esc.numero}",
    )

    slide.notes_slide.notes_text_frame.text = (
        f"Escena {esc.numero}: {esc.titulo}\n\n" + "\n\n".join(esc.parrafos)
    )


def _construir_slide_dato_salud(
    slide,
    esc: EscenaCuento,
    slide_portada,
    slides_escenas: list,
    slide_escena_origen,
    slide_reflexion,
    slide_infografia,
) -> None:
    pal = esc.paleta
    dato = esc.dato_salud
    _pintar_fondo(slide, pal)

    _rect(
        slide,
        Inches(0),
        Inches(0),
        Inches(0.2),
        Inches(6.82),
        _rgb(pal, pal.accent),
        shape_type=MSO_SHAPE.RECTANGLE,
    )

    _boton(
        slide,
        Inches(0.6),
        Inches(0.4),
        Inches(2.85),
        Inches(0.46),
        f"← Volver a Escena 0{esc.numero}",
        _rgb(pal, pal.surface),
        _rgb(pal, pal.accent),
        _rgb(pal, pal.accent),
        font_size=11,
        target_slide=slide_escena_origen,
    )

    _texto(
        slide,
        Inches(3.8),
        Inches(0.48),
        Inches(8.9),
        Inches(0.32),
        f"CÁPSULA DE SALUD MENTAL · VINCULADA A ESCENA 0{esc.numero}",
        FONT_BODY,
        10,
        _rgb(pal, pal.muted),
        bold=True,
        align=PP_ALIGN.RIGHT,
    )

    # Cifra hero izquierda
    caja_cifra = _rect(
        slide,
        Inches(0.6),
        Inches(1.25),
        Inches(4.3),
        Inches(4.95),
        _rgb(pal, pal.accent_soft),
        _rgb(pal, pal.accent),
    )
    tf_cf = caja_cifra.text_frame
    tf_cf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf_cf.margin_left = Inches(0.28)
    tf_cf.margin_right = Inches(0.28)

    p1 = tf_cf.paragraphs[0]
    p1.alignment = PP_ALIGN.CENTER
    r1 = p1.add_run()
    r1.text = dato.cifra_destacada
    r1.font.name = FONT_DISPLAY
    r1.font.size = Pt(54)
    r1.font.bold = True
    r1.font.color.rgb = _rgb(pal, pal.accent)

    p2 = tf_cf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(14)
    r2 = p2.add_run()
    r2.text = dato.subtitulo_cifra
    r2.font.name = FONT_BODY
    r2.font.size = Pt(14)
    r2.font.bold = True
    r2.font.color.rgb = _rgb(pal, pal.ink)

    # Explicación y acción práctica derecha
    caja_info = _rect(
        slide,
        Inches(5.2),
        Inches(1.25),
        Inches(7.55),
        Inches(4.95),
        _rgb(pal, pal.surface),
        _rgb(pal, pal.border),
    )
    tf_i = caja_info.text_frame
    tf_i.margin_left = Inches(0.32)
    tf_i.margin_right = Inches(0.32)
    tf_i.margin_top = Inches(0.3)

    pt = tf_i.paragraphs[0]
    rt = pt.add_run()
    rt.text = dato.titulo
    rt.font.name = FONT_DISPLAY
    rt.font.size = Pt(24)
    rt.font.bold = True
    rt.font.color.rgb = _rgb(pal, pal.ink)

    pe = tf_i.add_paragraph()
    pe.space_before = Pt(16)
    re = pe.add_run()
    re.text = dato.explicacion
    re.font.name = FONT_BODY
    re.font.size = Pt(14)
    re.font.color.rgb = _rgb(pal, pal.ink)

    pa_lbl = tf_i.add_paragraph()
    pa_lbl.space_before = Pt(20)
    ral = pa_lbl.add_run()
    ral.text = "ACCIÓN PRÁCTICA DE AUTOCUIDADO"
    ral.font.name = FONT_BODY
    ral.font.size = Pt(10)
    ral.font.bold = True
    ral.font.color.rgb = _rgb(pal, pal.accent)

    pa = tf_i.add_paragraph()
    pa.space_before = Pt(6)
    ra = pa.add_run()
    ra.text = dato.accion_practica
    ra.font.name = FONT_BODY
    ra.font.size = Pt(14)
    ra.font.bold = True
    ra.font.color.rgb = _rgb(pal, pal.ink)

    pf = tf_i.add_paragraph()
    pf.space_before = Pt(22)
    rf = pf.add_run()
    rf.text = f"Fuente de referencia: {dato.fuente}"
    rf.font.name = FONT_BODY
    rf.font.size = Pt(10)
    rf.font.color.rgb = _rgb(pal, pal.muted)

    _barra_navegacion_libro(
        slide, pal, slide_portada, slides_escenas, slide_reflexion, slide_infografia, ""
    )


def _construir_slide_reflexion(
    slide,
    spec: CuentoInfografiaSpec,
    assets_dir: Path,
    slide_portada,
    slides_escenas: list,
    slide_infografia,
) -> None:
    pal = spec.escenas[-1].paleta
    _pintar_fondo(slide, pal)

    _rect(
        slide,
        Inches(0),
        Inches(0),
        SLIDE_W,
        Inches(0.14),
        _rgb(pal, pal.accent),
        shape_type=MSO_SHAPE.RECTANGLE,
    )

    _texto(
        slide,
        Inches(0.65),
        Inches(0.45),
        Inches(12.0),
        Inches(0.32),
        "EPÍLOGO Y REFLEXIÓN FINAL",
        FONT_BODY,
        11,
        _rgb(pal, pal.accent),
        bold=True,
    )
    _texto(
        slide,
        Inches(0.65),
        Inches(0.8),
        Inches(12.0),
        Inches(0.68),
        spec.reflexion_final_titulo,
        FONT_DISPLAY,
        28,
        _rgb(pal, pal.ink),
        bold=True,
    )

    caja = _rect(
        slide,
        Inches(0.65),
        Inches(1.68),
        Inches(7.35),
        Inches(4.75),
        _rgb(pal, pal.surface),
        _rgb(pal, pal.border),
    )
    tf = caja.text_frame
    tf.margin_left = Inches(0.3)
    tf.margin_right = Inches(0.3)
    tf.margin_top = Inches(0.28)
    for idx, par in enumerate(spec.reflexion_final_parrafos):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.space_after = Pt(14)
        r = p.add_run()
        r.text = par
        r.font.name = FONT_BODY
        r.font.size = Pt(14)
        r.font.color.rgb = _rgb(pal, pal.ink)

    img_calma = assets_dir / spec.escenas[-1].imagen_archivo
    if img_calma.exists():
        slide.shapes.add_picture(str(img_calma), Inches(8.28), Inches(1.68), width=Inches(4.48), height=Inches(2.52))

    _boton(
        slide,
        Inches(8.28),
        Inches(4.5),
        Inches(4.48),
        Inches(0.66),
        "Ver Infografía & 5 Claves →",
        _rgb(pal, pal.accent),
        _rgb(pal, pal.accent_ink),
        font_size=13,
        target_slide=slide_infografia,
    )

    _texto(
        slide,
        Inches(8.28),
        Inches(5.36),
        Inches(4.48),
        Inches(0.9),
        f"Relato completo: {spec.total_palabras_relato()} palabras.\nCada escena incluye su cápsula interactiva de salud mental.",
        FONT_BODY,
        11,
        _rgb(pal, pal.muted),
    )

    _barra_navegacion_libro(
        slide, pal, slide_portada, slides_escenas, slide, slide_infografia, "reflexion"
    )


def _construir_slide_infografia(
    slide,
    spec: CuentoInfografiaSpec,
    slide_portada,
    slides_escenas: list,
    slide_reflexion,
) -> None:
    pal = spec.escenas[-1].paleta
    _pintar_fondo(slide, pal)

    _texto(
        slide,
        Inches(0.55),
        Inches(0.32),
        Inches(12.2),
        Inches(0.52),
        "Infografía de Cierre: De la Sobrecarga Fría a la Claridad Cálida",
        FONT_DISPLAY,
        22,
        _rgb(pal, pal.ink),
        bold=True,
    )
    _texto(
        slide,
        Inches(0.55),
        Inches(0.84),
        Inches(12.2),
        Inches(0.36),
        "Evolución emocional de Elena a lo largo de las 5 escenas y claves prácticas para cuidar la salud mental.",
        FONT_BODY,
        11,
        _rgb(pal, pal.muted),
    )

    # Gráfico nativo editable: Carga mental vs Calma interior
    chart_data = CategoryChartData()
    chart_data.categories = [f"Escena {e.numero}" for e in spec.escenas]
    chart_data.add_series("Carga mental (%)", tuple(e.nivel_carga_mental for e in spec.escenas))
    chart_data.add_series("Calma interior (%)", tuple(e.nivel_calma for e in spec.escenas))

    chart_shape = slide.shapes.add_chart(
        XL_CHART_TYPE.LINE_MARKERS,
        Inches(0.55),
        Inches(1.38),
        Inches(6.95),
        Inches(5.12),
        chart_data,
    )
    chart = chart_shape.chart
    chart.has_legend = True
    chart.series[0].format.line.color.rgb = RGBColor(0x47, 0x55, 0x69)
    chart.series[0].format.line.width = Pt(2.75)
    chart.series[1].format.line.color.rgb = _rgb(pal, pal.accent)
    chart.series[1].format.line.width = Pt(3.25)

    # Panel derecho: 5 claves para cerrar pestañas
    panel = _rect(
        slide,
        Inches(7.78),
        Inches(1.38),
        Inches(5.0),
        Inches(5.12),
        _rgb(pal, pal.surface),
        _rgb(pal, pal.border),
    )
    tf = panel.text_frame
    tf.margin_left = Inches(0.24)
    tf.margin_right = Inches(0.24)
    tf.margin_top = Inches(0.22)

    p0 = tf.paragraphs[0]
    r0 = p0.add_run()
    r0.text = "5 Claves para Cerrar Pestañas"
    r0.font.name = FONT_DISPLAY
    r0.font.size = Pt(16)
    r0.font.bold = True
    r0.font.color.rgb = _rgb(pal, pal.accent)

    for idx, clave in enumerate(spec.claves_autocuidado, start=1):
        p = tf.add_paragraph()
        p.space_before = Pt(11)
        rn = p.add_run()
        rn.text = f"0{idx}.  "
        rn.font.name = FONT_BODY
        rn.font.size = Pt(11)
        rn.font.bold = True
        rn.font.color.rgb = _rgb(pal, pal.accent)

        rc = p.add_run()
        rc.text = clave
        rc.font.name = FONT_BODY
        rc.font.size = Pt(11)
        rc.font.color.rgb = _rgb(pal, pal.ink)

    _barra_navegacion_libro(
        slide, pal, slide_portada, slides_escenas, slide_reflexion, slide, "infografia"
    )


def exportar_cuento_pptx_bytes(spec: CuentoInfografiaSpec, assets_dir: Path) -> bytes:
    """Genera el archivo PowerPoint interactivo e ilustrado (.pptx) en memoria."""
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    blank = prs.slide_layouts[6]

    # Fase 1: crear todas las diapositivas destino para cablear enlaces target_slide
    slide_portada = prs.slides.add_slide(blank)
    slides_escenas = [prs.slides.add_slide(blank) for _ in spec.escenas]
    slide_reflexion = prs.slides.add_slide(blank)
    slide_infografia = prs.slides.add_slide(blank)
    slides_datos = [prs.slides.add_slide(blank) for _ in spec.escenas]

    # Fase 2: poblar diapositivas con transición frío -> cálido e interactividad
    _construir_portada(
        slide_portada, spec, assets_dir, slides_escenas, slide_reflexion, slide_infografia
    )

    for idx, esc in enumerate(spec.escenas):
        _construir_slide_escena(
            slides_escenas[idx],
            esc,
            spec,
            assets_dir,
            slide_portada,
            slides_escenas,
            slides_datos[idx],
            slide_reflexion,
            slide_infografia,
        )

    _construir_slide_reflexion(
        slide_reflexion,
        spec,
        assets_dir,
        slide_portada,
        slides_escenas,
        slide_infografia,
    )

    _construir_slide_infografia(
        slide_infografia,
        spec,
        slide_portada,
        slides_escenas,
        slide_reflexion,
    )

    for idx, esc in enumerate(spec.escenas):
        _construir_slide_dato_salud(
            slides_datos[idx],
            esc,
            slide_portada,
            slides_escenas,
            slides_escenas[idx],
            slide_reflexion,
            slide_infografia,
        )

    buf = io.BytesIO()
    prs.save(buf)
    return buf.getvalue()


def guardar_cuento_pptx(
    spec: CuentoInfografiaSpec,
    assets_dir: str | Path,
    ruta_salida: str | Path,
) -> Path:
    destino = Path(ruta_salida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(exportar_cuento_pptx_bytes(spec, Path(assets_dir)))
    return destino
