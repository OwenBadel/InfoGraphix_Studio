"""Prepara las 5 láminas ilustradas (1600x900) para 'La mujer de las mil pestañas abiertas'."""

from __future__ import annotations

import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


W, H = 1600, 900
BRAIN_DIR = Path(r"C:\Users\USUARIO\.gemini\antigravity\brain\72f4e48d-0f46-4347-ac8a-7df790dfc428")
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "cuento_elena"


def _agregar_textura_papel(img: Image.Image, intensidad: float = 11.0, seed: int = 42) -> Image.Image:
    """Añade grano sutil de papel acuarela prensado en frío para cohesión gouache."""
    rng = np.random.default_rng(seed)
    arr = np.asarray(img, dtype=np.float32)
    ruido_fino = rng.normal(0.0, intensidad, (H, W, 1))
    # Textura orgánica suave a escala media (manchas acuarela)
    baja = rng.normal(0.0, intensidad * 0.65, (H // 16, W // 16, 1))
    baja_img = Image.fromarray(np.clip(baja[:, :, 0] + 128, 0, 255).astype(np.uint8)).resize(
        (W, H), Image.Resampling.BICUBIC
    )
    ruido_agua = (np.asarray(baja_img, dtype=np.float32)[:, :, None] - 128.0) * 0.45
    combinado = np.clip(arr + ruido_fino + ruido_agua, 0, 255).astype(np.uint8)
    return Image.fromarray(combinado, mode="RGB")


def _gradiente_vertical(colores: list[tuple[float, tuple[int, int, int]]]) -> Image.Image:
    """Genera un fondo con gradiente vertical suave multi-parada."""
    y = np.linspace(0.0, 1.0, H)[:, None]
    arr = np.zeros((H, W, 3), dtype=np.float32)
    for idx in range(len(colores) - 1):
        p0, c0 = colores[idx]
        p1, c1 = colores[idx + 1]
        mask = (y >= p0) & (y <= p1)
        t = np.clip((y - p0) / max(p1 - p0, 1e-6), 0.0, 1.0)
        for ch in range(3):
            vals = c0[ch] * (1.0 - t) + c1[ch] * t
            arr[:, :, ch] = np.where(mask, vals, arr[:, :, ch])
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), mode="RGB")


def _trazar_tinta(draw: ImageDraw.ImageDraw, pts, color=(26, 34, 46), width=3):
    draw.line(pts, fill=color, width=width, joint="curve")


def generar_escena_1_madrugada(destino: Path) -> None:
    """Escena 1 (5:30 a.m.): Ventana azul madrugada, tejados del barrio, café, laptop y pestañas en el aire."""
    base = _gradiente_vertical(
        [
            (0.0, (17, 26, 40)),
            (0.45, (30, 44, 64)),
            (0.75, (42, 58, 78)),
            (1.0, (24, 33, 46)),
        ]
    ).convert("RGBA")

    # Resplandor frío de pantalla y cielo pre-amanecer en ventana
    luz = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(luz)
    # Luz azul pálida de la ventana
    dl.rectangle([760, 70, 1460, 560], fill=(74, 102, 134, 155))
    dl.ellipse([820, 240, 1420, 620], fill=(118, 148, 178, 85))
    # Brillo frío de la laptop sobre la mesa
    dl.ellipse([120, 320, 760, 760], fill=(147, 197, 253, 85))
    luz = luz.filter(ImageFilter.GaussianBlur(36))
    base = Image.alpha_composite(base, luz)

    draw = ImageDraw.Draw(base)
    tinta = (18, 25, 36, 235)

    # Ventana con vista a tejados de barrio latinoamericano antes del sol
    vx0, vy0, vx1, vy1 = 760, 65, 1475, 555
    draw.rectangle([vx0, vy0, vx1, vy1], fill=(46, 66, 90, 255), outline=tinta, width=5)

    # Estrellas tenues y nube fría
    for sx, sy, sr in [(840, 125, 2), (960, 105, 2), (1120, 140, 2), (1320, 118, 2), (1390, 175, 2)]:
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(215, 230, 245, 190))

    # Luna creciente fina
    draw.ellipse([1320, 108, 1366, 154], fill=(224, 236, 248, 210))
    draw.ellipse([1334, 102, 1378, 148], fill=(46, 66, 90, 255))

    # Colinas suaves y tejados en silueta azul pizarra
    draw.polygon([(vx0, 415), (920, 365), (1140, 390), (1330, 350), (vx1, 385), (vx1, vy1), (vx0, vy1)], fill=(34, 49, 68, 255))
    tejados = [
        [(770, 555), (770, 445), (845, 395), (925, 445), (925, 555)],
        [(905, 555), (905, 430), (1010, 382), (1105, 430), (1105, 555)],
        [(1085, 555), (1085, 455), (1180, 412), (1265, 455), (1265, 555)],
        [(1245, 555), (1245, 420), (1355, 372), (1465, 420), (1465, 555)],
    ]
    for poly in tejados:
        draw.polygon(poly, fill=(24, 34, 48, 255), outline=tinta)
    # Ventanitas cálidas diminutas en dos casas madrugadoras
    for wx, wy in [(825, 472), (850, 472), (1000, 462), (1340, 458)]:
        draw.rectangle([wx, wy, wx + 16, wy + 22], fill=(214, 179, 120, 175))

    # Marco y divisiones de la ventana
    draw.rectangle([vx0, vy0, vx1, vy1], outline=(28, 38, 52, 255), width=16)
    draw.line([(1117, vy0), (1117, vy1)], fill=(28, 38, 52, 255), width=12)
    draw.line([(vx0, 315), (vx1, 315)], fill=(28, 38, 52, 255), width=10)
    # Cortinas suaves a los lados
    draw.polygon([(705, 45), (805, 45), (790, 575), (705, 585)], fill=(38, 50, 66, 230), outline=tinta)
    draw.polygon([(1430, 45), (1535, 45), (1535, 585), (1448, 575)], fill=(38, 50, 66, 230), outline=tinta)

    # Escritorio de madera en penumbra fría
    draw.polygon([(0, 610), (1600, 585), (1600, 900), (0, 900)], fill=(44, 48, 58, 255), outline=tinta)
    draw.line([(0, 610), (1600, 585)], fill=tinta, width=4)
    # Vetas suaves de madera
    for gy in (650, 710, 780, 845):
        draw.line([(0, gy), (1600, gy - 14)], fill=(34, 39, 48, 130), width=2)

    # Pila de cuadernos y hojas a la derecha
    cuadernos = [
        (1060, 650, 1385, 725, (64, 78, 96, 255)),
        (1078, 612, 1368, 662, (86, 102, 122, 255)),
        (1092, 578, 1352, 622, (118, 134, 152, 255)),
    ]
    for x0, y0, x1, y1, col in cuadernos:
        draw.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=col, outline=tinta, width=3)
        draw.line([(x0 + 18, y1 - 8), (x1 - 14, y1 - 8)], fill=(208, 220, 232, 180), width=3)

    # Laptop abierta a la izquierda con pantalla luminosa fría
    draw.polygon([(165, 365), (520, 340), (585, 650), (235, 688)], fill=(35, 46, 62, 255), outline=tinta, width=4)
    draw.polygon([(186, 382), (506, 360), (562, 636), (248, 670)], fill=(206, 224, 242, 255), outline=tinta, width=2)
    # Base y teclado
    draw.polygon([(235, 688), (585, 650), (815, 712), (430, 768)], fill=(72, 84, 100, 255), outline=tinta, width=4)
    draw.polygon([(295, 690), (575, 662), (720, 704), (445, 738)], fill=(45, 56, 70, 255), outline=tinta, width=2)

    # Taza de café humeante en el centro-derecha
    tx, ty = 855, 632
    draw.ellipse([tx + 92, ty + 24, tx + 144, ty + 88], outline=tinta, width=10)
    draw.ellipse([tx + 96, ty + 28, tx + 140, ty + 84], outline=(168, 182, 198, 255), width=5)
    draw.rounded_rectangle([tx, ty, tx + 112, ty + 116], radius=18, fill=(168, 182, 198, 255), outline=tinta, width=4)
    draw.ellipse([tx + 4, ty - 12, tx + 108, ty + 18], fill=(82, 58, 44, 255), outline=tinta, width=3)

    # Vapor delicado y pestañas translúcidas flotando (metáfora visual sin texto)
    capa_pestanas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dp = ImageDraw.Draw(capa_pestanas)
    for ox in (888, 912, 934):
        pts = [(ox + math.sin(k * 0.45) * 18, 610 - k * 24) for k in range(14)]
        dp.line(pts, fill=(210, 226, 242, 95), width=5, joint="curve")

    pestanas_coords = [
        (140, 120, 355, 225, 115),
        (300, 175, 535, 285, 130),
        (485, 95, 715, 200, 110),
        (560, 235, 780, 335, 95),
        (210, 255, 420, 345, 85),
        (650, 140, 865, 235, 85),
    ]
    for x0, y0, x1, y1, alfa in pestanas_coords:
        dp.rounded_rectangle([x0, y0, x1, y1], radius=12, fill=(190, 214, 240, alfa // 2), outline=(210, 230, 250, alfa + 45), width=2)
        dp.rectangle([x0 + 1, y0 + 1, x1 - 1, y0 + 24], fill=(147, 197, 253, alfa // 2 + 20))
        # Tres puntitos abstractos de pestaña y líneas de contenido sin letras
        for d in range(3):
            dp.ellipse([x0 + 12 + d * 12, y0 + 9, x0 + 18 + d * 12, y0 + 15], fill=(235, 244, 255, alfa + 60))
        dp.line([(x0 + 18, y0 + 46), (x1 - 36, y0 + 46)], fill=(230, 240, 252, alfa + 35), width=4)
        dp.line([(x0 + 18, y0 + 66), (x1 - 68, y0 + 66)], fill=(210, 226, 242, alfa + 10), width=3)

    base = Image.alpha_composite(base, capa_pestanas).convert("RGB")
    base = _agregar_textura_papel(base, intensidad=9.5, seed=101)
    base.save(destino, format="PNG")


def generar_escena_5_calma(destino: Path) -> None:
    """Escena 5 (Sol cálido y salvia): Escritorio limpio, ventana soleada, plantas, café y un solo cuaderno."""
    base = _gradiente_vertical(
        [
            (0.0, (251, 242, 226)),
            (0.45, (246, 229, 203)),
            (0.75, (237, 212, 178)),
            (1.0, (212, 173, 130)),
        ]
    ).convert("RGBA")

    # Rayos cálidos de sol entrando diagonalmente por la ventana
    sol = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sol)
    ds.polygon([(140, 60), (880, 60), (1460, 880), (460, 880)], fill=(255, 223, 160, 95))
    ds.ellipse([180, 50, 740, 520], fill=(255, 236, 186, 120))
    sol = sol.filter(ImageFilter.GaussianBlur(42))
    base = Image.alpha_composite(base, sol)

    draw = ImageDraw.Draw(base)
    tinta = (74, 52, 38, 225)

    # Ventana amplia izquierda abierta a mañana luminosa y vegetación
    vx0, vy0, vx1, vy1 = 110, 55, 865, 560
    draw.rectangle([vx0, vy0, vx1, vy1], fill=(254, 245, 223, 255), outline=tinta, width=5)
    # Sol suave en la ventana y colinas verdes/doradas lejanas
    draw.ellipse([230, 125, 360, 255], fill=(252, 211, 128, 215))
    draw.polygon([(vx0, 445), (310, 388), (540, 415), (735, 368), (vx1, 405), (vx1, vy1), (vx0, vy1)], fill=(154, 179, 146, 220))
    draw.polygon([(vx0, 495), (380, 445), (650, 470), (vx1, 435), (vx1, vy1), (vx0, vy1)], fill=(108, 140, 108, 235))
    # Marco madera cálida de la ventana
    draw.rectangle([vx0, vy0, vx1, vy1], outline=(138, 96, 66, 255), width=16)
    draw.line([(488, vy0), (488, vy1)], fill=(138, 96, 66, 255), width=12)
    draw.line([(vx0, 315), (vx1, 315)], fill=(138, 96, 66, 255), width=10)
    # Cortinas ligeras color lino
    draw.polygon([(65, 40), (165, 40), (145, 585), (65, 595)], fill=(248, 236, 216, 225), outline=tinta)
    draw.polygon([(825, 40), (925, 40), (925, 595), (845, 585)], fill=(248, 236, 216, 225), outline=tinta)

    # Repisa derecha con planta botánica colgante y cuadro minimalista cálido
    draw.rounded_rectangle([1070, 115, 1425, 345], radius=8, fill=(246, 234, 214, 255), outline=(146, 102, 70, 255), width=10)
    draw.ellipse([1165, 160, 1280, 275], fill=(218, 134, 84, 195))
    draw.arc([1120, 215, 1365, 330], 180, 360, fill=(92, 124, 98, 230), width=12)

    # Escritorio de madera miel despejado
    draw.polygon([(0, 590), (1600, 608), (1600, 900), (0, 900)], fill=(210, 166, 122, 255), outline=tinta)
    draw.line([(0, 590), (1600, 608)], fill=tinta, width=4)
    for gy in (645, 710, 785, 850):
        draw.line([(0, gy), (1600, gy + 12)], fill=(186, 140, 98, 140), width=2)

    # Maceta de terracota con planta salvia en el borde izquierdo de la mesa
    draw.polygon([(145, 555), (275, 555), (255, 695), (165, 695)], fill=(192, 104, 62, 255), outline=tinta, width=4)
    draw.rounded_rectangle([136, 535, 284, 565], radius=6, fill=(204, 116, 72, 255), outline=tinta, width=4)
    hojas = [
        (210, 535, 140, 425, 185, 455),
        (210, 535, 215, 385, 245, 445),
        (210, 535, 295, 420, 265, 475),
        (210, 535, 118, 495, 165, 515),
        (210, 535, 315, 490, 272, 518),
    ]
    for x0, y0, tx, ty, cx, cy in hojas:
        draw.line([(x0, y0), (tx, ty)], fill=(76, 108, 82, 255), width=5)
        draw.ellipse([tx - 34, ty - 22, tx + 34, ty + 22], fill=(98, 134, 104, 240), outline=tinta, width=3)

    # Un solo cuaderno abierto en el centro con páginas crema limpias (sin caos)
    # Tapa exterior
    draw.polygon([(470, 645), (1055, 650), (1120, 825), (415, 820)], fill=(124, 90, 64, 255), outline=tinta, width=4)
    # Página izquierda y derecha
    draw.polygon([(488, 652), (762, 656), (762, 808), (438, 804)], fill=(252, 246, 234, 255), outline=tinta, width=3)
    draw.polygon([(762, 656), (1038, 656), (1092, 808), (762, 808)], fill=(248, 240, 224, 255), outline=tinta, width=3)
    # Renglones suaves manuscritos (líneas orgánicas sin texto legible)
    for k in range(5):
        ly = 682 + k * 24
        draw.line([(505 - k * 6, ly), (728, ly)], fill=(168, 146, 124, 175), width=2)
        draw.line([(795, ly), (1005 + k * 5, ly)], fill=(168, 146, 124, 155), width=2)
    # Bolígrafo descansando tranquilo sobre el cuaderno
    draw.line([(920, 672), (1075, 792)], fill=(168, 74, 42, 255), width=10)
    draw.line([(920, 672), (1075, 792)], fill=tinta, width=2)

    # Taza artesanal de cerámica crema/terracota con vapor sereno a la derecha
    cx, cy = 1235, 625
    draw.ellipse([cx + 96, cy + 26, cx + 148, cy + 92], outline=tinta, width=10)
    draw.ellipse([cx + 100, cy + 30, cx + 144, cy + 88], outline=(235, 212, 186, 255), width=5)
    draw.rounded_rectangle([cx, cy, cx + 118, cy + 122], radius=22, fill=(238, 219, 196, 255), outline=tinta, width=4)
    draw.rectangle([cx + 3, cy + 72, cx + 115, cy + 118], fill=(194, 108, 66, 220))
    draw.ellipse([cx + 5, cy - 12, cx + 113, cy + 18], fill=(116, 74, 48, 255), outline=tinta, width=3)

    vapor = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dv = ImageDraw.Draw(vapor)
    for ox in (1276, 1304):
        pts = [(ox + math.sin(k * 0.4) * 14, 602 - k * 20) for k in range(11)]
        dv.line(pts, fill=(255, 248, 235, 135), width=6, joint="curve")
    vapor = vapor.filter(ImageFilter.GaussianBlur(2))
    base = Image.alpha_composite(base, vapor).convert("RGB")

    base = _agregar_textura_papel(base, intensidad=8.5, seed=505)
    base.save(destino, format="PNG")


def copiar_y_normalizar(origen: Path, destino: Path, recorte_pct: float = 0.0) -> None:
    """Copia una ilustración generada, recorta margen si aplica y la ajusta a 1600x900."""
    with Image.open(origen) as im:
        rgb = im.convert("RGB")
        if recorte_pct > 0:
            mx = int(rgb.width * recorte_pct)
            my = int(rgb.height * recorte_pct)
            rgb = rgb.crop((mx, my, rgb.width - mx, rgb.height - my))
        rgb = rgb.resize((W, H), Image.Resampling.LANCZOS)
        rgb.save(destino, format="PNG")


def preparar_todas() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    generar_escena_1_madrugada(ASSETS_DIR / "escena_1_madrugada.png")
    copiar_y_normalizar(
        BRAIN_DIR / "escena_2_armadura_1795567844253.jpg",
        ASSETS_DIR / "escena_2_armadura.png",
        recorte_pct=0.065,
    )
    copiar_y_normalizar(
        BRAIN_DIR / "escena_3_lluvia_1795567845040.jpg",
        ASSETS_DIR / "escena_3_lluvia.png",
    )
    copiar_y_normalizar(
        BRAIN_DIR / "escena_4_espejo_1795567846924.jpg",
        ASSETS_DIR / "escena_4_espejo.png",
    )
    generar_escena_5_calma(ASSETS_DIR / "escena_5_calma.png")
    print(f"[OK] 5 ilustraciones listas en {ASSETS_DIR}")


if __name__ == "__main__":
    preparar_todas()
