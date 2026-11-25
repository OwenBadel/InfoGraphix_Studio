"""Modelos de dominio validados con Pydantic v2 para infografías interactivas."""

from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field, field_validator


TemaId = Literal[
    "swiss_cobalt",
    "editorial_papel",
    "obsidian_sage",
    "terracota_estudio",
]

PlantillaId = Literal[
    "ejecutiva",
    "proceso",
    "comparativa",
    "linea_tiempo",
]

TipoGrafico = Literal["barras", "dona", "linea"]


class KpiItem(BaseModel):
    """Indicador clave destacado en la cabecera de la infografía."""

    etiqueta: str = Field(..., min_length=1, max_length=60)
    valor: str = Field(..., min_length=1, max_length=32)
    delta: str = Field(default="", max_length=32)
    tendencia: Literal["positiva", "neutra", "alerta"] = "positiva"
    detalle: str = Field(default="", max_length=240)


class SeccionItem(BaseModel):
    """Bloque narrativo interactivo con vista resumida y profundización."""

    id: str = Field(..., min_length=1, max_length=40)
    titulo: str = Field(..., min_length=1, max_length=90)
    categoria: str = Field(default="General", min_length=1, max_length=40)
    metrica: str = Field(default="", max_length=32)
    resumen: str = Field(..., min_length=1, max_length=260)
    detalle: str = Field(default="", max_length=650)
    puntos_clave: list[str] = Field(default_factory=list, max_length=6)

    @field_validator("puntos_clave")
    @classmethod
    def limpiar_puntos(cls, valor: list[str]) -> list[str]:
        return [p.strip() for p in valor if p and p.strip()]


class PuntoGrafico(BaseModel):
    """Punto de datos individual para el gráfico vectorial e interactivo."""

    etiqueta: str = Field(..., min_length=1, max_length=40)
    valor: float = Field(..., ge=0)
    detalle: str = Field(default="", max_length=180)


class GraficoSpec(BaseModel):
    """Especificación del gráfico principal de la infografía."""

    titulo: str = Field(..., min_length=1, max_length=100)
    tipo: TipoGrafico = "barras"
    unidad: str = Field(default="", max_length=16)
    descripcion: str = Field(default="", max_length=260)
    puntos: list[PuntoGrafico] = Field(default_factory=list, min_length=2, max_length=10)


class HitoItem(BaseModel):
    """Paso o hito de línea de tiempo interactiva."""

    fase: str = Field(..., min_length=1, max_length=24)
    titulo: str = Field(..., min_length=1, max_length=80)
    periodo: str = Field(default="", max_length=32)
    descripcion: str = Field(..., min_length=1, max_length=280)
    impacto: str = Field(default="", max_length=120)


class InfografiaSpec(BaseModel):
    """Especificación única y agnóstica del medio para HTML y PowerPoint."""

    titulo: str = Field(..., min_length=3, max_length=120)
    subtitulo: str = Field(default="", max_length=240)
    categoria: str = Field(default="Infografía Interactiva", max_length=50)
    autor: str = Field(default="Owen Badel Hooker", max_length=80)
    fuente: str = Field(default="", max_length=140)
    tema: TemaId = "swiss_cobalt"
    plantilla: PlantillaId = "ejecutiva"
    kpis: list[KpiItem] = Field(default_factory=list, max_length=4)
    secciones: list[SeccionItem] = Field(..., min_length=1, max_length=8)
    grafico: GraficoSpec | None = None
    hitos: list[HitoItem] = Field(default_factory=list, max_length=6)

    @field_validator("secciones")
    @classmethod
    def asegurar_ids_unicos(cls, secciones: list[SeccionItem]) -> list[SeccionItem]:
        vistos: set[str] = set()
        for indice, sec in enumerate(secciones, start=1):
            base = sec.id.strip() or f"sec-{indice}"
            candidato = base
            sufijo = 2
            while candidato in vistos:
                candidato = f"{base}-{sufijo}"
                sufijo += 1
            sec.id = candidato
            vistos.add(candidato)
        return secciones

    def categorias_unicas(self) -> list[str]:
        """Devuelve las categorías únicas presentes en las secciones en orden de aparición."""
        vistas: list[str] = []
        for sec in self.secciones:
            if sec.categoria not in vistas:
                vistas.append(sec.categoria)
        return vistas
