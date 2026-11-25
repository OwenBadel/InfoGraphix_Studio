"""Plantillas precargadas listas para visualizar y exportar en HTML y PowerPoint."""

from __future__ import annotations

from .models import GraficoSpec, HitoItem, InfografiaSpec, KpiItem, PuntoGrafico, SeccionItem


PRESETS: dict[str, InfografiaSpec] = {
    "transformacion_ia": InfografiaSpec(
        titulo="Adopción de Automatización Inteligente en Operaciones 2026",
        subtitulo="Panorama ejecutivo de impacto en eficiencia operativa, calidad de servicio y retorno de inversión por área.",
        categoria="Reporte Ejecutivo",
        autor="Owen Badel Hooker",
        fuente="Observatorio de Operaciones Digitales · Cohorte 2026",
        tema="swiss_cobalt",
        plantilla="ejecutiva",
        kpis=[
            KpiItem(
                etiqueta="Reducción de tiempos",
                valor="-42%",
                delta="+9 pts YoY",
                tendencia="positiva",
                detalle="Disminución promedio en ciclos de conciliación y generación de reportes.",
            ),
            KpiItem(
                etiqueta="ROI primer año",
                valor="3.4x",
                delta="Payback 4.2 meses",
                tendencia="positiva",
                detalle="Retorno acumulado descontando licencias, infraestructura y capacitación.",
            ),
            KpiItem(
                etiqueta="Procesos automatizados",
                valor="68%",
                delta="19 flujos activos",
                tendencia="neutra",
                detalle="Cobertura actual sobre procesos administrativos y analíticos críticos.",
            ),
            KpiItem(
                etiqueta="Precisión de datos",
                valor="99.4%",
                delta="-78% retrabajo",
                tendencia="positiva",
                detalle="Validación automática con reglas de negocio y trazabilidad de auditoría.",
            ),
        ],
        secciones=[
            SeccionItem(
                id="operaciones",
                titulo="Automatización de Flujos Operativos",
                categoria="Operaciones",
                metrica="1,420 h/mes ahorradas",
                resumen="Integración directa entre ERP, facturación y alertas tempranas sin captura manual repetitiva.",
                detalle="Se reemplazaron hojas de cálculo desconectadas por pipelines validados con registro de auditoría en tiempo real, liberando al equipo analítico para decisiones de mayor valor.",
                puntos_clave=[
                    "Validación automática de comprobantes y facturas antes de registro contable.",
                    "Alertas inmediatas ante desviaciones superiores al 3% en inventarios.",
                    "Trazabilidad completa por usuario, fecha y documento origen.",
                ],
            ),
            SeccionItem(
                id="analitica",
                titulo="Inteligencia Analítica en Tiempo Real",
                categoria="Datos",
                metrica="< 2 min latencia",
                resumen="Tableros ejecutivos actualizados de forma continua con indicadores unificados por sede.",
                detalle="La consolidación automatizada elimina el cierre manual de fin de mes y permite detectar tendencias comerciales con semanas de anticipación.",
                puntos_clave=[
                    "Fuente única de verdad compartida entre gerencia y operación.",
                    "Exportación inmediata en formatos interactivos HTML y PowerPoint.",
                    "Segmentación por región, canal de venta y margen neto.",
                ],
            ),
            SeccionItem(
                id="experiencia",
                titulo="Atención y Respuesta al Cliente",
                categoria="Servicio",
                metrica="94% CSAT",
                resumen="Clasificación inteligente de solicitudes y seguimiento proactivo de tickets prioritarios.",
                detalle="Los casos frecuentes se resuelven en minutos con respuestas verificadas, mientras los casos complejos escalan con contexto estructurado al especialista adecuado.",
                puntos_clave=[
                    "Tiempo medio de primera respuesta reducido de 6 horas a 14 minutos.",
                    "Escalamiento contextual sin obligar al cliente a repetir información.",
                    "Encuestas post-atención integradas al tablero de calidad.",
                ],
            ),
            SeccionItem(
                id="gobierno",
                titulo="Gobierno, Seguridad y Cumplimiento",
                categoria="Seguridad",
                metrica="0 incidentes",
                resumen="Control de acceso por roles, cifrado en tránsito y auditoría continua de integraciones.",
                detalle="Cada automatización opera con principio de mínimo privilegio, respaldo diario verificado y bitácora inmutable de cambios.",
                puntos_clave=[
                    "Separación estricta entre entornos de pruebas y producción.",
                    "Rotación programada de credenciales y monitoreo de anomalías.",
                    "Revisión trimestral de cumplimiento y continuidad operativa.",
                ],
            ),
        ],
        grafico=GraficoSpec(
            titulo="Ahorro Mensual de Horas por Área Funcional",
            tipo="barras",
            unidad="h",
            descripcion="Horas hombre recuperadas mensualmente tras seis meses de operación estabilizada.",
            puntos=[
                PuntoGrafico(etiqueta="Finanzas", valor=420, detalle="Conciliación bancaria y cierres automáticos."),
                PuntoGrafico(etiqueta="Operaciones", valor=380, detalle="Programación de despachos e inventarios."),
                PuntoGrafico(etiqueta="Comercial", valor=290, detalle="Cotizaciones y seguimiento de cartera."),
                PuntoGrafico(etiqueta="Soporte", valor=210, detalle="Clasificación y resolución de tickets."),
                PuntoGrafico(etiqueta="Talento", valor=120, detalle="Nómina, certificados y onboarding."),
            ],
        ),
        hitos=[
            HitoItem(
                fase="Fase 01",
                titulo="Diagnóstico y Mapa de Procesos",
                periodo="Mes 1",
                descripcion="Levantamiento de cuellos de botella, calidad de fuentes y priorización por impacto.",
                impacto="12 casos de uso priorizados",
            ),
            HitoItem(
                fase="Fase 02",
                titulo="Piloto en Finanzas y Reportes",
                periodo="Meses 2–3",
                descripcion="Despliegue controlado del primer flujo automatizado con validación paralela.",
                impacto="Primer ahorro de 320 h/mes",
            ),
            HitoItem(
                fase="Fase 03",
                titulo="Escalamiento Multisede",
                periodo="Meses 4–5",
                descripcion="Integración de operaciones, comercial y soporte bajo un modelo común de datos.",
                impacto="68% de cobertura operativa",
            ),
            HitoItem(
                fase="Fase 04",
                titulo="Optimización Continua",
                periodo="Mes 6+",
                descripcion="Gobierno de indicadores, alertas predictivas y formación de equipos internos.",
                impacto="ROI consolidado de 3.4x",
            ),
        ],
    ),
    "salud_publica": InfografiaSpec(
        titulo="Indicadores de Prevención y Atención Primaria Territorial",
        subtitulo="Síntesis visual de cobertura comunitaria, oportunidad de diagnóstico y seguimiento de pacientes crónicos.",
        categoria="Salud Pública",
        autor="Owen Badel Hooker",
        fuente="Red Territorial de Atención Primaria · Corte Semestral",
        tema="editorial_papel",
        plantilla="comparativa",
        kpis=[
            KpiItem(
                etiqueta="Cobertura territorial",
                valor="87.5%",
                delta="+11.2% semestral",
                tendencia="positiva",
                detalle="Hogares caracterizados y vinculados a rutas preventivas activas.",
            ),
            KpiItem(
                etiqueta="Control hipertensión",
                valor="76%",
                delta="+8 pts",
                tendencia="positiva",
                detalle="Pacientes en meta terapéutica con seguimiento trimestral.",
            ),
            KpiItem(
                etiqueta="Tiempo de remisión",
                valor="4.8 días",
                delta="-3.1 días",
                tendencia="positiva",
                detalle="Promedio desde tamizaje en campo hasta cita con medicina interna.",
            ),
            KpiItem(
                etiqueta="Adherencia digital",
                valor="81%",
                delta="3,480 familias",
                tendencia="neutra",
                detalle="Familias que confirman controles mediante recordatorios activos.",
            ),
        ],
        secciones=[
            SeccionItem(
                id="tamizaje",
                titulo="Tamizaje Preventivo en Campo",
                categoria="Prevención",
                metrica="4,920 valoraciones",
                resumen="Equipos extramurales con captura móvil offline para zonas rurales y periurbanas.",
                detalle="La digitalización en punto de atención eliminó la transcripción en papel y permitió detectar riesgo cardiovascular temprano en la misma jornada.",
                puntos_clave=[
                    "Registro offline con sincronización automática al recuperar señal.",
                    "Clasificación inmediata de riesgo bajo, moderado y alto.",
                    "Georreferenciación de microterritorios prioritarios.",
                ],
            ),
            SeccionItem(
                id="cronicos",
                titulo="Seguimiento de Pacientes Crónicos",
                categoria="Atención",
                metrica="1,240 activos",
                resumen="Monitoreo estructurado de hipertensión y diabetes con alertas de inasistencia.",
                detalle="Cada paciente cuenta con un calendario de controles, entregas de medicamentos y canal directo de teleorientación ante signos de alarma.",
                puntos_clave=[
                    "Reducción del 34% en urgencias evitables.",
                    "Recordatorios automatizados 48 horas antes de cada cita.",
                    "Tablero clínico para enfermería y medicina familiar.",
                ],
            ),
            SeccionItem(
                id="vacunacion",
                titulo="Esquemas de Vacunación Infantil",
                categoria="Prevención",
                metrica="93.2% cobertura",
                resumen="Cierre de brechas en menores de 5 años mediante jornadas focalizadas por barrio.",
                detalle="El cruce de carnés digitales identificó cohortes pendientes y optimizó la asignación de biológicos sin desperdicio de cadena de frío.",
                puntos_clave=[
                    "Seguimiento nominal de dosis de refuerzo.",
                    "Control diario de temperatura y stock por punto móvil.",
                ],
            ),
        ],
        grafico=GraficoSpec(
            titulo="Distribución de Atenciones por Ruta de Cuidado (%)",
            tipo="dona",
            unidad="%",
            descripcion="Proporción de intervenciones realizadas durante el último semestre.",
            puntos=[
                PuntoGrafico(etiqueta="Cardiovascular", valor=36, detalle="Tamizaje y control de hipertensión/diabetes."),
                PuntoGrafico(etiqueta="Materno-Infantil", valor=28, detalle="Control prenatal y vacunación."),
                PuntoGrafico(etiqueta="Salud Mental", valor=18, detalle="Tamizaje psicosocial y orientación."),
                PuntoGrafico(etiqueta="Nutrición", valor=18, detalle="Valoración nutricional y educación familiar."),
            ],
        ),
        hitos=[
            HitoItem(
                fase="Etapa 1",
                titulo="Caracterización Familiar",
                periodo="Trimestre 1",
                descripcion="Censo sanitario digital en 18 veredas y sectores urbanos priorizados.",
                impacto="4,920 personas caracterizadas",
            ),
            HitoItem(
                fase="Etapa 2",
                titulo="Activación de Rutas",
                periodo="Trimestre 2",
                descripcion="Asignación automática de citas preventivas según nivel de riesgo detectado.",
                impacto="-3.1 días en oportunidad",
            ),
            HitoItem(
                fase="Etapa 3",
                titulo="Seguimiento Longitudinal",
                periodo="Trimestre 3",
                descripcion="Evaluación de adherencia terapéutica y ajuste de intervenciones comunitarias.",
                impacto="76% en control clínico",
            ),
        ],
    ),
    "roadmap_producto": InfografiaSpec(
        titulo="Hoja de Ruta de Producto: Plataforma SaaS B2B",
        subtitulo="Evolución trimestral de capacidades técnicas, adopción de clientes empresariales y metas de ingresos recurrentes.",
        categoria="Estrategia de Producto",
        autor="Owen Badel Hooker",
        fuente="Plan Estratégico de Ingeniería y Producto",
        tema="obsidian_sage",
        plantilla="linea_tiempo",
        kpis=[
            KpiItem(
                etiqueta="ARR Proyectado",
                valor="$1.8M",
                delta="+64% meta anual",
                tendencia="positiva",
                detalle="Ingresos recurrentes anuales impulsados por expansión en cuentas medianas.",
            ),
            KpiItem(
                etiqueta="Retención Neta",
                valor="118%",
                delta="+6 pts",
                tendencia="positiva",
                detalle="Expansión por módulos adicionales superior a la tasa de cancelación.",
            ),
            KpiItem(
                etiqueta="Disponibilidad SLA",
                valor="99.95%",
                delta="Multi-región",
                tendencia="neutra",
                detalle="Arquitectura activa-activa con conmutación automática y observabilidad.",
            ),
        ],
        secciones=[
            SeccionItem(
                id="nucleo",
                titulo="Motor de Flujos y API Pública",
                categoria="Plataforma",
                metrica="45 webhooks",
                resumen="APIs versionadas con documentación interactiva y SDK oficial para integradores.",
                detalle="Permite a clientes empresariales conectar eventos internos con su ERP, CRM o almacén de datos en menos de una jornada.",
                puntos_clave=[
                    "Autenticación OAuth 2.0 y llaves con alcance granular.",
                    "Reintentos exponenciales y cola de eventos fallidos.",
                ],
            ),
            SeccionItem(
                id="colaboracion",
                titulo="Espacios Colaborativos en Tiempo Real",
                categoria="Experiencia",
                metrica="3.2x uso diario",
                resumen="Comentarios contextuales, aprobaciones con historial y vistas compartidas por rol.",
                detalle="Reduce el intercambio de archivos por correo y concentra la toma de decisiones directamente sobre los datos actualizados.",
                puntos_clave=[
                    "Permisos por equipo y enlace de solo lectura auditable.",
                    "Exportación inmediata para comités directivos.",
                ],
            ),
            SeccionItem(
                id="seguridad",
                titulo="Cumplimiento Enterprise y SSO",
                categoria="Seguridad",
                metrica="SAML 2.0",
                resumen="Inicio de sesión único corporativo, registro de auditoría y retención configurable.",
                detalle="Desbloquea ventas en banca, salud y manufactura donde la auditoría de accesos es requisito contractual.",
                puntos_clave=[
                    "Compatibilidad con Entra ID, Okta y Google Workspace.",
                    "Exportación de bitácoras en formato SIEM estándar.",
                ],
            ),
        ],
        grafico=GraficoSpec(
            titulo="Crecimiento Trimestral de Cuentas Activas",
            tipo="linea",
            unidad=" emp",
            descripcion="Evolución proyectada de organizaciones activas pagando suscripción anual.",
            puntos=[
                PuntoGrafico(etiqueta="Q1", valor=48, detalle="Base inicial tras lanzamiento v2."),
                PuntoGrafico(etiqueta="Q2", valor=74, detalle="Lanzamiento de API pública y conectores."),
                PuntoGrafico(etiqueta="Q3", valor=112, detalle="Adopción de SSO y expansión mid-market."),
                PuntoGrafico(etiqueta="Q4", valor=158, detalle="Consolidación de red de socios."),
            ],
        ),
        hitos=[
            HitoItem(
                fase="Q1",
                titulo="Fundación v2 y Observabilidad",
                periodo="Ene – Mar",
                descripcion="Refactorización de núcleo multi-tenant y telemetría de latencia p95.",
                impacto="Latencia < 120 ms",
            ),
            HitoItem(
                fase="Q2",
                titulo="Ecosistema API y Webhooks",
                periodo="Abr – Jun",
                descripcion="Portal de desarrolladores, conectores nativos y sandbox de pruebas.",
                impacto="+54% cuentas integradas",
            ),
            HitoItem(
                fase="Q3",
                titulo="Suite Enterprise (SSO + Auditoría)",
                periodo="Jul – Sep",
                descripcion="Habilitación de SAML 2.0, roles avanzados y cumplimiento corporativo.",
                impacto="Ticket promedio +38%",
            ),
            HitoItem(
                fase="Q4",
                titulo="Analítica Predictiva Embebida",
                periodo="Oct – Dic",
                descripcion="Alertas automáticas de riesgo y reportes ejecutivos programados.",
                impacto="Retención neta 118%",
            ),
        ],
    ),
}


def obtener_preset(preset_id: str) -> InfografiaSpec | None:
    """Devuelve una copia independiente del preset solicitado."""
    base = PRESETS.get(preset_id)
    return base.model_copy(deep=True) if base else None


def listar_presets() -> list[dict[str, str]]:
    """Resumen liviano de presets para el selector del estudio web."""
    return [
        {
            "id": key,
            "titulo": spec.titulo,
            "categoria": spec.categoria,
            "tema": spec.tema,
            "plantilla": spec.plantilla,
        }
        for key, spec in PRESETS.items()
    ]
