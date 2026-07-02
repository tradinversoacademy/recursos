from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "img" / "social"
LOGO = ROOT / "assets" / "img" / "tradinverso-logo.png"
FONT_REGULAR = Path("C:/Windows/Fonts/arial.ttf")
FONT_BOLD = Path("C:/Windows/Fonts/arialbd.ttf")

CARDS = {
    "biblioteca": ("BIBLIOTECA DE RECURSOS", "Trading, mentalidad, DATA e IA"),
    "checklist-entrada-mercado": ("CHECKLIST ANTES DE ENTRAR", "Contexto, riesgo y estado mental"),
    "orb-nasdaq": ("ORB NASDAQ", "Entrada de apertura paso a paso"),
    "amd-ifvg": ("AMD + IFVG", "Acumulación, manipulación y distribución"),
    "ifvg": ("INVERSE FVG", "La prueba del cambio de intención"),
    "data-tradinverso": ("DATA TRADINVERSO", "El centro de control del trader"),
    "metodo-c3": ("MÉTODO C3", "El sistema de trabajo de TRADINVERSO"),
    "protocolo-mental-trader": ("PROTOCOLO MENTAL", "Frena el impulso. Ejecuta tu plan."),
}


def font(path, size):
    return ImageFont.truetype(str(path), size)


def fit_title(draw, text, max_width):
    size = 72
    while size > 42:
        candidate = font(FONT_BOLD, size)
        if draw.textbbox((0, 0), text, font=candidate)[2] <= max_width:
            return candidate
        size -= 2
    return font(FONT_BOLD, size)


def build_card(slug, title, subtitle):
    image = Image.new("RGB", (1200, 630), "#f7faff")
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, 1200, 630), fill="#f7faff")
    draw.rectangle((0, 0, 34, 630), fill="#2d89ff")
    draw.rounded_rectangle((700, -110, 1320, 520), radius=150, fill="#eaf4ff")
    draw.rounded_rectangle((815, 170, 1250, 610), radius=110, fill="#dcecff")

    logo = Image.open(LOGO).convert("RGBA")
    logo.thumbnail((190, 190), Image.Resampling.LANCZOS)
    image.paste(logo, (70, 45), logo)

    draw.text((70, 250), "RECURSO GRATUITO", font=font(FONT_BOLD, 22), fill="#2d89ff")
    title_font = fit_title(draw, title, 880)
    draw.text((70, 292), title, font=title_font, fill="#06152e")
    draw.text((72, 397), subtitle, font=font(FONT_REGULAR, 29), fill="#566578")

    draw.rounded_rectangle((70, 500, 354, 558), radius=8, fill="#06245c")
    draw.text((99, 515), "TRADINVERSO.COM", font=font(FONT_BOLD, 23), fill="#ffffff")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT / f"{slug}.png", optimize=True)


def main():
    for slug, (title, subtitle) in CARDS.items():
        build_card(slug, title, subtitle)
        print(OUTPUT / f"{slug}.png")


if __name__ == "__main__":
    main()
