"""Exportador PowerPoint (.pptx) 16:9 limpio e ilustrado con popups nativos en la misma diapositiva."""

from __future__ import annotations

import io
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml import parse_xml
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
    border_pt: float = 1.0,
    shape_type=MSO_SHAPE.ROUNDED_RECTANGLE,
    corner_radius: float = 0.04,
):
    sh = slide.shapes.add_shape(shape_type, left, top, width, height)
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill_rgb
    sh.shadow.inherit = False
    if shape_type == MSO_SHAPE.ROUNDED_RECTANGLE and len(sh.adjustments) > 0:
        sh.adjustments[0] = corner_radius
    if border_rgb is not None:
        sh.line.color.rgb = border_rgb
        sh.line.width = Pt(border_pt)
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
    font_size: int = 11,
    target_slide=None,
):
    sh = _rect(slide, left, top, width, height, fill_rgb, border_rgb, corner_radius=0.16)
    tf = sh.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(0.1)
    tf.margin_right = Inches(0.1)
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


def _agregar_navegacion_simple(
    slide,
    pal: PaletaEscena,
    slide_anterior=None,
    slide_siguiente=None,
    texto_anterior: str = "← Regresar",
    texto_siguiente: str = "Siguiente →",
) -> None:
    """Agrega únicamente los botones de Regresar y Siguiente, sin barras ni pestañas."""
    if slide_anterior is not None:
        _boton(
            slide,
            Inches(0.6),
            Inches(6.72),
            Inches(1.85),
            Inches(0.46),
            texto_anterior,
            _rgb(pal, pal.surface),
            _rgb(pal, pal.ink),
            _rgb(pal, pal.border),
            font_size=11,
            target_slide=slide_anterior,
        )

    if slide_siguiente is not None:
        _boton(
            slide,
            Inches(10.88),
            Inches(6.72),
            Inches(1.85),
            Inches(0.46),
            texto_siguiente,
            _rgb(pal, pal.accent),
            _rgb(pal, pal.accent_ink),
            font_size=11,
            target_slide=slide_siguiente,
        )


def _inyectar_popup_trigger_xml(
    slide,
    open_btn_id: int,
    popup_card_id: int,
    close_btn_id: int,
) -> None:
    """Inyecta animaciones desencadenadas OpenXML (<p:timing>) 100% nativas de Microsoft PowerPoint.

    - Al iniciar la diapositiva, la ventana emergente y su botón '✕' permanecen ocultos.
    - Clic en '💡 Dato de salud mental' (open_btn_id): aparece la ventana emergente (grpId=0).
    - Clic en '✕' (close_btn_id) o sobre la tarjeta emergente (popup_card_id): se oculta (grpId=1 / grpId=2).
    """
    timing_xml = f"""
    <p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
      <p:tnLst>
        <p:par>
          <p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">
            <p:childTnLst>
              <p:seq concurrent="1" nextAc="seek">
                <p:cTn id="2" restart="whenNotActive" fill="hold" evtFilter="cancelBubble" nodeType="interactiveSeq">
                  <p:stCondLst>
                    <p:cond evt="onClick" delay="0">
                      <p:tgtEl><p:spTgt spid="{open_btn_id}"/></p:tgtEl>
                    </p:cond>
                  </p:stCondLst>
                  <p:endSync evt="end" delay="0"><p:rtn val="all"/></p:endSync>
                  <p:childTnLst>
                    <p:par>
                      <p:cTn id="3" fill="hold">
                        <p:stCondLst><p:cond delay="0"/></p:stCondLst>
                        <p:childTnLst>
                          <p:par>
                            <p:cTn id="4" fill="hold">
                              <p:stCondLst><p:cond delay="0"/></p:stCondLst>
                              <p:childTnLst>
                                <p:par>
                                  <p:cTn id="5" presetID="10" presetClass="entr" presetSubtype="0" fill="hold" grpId="0" nodeType="clickEffect">
                                    <p:stCondLst><p:cond delay="0"/></p:stCondLst>
                                    <p:childTnLst>
                                      <p:set>
                                        <p:cBhvr>
                                          <p:cTn id="6" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>
                                          <p:tgtEl><p:spTgt spid="{popup_card_id}"/></p:tgtEl>
                                          <p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>
                                        </p:cBhvr>
                                        <p:to><p:strVal val="visible"/></p:to>
                                      </p:set>
                                      <p:animEffect transition="in" filter="fade">
                                        <p:cBhvr>
                                          <p:cTn id="7" dur="300"/>
                                          <p:tgtEl><p:spTgt spid="{popup_card_id}"/></p:tgtEl>
                                        </p:cBhvr>
                                      </p:animEffect>
                                    </p:childTnLst>
                                  </p:cTn>
                                </p:par>
                                <p:par>
                                  <p:cTn id="8" presetID="10" presetClass="entr" presetSubtype="0" fill="hold" grpId="0" nodeType="withEffect">
                                    <p:stCondLst><p:cond delay="0"/></p:stCondLst>
                                    <p:childTnLst>
                                      <p:set>
                                        <p:cBhvr>
                                          <p:cTn id="9" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>
                                          <p:tgtEl><p:spTgt spid="{close_btn_id}"/></p:tgtEl>
                                          <p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>
                                        </p:cBhvr>
                                        <p:to><p:strVal val="visible"/></p:to>
                                      </p:set>
                                      <p:animEffect transition="in" filter="fade">
                                        <p:cBhvr>
                                          <p:cTn id="10" dur="300"/>
                                          <p:tgtEl><p:spTgt spid="{close_btn_id}"/></p:tgtEl>
                                        </p:cBhvr>
                                      </p:animEffect>
                                    </p:childTnLst>
                                  </p:cTn>
                                </p:par>
                              </p:childTnLst>
                            </p:cTn>
                          </p:par>
                        </p:childTnLst>
                      </p:cTn>
                    </p:par>
                  </p:childTnLst>
                </p:cTn>
                <p:nextCondLst>
                  <p:cond evt="onClick" delay="0">
                    <p:tgtEl><p:spTgt spid="{open_btn_id}"/></p:tgtEl>
                  </p:cond>
                </p:nextCondLst>
              </p:seq>
              <p:seq concurrent="1" nextAc="seek">
                <p:cTn id="11" restart="whenNotActive" fill="hold" evtFilter="cancelBubble" nodeType="interactiveSeq">
                  <p:stCondLst>
                    <p:cond evt="onClick" delay="0">
                      <p:tgtEl><p:spTgt spid="{close_btn_id}"/></p:tgtEl>
                    </p:cond>
                  </p:stCondLst>
                  <p:endSync evt="end" delay="0"><p:rtn val="all"/></p:endSync>
                  <p:childTnLst>
                    <p:par>
                      <p:cTn id="12" fill="hold">
                        <p:stCondLst><p:cond delay="0"/></p:stCondLst>
                        <p:childTnLst>
                          <p:par>
                            <p:cTn id="13" fill="hold">
                              <p:stCondLst><p:cond delay="0"/></p:stCondLst>
                              <p:childTnLst>
                                <p:par>
                                  <p:cTn id="14" presetID="10" presetClass="exit" presetSubtype="0" fill="hold" grpId="1" nodeType="clickEffect">
                                    <p:stCondLst><p:cond delay="0"/></p:stCondLst>
                                    <p:childTnLst>
                                      <p:animEffect transition="out" filter="fade">
                                        <p:cBhvr>
                                          <p:cTn id="15" dur="220"/>
                                          <p:tgtEl><p:spTgt spid="{popup_card_id}"/></p:tgtEl>
                                        </p:cBhvr>
                                      </p:animEffect>
                                      <p:set>
                                        <p:cBhvr>
                                          <p:cTn id="16" dur="1" fill="hold"><p:stCondLst><p:cond delay="219"/></p:stCondLst></p:cTn>
                                          <p:tgtEl><p:spTgt spid="{popup_card_id}"/></p:tgtEl>
                                          <p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>
                                        </p:cBhvr>
                                        <p:to><p:strVal val="hidden"/></p:to>
                                      </p:set>
                                    </p:childTnLst>
                                  </p:cTn>
                                </p:par>
                                <p:par>
                                  <p:cTn id="17" presetID="10" presetClass="exit" presetSubtype="0" fill="hold" grpId="1" nodeType="withEffect">
                                    <p:stCondLst><p:cond delay="0"/></p:stCondLst>
                                    <p:childTnLst>
                                      <p:animEffect transition="out" filter="fade">
                                        <p:cBhvr>
                                          <p:cTn id="18" dur="220"/>
                                          <p:tgtEl><p:spTgt spid="{close_btn_id}"/></p:tgtEl>
                                        </p:cBhvr>
                                      </p:animEffect>
                                      <p:set>
                                        <p:cBhvr>
                                          <p:cTn id="19" dur="1" fill="hold"><p:stCondLst><p:cond delay="219"/></p:stCondLst></p:cTn>
                                          <p:tgtEl><p:spTgt spid="{close_btn_id}"/></p:tgtEl>
                                          <p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>
                                        </p:cBhvr>
                                        <p:to><p:strVal val="hidden"/></p:to>
                                      </p:set>
                                    </p:childTnLst>
                                  </p:cTn>
                                </p:par>
                              </p:childTnLst>
                            </p:cTn>
                          </p:par>
                        </p:childTnLst>
                      </p:cTn>
                    </p:par>
                  </p:childTnLst>
                </p:cTn>
                <p:nextCondLst>
                  <p:cond evt="onClick" delay="0">
                    <p:tgtEl><p:spTgt spid="{close_btn_id}"/></p:tgtEl>
                  </p:cond>
                </p:nextCondLst>
              </p:seq>
              <p:seq concurrent="1" nextAc="seek">
                <p:cTn id="20" restart="whenNotActive" fill="hold" evtFilter="cancelBubble" nodeType="interactiveSeq">
                  <p:stCondLst>
                    <p:cond evt="onClick" delay="0">
                      <p:tgtEl><p:spTgt spid="{popup_card_id}"/></p:tgtEl>
                    </p:cond>
                  </p:stCondLst>
                  <p:endSync evt="end" delay="0"><p:rtn val="all"/></p:endSync>
                  <p:childTnLst>
                    <p:par>
                      <p:cTn id="21" fill="hold">
                        <p:stCondLst><p:cond delay="0"/></p:stCondLst>
                        <p:childTnLst>
                          <p:par>
                            <p:cTn id="22" fill="hold">
                              <p:stCondLst><p:cond delay="0"/></p:stCondLst>
                              <p:childTnLst>
                                <p:par>
                                  <p:cTn id="23" presetID="10" presetClass="exit" presetSubtype="0" fill="hold" grpId="2" nodeType="clickEffect">
                                    <p:stCondLst><p:cond delay="0"/></p:stCondLst>
                                    <p:childTnLst>
                                      <p:animEffect transition="out" filter="fade">
                                        <p:cBhvr>
                                          <p:cTn id="24" dur="220"/>
                                          <p:tgtEl><p:spTgt spid="{popup_card_id}"/></p:tgtEl>
                                        </p:cBhvr>
                                      </p:animEffect>
                                      <p:set>
                                        <p:cBhvr>
                                          <p:cTn id="25" dur="1" fill="hold"><p:stCondLst><p:cond delay="219"/></p:stCondLst></p:cTn>
                                          <p:tgtEl><p:spTgt spid="{popup_card_id}"/></p:tgtEl>
                                          <p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>
                                        </p:cBhvr>
                                        <p:to><p:strVal val="hidden"/></p:to>
                                      </p:set>
                                    </p:childTnLst>
                                  </p:cTn>
                                </p:par>
                                <p:par>
                                  <p:cTn id="26" presetID="10" presetClass="exit" presetSubtype="0" fill="hold" grpId="2" nodeType="withEffect">
                                    <p:stCondLst><p:cond delay="0"/></p:stCondLst>
                                    <p:childTnLst>
                                      <p:animEffect transition="out" filter="fade">
                                        <p:cBhvr>
                                          <p:cTn id="27" dur="220"/>
                                          <p:tgtEl><p:spTgt spid="{close_btn_id}"/></p:tgtEl>
                                        </p:cBhvr>
                                      </p:animEffect>
                                      <p:set>
                                        <p:cBhvr>
                                          <p:cTn id="28" dur="1" fill="hold"><p:stCondLst><p:cond delay="219"/></p:stCondLst></p:cTn>
                                          <p:tgtEl><p:spTgt spid="{close_btn_id}"/></p:tgtEl>
                                          <p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>
                                        </p:cBhvr>
                                        <p:to><p:strVal val="hidden"/></p:to>
                                      </p:set>
                                    </p:childTnLst>
                                  </p:cTn>
                                </p:par>
                              </p:childTnLst>
                            </p:cTn>
                          </p:par>
                        </p:childTnLst>
                      </p:cTn>
                    </p:par>
                  </p:childTnLst>
                </p:cTn>
                <p:nextCondLst>
                  <p:cond evt="onClick" delay="0">
                    <p:tgtEl><p:spTgt spid="{popup_card_id}"/></p:tgtEl>
                  </p:cond>
                </p:nextCondLst>
              </p:seq>
            </p:childTnLst>
          </p:cTn>
        </p:par>
      </p:tnLst>
      <p:bldLst>
        <p:bldP spid="{popup_card_id}" grpId="0" animBg="1"/>
        <p:bldP spid="{popup_card_id}" grpId="1" animBg="1"/>
        <p:bldP spid="{popup_card_id}" grpId="2" animBg="1"/>
        <p:bldP spid="{close_btn_id}" grpId="0" animBg="1"/>
        <p:bldP spid="{close_btn_id}" grpId="1" animBg="1"/>
        <p:bldP spid="{close_btn_id}" grpId="2" animBg="1"/>
      </p:bldLst>
    </p:timing>
    """
    slide._element.append(parse_xml(timing_xml))


def _construir_portada(
    slide,
    spec: CuentoInfografiaSpec,
    assets_dir: Path,
    primera_pagina,
) -> None:
    pal = spec.escenas[0].paleta
    _pintar_fondo(slide, pal)

    # Franja sutil superior mostrando la transición fría -> cálida
    ancho_franja = 13.333 / len(spec.escenas)
    for idx, esc in enumerate(spec.escenas):
        _rect(
            slide,
            Inches(idx * ancho_franja),
            Inches(0),
            Inches(ancho_franja + 0.02),
            Inches(0.1),
            _rgb(esc.paleta, esc.paleta.accent),
            shape_type=MSO_SHAPE.RECTANGLE,
        )

    # Columna izquierda minimalista: solo título, subtítulo y botón Comenzar
    _texto(
        slide,
        Inches(0.75),
        Inches(1.55),
        Inches(5.85),
        Inches(1.65),
        spec.titulo,
        FONT_DISPLAY,
        38,
        _rgb(pal, pal.ink),
        bold=True,
    )
    _texto(
        slide,
        Inches(0.75),
        Inches(3.45),
        Inches(5.65),
        Inches(1.15),
        spec.subtitulo,
        FONT_BODY,
        14,
        _rgb(pal, pal.muted),
    )
    _boton(
        slide,
        Inches(0.75),
        Inches(4.9),
        Inches(2.8),
        Inches(0.58),
        "Comenzar lectura →",
        _rgb(pal, pal.accent),
        _rgb(pal, pal.accent_ink),
        font_size=13,
        target_slide=primera_pagina,
    )

    # Columna derecha: dos láminas en contraste (madrugada y mañana soleada)
    img1 = assets_dir / spec.escenas[0].imagen_archivo
    img5 = assets_dir / spec.escenas[-1].imagen_archivo
    if img1.exists():
        slide.shapes.add_picture(str(img1), Inches(6.95), Inches(0.65), width=Inches(5.7), height=Inches(3.2))
    if img5.exists():
        slide.shapes.add_picture(str(img5), Inches(6.95), Inches(4.02), width=Inches(5.7), height=Inches(3.2))

    slide.notes_slide.notes_text_frame.text = f"Portada: {spec.titulo}."


def _construir_slide_pagina(
    slide,
    esc: EscenaCuento,
    assets_dir: Path,
    slide_anterior,
    slide_siguiente,
) -> None:
    pal = esc.paleta
    dato = esc.dato_salud
    _pintar_fondo(slide, pal)

    # Franja sutil superior
    _rect(
        slide,
        Inches(0),
        Inches(0),
        SLIDE_W,
        Inches(0.09),
        _rgb(pal, pal.accent),
        shape_type=MSO_SHAPE.RECTANGLE,
    )

    # Cabecera limpia: solo momento del día + título
    _texto(
        slide,
        Inches(0.6),
        Inches(0.28),
        Inches(8.4),
        Inches(0.32),
        esc.etiqueta_tiempo,
        FONT_BODY,
        11,
        _rgb(pal, pal.accent),
        bold=True,
    )
    _texto(
        slide,
        Inches(0.6),
        Inches(0.58),
        Inches(8.5),
        Inches(0.56),
        esc.titulo,
        FONT_DISPLAY,
        25,
        _rgb(pal, pal.ink),
        bold=True,
    )

    # Botón desencadenador de ventana emergente en la misma diapositiva
    btn_dato = _boton(
        slide,
        Inches(9.58),
        Inches(0.45),
        Inches(3.15),
        Inches(0.52),
        "💡 Dato de salud mental",
        _rgb(pal, pal.accent_soft),
        _rgb(pal, pal.accent),
        _rgb(pal, pal.accent),
        font_size=11,
    )

    # Columna izquierda: ilustración protagonista y cita breve
    img_path = assets_dir / esc.imagen_archivo
    if img_path.exists():
        slide.shapes.add_picture(str(img_path), Inches(0.6), Inches(1.32), width=Inches(5.8), height=Inches(3.26))
    else:
        _rect(slide, Inches(0.6), Inches(1.32), Inches(5.8), Inches(3.26), _rgb(pal, pal.surface), _rgb(pal, pal.border))

    cita_box = _rect(
        slide,
        Inches(0.6),
        Inches(4.82),
        Inches(5.8),
        Inches(1.45),
        _rgb(pal, pal.surface),
        _rgb(pal, pal.border),
    )
    tf_c = cita_box.text_frame
    tf_c.margin_left = Inches(0.24)
    tf_c.margin_right = Inches(0.24)
    tf_c.vertical_anchor = MSO_ANCHOR.MIDDLE
    pc = tf_c.paragraphs[0]
    rc = pc.add_run()
    rc.text = f"“{esc.cita_destacada}”"
    rc.font.name = FONT_DISPLAY
    rc.font.size = Pt(12)
    rc.font.italic = True
    rc.font.color.rgb = _rgb(pal, pal.ink)

    # Columna derecha: texto narrativo espacioso y limpio
    tarjeta_texto = _rect(
        slide,
        Inches(6.72),
        Inches(1.32),
        Inches(6.0),
        Inches(4.95),
        _rgb(pal, pal.surface),
        _rgb(pal, pal.border),
        corner_radius=0.035,
    )
    tf = tarjeta_texto.text_frame
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = Inches(0.32)
    tf.margin_right = Inches(0.32)
    tf.margin_top = Inches(0.28)
    tf.margin_bottom = Inches(0.22)

    total_chars = sum(len(p) for p in esc.parrafos)
    size_cuerpo = 11 if total_chars > 950 else 12

    for idx_p, parrafo in enumerate(esc.parrafos):
        p = tf.paragraphs[0] if idx_p == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(12)
        p.line_spacing = 1.22
        r = p.add_run()
        r.text = parrafo
        r.font.name = FONT_BODY
        r.font.size = Pt(size_cuerpo)
        r.font.color.rgb = _rgb(pal, pal.ink)

    # Navegación simple abajo: solo Regresar y Siguiente
    _agregar_navegacion_simple(slide, pal, slide_anterior, slide_siguiente)

    # Ventana emergente compacta sobre el área izquierda (no tapa el texto que estás leyendo)
    popup_card = _rect(
        slide,
        Inches(0.8),
        Inches(1.5),
        Inches(5.4),
        Inches(3.25),
        _rgb(pal, pal.surface_alt if pal.es_oscura else pal.surface),
        _rgb(pal, pal.accent),
        border_pt=1.75,
        corner_radius=0.05,
    )
    tf_p = popup_card.text_frame
    tf_p.vertical_anchor = MSO_ANCHOR.TOP
    tf_p.margin_left = Inches(0.26)
    tf_p.margin_right = Inches(0.55)
    tf_p.margin_top = Inches(0.22)
    tf_p.margin_bottom = Inches(0.18)

    p_etq = tf_p.paragraphs[0]
    p_etq.alignment = PP_ALIGN.LEFT
    r_etq = p_etq.add_run()
    r_etq.text = "DATO DE SALUD MENTAL"
    r_etq.font.name = FONT_BODY
    r_etq.font.size = Pt(9)
    r_etq.font.bold = True
    r_etq.font.color.rgb = _rgb(pal, pal.accent)

    p_tit = tf_p.add_paragraph()
    p_tit.alignment = PP_ALIGN.LEFT
    p_tit.space_before = Pt(4)
    r_tit = p_tit.add_run()
    r_tit.text = dato.titulo
    r_tit.font.name = FONT_DISPLAY
    r_tit.font.size = Pt(16)
    r_tit.font.bold = True
    r_tit.font.color.rgb = _rgb(pal, pal.ink)

    p_sub = tf_p.add_paragraph()
    p_sub.alignment = PP_ALIGN.LEFT
    p_sub.space_before = Pt(8)
    r_cif = p_sub.add_run()
    r_cif.text = f"{dato.cifra_destacada}: " if dato.cifra_destacada.endswith("real") else f"{dato.cifra_destacada} "
    r_cif.font.name = FONT_BODY
    r_cif.font.size = Pt(11)
    r_cif.font.bold = True
    r_cif.font.color.rgb = _rgb(pal, pal.accent)

    r_sub = p_sub.add_run()
    r_sub.text = dato.subtitulo_cifra
    r_sub.font.name = FONT_BODY
    r_sub.font.size = Pt(11)
    r_sub.font.bold = True
    r_sub.font.color.rgb = _rgb(pal, pal.ink)

    p_exp = tf_p.add_paragraph()
    p_exp.alignment = PP_ALIGN.LEFT
    p_exp.space_before = Pt(6)
    r_exp = p_exp.add_run()
    r_exp.text = dato.explicacion
    r_exp.font.name = FONT_BODY
    r_exp.font.size = Pt(11)
    r_exp.font.color.rgb = _rgb(pal, pal.ink)

    p_acc = tf_p.add_paragraph()
    p_acc.alignment = PP_ALIGN.LEFT
    p_acc.space_before = Pt(10)
    r_acc = p_acc.add_run()
    r_acc.text = f"Tip: {dato.accion_practica}"
    r_acc.font.name = FONT_BODY
    r_acc.font.size = Pt(11)
    r_acc.font.bold = True
    r_acc.font.color.rgb = _rgb(pal, pal.accent)

    p_f = tf_p.add_paragraph()
    p_f.alignment = PP_ALIGN.LEFT
    p_f.space_before = Pt(8)
    r_f = p_f.add_run()
    r_f.text = f"Fuente: {dato.fuente}"
    r_f.font.name = FONT_BODY
    r_f.font.size = Pt(9)
    r_f.font.color.rgb = _rgb(pal, pal.muted)

    btn_cerrar = _boton(
        slide,
        Inches(5.72),
        Inches(1.62),
        Inches(0.36),
        Inches(0.36),
        "✕",
        _rgb(pal, pal.accent),
        _rgb(pal, pal.accent_ink),
        font_size=11,
    )

    _inyectar_popup_trigger_xml(slide, btn_dato.shape_id, popup_card.shape_id, btn_cerrar.shape_id)

    slide.notes_slide.notes_text_frame.text = (
        f"{esc.etiqueta_tiempo} — {esc.titulo}\n\n"
        + "\n\n".join(esc.parrafos)
        + f"\n\n[Dato de salud mental] {dato.titulo} ({dato.cifra_destacada}): {dato.explicacion}"
    )


def _construir_slide_reflexion(
    slide,
    spec: CuentoInfografiaSpec,
    assets_dir: Path,
    slide_anterior,
    slide_portada,
) -> None:
    pal = spec.escenas[-1].paleta
    _pintar_fondo(slide, pal)

    _rect(
        slide,
        Inches(0),
        Inches(0),
        SLIDE_W,
        Inches(0.1),
        _rgb(pal, pal.accent),
        shape_type=MSO_SHAPE.RECTANGLE,
    )

    _texto(
        slide,
        Inches(0.65),
        Inches(0.45),
        Inches(12.0),
        Inches(0.32),
        "Cierre",
        FONT_BODY,
        11,
        _rgb(pal, pal.accent),
        bold=True,
    )
    _texto(
        slide,
        Inches(0.65),
        Inches(0.78),
        Inches(12.0),
        Inches(0.65),
        spec.reflexion_final_titulo,
        FONT_DISPLAY,
        28,
        _rgb(pal, pal.ink),
        bold=True,
    )

    caja = _rect(
        slide,
        Inches(0.65),
        Inches(1.65),
        Inches(7.3),
        Inches(4.55),
        _rgb(pal, pal.surface),
        _rgb(pal, pal.border),
        corner_radius=0.035,
    )
    tf = caja.text_frame
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = Inches(0.34)
    tf.margin_right = Inches(0.34)
    tf.margin_top = Inches(0.34)
    for idx, par in enumerate(spec.reflexion_final_parrafos):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(16)
        p.line_spacing = 1.25
        r = p.add_run()
        r.text = par
        r.font.name = FONT_BODY
        r.font.size = Pt(14)
        r.font.color.rgb = _rgb(pal, pal.ink)

    img_calma = assets_dir / spec.escenas[-1].imagen_archivo
    if img_calma.exists():
        slide.shapes.add_picture(str(img_calma), Inches(8.28), Inches(1.65), width=Inches(4.45), height=Inches(2.5))

    _agregar_navegacion_simple(
        slide,
        pal,
        slide_anterior=slide_anterior,
        slide_siguiente=slide_portada,
        texto_anterior="← Regresar",
        texto_siguiente="Volver al inicio",
    )

    slide.notes_slide.notes_text_frame.text = (
        f"{spec.reflexion_final_titulo}\n\n" + "\n\n".join(spec.reflexion_final_parrafos)
    )


def exportar_cuento_pptx_bytes(spec: CuentoInfografiaSpec, assets_dir: Path) -> bytes:
    """Genera un PowerPoint limpio de 7 diapositivas (Portada + 5 páginas con popup nativo + Reflexión)."""
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    blank = prs.slide_layouts[6]

    slide_portada = prs.slides.add_slide(blank)
    slides_paginas = [prs.slides.add_slide(blank) for _ in spec.escenas]
    slide_reflexion = prs.slides.add_slide(blank)

    _construir_portada(slide_portada, spec, assets_dir, slides_paginas[0])

    for idx, esc in enumerate(spec.escenas):
        anterior = slide_portada if idx == 0 else slides_paginas[idx - 1]
        siguiente = slides_paginas[idx + 1] if idx + 1 < len(spec.escenas) else slide_reflexion
        _construir_slide_pagina(slides_paginas[idx], esc, assets_dir, anterior, siguiente)

    _construir_slide_reflexion(slide_reflexion, spec, assets_dir, slides_paginas[-1], slide_portada)

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
