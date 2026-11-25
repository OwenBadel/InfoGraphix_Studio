"""Modelos de dominio para cuentos y libros-infografía interactivos."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PaletaEscena(BaseModel):
    """Paleta cromática específica de una escena (permite progresión frío -> cálido)."""

    nombre_clima: str = Field(..., min_length=1, max_length=50)
    es_oscura: bool = True
    bg: str = Field(..., pattern=r"^#[0-9a-fA-F]{6}$")
    surface: str = Field(..., pattern=r"^#[0-9a-fA-F]{6}$")
    surface_alt: str = Field(..., pattern=r"^#[0-9a-fA-F]{6}$")
    ink: str = Field(..., pattern=r"^#[0-9a-fA-F]{6}$")
    muted: str = Field(..., pattern=r"^#[0-9a-fA-F]{6}$")
    border: str = Field(..., pattern=r"^#[0-9a-fA-F]{6}$")
    accent: str = Field(..., pattern=r"^#[0-9a-fA-F]{6}$")
    accent_ink: str = Field(..., pattern=r"^#[0-9a-fA-F]{6}$")
    accent_soft: str = Field(..., pattern=r"^#[0-9a-fA-F]{6}$")

    def hex_a_rgb(self, color_hex: str) -> tuple[int, int, int]:
        limpio = color_hex.lstrip("#")
        return (int(limpio[0:2], 16), int(limpio[2:4], 16), int(limpio[4:6], 16))


class DatoSaludMental(BaseModel):
    """Ficha interactiva informativa vinculada a cada escena."""

    titulo: str = Field(..., min_length=1, max_length=90)
    cifra_destacada: str = Field(..., min_length=1, max_length=40)
    subtitulo_cifra: str = Field(..., min_length=1, max_length=160)
    explicacion: str = Field(..., min_length=1, max_length=500)
    accion_practica: str = Field(..., min_length=1, max_length=260)
    fuente: str = Field(..., min_length=1, max_length=140)


class EscenaCuento(BaseModel):
    """Una escena ilustrada e interactiva del libro-infografía."""

    numero: int = Field(..., ge=1, le=10)
    id: str = Field(..., min_length=1, max_length=40)
    etiqueta_tiempo: str = Field(..., min_length=1, max_length=50)
    titulo: str = Field(..., min_length=1, max_length=90)
    cita_destacada: str = Field(..., min_length=1, max_length=220)
    parrafos: list[str] = Field(..., min_length=1)
    imagen_archivo: str = Field(..., min_length=1)
    alt_imagen: str = Field(..., min_length=1, max_length=220)
    paleta: PaletaEscena
    dato_salud: DatoSaludMental
    nivel_carga_mental: int = Field(..., ge=0, le=100)
    nivel_calma: int = Field(..., ge=0, le=100)
    ambiente_sonoro: str = Field(default="ninguno", max_length=30)
    pestanas_mentales: list[str] = Field(default_factory=list)
    tiene_respiracion: bool = False

    def contar_palabras(self) -> int:
        return sum(len(p.split()) for p in self.parrafos)


class CuentoInfografiaSpec(BaseModel):
    """Especificación completa de un cuento/libro digital infográfico interactivo."""

    id: str = Field(..., min_length=1, max_length=60)
    titulo: str = Field(..., min_length=3, max_length=120)
    subtitulo: str = Field(..., min_length=3, max_length=260)
    etiqueta_coleccion: str = Field(default="Cuento Digital Interactivo · Salud Mental")
    autor: str = Field(default="Owen Badel Hooker", max_length=80)
    escenas: list[EscenaCuento] = Field(..., min_length=2, max_length=8)
    reflexion_final_titulo: str = Field(..., min_length=3, max_length=100)
    reflexion_final_parrafos: list[str] = Field(..., min_length=1)
    claves_autocuidado: list[str] = Field(default_factory=list, max_length=6)

    def total_palabras_relato(self) -> int:
        escenas_pal = sum(e.contar_palabras() for e in self.escenas)
        refl_pal = sum(len(p.split()) for p in self.reflexion_final_parrafos)
        return escenas_pal + refl_pal
