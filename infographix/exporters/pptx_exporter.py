"""Exportador de infografías interactivas en formato PowerPoint (.pptx) 16:9 editable."""

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

from ..domain.models import InfografiaSpec, SeccionItem
from ..domain.themes import TemaVisual, obtener_tema


SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)


def _rgb(tema: TemaVisual, hex_color: str) -> RGBColor:
    r, g, b = tema.hex_a_rgb(hex_color)
    return RGBColor(r, g, b)


def _pintar_fondo(slide, tema: TemaVisual) -> None:
    fondo = slide.background
    fill = fondo.fill
    fill.solid()
    fill.fore_color.rgb = _rgb(tema, tema.bg)


def _agregar_caja_texto(
    slide,
    left,
    top,
    width,
    height,
    texto: str,
    font_name: str,
    font_size: int,
    color: RGBColor,
    bold: bool = False,
    align=PP_ALIGN.LEFT,
):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.03)
    tf.margin_bottom = Inches(0.03)
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = texto
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def _agregar_tarjeta(
    slide,
    left,
    top,
    width,
    height,
    fill_rgb: RGBColor,
    border_rgb: RGBColor | None = None,
    shape_type=MSO_SHAPE.ROUNDED_RECTANGLE,
):
    shape = slide.shapes.add_shape(shape_type, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_rgb
    if border_rgb is not None:
        shape.line.color.rgb = border_rgb
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    shape.text_frame.word_wrap = True
    return shape


def _agregar_barra_navegacion(
    slide,
    tema: TemaVisual,
    slide_hub,
    slide_grafico,
    slide_hitos,
    activo: str,
    pie_texto: str,
) -> None:
    """Agrega una barra inferior interactiva con hipervínculos internos entre slides."""
    barra_top = Inches(6.78)
    barra = _agregar_tarjeta(
        slide,
        Inches(0.0),
        barra_top,
        SLIDE_W,
        Inches(0.72),
        _rgb(tema, tema.surface),
        _rgb(tema, tema.border),
        shape_type=MSO_SHAPE.RECTANGLE,
    )
    barra.shadow.inherit = False

    botones: list[tuple[str, str, object]] = [("hub", "Tablero", slide_hub)]
    if slide_grafico is not None:
        botones.append(("grafico", "Gráfico", slide_grafico))
    if slide_hitos is not None:
        botones.append(("hitos", "Hoja de Ruta", slide_hitos))

    x = Inches(0.55)
    for clave, etiqueta, destino in botones:
        es_activo = clave == activo
        btn = _agregar_tarjeta(
            slide,
            x,
            Inches(6.92),
            Inches(1.65),
            Inches(0.42),
            _rgb(tema, tema.accent if es_activo else tema.surface_alt),
            _rgb(tema, tema.accent if es_activo else tema.border),
        )
        tf = btn.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        run.text = etiqueta
        run.font.name = tema.font_body_pptx
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = _rgb(tema, tema.accent_ink if es_activo else tema.ink)
        if destino is not None and not es_activo:
            btn.click_action.target_slide = destino
        x += Inches(1.8)

    _agregar_caja_texto(
        slide,
        Inches(6.5),
        Inches(6.98),
        Inches(6.3),
        Inches(0.32),
        pie_texto,
        tema.font_body_pptx,
        10,
        _rgb(tema, tema.muted),
        align=PP_ALIGN.RIGHT,
    )


def _construir_slide_hub(
    slide,
    spec: InfografiaSpec,
    tema: TemaVisual,
    slides_secciones: dict[str, object],
    slide_grafico,
    slide_hitos,
) -> None:
    _pintar_fondo(slide, tema)

    # Franja superior de acento
    _agregar_tarjeta(
        slide,
        Inches(0),
        Inches(0),
        SLIDE_W,
        Inches(0.12),
        _rgb(tema, tema.accent),
        shape_type=MSO_SHAPE.RECTANGLE,
    )

    # Etiqueta de categoría
    badge = _agregar_tarjeta(
        slide,
        Inches(0.55),
        Inches(0.32),
        Inches(2.8),
        Inches(0.34),
        _rgb(tema, tema.accent_soft),
    )
    tf_b = badge.text_frame
    tf_b.vertical_anchor = MSO_ANCHOR.MIDDLE
    pb = tf_b.paragraphs[0]
    pb.alignment = PP_ALIGN.CENTER
    rb = pb.add_run()
    rb.text = spec.categoria.upper()
    rb.font.name = tema.font_body_pptx
    rb.font.size = Pt(9)
    rb.font.bold = True
    rb.font.color.rgb = _rgb(tema, tema.accent)

    # Título y subtítulo
    _agregar_caja_texto(
        slide,
        Inches(0.55),
        Inches(0.72),
        Inches(12.2),
        Inches(0.62),
        spec.titulo,
        tema.font_display_pptx,
        24,
        _rgb(tema, tema.ink),
        bold=True,
    )
    if spec.subtitulo:
        _agregar_caja_texto(
            slide,
            Inches(0.55),
            Inches(1.32),
            Inches(12.2),
            Inches(0.45),
            spec.subtitulo,
            tema.font_body_pptx,
            12,
            _rgb(tema, tema.muted),
        )

    # KPIs destacados
    y_actual = Inches(1.88)
    if spec.kpis:
        n_kpis = len(spec.kpis)
        gap = 0.22
        ancho_total = 12.23
        kpi_w = (ancho_total - gap * (n_kpis - 1)) / n_kpis
        for idx, kpi in enumerate(spec.kpis):
            x = Inches(0.55 + idx * (kpi_w + gap))
            _agregar_tarjeta(
                slide,
                x,
                y_actual,
                Inches(kpi_w),
                Inches(1.18),
                _rgb(tema, tema.surface),
                _rgb(tema, tema.border),
            )
            _agregar_caja_texto(
                slide,
                x + Inches(0.14),
                y_actual + Inches(0.1),
                Inches(kpi_w - 0.28),
                Inches(0.28),
                kpi.etiqueta.upper(),
                tema.font_body_pptx,
                9,
                _rgb(tema, tema.muted),
                bold=True,
            )
            _agregar_caja_texto(
                slide,
                x + Inches(0.14),
                y_actual + Inches(0.36),
                Inches(kpi_w - 0.28),
                Inches(0.44),
                kpi.valor,
                tema.font_display_pptx,
                22,
                _rgb(tema, tema.ink),
                bold=True,
            )
            if kpi.delta:
                color_delta = (
                    tema.success
                    if kpi.tendencia == "positiva"
                    else tema.warning
                    if kpi.tendencia == "alerta"
                    else tema.secondary
                )
                _agregar_caja_texto(
                    slide,
                    x + Inches(0.14),
                    y_actual + Inches(0.84),
                    Inches(kpi_w - 0.28),
                    Inches(0.26),
                    kpi.delta,
                    tema.font_body_pptx,
                    10,
                    _rgb(tema, color_delta),
                    bold=True,
                )
        y_actual += Inches(1.38)

    # Grilla de tarjetas interactivas (enlazadas a cada diapositiva de sección)
    _agregar_caja_texto(
        slide,
        Inches(0.55),
        y_actual,
        Inches(12.2),
        Inches(0.32),
        "Haz clic en cualquier bloque en Modo Presentación (F5) para explorar su ficha detallada:",
        tema.font_body_pptx,
        11,
        _rgb(tema, tema.muted),
        bold=True,
    )
    y_cards = y_actual + Inches(0.36)
    secciones = spec.secciones[:6]
    cols = 2 if len(secciones) <= 4 else 3
    rows = (len(secciones) + cols - 1) // cols
    gap_x = 0.22
    gap_y = 0.2
    total_w = 12.23
    avail_h = 6.55 - (y_cards / Inches(1))
    card_w = (total_w - gap_x * (cols - 1)) / cols
    card_h = min(1.55, (avail_h - gap_y * (rows - 1)) / max(rows, 1))

    for i, sec in enumerate(secciones):
        col = i % cols
        row = i // cols
        x = Inches(0.55 + col * (card_w + gap_x))
        y = y_cards + Inches(row * (card_h + gap_y))
        tarjeta = _agregar_tarjeta(
            slide,
            x,
            y,
            Inches(card_w),
            Inches(card_h),
            _rgb(tema, tema.surface),
            _rgb(tema, tema.accent),
        )
        tf = tarjeta.text_frame
        tf.margin_left = Inches(0.18)
        tf.margin_right = Inches(0.18)
        tf.margin_top = Inches(0.12)
        tf.margin_bottom = Inches(0.1)

        p1 = tf.paragraphs[0]
        r_cat = p1.add_run()
        r_cat.text = f"{sec.categoria.upper()}" + (f"  ·  {sec.metrica}" if sec.metrica else "")
        r_cat.font.name = tema.font_body_pptx
        r_cat.font.size = Pt(9)
        r_cat.font.bold = True
        r_cat.font.color.rgb = _rgb(tema, tema.accent)

        p2 = tf.add_paragraph()
        p2.space_before = Pt(4)
        r_tit = p2.add_run()
        r_tit.text = sec.titulo
        r_tit.font.name = tema.font_display_pptx
        r_tit.font.size = Pt(14)
        r_tit.font.bold = True
        r_tit.font.color.rgb = _rgb(tema, tema.ink)

        p3 = tf.add_paragraph()
        p3.space_before = Pt(4)
        r_res = p3.add_run()
        resumen_corto = sec.resumen if len(sec.resumen) <= 110 else sec.resumen[:107] + "..."
        r_res.text = f"{resumen_corto}  [Ver ficha →]"
        r_res.font.name = tema.font_body_pptx
        r_res.font.size = Pt(10)
        r_res.font.color.rgb = _rgb(tema, tema.muted)

        destino = slides_secciones.get(sec.id)
        if destino is not None:
            tarjeta.click_action.target_slide = destino

    pie = f"{spec.autor}" + (f" · {spec.fuente}" if spec.fuente else "")
    _agregar_barra_navegacion(slide, tema, slide, slide_grafico, slide_hitos, "hub", pie)


def _construir_slide_grafico(
    slide,
    spec: InfografiaSpec,
    tema: TemaVisual,
    slide_hub,
    slide_hitos,
) -> None:
    assert spec.grafico is not None
    _pintar_fondo(slide, tema)
    grafico_spec = spec.grafico

    _agregar_caja_texto(
        slide,
        Inches(0.55),
        Inches(0.35),
        Inches(12.2),
        Inches(0.55),
        grafico_spec.titulo,
        tema.font_display_pptx,
        22,
        _rgb(tema, tema.ink),
        bold=True,
    )
    if grafico_spec.descripcion:
        _agregar_caja_texto(
            slide,
            Inches(0.55),
            Inches(0.92),
            Inches(12.2),
            Inches(0.42),
            grafico_spec.descripcion,
            tema.font_body_pptx,
            12,
            _rgb(tema, tema.muted),
        )

    # Gráfico nativo editable de PowerPoint
    chart_data = CategoryChartData()
    chart_data.categories = [p.etiqueta for p in grafico_spec.puntos]
    serie_nombre = f"Valor ({grafico_spec.unidad})" if grafico_spec.unidad else "Valor"
    chart_data.add_series(serie_nombre, tuple(float(p.valor) for p in grafico_spec.puntos))

    mapa_tipo = {
        "barras": XL_CHART_TYPE.COLUMN_CLUSTERED,
        "dona": XL_CHART_TYPE.DOUGHNUT,
        "linea": XL_CHART_TYPE.LINE_MARKERS,
    }
    tipo_xl = mapa_tipo.get(grafico_spec.tipo, XL_CHART_TYPE.COLUMN_CLUSTERED)

    chart_shape = slide.shapes.add_chart(
        tipo_xl,
        Inches(0.55),
        Inches(1.5),
        Inches(7.7),
        Inches(4.95),
        chart_data,
    )
    chart = chart_shape.chart
    chart.has_legend = grafico_spec.tipo == "dona"
    serie = chart.series[0]
    if grafico_spec.tipo in ("barras", "dona"):
        for idx, pt in enumerate(serie.points):
            color_hex = tema.chart_palette[idx % len(tema.chart_palette)]
            pt.format.fill.solid()
            pt.format.fill.fore_color.rgb = _rgb(tema, color_hex)
    else:
        serie.format.line.color.rgb = _rgb(tema, tema.accent)
        serie.format.line.width = Pt(3)

    # Panel lateral de hallazgos por punto
    panel = _agregar_tarjeta(
        slide,
        Inches(8.5),
        Inches(1.5),
        Inches(4.28),
        Inches(4.95),
        _rgb(tema, tema.surface),
        _rgb(tema, tema.border),
    )
    tf = panel.text_frame
    tf.margin_left = Inches(0.2)
    tf.margin_right = Inches(0.2)
    tf.margin_top = Inches(0.18)

    p0 = tf.paragraphs[0]
    r0 = p0.add_run()
    r0.text = "Desglose de Datos"
    r0.font.name = tema.font_display_pptx
    r0.font.size = Pt(15)
    r0.font.bold = True
    r0.font.color.rgb = _rgb(tema, tema.accent)

    for punto in grafico_spec.puntos:
        p = tf.add_paragraph()
        p.space_before = Pt(10)
        r_et = p.add_run()
        r_et.text = f"{punto.etiqueta}: {punto.valor:g}{grafico_spec.unidad}"
        r_et.font.name = tema.font_body_pptx
        r_et.font.size = Pt(12)
        r_et.font.bold = True
        r_et.font.color.rgb = _rgb(tema, tema.ink)
        if punto.detalle:
            pd = tf.add_paragraph()
            pd.space_before = Pt(2)
            r_det = pd.add_run()
            r_det.text = punto.detalle
            r_det.font.name = tema.font_body_pptx
            r_det.font.size = Pt(10)
            r_det.font.color.rgb = _rgb(tema, tema.muted)

    pie = f"Gráfico nativo editable · {spec.autor}"
    _agregar_barra_navegacion(slide, tema, slide_hub, slide, slide_hitos, "grafico", pie)


def _construir_slide_hitos(
    slide,
    spec: InfografiaSpec,
    tema: TemaVisual,
    slide_hub,
    slide_grafico,
) -> None:
    _pintar_fondo(slide, tema)
    _agregar_caja_texto(
        slide,
        Inches(0.55),
        Inches(0.35),
        Inches(12.2),
        Inches(0.55),
        "Hoja de Ruta y Secuencia de Implementación",
        tema.font_display_pptx,
        22,
        _rgb(tema, tema.ink),
        bold=True,
    )
    _agregar_caja_texto(
        slide,
        Inches(0.55),
        Inches(0.9),
        Inches(12.2),
        Inches(0.38),
        spec.titulo,
        tema.font_body_pptx,
        12,
        _rgb(tema, tema.muted),
    )

    hitos = spec.hitos[:5]
    n = len(hitos)
    if n > 0:
        # Línea conectora horizontal
        _agregar_tarjeta(
            slide,
            Inches(0.85),
            Inches(2.12),
            Inches(11.6),
            Inches(0.06),
            _rgb(tema, tema.accent),
            shape_type=MSO_SHAPE.RECTANGLE,
        )

        gap = 0.22
        total_w = 12.23
        card_w = (total_w - gap * (n - 1)) / n

        for i, hito in enumerate(hitos):
            x = Inches(0.55 + i * (card_w + gap))
            # Nodo circular de fase
            nodo = _agregar_tarjeta(
                slide,
                x + Inches(card_w / 2 - 0.38),
                Inches(1.78),
                Inches(0.76),
                Inches(0.76),
                _rgb(tema, tema.accent),
                shape_type=MSO_SHAPE.OVAL,
            )
            tf_n = nodo.text_frame
            tf_n.vertical_anchor = MSO_ANCHOR.MIDDLE
            pn = tf_n.paragraphs[0]
            pn.alignment = PP_ALIGN.CENTER
            rn = pn.add_run()
            rn.text = f"{i + 1:02d}"
            rn.font.name = tema.font_display_pptx
            rn.font.size = Pt(15)
            rn.font.bold = True
            rn.font.color.rgb = _rgb(tema, tema.accent_ink)

            # Tarjeta de contenido del hito
            card = _agregar_tarjeta(
                slide,
                x,
                Inches(2.75),
                Inches(card_w),
                Inches(3.65),
                _rgb(tema, tema.surface),
                _rgb(tema, tema.border),
            )
            tf = card.text_frame
            tf.margin_left = Inches(0.16)
            tf.margin_right = Inches(0.16)
            tf.margin_top = Inches(0.16)

            p_fase = tf.paragraphs[0]
            rf = p_fase.add_run()
            rf.text = f"{hito.fase}" + (f" · {hito.periodo}" if hito.periodo else "")
            rf.font.name = tema.font_body_pptx
            rf.font.size = Pt(9)
            rf.font.bold = True
            rf.font.color.rgb = _rgb(tema, tema.accent)

            p_tit = tf.add_paragraph()
            p_tit.space_before = Pt(6)
            rt = p_tit.add_run()
            rt.text = hito.titulo
            rt.font.name = tema.font_display_pptx
            rt.font.size = Pt(13)
            rt.font.bold = True
            rt.font.color.rgb = _rgb(tema, tema.ink)

            p_desc = tf.add_paragraph()
            p_desc.space_before = Pt(8)
            rd = p_desc.add_run()
            rd.text = hito.descripcion
            rd.font.name = tema.font_body_pptx
            rd.font.size = Pt(10)
            rd.font.color.rgb = _rgb(tema, tema.muted)

            if hito.impacto:
                p_imp = tf.add_paragraph()
                p_imp.space_before = Pt(10)
                ri = p_imp.add_run()
                ri.text = f"Impacto: {hito.impacto}"
                ri.font.name = tema.font_body_pptx
                ri.font.size = Pt(10)
                ri.font.bold = True
                ri.font.color.rgb = _rgb(tema, tema.success)

    pie = f"Línea de tiempo · {spec.autor}"
    _agregar_barra_navegacion(slide, tema, slide_hub, slide_grafico, slide, "hitos", pie)


def _construir_slide_seccion(
    slide,
    sec: SeccionItem,
    indice: int,
    total: int,
    spec: InfografiaSpec,
    tema: TemaVisual,
    slide_hub,
    slide_grafico,
    slide_hitos,
    slide_anterior,
    slide_siguiente,
) -> None:
    _pintar_fondo(slide, tema)

    # Franja lateral de acento
    _agregar_tarjeta(
        slide,
        Inches(0),
        Inches(0),
        Inches(0.18),
        Inches(6.78),
        _rgb(tema, tema.accent),
        shape_type=MSO_SHAPE.RECTANGLE,
    )

    # Botón volver al tablero
    btn_volver = _agregar_tarjeta(
        slide,
        Inches(0.55),
        Inches(0.32),
        Inches(2.3),
        Inches(0.42),
        _rgb(tema, tema.surface),
        _rgb(tema, tema.accent),
    )
    tf_v = btn_volver.text_frame
    tf_v.vertical_anchor = MSO_ANCHOR.MIDDLE
    pv = tf_v.paragraphs[0]
    pv.alignment = PP_ALIGN.CENTER
    rv = pv.add_run()
    rv.text = "← Volver al Tablero"
    rv.font.name = tema.font_body_pptx
    rv.font.size = Pt(11)
    rv.font.bold = True
    rv.font.color.rgb = _rgb(tema, tema.accent)
    btn_volver.click_action.target_slide = slide_hub

    # Indicador de categoría y numeración
    _agregar_caja_texto(
        slide,
        Inches(3.1),
        Inches(0.38),
        Inches(9.6),
        Inches(0.34),
        f"{sec.categoria.upper()}  ·  BLOQUE {indice} DE {total}",
        tema.font_body_pptx,
        10,
        _rgb(tema, tema.muted),
        bold=True,
        align=PP_ALIGN.RIGHT,
    )

    # Título y métrica
    _agregar_caja_texto(
        slide,
        Inches(0.55),
        Inches(0.95),
        Inches(8.8),
        Inches(0.7),
        sec.titulo,
        tema.font_display_pptx,
        26,
        _rgb(tema, tema.ink),
        bold=True,
    )
    if sec.metrica:
        badge_m = _agregar_tarjeta(
            slide,
            Inches(9.55),
            Inches(0.95),
            Inches(3.2),
            Inches(0.65),
            _rgb(tema, tema.accent_soft),
            _rgb(tema, tema.accent),
        )
        tf_m = badge_m.text_frame
        tf_m.vertical_anchor = MSO_ANCHOR.MIDDLE
        pm = tf_m.paragraphs[0]
        pm.alignment = PP_ALIGN.CENTER
        rm = pm.add_run()
        rm.text = sec.metrica
        rm.font.name = tema.font_display_pptx
        rm.font.size = Pt(15)
        rm.font.bold = True
        rm.font.color.rgb = _rgb(tema, tema.accent)

    # Columna izquierda: Resumen y análisis
    izq = _agregar_tarjeta(
        slide,
        Inches(0.55),
        Inches(1.85),
        Inches(6.2),
        Inches(4.3),
        _rgb(tema, tema.surface),
        _rgb(tema, tema.border),
    )
    tf_i = izq.text_frame
    tf_i.margin_left = Inches(0.24)
    tf_i.margin_right = Inches(0.24)
    tf_i.margin_top = Inches(0.22)

    p_sub1 = tf_i.paragraphs[0]
    r_sub1 = p_sub1.add_run()
    r_sub1.text = "Síntesis Ejecutiva"
    r_sub1.font.name = tema.font_body_pptx
    r_sub1.font.size = Pt(11)
    r_sub1.font.bold = True
    r_sub1.font.color.rgb = _rgb(tema, tema.accent)

    p_res = tf_i.add_paragraph()
    p_res.space_before = Pt(8)
    r_res = p_res.add_run()
    r_res.text = sec.resumen
    r_res.font.name = tema.font_body_pptx
    r_res.font.size = Pt(14)
    r_res.font.bold = True
    r_res.font.color.rgb = _rgb(tema, tema.ink)

    if sec.detalle:
        p_det = tf_i.add_paragraph()
        p_det.space_before = Pt(14)
        r_det = p_det.add_run()
        r_det.text = sec.detalle
        r_det.font.name = tema.font_body_pptx
        r_det.font.size = Pt(12)
        r_det.font.color.rgb = _rgb(tema, tema.muted)

    # Columna derecha: Puntos clave
    der = _agregar_tarjeta(
        slide,
        Inches(7.0),
        Inches(1.85),
        Inches(5.78),
        Inches(4.3),
        _rgb(tema, tema.surface),
        _rgb(tema, tema.border),
    )
    tf_d = der.text_frame
    tf_d.margin_left = Inches(0.24)
    tf_d.margin_right = Inches(0.24)
    tf_d.margin_top = Inches(0.22)

    p_sub2 = tf_d.paragraphs[0]
    r_sub2 = p_sub2.add_run()
    r_sub2.text = "Puntos Clave y Evidencia"
    r_sub2.font.name = tema.font_body_pptx
    r_sub2.font.size = Pt(11)
    r_sub2.font.bold = True
    r_sub2.font.color.rgb = _rgb(tema, tema.secondary)

    puntos = sec.puntos_clave or ["Información complementaria lista para personalizar en PowerPoint."]
    for punto in puntos:
        pp = tf_d.add_paragraph()
        pp.space_before = Pt(12)
        rp = pp.add_run()
        rp.text = f"▸  {punto}"
        rp.font.name = tema.font_body_pptx
        rp.font.size = Pt(12)
        rp.font.color.rgb = _rgb(tema, tema.ink)

    # Botones Anterior / Siguiente entre fichas
    if slide_anterior is not None:
        btn_prev = _agregar_tarjeta(
            slide,
            Inches(9.15),
            Inches(6.25),
            Inches(1.7),
            Inches(0.38),
            _rgb(tema, tema.surface_alt),
            _rgb(tema, tema.border),
        )
        btn_prev.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        pprev = btn_prev.text_frame.paragraphs[0]
        pprev.alignment = PP_ALIGN.CENTER
        rprev = pprev.add_run()
        rprev.text = "← Anterior"
        rprev.font.name = tema.font_body_pptx
        rprev.font.size = Pt(10)
        rprev.font.bold = True
        rprev.font.color.rgb = _rgb(tema, tema.ink)
        btn_prev.click_action.target_slide = slide_anterior

    if slide_siguiente is not None:
        btn_next = _agregar_tarjeta(
            slide,
            Inches(11.05),
            Inches(6.25),
            Inches(1.7),
            Inches(0.38),
            _rgb(tema, tema.accent),
        )
        btn_next.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        pnext = btn_next.text_frame.paragraphs[0]
        pnext.alignment = PP_ALIGN.CENTER
        rnext = pnext.add_run()
        rnext.text = "Siguiente →"
        rnext.font.name = tema.font_body_pptx
        rnext.font.size = Pt(10)
        rnext.font.bold = True
        rnext.font.color.rgb = _rgb(tema, tema.accent_ink)
        btn_next.click_action.target_slide = slide_siguiente

    pie = f"{spec.titulo[:58]} · {spec.autor}"
    _agregar_barra_navegacion(slide, tema, slide_hub, slide_grafico, slide_hitos, "", pie)


def exportar_pptx_bytes(spec: InfografiaSpec) -> bytes:
    """Construye la presentación PowerPoint interactiva y devuelve sus bytes .pptx."""
    tema = obtener_tema(spec.tema)
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    blank_layout = prs.slide_layouts[6]

    # Fase 1: crear todas las diapositivas para disponer de referencias target_slide
    slide_hub = prs.slides.add_slide(blank_layout)
    slide_grafico = prs.slides.add_slide(blank_layout) if spec.grafico else None
    slide_hitos = prs.slides.add_slide(blank_layout) if spec.hitos else None
    slides_secciones_lista = [prs.slides.add_slide(blank_layout) for _ in spec.secciones]
    slides_secciones_mapa = {
        sec.id: slides_secciones_lista[i] for i, sec in enumerate(spec.secciones)
    }

    # Fase 2: poblar diapositivas y cablear interactividad
    _construir_slide_hub(
        slide_hub, spec, tema, slides_secciones_mapa, slide_grafico, slide_hitos
    )

    if slide_grafico is not None:
        _construir_slide_grafico(slide_grafico, spec, tema, slide_hub, slide_hitos)

    if slide_hitos is not None:
        _construir_slide_hitos(slide_hitos, spec, tema, slide_hub, slide_grafico)

    total_sec = len(spec.secciones)
    for idx, sec in enumerate(spec.secciones):
        slide_ant = slides_secciones_lista[idx - 1] if idx > 0 else None
        slide_sig = slides_secciones_lista[idx + 1] if idx + 1 < total_sec else None
        _construir_slide_seccion(
            slides_secciones_lista[idx],
            sec,
            idx + 1,
            total_sec,
            spec,
            tema,
            slide_hub,
            slide_grafico,
            slide_hitos,
            slide_ant,
            slide_sig,
        )

    buffer = io.BytesIO()
    prs.save(buffer)
    return buffer.getvalue()


def guardar_pptx(spec: InfografiaSpec, ruta_salida: str | Path) -> Path:
    """Guarda la presentación PowerPoint interactiva (.pptx) en disco."""
    destino = Path(ruta_salida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(exportar_pptx_bytes(spec))
    return destino
