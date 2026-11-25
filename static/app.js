"use strict";

let estadoSpec = null;
let ultimoHtmlGenerado = "";
let debounceTimer = null;

const el = (id) => document.getElementById(id);

function mostrarBanner(mensaje, esError = false) {
  const banner = el("estado-banner");
  banner.textContent = mensaje;
  banner.classList.toggle("error", esError);
  banner.hidden = false;
  if (!esError) {
    window.setTimeout(() => {
      banner.hidden = true;
    }, 3500);
  }
}

function setEstadoPreview(texto) {
  el("preview-estado").textContent = texto;
}

function programarPreview() {
  el("textarea-json").value = JSON.stringify(estadoSpec, null, 2);
  setEstadoPreview("Actualizando...");
  window.clearTimeout(debounceTimer);
  debounceTimer = window.setTimeout(() => actualizarPreview(), 220);
}

async function actualizarPreview() {
  if (!estadoSpec) return;
  try {
    const resp = await fetch("/api/preview/html", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(estadoSpec),
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(err.detail ? JSON.stringify(err.detail) : "Error de validación");
    }
    const html = await resp.text();
    ultimoHtmlGenerado = html;
    el("preview-iframe").srcdoc = html;
    setEstadoPreview("Sincronizado");
    el("estado-banner").hidden = true;
  } catch (error) {
    setEstadoPreview("Revisar datos");
    mostrarBanner(`No se pudo actualizar la vista previa: ${error.message}`, true);
  }
}

async function descargarArchivo(endpoint, extension) {
  if (!estadoSpec) return;
  setEstadoPreview(`Generando ${extension.toUpperCase()}...`);
  try {
    const resp = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(estadoSpec),
    });
    if (!resp.ok) {
      throw new Error("Revisa que los campos obligatorios estén completos.");
    }
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const enlace = document.createElement("a");
    const slug = (estadoSpec.titulo || "infografia")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_|_$/g, "")
      .slice(0, 50) || "infografia";
    enlace.href = url;
    enlace.download = `${slug}.${extension}`;
    document.body.appendChild(enlace);
    enlace.click();
    enlace.remove();
    URL.revokeObjectURL(url);
    setEstadoPreview("Sincronizado");
    mostrarBanner(`Archivo .${extension} descargado correctamente.`);
  } catch (error) {
    setEstadoPreview("Error al exportar");
    mostrarBanner(`Error al exportar .${extension}: ${error.message}`, true);
  }
}

function sincronizarFormularioDesdeSpec() {
  el("inp-titulo").value = estadoSpec.titulo || "";
  el("inp-subtitulo").value = estadoSpec.subtitulo || "";
  el("inp-categoria").value = estadoSpec.categoria || "";
  el("inp-autor").value = estadoSpec.autor || "";
  el("inp-fuente").value = estadoSpec.fuente || "";
  el("inp-tema").value = estadoSpec.tema || "swiss_cobalt";
  el("inp-plantilla").value = estadoSpec.plantilla || "ejecutiva";

  renderEditorKpis();
  renderEditorSecciones();
  renderEditorGrafico();
  renderEditorHitos();
  el("textarea-json").value = JSON.stringify(estadoSpec, null, 2);
}

function renderEditorKpis() {
  const cont = el("lista-kpis");
  cont.innerHTML = "";
  const kpis = estadoSpec.kpis || [];
  if (kpis.length === 0) {
    cont.innerHTML = `<p class="ayuda-texto">Sin KPIs configurados. Pulsa "+ Agregar KPI" para añadir indicadores.</p>`;
    return;
  }
  kpis.forEach((kpi, idx) => {
    const div = document.createElement("div");
    div.className = "item-bloque";
    div.innerHTML = `
      <div class="item-bloque-top">
        <span class="item-indice">KPI #${idx + 1}</span>
        <button type="button" class="btn btn-pequeno btn-peligro" data-del="${idx}">Eliminar</button>
      </div>
      <div class="fila-dos">
        <div class="campo"><label>Etiqueta</label><input type="text" data-k="etiqueta" value="${escAttr(kpi.etiqueta)}"></div>
        <div class="campo"><label>Valor</label><input type="text" data-k="valor" value="${escAttr(kpi.valor)}"></div>
      </div>
      <div class="fila-dos">
        <div class="campo"><label>Delta / Variación</label><input type="text" data-k="delta" value="${escAttr(kpi.delta)}"></div>
        <div class="campo"><label>Tendencia</label>
          <select data-k="tendencia">
            <option value="positiva" ${kpi.tendencia === "positiva" ? "selected" : ""}>Positiva</option>
            <option value="neutra" ${kpi.tendencia === "neutra" ? "selected" : ""}>Neutra</option>
            <option value="alerta" ${kpi.tendencia === "alerta" ? "selected" : ""}>Alerta</option>
          </select>
        </div>
      </div>
      <div class="campo"><label>Detalle expandible</label><input type="text" data-k="detalle" value="${escAttr(kpi.detalle)}"></div>
    `;
    div.querySelectorAll("[data-k]").forEach((inp) => {
      inp.addEventListener("input", () => {
        estadoSpec.kpis[idx][inp.dataset.k] = inp.value;
        programarPreview();
      });
    });
    div.querySelector("[data-del]").addEventListener("click", () => {
      estadoSpec.kpis.splice(idx, 1);
      renderEditorKpis();
      programarPreview();
    });
    cont.appendChild(div);
  });
}

function renderEditorSecciones() {
  const cont = el("lista-secciones");
  cont.innerHTML = "";
  estadoSpec.secciones.forEach((sec, idx) => {
    const div = document.createElement("div");
    div.className = "item-bloque";
    div.innerHTML = `
      <div class="item-bloque-top">
        <span class="item-indice">SECCIÓN #${idx + 1}</span>
        <button type="button" class="btn btn-pequeno btn-peligro" data-del="${idx}" ${estadoSpec.secciones.length <= 1 ? "disabled" : ""}>Eliminar</button>
      </div>
      <div class="campo"><label>Título</label><input type="text" data-k="titulo" value="${escAttr(sec.titulo)}"></div>
      <div class="fila-dos">
        <div class="campo"><label>Categoría</label><input type="text" data-k="categoria" value="${escAttr(sec.categoria)}"></div>
        <div class="campo"><label>Métrica destacada</label><input type="text" data-k="metrica" value="${escAttr(sec.metrica)}"></div>
      </div>
      <div class="campo"><label>Resumen</label><textarea rows="2" data-k="resumen">${escText(sec.resumen)}</textarea></div>
      <div class="campo"><label>Análisis detallado</label><textarea rows="2" data-k="detalle">${escText(sec.detalle)}</textarea></div>
      <div class="campo"><label>Puntos clave (uno por línea)</label><textarea rows="3" data-puntos="1">${escText((sec.puntos_clave || []).join("\n"))}</textarea></div>
    `;
    div.querySelectorAll("[data-k]").forEach((inp) => {
      inp.addEventListener("input", () => {
        estadoSpec.secciones[idx][inp.dataset.k] = inp.value;
        programarPreview();
      });
    });
    div.querySelector("[data-puntos]").addEventListener("input", (e) => {
      estadoSpec.secciones[idx].puntos_clave = e.target.value
        .split("\n")
        .map((s) => s.trim())
        .filter(Boolean);
      programarPreview();
    });
    div.querySelector("[data-del]").addEventListener("click", () => {
      if (estadoSpec.secciones.length <= 1) return;
      estadoSpec.secciones.splice(idx, 1);
      renderEditorSecciones();
      programarPreview();
    });
    cont.appendChild(div);
  });
}

function renderEditorGrafico() {
  const activo = Boolean(estadoSpec.grafico);
  el("chk-grafico-activo").checked = activo;
  el("form-grafico-wrap").hidden = !activo;
  if (!activo) return;

  el("inp-grafico-titulo").value = estadoSpec.grafico.titulo || "";
  el("inp-grafico-tipo").value = estadoSpec.grafico.tipo || "barras";
  el("inp-grafico-unidad").value = estadoSpec.grafico.unidad || "";
  el("inp-grafico-desc").value = estadoSpec.grafico.descripcion || "";

  const cont = el("lista-puntos");
  cont.innerHTML = "";
  estadoSpec.grafico.puntos.forEach((pt, idx) => {
    const div = document.createElement("div");
    div.className = "item-bloque";
    div.innerHTML = `
      <div class="item-bloque-top">
        <span class="item-indice">DATO #${idx + 1}</span>
        <button type="button" class="btn btn-pequeno btn-peligro" data-del="${idx}" ${estadoSpec.grafico.puntos.length <= 2 ? "disabled" : ""}>Eliminar</button>
      </div>
      <div class="fila-dos">
        <div class="campo"><label>Etiqueta</label><input type="text" data-k="etiqueta" value="${escAttr(pt.etiqueta)}"></div>
        <div class="campo"><label>Valor numérico</label><input type="number" step="any" min="0" data-k="valor" value="${escAttr(pt.valor)}"></div>
      </div>
      <div class="campo"><label>Detalle al seleccionar</label><input type="text" data-k="detalle" value="${escAttr(pt.detalle)}"></div>
    `;
    div.querySelectorAll("[data-k]").forEach((inp) => {
      inp.addEventListener("input", () => {
        const clave = inp.dataset.k;
        estadoSpec.grafico.puntos[idx][clave] = clave === "valor" ? Number(inp.value) || 0 : inp.value;
        programarPreview();
      });
    });
    div.querySelector("[data-del]").addEventListener("click", () => {
      if (estadoSpec.grafico.puntos.length <= 2) return;
      estadoSpec.grafico.puntos.splice(idx, 1);
      renderEditorGrafico();
      programarPreview();
    });
    cont.appendChild(div);
  });
}

function renderEditorHitos() {
  const cont = el("lista-hitos");
  cont.innerHTML = "";
  const hitos = estadoSpec.hitos || [];
  if (hitos.length === 0) {
    cont.innerHTML = `<p class="ayuda-texto">Sin hitos definidos. Pulsa "+ Agregar hito" para construir una línea de tiempo interactiva.</p>`;
    return;
  }
  hitos.forEach((h, idx) => {
    const div = document.createElement("div");
    div.className = "item-bloque";
    div.innerHTML = `
      <div class="item-bloque-top">
        <span class="item-indice">HITO #${idx + 1}</span>
        <button type="button" class="btn btn-pequeno btn-peligro" data-del="${idx}">Eliminar</button>
      </div>
      <div class="fila-dos">
        <div class="campo"><label>Fase</label><input type="text" data-k="fase" value="${escAttr(h.fase)}"></div>
        <div class="campo"><label>Periodo</label><input type="text" data-k="periodo" value="${escAttr(h.periodo)}"></div>
      </div>
      <div class="campo"><label>Título</label><input type="text" data-k="titulo" value="${escAttr(h.titulo)}"></div>
      <div class="campo"><label>Descripción</label><textarea rows="2" data-k="descripcion">${escText(h.descripcion)}</textarea></div>
      <div class="campo"><label>Impacto</label><input type="text" data-k="impacto" value="${escAttr(h.impacto)}"></div>
    `;
    div.querySelectorAll("[data-k]").forEach((inp) => {
      inp.addEventListener("input", () => {
        estadoSpec.hitos[idx][inp.dataset.k] = inp.value;
        programarPreview();
      });
    });
    div.querySelector("[data-del]").addEventListener("click", () => {
      estadoSpec.hitos.splice(idx, 1);
      renderEditorHitos();
      programarPreview();
    });
    cont.appendChild(div);
  });
}

function escAttr(v) {
  return String(v ?? "").replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");
}

function escText(v) {
  return String(v ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;");
}

function enlazarEventos() {
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.tab;
      document.querySelectorAll(".tab-btn").forEach((b) => {
        const activo = b.dataset.tab === target;
        b.classList.toggle("activo", activo);
        b.setAttribute("aria-selected", String(activo));
      });
      document.querySelectorAll("[data-panel]").forEach((p) => {
        p.hidden = p.dataset.panel !== target;
      });
    });
  });

  const camposGenerales = [
    ["inp-titulo", "titulo"],
    ["inp-subtitulo", "subtitulo"],
    ["inp-categoria", "categoria"],
    ["inp-autor", "autor"],
    ["inp-fuente", "fuente"],
    ["inp-tema", "tema"],
    ["inp-plantilla", "plantilla"],
  ];
  camposGenerales.forEach(([id, prop]) => {
    el(id).addEventListener("input", (e) => {
      estadoSpec[prop] = e.target.value;
      programarPreview();
    });
  });

  el("btn-add-kpi").addEventListener("click", () => {
    if (estadoSpec.kpis.length >= 4) {
      mostrarBanner("El máximo recomendado es de 4 KPIs destacados.", true);
      return;
    }
    estadoSpec.kpis.push({
      etiqueta: "Nuevo indicador",
      valor: "100%",
      delta: "+10%",
      tendencia: "positiva",
      detalle: "Descripción del indicador.",
    });
    renderEditorKpis();
    programarPreview();
  });

  el("btn-add-seccion").addEventListener("click", () => {
    if (estadoSpec.secciones.length >= 8) {
      mostrarBanner("Máximo 8 secciones por infografía.", true);
      return;
    }
    const n = estadoSpec.secciones.length + 1;
    estadoSpec.secciones.push({
      id: `sec-${n}`,
      titulo: `Bloque temático ${n}`,
      categoria: "General",
      metrica: "Destacado",
      resumen: "Síntesis ejecutiva del bloque.",
      detalle: "Análisis ampliado visible al desplegar en HTML y en la ficha de PowerPoint.",
      puntos_clave: ["Hallazgo principal verificable."],
    });
    renderEditorSecciones();
    programarPreview();
  });

  el("chk-grafico-activo").addEventListener("change", (e) => {
    if (e.target.checked) {
      estadoSpec.grafico = estadoSpec.grafico || {
        titulo: "Comparativa de Indicadores",
        tipo: "barras",
        unidad: "%",
        descripcion: "Distribución de resultados por categoría.",
        puntos: [
          { etiqueta: "Categoría A", valor: 65, detalle: "Desempeño inicial." },
          { etiqueta: "Categoría B", valor: 88, detalle: "Desempeño optimizado." },
        ],
      };
    } else {
      estadoSpec.grafico = null;
    }
    renderEditorGrafico();
    programarPreview();
  });

  [
    ["inp-grafico-titulo", "titulo"],
    ["inp-grafico-tipo", "tipo"],
    ["inp-grafico-unidad", "unidad"],
    ["inp-grafico-desc", "descripcion"],
  ].forEach(([id, prop]) => {
    el(id).addEventListener("input", (e) => {
      if (!estadoSpec.grafico) return;
      estadoSpec.grafico[prop] = e.target.value;
      programarPreview();
    });
  });

  el("btn-add-punto").addEventListener("click", () => {
    if (!estadoSpec.grafico || estadoSpec.grafico.puntos.length >= 10) return;
    estadoSpec.grafico.puntos.push({
      etiqueta: `Dato ${estadoSpec.grafico.puntos.length + 1}`,
      valor: 50,
      detalle: "Detalle del punto.",
    });
    renderEditorGrafico();
    programarPreview();
  });

  el("btn-add-hito").addEventListener("click", () => {
    if (estadoSpec.hitos.length >= 6) {
      mostrarBanner("Máximo 6 hitos en la línea de tiempo.", true);
      return;
    }
    const n = estadoSpec.hitos.length + 1;
    estadoSpec.hitos.push({
      fase: `Fase 0${n}`,
      titulo: `Etapa ${n}`,
      periodo: `Mes ${n}`,
      descripcion: "Descripción de la etapa.",
      impacto: "Entregable verificado",
    });
    renderEditorHitos();
    programarPreview();
  });

  el("btn-aplicar-json").addEventListener("click", () => {
    try {
      const parsed = JSON.parse(el("textarea-json").value);
      estadoSpec = parsed;
      sincronizarFormularioDesdeSpec();
      actualizarPreview();
      mostrarBanner("Esquema JSON aplicado correctamente.");
    } catch (error) {
      mostrarBanner(`JSON inválido: ${error.message}`, true);
    }
  });

  el("btn-descargar-json").addEventListener("click", () => {
    const blob = new Blob([JSON.stringify(estadoSpec, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "infografia_spec.json";
    a.click();
    URL.revokeObjectURL(url);
  });

  el("select-preset").addEventListener("change", async (e) => {
    await cargarPreset(e.target.value);
  });

  el("btn-export-html").addEventListener("click", () => descargarArchivo("/api/export/html", "html"));
  el("btn-export-pptx").addEventListener("click", () => descargarArchivo("/api/export/pptx", "pptx"));

  el("btn-abrir-ventana").addEventListener("click", () => {
    if (!ultimoHtmlGenerado) return;
    const blob = new Blob([ultimoHtmlGenerado], { type: "text/html;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    window.open(url, "_blank", "noopener");
  });

  document.querySelectorAll(".btn-vp").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".btn-vp").forEach((b) => b.classList.remove("activo"));
      btn.classList.add("activo");
      const stage = el("preview-stage");
      stage.classList.remove("vp-tablet", "vp-mobile");
      if (btn.dataset.vp === "tablet") stage.classList.add("vp-tablet");
      if (btn.dataset.vp === "mobile") stage.classList.add("vp-mobile");
    });
  });
}

async function cargarPreset(presetId) {
  const resp = await fetch(`/api/presets/${encodeURIComponent(presetId)}`);
  if (!resp.ok) {
    mostrarBanner("No se pudo cargar la plantilla seleccionada.", true);
    return;
  }
  estadoSpec = await resp.json();
  sincronizarFormularioDesdeSpec();
  await actualizarPreview();
}

async function iniciar() {
  try {
    const [temasResp, presetsResp] = await Promise.all([
      fetch("/api/temas"),
      fetch("/api/presets"),
    ]);
    const temas = await temasResp.json();
    const presets = await presetsResp.json();

    el("inp-tema").innerHTML = temas
      .map((t) => `<option value="${escAttr(t.id)}">${escText(t.nombre)}</option>`)
      .join("");

    el("select-preset").innerHTML = presets
      .map((p) => `<option value="${escAttr(p.id)}">${escText(p.categoria)} — ${escText(p.titulo.slice(0, 42))}</option>`)
      .join("");

    enlazarEventos();
    if (presets.length > 0) {
      await cargarPreset(presets[0].id);
    }
  } catch (error) {
    mostrarBanner(`Error inicializando el estudio: ${error.message}`, true);
  }
}

document.addEventListener("DOMContentLoaded", iniciar);
