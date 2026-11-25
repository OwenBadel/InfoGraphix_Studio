"""Exportador de infografías interactivas en HTML5 autocontenido (offline-ready)."""

from __future__ import annotations

import html
import json
from pathlib import Path

from ..domain.models import InfografiaSpec
from ..domain.themes import TEMAS, obtener_tema


def _json_seguro_en_script(datos: object) -> str:
    """Serializa JSON evitando cierre accidental de etiqueta </script>."""
    raw = json.dumps(datos, ensure_ascii=False)
    return raw.replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def _serializar_temas_js() -> str:
    mapa = {}
    for tema_id, t in TEMAS.items():
        mapa[tema_id] = {
            "nombre": t.nombre,
            "bg": t.bg,
            "surface": t.surface,
            "surfaceAlt": t.surface_alt,
            "ink": t.ink,
            "muted": t.muted,
            "border": t.border,
            "accent": t.accent,
            "accentInk": t.accent_ink,
            "accentSoft": t.accent_soft,
            "secondary": t.secondary,
            "success": t.success,
            "warning": t.warning,
            "chartPalette": list(t.chart_palette),
            "fontDisplay": t.font_display_html,
            "fontBody": t.font_body_html,
            "fontMono": t.font_mono_html,
        }
    return _json_seguro_en_script(mapa)


def exportar_html(spec: InfografiaSpec) -> str:
    """Genera un archivo HTML5 interactivo autocontenido a partir de InfografiaSpec."""
    tema = obtener_tema(spec.tema)
    titulo_esc = html.escape(spec.titulo)
    subtitulo_esc = html.escape(spec.subtitulo)
    categoria_esc = html.escape(spec.categoria)
    autor_esc = html.escape(spec.autor)
    fuente_esc = html.escape(spec.fuente)

    datos_json = _json_seguro_en_script(spec.model_dump())
    temas_json = _serializar_temas_js()

    opciones_tema_html = "\n".join(
        f'<option value="{tid}"{" selected" if tid == spec.tema else ""}>{html.escape(t.nombre)}</option>'
        for tid, t in TEMAS.items()
    )

    return f"""<!DOCTYPE html>
<html lang="es" data-tema="{html.escape(spec.tema)}" data-plantilla="{html.escape(spec.plantilla)}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{titulo_esc}</title>
  <style>
    :root {{
      --bg: {tema.bg};
      --surface: {tema.surface};
      --surface-alt: {tema.surface_alt};
      --ink: {tema.ink};
      --muted: {tema.muted};
      --border: {tema.border};
      --accent: {tema.accent};
      --accent-ink: {tema.accent_ink};
      --accent-soft: {tema.accent_soft};
      --secondary: {tema.secondary};
      --success: {tema.success};
      --warning: {tema.warning};
      --font-display: {tema.font_display_html};
      --font-body: {tema.font_body_html};
      --font-mono: {tema.font_mono_html};
      --radius: 12px;
      --radius-sm: 8px;
      --max-w: 1180px;
    }}

    *, *::before, *::after {{
      box-sizing: border-box;
    }}

    html {{
      scroll-behavior: smooth;
    }}

    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: var(--font-body);
      line-height: 1.55;
      -webkit-font-smoothing: antialiased;
      transition: background-color 0.2s ease, color 0.2s ease;
    }}

    .infografia-shell {{
      max-width: var(--max-w);
      margin: 0 auto;
      padding: clamp(1rem, 2.5vw, 2.25rem);
      display: flex;
      flex-direction: column;
      gap: clamp(1.25rem, 2.6vw, 2.25rem);
    }}

    .barra-utilidades {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 0.75rem;
      padding: 0.75rem 1rem;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
    }}

    .etiqueta-categoria {{
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
      font-family: var(--font-mono);
      font-size: 0.78rem;
      font-weight: 600;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--accent);
      background: var(--accent-soft);
      padding: 0.35rem 0.7rem;
      border-radius: 999px;
    }}

    .controles-barra {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 0.5rem;
    }}

    .btn, .select-tema {{
      min-height: 44px;
      padding: 0.5rem 0.9rem;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border);
      background: var(--surface-alt);
      color: var(--ink);
      font-family: var(--font-body);
      font-size: 0.875rem;
      font-weight: 600;
      cursor: pointer;
      transition: border-color 0.15s ease, background-color 0.15s ease, transform 0.15s ease;
    }}

    .btn:hover, .select-tema:hover {{
      border-color: var(--accent);
    }}

    .btn:focus-visible, .select-tema:focus-visible, .chip-filtro:focus-visible, .kpi-card:focus-visible, .hito-btn:focus-visible {{
      outline: 2px solid var(--accent);
      outline-offset: 2px;
    }}

    .btn-primario {{
      background: var(--accent);
      color: var(--accent-ink);
      border-color: var(--accent);
    }}

    .hero {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-top: 4px solid var(--accent);
      border-radius: var(--radius);
      padding: clamp(1.35rem, 3vw, 2.5rem);
      display: flex;
      flex-direction: column;
      gap: 0.85rem;
    }}

    .hero h1 {{
      margin: 0;
      font-family: var(--font-display);
      font-size: clamp(1.7rem, 3.6vw, 2.85rem);
      line-height: 1.12;
      letter-spacing: -0.02em;
      max-width: 28ch;
    }}

    .hero p {{
      margin: 0;
      color: var(--muted);
      font-size: clamp(0.98rem, 1.35vw, 1.15rem);
      max-width: 68ch;
    }}

    .hero-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      padding-top: 0.5rem;
      border-top: 1px solid var(--border);
      font-size: 0.85rem;
      color: var(--muted);
    }}

    .kpis-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr));
      gap: 1rem;
    }}

    .kpi-card {{
      text-align: left;
      width: 100%;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1.15rem 1.2rem;
      cursor: pointer;
      color: var(--ink);
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
      transition: border-color 0.15s ease, transform 0.15s ease;
    }}

    .kpi-card:hover {{
      border-color: var(--accent);
      transform: translateY(-2px);
    }}

    .kpi-etiqueta {{
      font-size: 0.82rem;
      font-weight: 600;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    .kpi-valor {{
      font-family: var(--font-display);
      font-size: clamp(1.65rem, 2.8vw, 2.25rem);
      font-weight: 700;
      font-variant-numeric: tabular-nums;
      line-height: 1.1;
    }}

    .kpi-delta {{
      font-family: var(--font-mono);
      font-size: 0.8rem;
      font-weight: 600;
    }}

    .kpi-delta.positiva {{ color: var(--success); }}
    .kpi-delta.neutra {{ color: var(--secondary); }}
    .kpi-delta.alerta {{ color: var(--warning); }}

    .kpi-detalle {{
      margin-top: 0.45rem;
      padding-top: 0.5rem;
      border-top: 1px dashed var(--border);
      font-size: 0.85rem;
      color: var(--muted);
      display: none;
    }}

    .kpi-card[aria-expanded="true"] .kpi-detalle {{
      display: block;
    }}

    .bloque {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: clamp(1.15rem, 2.4vw, 1.85rem);
      display: flex;
      flex-direction: column;
      gap: 1.1rem;
    }}

    .bloque-cabecera {{
      display: flex;
      flex-wrap: wrap;
      align-items: flex-end;
      justify-content: space-between;
      gap: 0.75rem;
    }}

    .bloque-cabecera h2 {{
      margin: 0;
      font-family: var(--font-display);
      font-size: clamp(1.25rem, 2.1vw, 1.65rem);
      line-height: 1.2;
    }}

    .bloque-cabecera p {{
      margin: 0.25rem 0 0;
      color: var(--muted);
      font-size: 0.92rem;
      max-width: 65ch;
    }}

    .filtros-wrap {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 0.5rem;
    }}

    .chip-filtro {{
      min-height: 44px;
      padding: 0.4rem 0.9rem;
      border-radius: 999px;
      border: 1px solid var(--border);
      background: var(--surface-alt);
      color: var(--ink);
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
    }}

    .chip-filtro.activo {{
      background: var(--accent);
      color: var(--accent-ink);
      border-color: var(--accent);
    }}

    .input-buscar {{
      min-height: 44px;
      padding: 0.45rem 0.85rem;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border);
      background: var(--bg);
      color: var(--ink);
      font-size: 0.88rem;
      min-width: 210px;
      max-width: 100%;
    }}

    .secciones-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(min(100%, 300px), 1fr));
      gap: 1rem;
    }}

    .seccion-card {{
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 1.1rem;
      display: flex;
      flex-direction: column;
      gap: 0.65rem;
      transition: border-color 0.15s ease;
    }}

    .seccion-card:hover {{
      border-color: var(--accent);
    }}

    .seccion-top {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
    }}

    .badge-cat {{
      font-family: var(--font-mono);
      font-size: 0.74rem;
      font-weight: 600;
      color: var(--accent);
      background: var(--accent-soft);
      padding: 0.2rem 0.55rem;
      border-radius: 999px;
    }}

    .badge-metrica {{
      font-family: var(--font-mono);
      font-size: 0.78rem;
      font-weight: 700;
      color: var(--secondary);
      font-variant-numeric: tabular-nums;
    }}

    .seccion-card h3 {{
      margin: 0;
      font-family: var(--font-display);
      font-size: 1.12rem;
      line-height: 1.25;
    }}

    .seccion-card p {{
      margin: 0;
      font-size: 0.92rem;
      color: var(--muted);
    }}

    .btn-expandir {{
      align-self: flex-start;
      min-height: 44px;
      padding: 0.4rem 0.8rem;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border);
      background: var(--surface);
      color: var(--ink);
      font-size: 0.84rem;
      font-weight: 600;
      cursor: pointer;
    }}

    .seccion-detalle {{
      display: none;
      padding-top: 0.75rem;
      border-top: 1px solid var(--border);
      font-size: 0.9rem;
      color: var(--ink);
    }}

    .seccion-card.abierta .seccion-detalle {{
      display: flex;
      flex-direction: column;
      gap: 0.55rem;
    }}

    .puntos-lista {{
      margin: 0;
      padding-left: 1.15rem;
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
      color: var(--muted);
    }}

    .grafico-layout {{
      display: grid;
      grid-template-columns: minmax(0, 1.7fr) minmax(0, 1fr);
      gap: 1.25rem;
      align-items: center;
    }}

    .svg-contenedor {{
      width: 100%;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 0.85rem;
      position: relative;
    }}

    .svg-contenedor svg {{
      width: 100%;
      height: auto;
      display: block;
    }}

    .panel-dato-activo {{
      background: var(--bg);
      border: 1px solid var(--border);
      border-left: 4px solid var(--accent);
      border-radius: var(--radius-sm);
      padding: 1.1rem;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }}

    .panel-dato-activo .dato-etiqueta {{
      font-family: var(--font-mono);
      font-size: 0.78rem;
      text-transform: uppercase;
      color: var(--muted);
    }}

    .panel-dato-activo .dato-valor {{
      font-family: var(--font-display);
      font-size: clamp(1.6rem, 2.5vw, 2.1rem);
      font-weight: 700;
      color: var(--accent);
      font-variant-numeric: tabular-nums;
    }}

    .leyenda-datos {{
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
      margin-top: 0.5rem;
    }}

    .leyenda-item {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
      min-height: 44px;
      padding: 0.4rem 0.65rem;
      border-radius: var(--radius-sm);
      border: 1px solid transparent;
      background: var(--surface);
      color: var(--ink);
      font-size: 0.86rem;
      cursor: pointer;
      text-align: left;
    }}

    .leyenda-item.activo, .leyenda-item:hover {{
      border-color: var(--accent);
    }}

    .leyenda-dot {{
      width: 10px;
      height: 10px;
      border-radius: 50%;
      flex-shrink: 0;
    }}

    .timeline-nav {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(min(100%, 170px), 1fr));
      gap: 0.65rem;
    }}

    .hito-btn {{
      min-height: 56px;
      text-align: left;
      padding: 0.75rem 0.9rem;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border);
      background: var(--bg);
      color: var(--ink);
      cursor: pointer;
      display: flex;
      flex-direction: column;
      gap: 0.2rem;
    }}

    .hito-btn.activo {{
      background: var(--accent);
      color: var(--accent-ink);
      border-color: var(--accent);
    }}

    .hito-btn .hito-fase {{
      font-family: var(--font-mono);
      font-size: 0.74rem;
      opacity: 0.85;
    }}

    .hito-btn .hito-titulo {{
      font-weight: 700;
      font-size: 0.9rem;
    }}

    .hito-detalle {{
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 1.2rem;
      display: flex;
      flex-direction: column;
      gap: 0.55rem;
    }}

    .hito-detalle-top {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
    }}

    .hito-impacto {{
      font-family: var(--font-mono);
      font-size: 0.82rem;
      font-weight: 600;
      color: var(--success);
      background: var(--surface);
      border: 1px solid var(--border);
      padding: 0.25rem 0.65rem;
      border-radius: 999px;
    }}

    .pie-pagina {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 0.75rem;
      padding: 0.9rem 0.25rem;
      border-top: 1px solid var(--border);
      font-size: 0.84rem;
      color: var(--muted);
    }}

    .vacio {{
      padding: 1.25rem;
      text-align: center;
      color: var(--muted);
      border: 1px dashed var(--border);
      border-radius: var(--radius-sm);
    }}

    @media (max-width: 820px) {{
      .grafico-layout {{
        grid-template-columns: 1fr;
      }}
    }}

    @media (prefers-reduced-motion: reduce) {{
      *, *::before, *::after {{
        animation: none !important;
        transition: none !important;
        scroll-behavior: auto !important;
      }}
    }}

    @media print {{
      .barra-utilidades, .filtros-wrap, .btn-expandir {{
        display: none !important;
      }}
      .seccion-detalle, .kpi-detalle {{
        display: block !important;
      }}
      body {{
        background: #ffffff;
        color: #111111;
      }}
    }}
  </style>
</head>
<body>
  <main class="infografia-shell" id="infografia-root">
    <nav class="barra-utilidades" aria-label="Controles de la infografía">
      <span class="etiqueta-categoria">{categoria_esc}</span>
      <div class="controles-barra">
        <label for="selector-tema" class="sr-only" style="position:absolute;width:1px;height:1px;overflow:hidden;">Tema visual</label>
        <select id="selector-tema" class="select-tema" aria-label="Cambiar tema visual">
          {opciones_tema_html}
        </select>
        <button type="button" class="btn" id="btn-expandir-todo">Expandir todo</button>
        <button type="button" class="btn" id="btn-pantalla-completa">Presentación</button>
        <button type="button" class="btn btn-primario" id="btn-imprimir">Imprimir / PDF</button>
      </div>
    </nav>

    <header class="hero">
      <h1>{titulo_esc}</h1>
      <p>{subtitulo_esc}</p>
      <div class="hero-meta">
        <span><strong>Autor:</strong> {autor_esc}</span>
        {f'<span><strong>Fuente:</strong> {fuente_esc}</span>' if fuente_esc else ''}
      </div>
    </header>

    <section id="bloque-kpis" aria-label="Indicadores clave"></section>
    <section id="bloque-secciones" class="bloque" aria-label="Secciones interactivas"></section>
    <section id="bloque-grafico" class="bloque" aria-label="Visualización de datos"></section>
    <section id="bloque-hitos" class="bloque" aria-label="Línea de tiempo interactiva"></section>

    <footer class="pie-pagina">
      <span>{autor_esc}</span>
      <span>Infografía interactiva HTML5 · Navegación por clic y teclado</span>
    </footer>
  </main>

  <script>
    const SPEC = {datos_json};
    const TEMAS = {temas_json};

    const estado = {{
      tema: SPEC.tema || "swiss_cobalt",
      categoriaActiva: "Todas",
      busqueda: "",
      todoExpandido: false,
      puntoGraficoActivo: 0,
      hitoActivo: 0,
    }};

    function esc(texto) {{
      return String(texto ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
    }}

    function aplicarTema(temaId) {{
      const t = TEMAS[temaId] || TEMAS.swiss_cobalt;
      estado.tema = temaId;
      const r = document.documentElement.style;
      r.setProperty("--bg", t.bg);
      r.setProperty("--surface", t.surface);
      r.setProperty("--surface-alt", t.surfaceAlt);
      r.setProperty("--ink", t.ink);
      r.setProperty("--muted", t.muted);
      r.setProperty("--border", t.border);
      r.setProperty("--accent", t.accent);
      r.setProperty("--accent-ink", t.accentInk);
      r.setProperty("--accent-soft", t.accentSoft);
      r.setProperty("--secondary", t.secondary);
      r.setProperty("--success", t.success);
      r.setProperty("--warning", t.warning);
      r.setProperty("--font-display", t.fontDisplay);
      r.setProperty("--font-body", t.fontBody);
      r.setProperty("--font-mono", t.fontMono);
      renderGrafico();
    }}

    function renderKpis() {{
      const cont = document.getElementById("bloque-kpis");
      if (!SPEC.kpis || SPEC.kpis.length === 0) {{
        cont.style.display = "none";
        return;
      }}
      cont.innerHTML = `<div class="kpis-grid">${{SPEC.kpis.map((k, idx) => `
        <button type="button" class="kpi-card" aria-expanded="false" data-kpi="${{idx}}">
          <span class="kpi-etiqueta">${{esc(k.etiqueta)}}</span>
          <span class="kpi-valor">${{esc(k.valor)}}</span>
          ${{k.delta ? `<span class="kpi-delta ${{esc(k.tendencia || 'positiva')}}">${{esc(k.delta)}}</span>` : ""}}
          ${{k.detalle ? `<span class="kpi-detalle">${{esc(k.detalle)}}</span>` : ""}}
        </button>
      `).join("")}}</div>`;

      cont.querySelectorAll(".kpi-card").forEach((btn) => {{
        btn.addEventListener("click", () => {{
          const abierto = btn.getAttribute("aria-expanded") === "true";
          btn.setAttribute("aria-expanded", String(!abierto));
        }});
      }});
    }}

    function renderSecciones() {{
      const cont = document.getElementById("bloque-secciones");
      const categorias = ["Todas", ...Array.from(new Set(SPEC.secciones.map((s) => s.categoria)))];
      const filtradas = SPEC.secciones.filter((s) => {{
        const okCat = estado.categoriaActiva === "Todas" || s.categoria === estado.categoriaActiva;
        const q = estado.busqueda.trim().toLowerCase();
        const texto = `${{s.titulo}} ${{s.resumen}} ${{s.detalle}} ${{(s.puntos_clave || []).join(" ")}}`.toLowerCase();
        const okBusq = !q || texto.includes(q);
        return okCat && okBusq;
      }});

      cont.innerHTML = `
        <div class="bloque-cabecera">
          <div>
            <h2>Exploración Interactiva por Pilar</h2>
            <p>Filtra por categoría o despliega cada tarjeta para consultar hallazgos y puntos clave.</p>
          </div>
          <div class="filtros-wrap">
            ${{categorias.map((c) => `
              <button type="button" class="chip-filtro ${{c === estado.categoriaActiva ? "activo" : ""}}" data-cat="${{esc(c)}}">${{esc(c)}}</button>
            `).join("")}}
            <input type="search" class="input-buscar" id="buscador-secciones" placeholder="Buscar contenido..." value="${{esc(estado.busqueda)}}" aria-label="Buscar secciones">
          </div>
        </div>
        ${{filtradas.length === 0
          ? `<div class="vacio">No se encontraron bloques que coincidan con el filtro actual.</div>`
          : `<div class="secciones-grid">${{filtradas.map((s) => `
            <article class="seccion-card ${{estado.todoExpandido ? "abierta" : ""}}" data-sec-id="${{esc(s.id)}}">
              <div class="seccion-top">
                <span class="badge-cat">${{esc(s.categoria)}}</span>
                ${{s.metrica ? `<span class="badge-metrica">${{esc(s.metrica)}}</span>` : ""}}
              </div>
              <h3>${{esc(s.titulo)}}</h3>
              <p>${{esc(s.resumen)}}</p>
              <button type="button" class="btn-expandir" aria-expanded="${{estado.todoExpandido ? "true" : "false"}}">
                ${{estado.todoExpandido ? "Ocultar detalle" : "Ver detalle"}}
              </button>
              <div class="seccion-detalle">
                ${{s.detalle ? `<p>${{esc(s.detalle)}}</p>` : ""}}
                ${{s.puntos_clave && s.puntos_clave.length ? `<ul class="puntos-lista">${{s.puntos_clave.map((p) => `<li>${{esc(p)}}</li>`).join("")}}</ul>` : ""}}
              </div>
            </article>
          `).join("")}}</div>`
        }}
      `;

      cont.querySelectorAll(".chip-filtro").forEach((chip) => {{
        chip.addEventListener("click", () => {{
          estado.categoriaActiva = chip.getAttribute("data-cat") || "Todas";
          renderSecciones();
        }});
      }});

      const input = document.getElementById("buscador-secciones");
      if (input) {{
        input.addEventListener("input", (e) => {{
          estado.busqueda = e.target.value;
          renderSecciones();
        }});
      }}

      cont.querySelectorAll(".btn-expandir").forEach((btn) => {{
        btn.addEventListener("click", () => {{
          const card = btn.closest(".seccion-card");
          const abierta = card.classList.toggle("abierta");
          btn.setAttribute("aria-expanded", String(abierta));
          btn.textContent = abierta ? "Ocultar detalle" : "Ver detalle";
        }});
      }});
    }}

    function construirSvgGrafico(grafico, paleta) {{
      const puntos = grafico.puntos || [];
      if (puntos.length === 0) return "";
      const unidad = grafico.unidad || "";
      const maxVal = Math.max(...puntos.map((p) => Number(p.valor) || 0), 1);

      if (grafico.tipo === "dona") {{
        const total = puntos.reduce((acc, p) => acc + (Number(p.valor) || 0), 0) || 1;
        const cx = 180, cy = 140, r = 92, strokeW = 36;
        const circ = 2 * Math.PI * r;
        let offset = 0;
        const arcos = puntos.map((p, i) => {{
          const frac = (Number(p.valor) || 0) / total;
          const dash = frac * circ;
          const color = paleta[i % paleta.length];
          const activo = i === estado.puntoGraficoActivo;
          const seg = `<circle cx="${{cx}}" cy="${{cy}}" r="${{r}}" fill="none" stroke="${{color}}" stroke-width="${{activo ? strokeW + 8 : strokeW}}" stroke-dasharray="${{dash}} ${{circ - dash}}" stroke-dashoffset="${{-offset}}" transform="rotate(-90 ${{cx}} ${{cy}})" data-punto-idx="${{i}}" style="cursor:pointer;transition:stroke-width 0.15s ease;"/>`;
          offset += dash;
          return seg;
        }}).join("");
        const activoP = puntos[estado.puntoGraficoActivo] || puntos[0];
        return `<svg viewBox="0 0 360 280" role="img" aria-label="${{esc(grafico.titulo)}}">
          ${{arcos}}
          <text x="${{cx}}" y="${{cy - 4}}" text-anchor="middle" fill="var(--ink)" font-size="22" font-weight="700" font-family="var(--font-display)">${{esc(activoP.valor)}}${{esc(unidad)}}</text>
          <text x="${{cx}}" y="${{cy + 18}}" text-anchor="middle" fill="var(--muted)" font-size="12" font-family="var(--font-body)">${{esc(activoP.etiqueta)}}</text>
        </svg>`;
      }}

      if (grafico.tipo === "linea") {{
        const W = 560, H = 260, padL = 46, padR = 24, padT = 24, padB = 42;
        const ancho = W - padL - padR;
        const alto = H - padT - padB;
        const coords = puntos.map((p, i) => {{
          const x = padL + (puntos.length === 1 ? ancho / 2 : (i / (puntos.length - 1)) * ancho);
          const y = padT + alto - ((Number(p.valor) || 0) / maxVal) * alto;
          return {{ x, y, p, i }};
        }});
        const poly = coords.map((c) => `${{c.x.toFixed(1)}},${{c.y.toFixed(1)}}`).join(" ");
        const grid = [0, 0.25, 0.5, 0.75, 1].map((f) => {{
          const y = padT + alto - f * alto;
          return `<line x1="${{padL}}" y1="${{y}}" x2="${{W - padR}}" y2="${{y}}" stroke="var(--border)" stroke-dasharray="3 3" stroke-width="1"/>`;
        }}).join("");
        const nodos = coords.map((c) => {{
          const activo = c.i === estado.puntoGraficoActivo;
          return `
            <g data-punto-idx="${{c.i}}" style="cursor:pointer;">
              <circle cx="${{c.x}}" cy="${{c.y}}" r="${{activo ? 9 : 6}}" fill="${{activo ? paleta[0] : "var(--surface)"}}" stroke="${{paleta[0]}}" stroke-width="3"/>
              <text x="${{c.x}}" y="${{c.y - 14}}" text-anchor="middle" fill="var(--ink)" font-size="11" font-weight="700" font-family="var(--font-mono)">${{esc(c.p.valor)}}${{esc(unidad)}}</text>
              <text x="${{c.x}}" y="${{H - 14}}" text-anchor="middle" fill="var(--muted)" font-size="11" font-family="var(--font-body)">${{esc(c.p.etiqueta)}}</text>
            </g>`;
        }}).join("");
        return `<svg viewBox="0 0 ${{W}} ${{H}}" role="img" aria-label="${{esc(grafico.titulo)}}">
          ${{grid}}
          <polyline fill="none" stroke="${{paleta[0]}}" stroke-width="3" points="${{poly}}"/>
          ${{nodos}}
        </svg>`;
      }}

      // Barras por defecto
      const W = 560, H = 270, padL = 24, padR = 24, padT = 30, padB = 46;
      const ancho = W - padL - padR;
      const alto = H - padT - padB;
      const step = ancho / puntos.length;
      const barW = Math.min(64, step * 0.62);
      const barras = puntos.map((p, i) => {{
        const val = Number(p.valor) || 0;
        const h = Math.max(6, (val / maxVal) * alto);
        const x = padL + i * step + (step - barW) / 2;
        const y = padT + alto - h;
        const color = paleta[i % paleta.length];
        const activo = i === estado.puntoGraficoActivo;
        return `
          <g data-punto-idx="${{i}}" style="cursor:pointer;">
            <rect x="${{x}}" y="${{y}}" width="${{barW}}" height="${{h}}" rx="6" fill="${{color}}" opacity="${{activo ? 1 : 0.72}}"/>
            <text x="${{x + barW / 2}}" y="${{y - 8}}" text-anchor="middle" fill="var(--ink)" font-size="12" font-weight="700" font-family="var(--font-mono)">${{esc(val)}}${{esc(unidad)}}</text>
            <text x="${{x + barW / 2}}" y="${{H - 16}}" text-anchor="middle" fill="var(--muted)" font-size="11" font-family="var(--font-body)">${{esc(p.etiqueta)}}</text>
          </g>`;
      }}).join("");
      return `<svg viewBox="0 0 ${{W}} ${{H}}" role="img" aria-label="${{esc(grafico.titulo)}}">
        <line x1="${{padL}}" y1="${{padT + alto}}" x2="${{W - padR}}" y2="${{padT + alto}}" stroke="var(--border)" stroke-width="1.5"/>
        ${{barras}}
      </svg>`;
    }}

    function renderGrafico() {{
      const cont = document.getElementById("bloque-grafico");
      if (!SPEC.grafico || !SPEC.grafico.puntos || SPEC.grafico.puntos.length === 0) {{
        cont.style.display = "none";
        return;
      }}
      cont.style.display = "flex";
      const t = TEMAS[estado.tema] || TEMAS.swiss_cobalt;
      const paleta = t.chartPalette;
      const puntos = SPEC.grafico.puntos;
      if (estado.puntoGraficoActivo >= puntos.length) estado.puntoGraficoActivo = 0;
      const activo = puntos[estado.puntoGraficoActivo];
      const unidad = SPEC.grafico.unidad || "";

      cont.innerHTML = `
        <div class="bloque-cabecera">
          <div>
            <h2>${{esc(SPEC.grafico.titulo)}}</h2>
            ${{SPEC.grafico.descripcion ? `<p>${{esc(SPEC.grafico.descripcion)}}</p>` : ""}}
          </div>
        </div>
        <div class="grafico-layout">
          <div class="svg-contenedor">${{construirSvgGrafico(SPEC.grafico, paleta)}}</div>
          <div class="panel-dato-activo">
            <span class="dato-etiqueta">Dato seleccionado</span>
            <strong class="dato-valor">${{esc(activo.valor)}}${{esc(unidad)}}</strong>
            <div><strong>${{esc(activo.etiqueta)}}</strong></div>
            <p style="margin:0;color:var(--muted);font-size:0.9rem;">${{esc(activo.detalle || "Haz clic en otro elemento del gráfico para comparar.")}}</p>
            <div class="leyenda-datos">
              ${{puntos.map((p, i) => `
                <button type="button" class="leyenda-item ${{i === estado.puntoGraficoActivo ? "activo" : ""}}" data-punto-idx="${{i}}">
                  <span style="display:flex;align-items:center;gap:0.5rem;">
                    <span class="leyenda-dot" style="background:${{paleta[i % paleta.length]}}"></span>
                    <span>${{esc(p.etiqueta)}}</span>
                  </span>
                  <strong style="font-family:var(--font-mono);">${{esc(p.valor)}}${{esc(unidad)}}</strong>
                </button>
              `).join("")}}
            </div>
          </div>
        </div>
      `;

      cont.querySelectorAll("[data-punto-idx]").forEach((el) => {{
        el.addEventListener("click", () => {{
          estado.puntoGraficoActivo = Number(el.getAttribute("data-punto-idx")) || 0;
          renderGrafico();
        }});
      }});
    }}

    function renderHitos() {{
      const cont = document.getElementById("bloque-hitos");
      if (!SPEC.hitos || SPEC.hitos.length === 0) {{
        cont.style.display = "none";
        return;
      }}
      cont.style.display = "flex";
      if (estado.hitoActivo >= SPEC.hitos.length) estado.hitoActivo = 0;
      const h = SPEC.hitos[estado.hitoActivo];

      cont.innerHTML = `
        <div class="bloque-cabecera">
          <div>
            <h2>Hoja de Ruta y Secuencia Interactiva</h2>
            <p>Selecciona cada fase o utiliza las teclas ← / → para recorrer la evolución.</p>
          </div>
          <div class="controles-barra">
            <button type="button" class="btn" id="hito-prev">← Anterior</button>
            <button type="button" class="btn" id="hito-next">Siguiente →</button>
          </div>
        </div>
        <div class="timeline-nav">
          ${{SPEC.hitos.map((item, i) => `
            <button type="button" class="hito-btn ${{i === estado.hitoActivo ? "activo" : ""}}" data-hito-idx="${{i}}">
              <span class="hito-fase">${{esc(item.fase)}} ${{item.periodo ? "· " + esc(item.periodo) : ""}}</span>
              <span class="hito-titulo">${{esc(item.titulo)}}</span>
            </button>
          `).join("")}}
        </div>
        <div class="hito-detalle">
          <div class="hito-detalle-top">
            <h3 style="margin:0;font-family:var(--font-display);font-size:1.25rem;">${{esc(h.fase)}}: ${{esc(h.titulo)}}</h3>
            ${{h.impacto ? `<span class="hito-impacto">${{esc(h.impacto)}}</span>` : ""}}
          </div>
          ${{h.periodo ? `<div style="font-family:var(--font-mono);font-size:0.82rem;color:var(--muted);">Periodo: ${{esc(h.periodo)}}</div>` : ""}}
          <p style="margin:0;color:var(--ink);font-size:0.96rem;">${{esc(h.descripcion)}}</p>
        </div>
      `;

      cont.querySelectorAll(".hito-btn").forEach((btn) => {{
        btn.addEventListener("click", () => {{
          estado.hitoActivo = Number(btn.getAttribute("data-hito-idx")) || 0;
          renderHitos();
        }});
      }});

      document.getElementById("hito-prev")?.addEventListener("click", () => {{
        estado.hitoActivo = (estado.hitoActivo - 1 + SPEC.hitos.length) % SPEC.hitos.length;
        renderHitos();
      }});
      document.getElementById("hito-next")?.addEventListener("click", () => {{
        estado.hitoActivo = (estado.hitoActivo + 1) % SPEC.hitos.length;
        renderHitos();
      }});
    }}

    document.getElementById("selector-tema").addEventListener("change", (e) => {{
      aplicarTema(e.target.value);
    }});

    document.getElementById("btn-expandir-todo").addEventListener("click", (e) => {{
      estado.todoExpandido = !estado.todoExpandido;
      e.target.textContent = estado.todoExpandido ? "Contraer todo" : "Expandir todo";
      renderSecciones();
    }});

    document.getElementById("btn-pantalla-completa").addEventListener("click", () => {{
      if (!document.fullscreenElement) {{
        document.documentElement.requestFullscreen?.().catch(() => {{}});
      }} else {{
        document.exitFullscreen?.().catch(() => {{}});
      }}
    }});

    document.getElementById("btn-imprimir").addEventListener("click", () => window.print());

    document.addEventListener("keydown", (e) => {{
      if (e.target && ["INPUT", "TEXTAREA", "SELECT"].includes(e.target.tagName)) return;
      if (!SPEC.hitos || SPEC.hitos.length === 0) return;
      if (e.key === "ArrowRight") {{
        estado.hitoActivo = (estado.hitoActivo + 1) % SPEC.hitos.length;
        renderHitos();
      }} else if (e.key === "ArrowLeft") {{
        estado.hitoActivo = (estado.hitoActivo - 1 + SPEC.hitos.length) % SPEC.hitos.length;
        renderHitos();
      }}
    }});

    renderKpis();
    renderSecciones();
    renderGrafico();
    renderHitos();
  </script>
</body>
</html>
"""


def guardar_html(spec: InfografiaSpec, ruta_salida: str | Path) -> Path:
    """Exporta la infografía HTML interactiva a un archivo en disco."""
    destino = Path(ruta_salida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(exportar_html(spec), encoding="utf-8")
    return destino
