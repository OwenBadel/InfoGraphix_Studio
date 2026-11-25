# InfoGraphix Studio

Aplicación web y herramienta de línea de comandos para diseñar y exportar **infografías interactivas** desde un único modelo de datos hacia dos formatos profesionales:

1. **Navegador Web (HTML5 autocontenido):** archivo `.html` portátil (funciona sin conexión) con filtros por categoría, buscador, KPIs y tarjetas expandibles, gráficos vectoriales SVG interactivos (barras, dona y línea), línea de tiempo navegable por teclado, cambio de tema en vivo, modo presentación y estilos de impresión/PDF.
2. **PowerPoint Interactivo (`.pptx` 16:9 editable):** presentación nativa editable con tablero ejecutivo inicial, tarjetas con hipervínculos internos hacia fichas de profundización (`click_action.target_slide`), gráficos nativos editables de PowerPoint, diagrama vectorial de hoja de ruta y barra de navegación interactiva en modo presentación (`F5`).

Desarrollado por **Owen Badel Hooker** — Ingeniero de Sistemas.

---

## Características Principales

- **Estudio Web Interactivo en Vivo:** editor estructurado por pestañas (General, KPIs, Secciones, Gráfico, Hitos y JSON) con vista previa sincronizada en escritorio, tablet y móvil.
- **4 Temas Visuales de Alto Contraste (WCAG AA):** *Swiss Cobalt*, *Editorial Papel y Tinta*, *Obsidian & Sage* y *Estudio Botánico*, sincronizados automáticamente entre HTML y PowerPoint.
- **3 Plantillas Precargadas:** Operaciones & Automatización, Salud Pública Territorial y Hoja de Ruta SaaS B2B.
- **Interfaz CLI:** automatización por lotes desde archivos JSON o plantillas integradas.

---

## Instalación y Uso

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Iniciar el Estudio Web
```bash
python app.py
```
Abre en tu navegador: `http://127.0.0.1:8020`

### 3. Generar desde la Terminal (CLI)
```bash
# Generar HTML y PowerPoint a partir de una plantilla integrada
python -m infographix.cli --preset transformacion_ia --formato ambos --salida output --nombre reporte_2026

# Generar desde un archivo JSON personalizado
python -m infographix.cli --entrada-json mi_infografia.json --formato pptx --salida output --nombre mi_presentacion
```

---

## Estructura del Proyecto

```text
PROJ_020_InfoGraphix_Studio/
├── app.py                     # API FastAPI y servidor del estudio web
├── infographix/
│   ├── cli.py                 # Generación desatendida por terminal
│   ├── domain/
│   │   ├── models.py          # Esquemas Pydantic v2 (InfografiaSpec)
│   │   ├── themes.py          # Paletas WCAG compartidas HTML / PPTX
│   │   └── presets.py         # Plantillas listas para usar
│   └── exporters/
│       ├── html_exporter.py   # Generador HTML5 + SVG + JS autocontenido
│       └── pptx_exporter.py   # Generador PowerPoint 16:9 interactivo
├── static/
│   ├── index.html             # Estudio web responsivo
│   ├── styles.css             # Sistema visual Swiss Precision
│   └── app.js                 # Editor reactivo y descargas
└── tests/                     # Suite automatizada con Pytest
```

## Pruebas Automatizadas

```bash
pytest -v
```
