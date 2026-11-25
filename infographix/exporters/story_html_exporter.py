"""Exportador HTML5 minimalista e interactivo para Cuentos Ilustrados con popup de salud mental."""

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
    """Genera un libro digital HTML5 limpio, sin ruido visual, con ventana emergente de salud mental."""
    payload = spec.model_dump()
    for esc in payload["escenas"]:
        esc["imagen_uri"] = _imagen_a_data_uri(assets_dir / esc["imagen_archivo"])
    datos_json = _json_seguro(payload)

    p0 = spec.escenas[0].paleta
    titulo_esc = html.escape(spec.titulo)
    subtitulo_esc = html.escape(spec.subtitulo)
    autor_esc = html.escape(spec.autor)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{titulo_esc}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,700;1,9..144,500&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
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
      --radius: 14px;
      --radius-sm: 10px;
    }}

    *, *::before, *::after {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--ink);
      font-family: var(--font-body);
      line-height: 1.7;
      transition: background-color 0.55s ease, color 0.45s ease;
      overflow-x: hidden;
    }}

    .franja-progreso {{
      height: 5px;
      width: 100%;
      background: var(--accent);
      transition: background-color 0.5s ease;
    }}

    .libro-shell {{
      max-width: 1120px;
      margin: 0 auto;
      padding: clamp(1rem, 2.8vw, 2.2rem);
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }}

    .portada-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1.05fr);
      gap: clamp(1.25rem, 3vw, 2.5rem);
      align-items: center;
      min-height: 74vh;
    }}

    .portada-texto {{
      display: flex;
      flex-direction: column;
      gap: 1.1rem;
      align-items: flex-start;
    }}

    .portada-texto h1 {{
      margin: 0;
      font-family: var(--font-display);
      font-size: clamp(2rem, 4.2vw, 3.25rem);
      line-height: 1.1;
      letter-spacing: -0.02em;
    }}

    .portada-texto p {{
      margin: 0;
      color: var(--muted);
      font-size: clamp(1rem, 1.4vw, 1.12rem);
      max-width: 48ch;
    }}

    .portada-mosaico {{
      display: grid;
      gap: 0.9rem;
    }}

    .marco-imagen {{
      width: 100%;
      border-radius: var(--radius);
      overflow: hidden;
      border: 1px solid var(--border);
      background: var(--surface-alt);
      aspect-ratio: 16 / 9;
      position: relative;
    }}

    .marco-imagen img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }}

    .pagina-cabecera {{
      display: flex;
      flex-wrap: wrap;
      align-items: flex-end;
      justify-content: space-between;
      gap: 0.85rem;
    }}

    .etiqueta-tiempo {{
      display: block;
      font-size: 0.85rem;
      font-weight: 700;
      letter-spacing: 0.03em;
      color: var(--accent);
      margin-bottom: 0.25rem;
    }}

    .pagina-cabecera h2 {{
      margin: 0;
      font-family: var(--font-display);
      font-size: clamp(1.5rem, 2.8vw, 2.2rem);
      line-height: 1.16;
    }}

    .acciones-cabecera {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }}

    .pagina-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.05fr) minmax(0, 1fr);
      gap: clamp(1.1rem, 2.5vw, 1.75rem);
      align-items: start;
    }}

    .col-visual {{
      display: flex;
      flex-direction: column;
      gap: 1rem;
      position: relative;
    }}

    .cita-poetica {{
      margin: 0;
      padding: 1rem 1.2rem;
      background: var(--surface);
      border: 1px solid var(--border);
      border-left: 3px solid var(--accent);
      border-radius: var(--radius-sm);
      font-family: var(--font-display);
      font-style: italic;
      font-size: clamp(0.98rem, 1.3vw, 1.08rem);
      color: var(--ink);
    }}

    .tarjeta-relato {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: clamp(1.2rem, 2.5vw, 1.85rem);
      transition: background-color 0.45s ease, border-color 0.45s ease;
    }}

    .tarjeta-relato p {{
      margin: 0 0 1rem;
      font-size: clamp(0.97rem, 1.15vw, 1.04rem);
      max-width: 62ch;
    }}

    .tarjeta-relato p:last-child {{
      margin-bottom: 0;
    }}

    .btn {{
      min-height: 44px;
      padding: 0.55rem 1.1rem;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border);
      background: var(--surface);
      color: var(--ink);
      font-family: var(--font-body);
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      transition: border-color 0.18s ease, background-color 0.18s ease, color 0.18s ease;
    }}

    .btn:hover {{ border-color: var(--accent); }}
    .btn:focus-visible {{
      outline: 2px solid var(--accent);
      outline-offset: 2px;
    }}

    .btn-primario {{
      background: var(--accent);
      border-color: var(--accent);
      color: var(--accent-ink);
    }}

    .btn-dato {{
      background: var(--accent-soft);
      border-color: var(--accent);
      color: var(--accent);
    }}

    .nav-simple {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      padding-top: 0.5rem;
    }}

    /* Ventana emergente compacta (superpuesta sin sacarte de la lectura) */
    .popup-fondo {{
      position: fixed;
      inset: 0;
      background: rgba(10, 14, 22, 0.52);
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1rem;
      z-index: 50;
    }}

    .popup-fondo[hidden] {{ display: none; }}

    .popup-ventana {{
      width: min(100%, 460px);
      background: var(--surface);
      color: var(--ink);
      border: 2px solid var(--accent);
      border-radius: var(--radius);
      padding: 1.35rem 1.4rem;
      display: flex;
      flex-direction: column;
      gap: 0.65rem;
      position: relative;
    }}

    .popup-top {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 0.75rem;
    }}

    .popup-etq {{
      font-size: 0.78rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--accent);
    }}

    .popup-ventana h3 {{
      margin: 0.2rem 0 0;
      font-family: var(--font-display);
      font-size: 1.35rem;
      line-height: 1.2;
    }}

    .popup-cerrar {{
      min-width: 44px;
      min-height: 44px;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border);
      background: var(--surface-alt);
      color: var(--ink);
      font-size: 1rem;
      font-weight: 700;
      cursor: pointer;
      flex-shrink: 0;
    }}

    .popup-tip {{
      padding: 0.75rem 0.9rem;
      border-radius: var(--radius-sm);
      background: var(--surface-alt);
      border-left: 3px solid var(--accent);
      font-size: 0.92rem;
    }}

    .popup-fuente {{
      font-size: 0.78rem;
      color: var(--muted);
    }}

    .reflexion-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.35fr) minmax(0, 0.95fr);
      gap: 1.5rem;
      align-items: start;
    }}

    @media (max-width: 860px) {{
      .portada-grid, .pagina-grid, .reflexion-grid {{
        grid-template-columns: 1fr;
      }}
      .portada-grid {{ min-height: auto; }}
    }}

    @media (prefers-reduced-motion: reduce) {{
      *, *::before, *::after {{
        animation: none !important;
        transition: none !important;
      }}
    }}

    @media print {{
      .nav-simple, .acciones-cabecera, .popup-fondo {{ display: none !important; }}
      body {{ background: #ffffff !important; color: #111111 !important; }}
    }}
  </style>
</head>
<body>
  <div class="franja-progreso" aria-hidden="true"></div>

  <main class="libro-shell" id="app-root" aria-live="polite"></main>

  <div class="popup-fondo" id="popup-fondo" hidden role="dialog" aria-modal="true" aria-labelledby="popup-titulo">
    <div class="popup-ventana">
      <div class="popup-top">
        <div>
          <span class="popup-etq" id="popup-cifra"></span>
          <h3 id="popup-titulo"></h3>
        </div>
        <button type="button" class="popup-cerrar" id="btn-cerrar-popup" aria-label="Cerrar dato">✕</button>
      </div>
      <p id="popup-texto" style="margin:0;font-size:0.95rem;"></p>
      <div class="popup-tip" id="popup-tip"></div>
      <span class="popup-fuente" id="popup-fuente"></span>
    </div>
  </div>

  <script>
    const OBRA = {datos_json};
    // paso: 0 = portada, 1..N = páginas del cuento, N+1 = reflexión final
    const estado = {{
      paso: 0,
      narrando: false,
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
      if ("speechSynthesis" in window) window.speechSynthesis.cancel();
      estado.narrando = false;
      const b = document.getElementById("btn-voz");
      if (b) b.textContent = "Escuchar";
    }}

    function alternarVoz(texto) {{
      if (!("speechSynthesis" in window)) return;
      if (estado.narrando) {{ detenerVoz(); return; }}
      const utt = new SpeechSynthesisUtterance(texto);
      utt.lang = "es-CO";
      utt.rate = 0.96;
      const voz = window.speechSynthesis.getVoices().find((v) => v.lang.toLowerCase().startsWith("es"));
      if (voz) utt.voice = voz;
      utt.onend = detenerVoz;
      utt.onerror = detenerVoz;
      estado.narrando = true;
      const b = document.getElementById("btn-voz");
      if (b) b.textContent = "Detener audio";
      window.speechSynthesis.speak(utt);
    }}

    function abrirPopup(dato) {{
      document.getElementById("popup-cifra").textContent = "Dato de salud mental";
      document.getElementById("popup-titulo").textContent = dato.titulo;
      const pref = dato.cifra_destacada.endsWith("real") ? `${{dato.cifra_destacada}}:` : dato.cifra_destacada;
      document.getElementById("popup-texto").innerHTML = `<strong>${{esc(pref)}} ${{esc(dato.subtitulo_cifra)}}</strong><br>${{esc(dato.explicacion)}}`;
      document.getElementById("popup-tip").innerHTML = `<strong>Tip:</strong> ${{esc(dato.accion_practica)}}`;
      document.getElementById("popup-fuente").textContent = `Fuente: ${{dato.fuente}}`;
      document.getElementById("popup-fondo").hidden = false;
      document.getElementById("btn-cerrar-popup").focus();
    }}

    function cerrarPopup() {{
      document.getElementById("popup-fondo").hidden = true;
    }}

    function render() {{
      detenerVoz();
      cerrarPopup();
      const root = document.getElementById("app-root");
      const totalEsc = OBRA.escenas.length;

      // Portada limpia
      if (estado.paso === 0) {{
        aplicarPaleta(OBRA.escenas[0].paleta);
        const imgInicio = OBRA.escenas[0].imagen_uri;
        const imgFinal = OBRA.escenas[totalEsc - 1].imagen_uri;
        root.innerHTML = `
          <section class="portada-grid">
            <div class="portada-texto">
              <h1>${{esc(OBRA.titulo)}}</h1>
              <p>${{esc(OBRA.subtitulo)}}</p>
              <button type="button" class="btn btn-primario" id="btn-comenzar">Comenzar lectura →</button>
            </div>
            <div class="portada-mosaico">
              ${{imgInicio ? `<div class="marco-imagen"><img src="${{imgInicio}}" alt="${{esc(OBRA.escenas[0].alt_imagen)}}"></div>` : ""}}
              ${{imgFinal ? `<div class="marco-imagen"><img src="${{imgFinal}}" alt="${{esc(OBRA.escenas[totalEsc - 1].alt_imagen)}}"></div>` : ""}}
            </div>
          </section>
        `;
        document.getElementById("btn-comenzar").addEventListener("click", () => {{
          estado.paso = 1;
          render();
          window.scrollTo({{ top: 0, behavior: "smooth" }});
        }});
        return;
      }}

      // Páginas del relato (1..5)
      if (estado.paso >= 1 && estado.paso <= totalEsc) {{
        const e = OBRA.escenas[estado.paso - 1];
        aplicarPaleta(e.paleta);
        root.innerHTML = `
          <header class="pagina-cabecera">
            <div>
              <span class="etiqueta-tiempo">${{esc(e.etiqueta_tiempo)}}</span>
              <h2>${{esc(e.titulo)}}</h2>
            </div>
            <div class="acciones-cabecera">
              <button type="button" class="btn btn-dato" id="btn-abrir-dato">💡 Dato de salud mental</button>
              <button type="button" class="btn" id="btn-voz">Escuchar</button>
            </div>
          </header>

          <section class="pagina-grid">
            <div class="col-visual">
              <div class="marco-imagen">
                ${{e.imagen_uri ? `<img src="${{e.imagen_uri}}" alt="${{esc(e.alt_imagen)}}">` : ""}}
              </div>
              <blockquote class="cita-poetica">“${{esc(e.cita_destacada)}}”</blockquote>
            </div>
            <article class="tarjeta-relato">
              ${{e.parrafos.map((p) => `<p>${{esc(p)}}</p>`).join("")}}
            </article>
          </section>

          <nav class="nav-simple" aria-label="Navegación entre páginas">
            <button type="button" class="btn" id="btn-regresar">← Regresar</button>
            <button type="button" class="btn btn-primario" id="btn-siguiente">Siguiente →</button>
          </nav>
        `;

        document.getElementById("btn-abrir-dato").addEventListener("click", () => abrirPopup(e.dato_salud));
        document.getElementById("btn-voz").addEventListener("click", () => alternarVoz(`${{e.titulo}}. ${{e.parrafos.join(" ")}}`));
        document.getElementById("btn-regresar").addEventListener("click", () => {{
          estado.paso--;
          render();
          window.scrollTo({{ top: 0, behavior: "smooth" }});
        }});
        document.getElementById("btn-siguiente").addEventListener("click", () => {{
          estado.paso++;
          render();
          window.scrollTo({{ top: 0, behavior: "smooth" }});
        }});
        return;
      }}

      // Reflexión final
      const ultima = OBRA.escenas[totalEsc - 1];
      aplicarPaleta(ultima.paleta);
      root.innerHTML = `
        <header class="pagina-cabecera">
          <div>
            <span class="etiqueta-tiempo">Cierre</span>
            <h2>${{esc(OBRA.reflexion_final_titulo)}}</h2>
          </div>
          <div class="acciones-cabecera">
            <button type="button" class="btn" id="btn-voz">Escuchar</button>
          </div>
        </header>

        <section class="reflexion-grid">
          <article class="tarjeta-relato">
            ${{OBRA.reflexion_final_parrafos.map((p) => `<p>${{esc(p)}}</p>`).join("")}}
          </article>
          <div class="marco-imagen">
            ${{ultima.imagen_uri ? `<img src="${{ultima.imagen_uri}}" alt="${{esc(ultima.alt_imagen)}}">` : ""}}
          </div>
        </section>

        <nav class="nav-simple" aria-label="Navegación de cierre">
          <button type="button" class="btn" id="btn-regresar">← Regresar</button>
          <button type="button" class="btn btn-primario" id="btn-inicio">Volver al inicio</button>
        </nav>
      `;

      document.getElementById("btn-voz").addEventListener("click", () =>
        alternarVoz(`${{OBRA.reflexion_final_titulo}}. ${{OBRA.reflexion_final_parrafos.join(" ")}}`)
      );
      document.getElementById("btn-regresar").addEventListener("click", () => {{
        estado.paso = totalEsc;
        render();
        window.scrollTo({{ top: 0, behavior: "smooth" }});
      }});
      document.getElementById("btn-inicio").addEventListener("click", () => {{
        estado.paso = 0;
        render();
        window.scrollTo({{ top: 0, behavior: "smooth" }});
      }});
    }}

    document.getElementById("btn-cerrar-popup").addEventListener("click", cerrarPopup);
    document.getElementById("popup-fondo").addEventListener("click", (e) => {{
      if (e.target.id === "popup-fondo") cerrarPopup();
    }});

    document.addEventListener("keydown", (e) => {{
      const popupAbierto = !document.getElementById("popup-fondo").hidden;
      if (e.key === "Escape" && popupAbierto) {{ cerrarPopup(); return; }}
      if (popupAbierto) return;
      const maxPaso = OBRA.escenas.length + 1;
      if (e.key === "ArrowRight" && estado.paso < maxPaso) {{
        estado.paso++; render();
      }} else if (e.key === "ArrowLeft" && estado.paso > 0) {{
        estado.paso--; render();
      }}
    }});

    render();
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
