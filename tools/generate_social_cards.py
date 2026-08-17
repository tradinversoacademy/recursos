"""Genera las social cards (Open Graph, 1200x630) de todos los recursos.

Diseño de marca: fondo navy oscuro, acento azul, logo en caja blanca,
título y subtítulo del recurso. Estas cards son lo que se ve al compartir
un enlace por DM, WhatsApp o redes.
"""

from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "img" / "social"
LOGO = ROOT / "assets" / "img" / "tradinverso-social-logo.png"

W, H = 1200, 630
DARK = (3, 23, 59)
NAVY = (6, 36, 92)
BLUE = (45, 137, 255)
SKY = (93, 178, 255)
ICE = (207, 228, 255)

FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REGULAR = "C:/Windows/Fonts/segoeui.ttf"

CARDS = {
    "biblioteca": ("Biblioteca de recursos", "Trading, mentalidad, DATA e IA"),
    "checklist-entrada-mercado": ("Checklist antes de entrar", "Contexto, riesgo y estado mental"),
    "orb-nasdaq": ("ORB Nasdaq", "Entrada de apertura paso a paso"),
    "amd-ifvg": ("AMD + IFVG", "Acumulación, manipulación y distribución"),
    "apertura-0000-nueva-york": ("Apertura 00:00 NY", "Abre, manipula y expande"),
    "plan-trader-rentable": ("El plan contrario", "10 errores que frenan tu rentabilidad"),
    "guia-5-conceptos-trading": ("5 conceptos esenciales", "La base para leer el precio"),
    "ifvg": ("Inverse FVG", "La prueba del cambio de intención"),
    "data-tradinverso": ("DATA TRADINVERSO", "El centro de control del trader"),
    "metodo-c3": ("Método C3", "El sistema de trabajo de TRADINVERSO"),
    "programa-tradinverso": ("Programa TRADINVERSO", "Todo lo que incluye nuestro programa"),
    "test-objetividad-sistema": ("Test de objetividad", "¿Tu sistema tiene reglas claras?"),
    "claridad-trader": ("Claridad para tu trading", "Descubre qué frena tus resultados"),
    "protocolo-mental-trader": ("Protocolo mental", "Frena el impulso. Ejecuta tu plan."),
    "rango-asiatico": ("Rango asiático", "Estructura, manipulación y ejecución"),
    "manipulacion-maximos-minimos": ("Máximos y mínimos", "Toma de liquidez y confirmación"),
    "modelo-liquidez-estructura-fvg": ("Liquidez + Estructura + FVG", "El modelo de compra en tres pasos"),
    "amd": ("AMD", "Acumulación, manipulación y distribución"),
    "backtesting-orb": ("Backtesting del ORB", "Vídeo y plantilla para medir tus datos"),
    "mechas-velas": ("Cómo leer las mechas", "Quién tiene el control del mercado"),
}


def load_logo():
    logo = Image.open(LOGO).convert("RGB")
    white = Image.new("RGB", logo.size, "#ffffff")
    box = ImageChops.difference(logo, white).getbbox()
    if box:
        logo = logo.crop(box)
    return logo


def fit_title(draw, text, max_width, start=88, minimum=54):
    size = start
    while size > minimum:
        font = ImageFont.truetype(FONT_BOLD, size)
        lines = wrap_text(draw, text, font, max_width)
        if len(lines) <= 2:
            return font, lines
        size -= 4
    font = ImageFont.truetype(FONT_BOLD, minimum)
    return font, wrap_text(draw, text, font, max_width)[:2]


def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def build_card(slug, title, subtitle):
    image = Image.new("RGB", (W, H), DARK)

    # Resplandor azul suave en la esquina inferior derecha
    glow = Image.new("RGB", (W, H), DARK)
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((W - 480, H - 380, W + 260, H + 320), fill=NAVY)
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    image = ImageChops.lighter(image, glow)

    draw = ImageDraw.Draw(image)

    # Barra de acento superior
    draw.rectangle((0, 0, W, 16), fill=BLUE)

    # Logo en caja blanca redondeada
    logo = load_logo()
    logo.thumbnail((150, 96), Image.Resampling.LANCZOS)
    box_w, box_h = logo.width + 44, logo.height + 36
    draw.rounded_rectangle((72, 64, 72 + box_w, 64 + box_h), radius=14, fill=(255, 255, 255))
    image.paste(logo, (72 + 22, 64 + 18))

    # Kicker
    kicker_font = ImageFont.truetype(FONT_BOLD, 27)
    draw.text((76, 250), "RECURSO GRATUITO · TRADINVERSO", font=kicker_font, fill=SKY)

    # Título (máximo dos líneas)
    title_font, title_lines = fit_title(draw, title, W - 152)
    y = 300
    for line in title_lines:
        draw.text((72, y), line, font=title_font, fill=(255, 255, 255))
        y += int(title_font.size * 1.16)

    # Subtítulo
    subtitle_font = ImageFont.truetype(FONT_REGULAR, 36)
    for line in wrap_text(draw, subtitle, subtitle_font, W - 152)[:2]:
        draw.text((74, y + 10), line, font=subtitle_font, fill=ICE)
        y += 48

    # Pie
    footer_font = ImageFont.truetype(FONT_REGULAR, 26)
    draw.text((76, H - 74), "davidrosell.fx", font=footer_font, fill=(140, 165, 205))
    chip_font = ImageFont.truetype(FONT_BOLD, 26)
    chip_text = "Biblioteca de recursos →"
    chip_w = draw.textlength(chip_text, font=chip_font)
    draw.rounded_rectangle((W - chip_w - 132, H - 92, W - 72, H - 44), radius=24, fill=BLUE)
    draw.text((W - chip_w - 102, H - 84), chip_text, font=chip_font, fill=(255, 255, 255))

    OUTPUT.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT / f"{slug}.png", optimize=True)


def main():
    for slug, (title, subtitle) in CARDS.items():
        build_card(slug, title, subtitle)
        print(OUTPUT / f"{slug}.png")


if __name__ == "__main__":
    main()
