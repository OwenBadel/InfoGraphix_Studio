"""Exportador HTML5 interactivo para Cuentos / Libros Digitales Infográficos."""

from __future__ import annotations

import base64
import html
import io
import json
from pathlib import Path

from PIL import Image

from ..domain.story_models import CuentoInfografiaSpec


def _json_seguro(datos: object) -> str:
    raw = json.dumps(datos, ensure_ascii=False)
    return raw.replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def _imagen_a_data_uri(ruta_img: Path) -> str:
    """Optimiza la ilustración (1280px ancho JPEG q86) y la embebe en base64 offline."""
    if not ruta_img.exists():
        return ""
    with Image.open(ruta_img) as im:
        rgb = im.convert("RGB")
        if rgb.width > 1280:
            alto = int(rgb.height * (1280 / rgb.width))
            rgb = rgb.resize((1280, alto), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        rgb.save(buf, format="JPEG", quality=86, optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/jpeg;base64,{b64}"


def exportar_cuento_html(spec: CuentoInfografiaSpec, assets_dir: Path) -> str:
    """Genera un libro digital + infografía interactiva HTML5 autocontenido."""
    total_palabras = spec.total_palabras_relato()
    payload = spec.model_dump()
    for esc in payload["escenas"]:
        esc["imagen_uri"] = _imagen_a_data_uri(assets_dir / esc["imagen_archivo"])
    payload["total_palabras"] = total_palabras

    datos_json = _json_seguro(payload)
    p0 = spec.escenas[0].paleta
    titulo_esc = html.escape(spec.titulo)
    subtitulo_esc = html.escape(spec.subtitulo)
    coleccion_esc = html.escape(spec.etiqueta_coleccion)
    autor_esc = html.escape(spec.autor)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{titulo_esc} — Libro Digital &amp; Infografía Interactiva</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,700;1,9..144,500&family=IBM+Plex+Mono:wght@500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: {p0.bg};
      --surface: {p0.surface};
      --surface-alt: {p0.surface_alt};
      --ink: {p0.ink};
      --muted: {p0.muted};
      --border: {p0.border};
      --accent: {p0.accent};
      --accent-ink: {p0.accent_ink};
      --accent-soft: {p0.accent_soft};
      --font-display: 'Fraunces', Georgia, serif;
      --font-body: 'Plus Jakarta Sans', 'Segoe UI', system-ui, sans-serif;
      --font-mono: 'IBM Plex Mono', Consolas, monospace;
      --radius: 14px;
      --radius-sm: 10px;
    }}

    *, *::before, *::after {{ box-sizing: border-box; }}

    html {{ scroll-behavior: smooth; }}

    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: var(--font-body);
      line-height: 1.65;
      transition: background-color 0.55s ease, color 0.45s ease;
      overflow-x: hidden;
    }}

    .libro-shell {{
      max-width: 1180px;
      margin: 0 auto;
      padding: clamp(0.9rem, 2.4vw, 2rem);
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }}

    .barra-superior {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 0.75rem;
      padding: 0.75rem 1rem;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      transition: background-color 0.45s ease, border-color 0.45s ease;
    }}

    .etiqueta-coleccion {{
      font-family: var(--font-mono);
      font-size: 0.76rem;
      font-weight: 600;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      color: var(--accent);
      background: var(--accent-soft);
      padding: 0.32rem 0.7rem;
      border-radius: 999px;
    }}

    .grupo-acciones {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 0.45rem;
    }}

    .btn {{
      min-height: 44px;
      padding: 0.48rem 0.9rem;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border);
      background: var(--surface-alt);
      color: var(--ink);
      font-family: var(--font-body);
      font-size: 0.86rem;
      font-weight: 600;
      cursor: pointer;
      transition: border-color 0.2s ease, background-color 0.2s ease, color 0.2s ease;
    }}

    .btn:hover {{ border-color: var(--accent); }}
    .btn:focus-visible, .paso-escena:focus-visible, .pestana-chip:focus-visible {{
      outline: 2px solid var(--accent);
      outline-offset: 2px;
    }}

    .btn-primario {{
      background: var(--accent);
      border-color: var(--accent);
      color: var(--accent-ink);
    }}

    .btn-activo {{
      border-color: var(--accent);
      background: var(--accent-soft);
      color: var(--accent);
    }}

    .cabecera-obra {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-top: 4px solid var(--accent);
      border-radius: var(--radius);
      padding: clamp(1.2rem, 2.8vw, 2rem);
      display: flex;
      flex-direction: column;
      gap: 0.65rem;
    }}

    .cabecera-obra h1 {{
      margin: 0;
      font-family: var(--font-display);
      font-size: clamp(1.75rem, 3.6vw, 2.9rem);
      line-height: 1.1;
      letter-spacing: -0.02em;
    }}

    .cabecera-obra p {{
      margin: 0;
      color: var(--muted);
      font-size: clamp(0.95rem, 1.3vw, 1.08rem);
      max-width: 72ch;
    }}

    .meta-obra {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem 1.25rem;
      padding-top: 0.6rem;
      border-top: 1px solid var(--border);
      font-family: var(--font-mono);
      font-size: 0.8rem;
      color: var(--muted);
    }}

    .progresion-bar {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(min(100%, 155px), 1fr));
      gap: 0.5rem;
    }}

    .paso-escena {{
      min-height: 56px;
      padding: 0.6rem 0.75rem;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border);
      background: var(--surface);
      color: var(--ink);
      text-align: left;
      cursor: pointer;
      display: flex;
      flex-direction: column;
      gap: 0.2rem;
      position: relative;
      overflow: hidden;
    }}

    .paso-escena::before {{
      content: "";
      position: absolute;
      inset: 0 0 auto 0;
      height: 4px;
      background: var(--swatch, var(--accent));
    }}

    .paso-escena.activo {{
      border-color: var(--accent);
      background: var(--accent-soft);
    }}

    .paso-num {{
      font-family: var(--font-mono);
      font-size: 0.72rem;
      color: var(--muted);
    }}

    .paso-tit {{
      font-size: 0.84rem;
      font-weight: 700;
      line-height: 1.2;
    }}

    .escena-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr);
      gap: 1.25rem;
      align-items: start;
    }}

    .panel-visual,
    .panel-relato,
    .panel-bloque {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: clamp(1rem, 2.2vw, 1.6rem);
      transition: background-color 0.45s ease, border-color 0.45s ease;
    }}

    .marco-imagen {{
      width: 100%;
      border-radius: var(--radius-sm);
      overflow: hidden;
      border: 1px solid var(--border);
      background: var(--surface-alt);
      aspect-ratio: 16 / 9;
    }}

    .marco-imagen img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }}

    .clima-row {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
      margin-top: 0.85rem;
    }}

    .clima-badge {{
      font-family: var(--font-mono);
      font-size: 0.78rem;
      color: var(--accent);
      background: var(--accent-soft);
      padding: 0.25rem 0.65rem;
      border-radius: 999px;
    }}

    .cita-poetica {{
      margin: 0.9rem 0 0;
      padding: 0.85rem 1rem;
      border-left: 3px solid var(--accent);
      background: var(--surface-alt);
      border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
      font-family: var(--font-display);
      font-style: italic;
      font-size: clamp(0.98rem, 1.35vw, 1.1rem);
      color: var(--ink);
    }}

    .medidores-escena {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 0.75rem;
      margin-top: 0.95rem;
    }}

    .medidor {{
      background: var(--surface-alt);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 0.65rem 0.8rem;
    }}

    .medidor-top {{
      display: flex;
      justify-content: space-between;
      font-family: var(--font-mono);
      font-size: 0.76rem;
      color: var(--muted);
      margin-bottom: 0.35rem;
    }}

    .barra-fondo {{
      height: 8px;
      border-radius: 999px;
      background: var(--border);
      overflow: hidden;
    }}

    .barra-relleno {{
      height: 100%;
      border-radius: 999px;
      background: var(--accent);
      transition: width 0.45s ease;
    }}

    .escena-tiempo {{
      font-family: var(--font-mono);
      font-size: 0.8rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--accent);
    }}

    .panel-relato h2 {{
      margin: 0.3rem 0 0.85rem;
      font-family: var(--font-display);
      font-size: clamp(1.35rem, 2.3vw, 1.9rem);
      line-height: 1.18;
    }}

    .relato-cuerpo p {{
      margin: 0 0 0.95rem;
      font-size: clamp(0.96rem, 1.15vw, 1.03rem);
      color: var(--ink);
      max-width: 65ch;
    }}

    .controles-escena {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-top: 1rem;
      padding-top: 0.95rem;
      border-top: 1px solid var(--border);
    }}

    .panel-salud {{
      margin-top: 1rem;
      padding: 1rem 1.1rem;
      border-radius: var(--radius-sm);
      border: 1px solid var(--accent);
      background: var(--surface-alt);
      display: flex;
      flex-direction: column;
      gap: 0.55rem;
    }}

    .panel-salud[hidden] {{ display: none; }}

    .salud-top {{
      display: flex;
      flex-wrap: wrap;
      align-items: baseline;
      gap: 0.75rem;
    }}

    .salud-cifra {{
      font-family: var(--font-display);
      font-size: clamp(1.65rem, 2.6vw, 2.15rem);
      font-weight: 700;
      color: var(--accent);
      line-height: 1;
    }}

    .salud-accion {{
      padding: 0.65rem 0.85rem;
      border-radius: var(--radius-sm);
      background: var(--surface);
      border: 1px solid var(--border);
      font-size: 0.9rem;
    }}

    .salud-fuente {{
      font-family: var(--font-mono);
      font-size: 0.75rem;
      color: var(--muted);
    }}

    .widget-interactivo {{
      margin-top: 1rem;
      padding: 0.95rem 1rem;
      border-radius: var(--radius-sm);
      border: 1px dashed var(--accent);
      background: var(--surface-alt);
      display: flex;
      flex-direction: column;
      gap: 0.65rem;
    }}

    .pestanas-wrap {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.45rem;
    }}

    .pestana-chip {{
      min-height: 44px;
      padding: 0.4rem 0.75rem;
      border-radius: 999px;
      border: 1px solid var(--border);
      background: var(--surface);
      color: var(--ink);
      font-size: 0.84rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
    }}

    .pestana-chip.cerrada {{
      opacity: 0.42;
      text-decoration: line-through;
      border-style: dashed;
    }}

    .respirador-wrap {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 1rem;
    }}

    .circulo-resp {{
      width: 84px;
      height: 84px;
      border-radius: 50%;
      border: 3px solid var(--accent);
      background: var(--accent-soft);
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: var(--font-mono);
      font-weight: 700;
      color: var(--accent);
      transition: transform 1s ease;
      flex-shrink: 0;
    }}

    .circulo-resp.expandido {{ transform: scale(1.16); }}

    .nav-inferior {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 0.75rem;
      padding: 0.85rem 1rem;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
    }}

    .svg-curva {{
      width: 100%;
      height: auto;
      display: block;
      background: var(--surface-alt);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 0.75rem;
    }}

    .claves-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(min(100%, 240px), 1fr));
      gap: 0.85rem;
      margin-top: 1rem;
    }}

    .clave-card {{
      background: var(--surface-alt);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 0.9rem 1rem;
    }}

    .clave-num {{
      font-family: var(--font-mono);
      font-size: 0.78rem;
      font-weight: 700;
      color: var(--accent);
    }}

    .lectura-completa {{
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }}

    .lectura-escena {{
      border-bottom: 1px solid var(--border);
      padding-bottom: 1.1rem;
    }}

    .pie-libro {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 0.65rem;
      padding: 0.75rem 0.25rem;
      border-top: 1px solid var(--border);
      font-size: 0.84rem;
      color: var(--muted);
    }}

    @media (max-width: 900px) {{
      .escena-grid {{ grid-template-columns: 1fr; }}
    }}

    @media (prefers-reduced-motion: reduce) {{
      *, *::before, *::after {{
        animation: none !important;
        transition: none !important;
        scroll-behavior: auto !important;
      }}
    }}

    @media print {{
      .barra-superior, .progresion-bar, .nav-inferior, .controles-escena, .widget-interactivo {{
        display: none !important;
      }}
      body {{ background: #ffffff !important; color: #111111 !important; }}
    }}
  </style>
</head>
<body>
  <main class="libro-shell">
    <nav class="barra-superior" aria-label="Navegación principal del libro interactivo">
      <span class="etiqueta-coleccion">{coleccion_esc}</span>
      <div class="grupo-acciones">
        <button type="button" class="btn btn-activo" id="modo-escenas">Libro 5 Escenas</button>
        <button type="button" class="btn" id="modo-infografia">Infografía &amp; Reflexión</button>
        <button type="button" class="btn" id="modo-completo">Lectura Completa</button>
        <button type="button" class="btn" id="btn-audio-voz">Escuchar narración</button>
        <button type="button" class="btn" id="btn-sonido-amb">Sonido ambiente: Off</button>
        <button type="button" class="btn btn-primario" id="btn-imprimir">Imprimir / PDF</button>
      </div>
    </nav>

    <header class="cabecera-obra">
      <h1>{titulo_esc}</h1>
      <p>{subtitulo_esc}</p>
      <div class="meta-obra">
        <span><strong>Extensión del relato:</strong> {total_palabras} palabras</span>
        <span><strong>Formato:</strong> 5 escenas ilustradas (paleta frío → cálido)</span>
        <span><strong>Controles:</strong> Clic o teclas ← / →</span>
      </div>
    </header>

    <div class="progresion-bar" id="barra-escenas" role="tablist" aria-label="Escenas del cuento"></div>

    <section id="vista-escena" aria-live="polite"></section>
    <section id="vista-infografia" class="panel-bloque" hidden></section>
    <section id="vista-completa" class="panel-bloque" hidden></section>

    <nav class="nav-inferior" id="nav-inferior" aria-label="Controles de paso de escena">
      <button type="button" class="btn" id="btn-prev">← Escena anterior</button>
      <span id="indicador-progreso" style="font-family:var(--font-mono);font-size:0.84rem;color:var(--muted);"></span>
      <button type="button" class="btn btn-primario" id="btn-next">Siguiente escena →</button>
    </nav>

    <footer class="pie-libro">
      <span>{autor_esc} · Relato Multimedia e Infografía de Salud Mental</span>
      <span>Archivo HTML5 autocontenido · Funciona sin conexión</span>
    </footer>
  </main>

  <script>
    const OBRA = {datos_json};

    const estado = {{
      modo: "escenas",
      escenaIdx: 0,
      datoAbierto: false,
      pestanasCerradas: {{}},
      narrando: false,
      ambienteActivo: false,
      respActiva: false,
      respTimer: null,
      audioCtx: null,
      ambNode: null,
    }};

    function esc(t) {{
      return String(t ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
    }}

    function aplicarPaleta(pal) {{
      const r = document.documentElement.style;
      r.setProperty("--bg", pal.bg);
      r.setProperty("--surface", pal.surface);
      r.setProperty("--surface-alt", pal.surface_alt);
      r.setProperty("--ink", pal.ink);
      r.setProperty("--muted", pal.muted);
      r.setProperty("--border", pal.border);
      r.setProperty("--accent", pal.accent);
      r.setProperty("--accent-ink", pal.accent_ink);
      r.setProperty("--accent-soft", pal.accent_soft);
    }}

    function detenerVoz() {{
      if ("speechSynthesis" in window) {{
        window.speechSynthesis.cancel();
      }}
      estado.narrando = false;
      const b = document.getElementById("btn-audio-voz");
      if (b) b.textContent = "Escuchar narración";
    }}

    function alternarVoz() {{
      if (!("speechSynthesis" in window)) {{
        alert("Tu navegador no soporta síntesis de voz Web Speech.");
        return;
      }}
      if (estado.narrando) {{
        detenerVoz();
        return;
      }}
      const e = OBRA.escenas[estado.escenaIdx];
      const texto = estado.modo === "infografia"
        ? `${{OBRA.reflexion_final_titulo}}. ${{OBRA.reflexion_final_parrafos.join(" ")}}`
        : `${{e.titulo}}. ${{e.parrafos.join(" ")}}`;
      const utt = new SpeechSynthesisUtterance(texto);
      utt.lang = "es-CO";
      utt.rate = 0.96;
      const voces = window.speechSynthesis.getVoices();
      const vozEs = voces.find((v) => v.lang.toLowerCase().startsWith("es"));
      if (vozEs) utt.voice = vozEs;
      utt.onend = () => detenerVoz();
      utt.onerror = () => detenerVoz();
      estado.narrando = true;
      document.getElementById("btn-audio-voz").textContent = "Detener narración";
      window.speechSynthesis.speak(utt);
    }}

    function detenerAmbiente() {{
      if (estado.ambNode) {{
        try {{ estado.ambNode.stop(); }} catch (_) {{}}
        try {{ estado.ambNode.disconnect(); }} catch (_) {{}}
        estado.ambNode = null;
      }}
    }}

    function iniciarAmbienteParaEscena(tipo) {{
      detenerAmbiente();
      if (!estado.ambienteActivo) return;
      const Ctx = window.AudioContext || window.webkitAudioContext;
      if (!Ctx) return;
      if (!estado.audioCtx) estado.audioCtx = new Ctx();
      if (estado.audioCtx.state === "suspended") estado.audioCtx.resume();

      const ctx = estado.audioCtx;
      const gain = ctx.createGain();
      gain.gain.value = 0.045;
      gain.connect(ctx.destination);

      if (tipo === "lluvia") {{
        // Ruido rosa filtrado suave evocando lluvia sobre tejado
        const bufSize = ctx.sampleRate * 2;
        const buf = ctx.createBuffer(1, bufSize, ctx.sampleRate);
        const data = buf.getChannelData(0);
        let b0 = 0, b1 = 0, b2 = 0;
        for (let i = 0; i < bufSize; i++) {{
          const w = Math.random() * 2 - 1;
          b0 = 0.997 * b0 + w * 0.029;
          b1 = 0.985 * b1 + w * 0.032;
          b2 = 0.950 * b2 + w * 0.048;
          data[i] = (b0 + b1 + b2 + w * 0.01) * 0.6;
        }}
        const src = ctx.createBufferSource();
        src.buffer = buf;
        src.loop = true;
        const filtro = ctx.createBiquadFilter();
        filtro.type = "lowpass";
        filtro.frequency.value = 900;
        src.connect(filtro);
        filtro.connect(gain);
        src.start();
        estado.ambNode = src;
      }} else {{
        // Acorde armónico suave adaptado al clima emocional (grave frío -> cálido abierto)
        const freq = tipo === "calma" ? 261.63 : tipo === "respiracion" ? 220.0 : 174.61;
        const osc = ctx.createOscillator();
        osc.type = "sine";
        osc.frequency.value = freq;
        osc.connect(gain);
        osc.start();
        estado.ambNode = osc;
      }}
    }}

    function detenerRespiracion() {{
      if (estado.respTimer) {{
        window.clearInterval(estado.respTimer);
        estado.respTimer = null;
      }}
      estado.respActiva = false;
    }}

    function renderBarraEscenas() {{
      const cont = document.getElementById("barra-escenas");
      cont.innerHTML = OBRA.escenas.map((e, i) => `
        <button type="button" class="paso-escena ${{estado.modo === "escenas" && i === estado.escenaIdx ? "activo" : ""}}"
          style="--swatch:${{e.paleta.accent}}" data-esc-idx="${{i}}">
          <span class="paso-num">0${{e.numero}} · ${{esc(e.paleta.nombre_clima.split("·")[0].trim())}}</span>
          <span class="paso-tit">${{esc(e.titulo)}}</span>
        </button>
      `).join("");

      cont.querySelectorAll(".paso-escena").forEach((btn) => {{
        btn.addEventListener("click", () => {{
          estado.modo = "escenas";
          estado.escenaIdx = Number(btn.dataset.escIdx) || 0;
          estado.datoAbierto = false;
          detenerVoz();
          detenerRespiracion();
          renderTodo();
        }});
      }});
    }}

    function renderEscenaActual() {{
      const e = OBRA.escenas[estado.escenaIdx];
      aplicarPaleta(e.paleta);
      iniciarAmbienteParaEscena(e.ambiente_sonoro);

      const pestanas = e.pestanas_mentales || [];
      const cerradasSet = estado.pestanasCerradas[e.id] || [];
      const reduccion = pestanas.length ? Math.round((cerradasSet.length / pestanas.length) * 45) : 0;
      const cargaDinamica = Math.max(12, e.nivel_carga_mental - reduccion);
      const calmaDinamica = Math.min(96, e.nivel_calma + reduccion);

      const widgetPestanas = pestanas.length ? `
        <div class="widget-interactivo">
          <strong>Interacción simbólica · Haz clic para cerrar pestañas mentales (${{cerradasSet.length}}/${{pestanas.length}} cerradas):</strong>
          <div class="pestanas-wrap">
            ${{pestanas.map((p, idx) => {{
              const cerr = cerradasSet.includes(idx);
              return `<button type="button" class="pestana-chip ${{cerr ? "cerrada" : ""}}" data-tab-idx="${{idx}}">
                <span>${{esc(p)}}</span>
                <span aria-hidden="true">${{cerr ? "✓" : "×"}}</span>
              </button>`;
            }}).join("")}}
          </div>
        </div>
      ` : "";

      const widgetRespiracion = e.tiene_respiracion ? `
        <div class="widget-interactivo">
          <strong>Pausa guiada de respiración 4–4–6:</strong>
          <div class="respirador-wrap">
            <div class="circulo-resp" id="circulo-resp">4-4-6</div>
            <div style="display:flex;flex-direction:column;gap:0.45rem;">
              <div id="texto-resp" style="font-weight:600;">Pulsa iniciar para acompañar a Elena en una respiración profunda.</div>
              <button type="button" class="btn btn-primario" id="btn-iniciar-resp" style="align-self:flex-start;">Iniciar pausa (4-4-6)</button>
            </div>
          </div>
        </div>
      ` : "";

      const vista = document.getElementById("vista-escena");
      vista.innerHTML = `
        <div class="escena-grid">
          <div class="panel-visual">
            <div class="marco-imagen">
              ${{e.imagen_uri ? `<img src="${{e.imagen_uri}}" alt="${{esc(e.alt_imagen)}}">` : ""}}
            </div>
            <div class="clima-row">
              <span class="clima-badge">${{esc(e.paleta.nombre_clima)}}</span>
              <span style="font-family:var(--font-mono);font-size:0.78rem;color:var(--muted);">Escena ${{e.numero}} de ${{OBRA.escenas.length}}</span>
            </div>
            <blockquote class="cita-poetica">“${{esc(e.cita_destacada)}}”</blockquote>
            <div class="medidores-escena">
              <div class="medidor">
                <div class="medidor-top"><span>Carga mental</span><strong>${{cargaDinamica}}%</strong></div>
                <div class="barra-fondo"><div class="barra-relleno" style="width:${{cargaDinamica}}%"></div></div>
              </div>
              <div class="medidor">
                <div class="medidor-top"><span>Calma interior</span><strong>${{calmaDinamica}}%</strong></div>
                <div class="barra-fondo"><div class="barra-relleno" style="width:${{calmaDinamica}}%"></div></div>
              </div>
            </div>
          </div>

          <article class="panel-relato">
            <span class="escena-tiempo">${{esc(e.etiqueta_tiempo)}}</span>
            <h2>${{esc(e.titulo)}}</h2>
            <div class="relato-cuerpo">
              ${{e.parrafos.map((p) => `<p>${{esc(p)}}</p>`).join("")}}
            </div>
            <div class="controles-escena">
              <button type="button" class="btn btn-primario" id="btn-toggle-salud" aria-expanded="${{estado.datoAbierto}}">
                ${{estado.datoAbierto ? "Ocultar dato de salud mental" : "💡 Ver dato sobre salud mental"}}
              </button>
              <button type="button" class="btn" id="btn-escuchar-escena">Escuchar esta escena</button>
            </div>

            <div class="panel-salud" id="panel-salud" ${{estado.datoAbierto ? "" : "hidden"}}>
              <div class="salud-top">
                <span class="salud-cifra">${{esc(e.dato_salud.cifra_destacada)}}</span>
                <strong>${{esc(e.dato_salud.titulo)}}</strong>
              </div>
              <div style="font-weight:600;color:var(--ink);">${{esc(e.dato_salud.subtitulo_cifra)}}</div>
              <p style="margin:0;color:var(--muted);font-size:0.93rem;">${{esc(e.dato_salud.explicacion)}}</p>
              <div class="salud-accion"><strong>Clave práctica:</strong> ${{esc(e.dato_salud.accion_practica)}}</div>
              <span class="salud-fuente">Fuente: ${{esc(e.dato_salud.fuente)}}</span>
            </div>

            ${{widgetPestanas}}
            ${{widgetRespiracion}}
          </article>
        </div>
      `;

      document.getElementById("btn-toggle-salud")?.addEventListener("click", () => {{
        estado.datoAbierto = !estado.datoAbierto;
        renderEscenaActual();
      }});

      document.getElementById("btn-escuchar-escena")?.addEventListener("click", () => alternarVoz());

      vista.querySelectorAll(".pestana-chip").forEach((chip) => {{
        chip.addEventListener("click", () => {{
          const idx = Number(chip.dataset.tabIdx);
          const actual = estado.pestanasCerradas[e.id] || [];
          if (actual.includes(idx)) {{
            estado.pestanasCerradas[e.id] = actual.filter((v) => v !== idx);
          }} else {{
            estado.pestanasCerradas[e.id] = [...actual, idx];
          }}
          renderEscenaActual();
        }});
      }});

      document.getElementById("btn-iniciar-resp")?.addEventListener("click", (ev) => {{
        if (estado.respActiva) {{
          detenerRespiracion();
          ev.target.textContent = "Iniciar pausa (4-4-6)";
          return;
        }}
        estado.respActiva = true;
        ev.target.textContent = "Detener pausa";
        const fases = [
          {{ txt: "Inhala despacio por la nariz (4s)...", seg: 4, exp: true }},
          {{ txt: "Sostén el aire con suavidad (4s)...", seg: 4, exp: true }},
          {{ txt: "Exhala soltando los hombros (6s)...", seg: 6, exp: false }},
        ];
        let fIdx = 0;
        let cuenta = fases[0].seg;
        const actualizar = () => {{
          const circ = document.getElementById("circulo-resp");
          const lbl = document.getElementById("texto-resp");
          if (!circ || !lbl) {{ detenerRespiracion(); return; }}
          const fase = fases[fIdx];
          circ.textContent = `${{cuenta}}s`;
          circ.classList.toggle("expandido", fase.exp);
          lbl.textContent = fase.txt;
          cuenta--;
          if (cuenta <= 0) {{
            fIdx = (fIdx + 1) % fases.length;
            cuenta = fases[fIdx].seg;
          }}
        }};
        actualizar();
        estado.respTimer = window.setInterval(actualizar, 1000);
      }});

      document.getElementById("indicador-progreso").textContent =
        `Escena ${{e.numero}} / ${{OBRA.escenas.length}} · ${{e.paleta.nombre_clima}}`;
      document.getElementById("btn-prev").disabled = estado.escenaIdx === 0;
      document.getElementById("btn-next").textContent =
        estado.escenaIdx === OBRA.escenas.length - 1 ? "Ver reflexión e infografía →" : "Siguiente escena →";
    }}

    function construirSvgCurvaEmocional() {{
      const W = 760, H = 270, padL = 52, padR = 36, padT = 28, padB = 48;
      const ancho = W - padL - padR;
      const alto = H - padT - padB;
      const n = OBRA.escenas.length;

      const xPos = (i) => padL + (i / (n - 1)) * ancho;
      const yPos = (val) => padT + alto - (val / 100) * alto;

      const ptsCarga = OBRA.escenas.map((e, i) => `${{xPos(i).toFixed(1)}},${{yPos(e.nivel_carga_mental).toFixed(1)}}`).join(" ");
      const ptsCalma = OBRA.escenas.map((e, i) => `${{xPos(i).toFixed(1)}},${{yPos(e.nivel_calma).toFixed(1)}}`).join(" ");

      const grid = [0, 25, 50, 75, 100].map((v) => {{
        const y = yPos(v);
        return `<line x1="${{padL}}" y1="${{y}}" x2="${{W - padR}}" y2="${{y}}" stroke="var(--border)" stroke-dasharray="3 3"/>
                <text x="${{padL - 10}}" y="${{y + 4}}" text-anchor="end" fill="var(--muted)" font-size="11" font-family="var(--font-mono)">${{v}}%</text>`;
      }}).join("");

      const nodos = OBRA.escenas.map((e, i) => {{
        const x = xPos(i);
        return `
          <circle cx="${{x}}" cy="${{yPos(e.nivel_carga_mental)}}" r="6" fill="#64748b"/>
          <circle cx="${{x}}" cy="${{yPos(e.nivel_calma)}}" r="6" fill="var(--accent)"/>
          <text x="${{x}}" y="${{H - 16}}" text-anchor="middle" fill="var(--ink)" font-size="11" font-weight="600" font-family="var(--font-body)">Escena 0${{e.numero}}</text>`;
      }}).join("");

      return `<svg class="svg-curva" viewBox="0 0 ${{W}} ${{H}}" role="img" aria-label="Curva emocional del cuento">
        ${{grid}}
        <polyline fill="none" stroke="#64748b" stroke-width="3" stroke-dasharray="6 4" points="${{ptsCarga}}"/>
        <polyline fill="none" stroke="var(--accent)" stroke-width="3.5" points="${{ptsCalma}}"/>
        ${{nodos}}
      </svg>`;
    }}

    function renderInfografiaFinal() {{
      const palCalida = OBRA.escenas[OBRA.escenas.length - 1].paleta;
      aplicarPaleta(palCalida);
      iniciarAmbienteParaEscena("calma");

      const cont = document.getElementById("vista-infografia");
      cont.innerHTML = `
        <span class="escena-tiempo">Cierre Editorial &amp; Mapa Emocional</span>
        <h2 style="margin:0.35rem 0 0.85rem;font-family:var(--font-display);font-size:clamp(1.45rem,2.5vw,2.1rem);">${{esc(OBRA.reflexion_final_titulo)}}</h2>
        ${{OBRA.reflexion_final_parrafos.map((p) => `<p style="max-width:72ch;margin:0 0 0.85rem;">${{esc(p)}}</p>`).join("")}}

        <h3 style="margin:1.35rem 0 0.5rem;font-family:var(--font-display);">Curva Emocional: de la sobrecarga fría a la claridad cálida</h3>
        <p style="margin:0 0 0.75rem;color:var(--muted);font-size:0.9rem;">Línea punteada gris: Carga mental (%) · Línea sólida terracota: Calma y autocuidado (%).</p>
        ${{construirSvgCurvaEmocional()}}

        <h3 style="margin:1.5rem 0 0.5rem;font-family:var(--font-display);">5 Claves para Cerrar Pestañas</h3>
        <div class="claves-grid">
          ${{OBRA.claves_autocuidado.map((c, i) => `
            <div class="clave-card">
              <div class="clave-num">CLAVE 0${{i + 1}}</div>
              <p style="margin:0.35rem 0 0;font-size:0.92rem;">${{esc(c)}}</p>
            </div>
          `).join("")}}
        </div>
      `;
    }}

    function renderLecturaCompleta() {{
      const palCalida = OBRA.escenas[OBRA.escenas.length - 1].paleta;
      aplicarPaleta(palCalida);
      const cont = document.getElementById("vista-completa");
      cont.innerHTML = `
        <div class="lectura-completa">
          <div>
            <span class="escena-tiempo">Versión Íntegra · ${{OBRA.total_palabras}} palabras</span>
            <h2 style="margin:0.3rem 0 0;font-family:var(--font-display);font-size:clamp(1.5rem,2.6vw,2.2rem);">${{esc(OBRA.titulo)}}</h2>
          </div>
          ${{OBRA.escenas.map((e) => `
            <article class="lectura-escena">
              <h3 style="margin:0 0 0.5rem;font-family:var(--font-display);">${{esc(e.etiqueta_tiempo)}} — ${{esc(e.titulo)}}</h3>
              ${{e.parrafos.map((p) => `<p style="max-width:72ch;margin:0 0 0.75rem;">${{esc(p)}}</p>`).join("")}}
            </article>
          `).join("")}}
          <article>
            <h3 style="margin:0 0 0.5rem;font-family:var(--font-display);">${{esc(OBRA.reflexion_final_titulo)}}</h3>
            ${{OBRA.reflexion_final_parrafos.map((p) => `<p style="max-width:72ch;margin:0 0 0.75rem;">${{esc(p)}}</p>`).join("")}}
          </article>
        </div>
      `;
    }}

    function renderTodo() {{
      renderBarraEscenas();
      const vEsc = document.getElementById("vista-escena");
      const vInf = document.getElementById("vista-infografia");
      const vCom = document.getElementById("vista-completa");
      const navInf = document.getElementById("nav-inferior");

      document.getElementById("modo-escenas").classList.toggle("btn-activo", estado.modo === "escenas");
      document.getElementById("modo-infografia").classList.toggle("btn-activo", estado.modo === "infografia");
      document.getElementById("modo-completo").classList.toggle("btn-activo", estado.modo === "completo");

      vEsc.hidden = estado.modo !== "escenas";
      vInf.hidden = estado.modo !== "infografia";
      vCom.hidden = estado.modo !== "completo";
      navInf.hidden = estado.modo !== "escenas";

      if (estado.modo === "escenas") renderEscenaActual();
      if (estado.modo === "infografia") renderInfografiaFinal();
      if (estado.modo === "completo") renderLecturaCompleta();
    }}

    document.getElementById("modo-escenas").addEventListener("click", () => {{
      estado.modo = "escenas"; detenerVoz(); detenerRespiracion(); renderTodo();
    }});
    document.getElementById("modo-infografia").addEventListener("click", () => {{
      estado.modo = "infografia"; detenerVoz(); detenerRespiracion(); renderTodo();
    }});
    document.getElementById("modo-completo").addEventListener("click", () => {{
      estado.modo = "completo"; detenerVoz(); detenerRespiracion(); renderTodo();
    }});
    document.getElementById("btn-audio-voz").addEventListener("click", alternarVoz);
    document.getElementById("btn-sonido-amb").addEventListener("click", (e) => {{
      estado.ambienteActivo = !estado.ambienteActivo;
      e.target.textContent = estado.ambienteActivo ? "Sonido ambiente: On" : "Sonido ambiente: Off";
      if (estado.ambienteActivo) {{
        iniciarAmbienteParaEscena(OBRA.escenas[estado.escenaIdx].ambiente_sonoro);
      }} else {{
        detenerAmbiente();
      }}
    }});
    document.getElementById("btn-imprimir").addEventListener("click", () => window.print());

    document.getElementById("btn-prev").addEventListener("click", () => {{
      if (estado.escenaIdx > 0) {{
        estado.escenaIdx--; estado.datoAbierto = false; detenerVoz(); detenerRespiracion(); renderTodo();
      }}
    }});
    document.getElementById("btn-next").addEventListener("click", () => {{
      detenerVoz(); detenerRespiracion();
      if (estado.escenaIdx < OBRA.escenas.length - 1) {{
        estado.escenaIdx++; estado.datoAbierto = false; renderTodo();
      }} else {{
        estado.modo = "infografia"; renderTodo();
      }}
    }});

    document.addEventListener("keydown", (e) => {{
      if (estado.modo !== "escenas") return;
      if (e.key === "ArrowRight") {{
        document.getElementById("btn-next").click();
      }} else if (e.key === "ArrowLeft" && estado.escenaIdx > 0) {{
        document.getElementById("btn-prev").click();
      }}
    }});

    renderTodo();
  </script>
</body>
</html>
"""


def guardar_cuento_html(
    spec: CuentoInfografiaSpec,
    assets_dir: str | Path,
    ruta_salida: str | Path,
) -> Path:
    destino = Path(ruta_salida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(exportar_cuento_html(spec, Path(assets_dir)), encoding="utf-8")
    return destino
