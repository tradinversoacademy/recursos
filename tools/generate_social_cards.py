from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "img" / "social"
LOGO = ROOT / "assets" / "img" / "tradinverso-social-logo.png"

CARDS = {
    "biblioteca": ("BIBLIOTECA DE RECURSOS", "Trading, mentalidad, DATA e IA"),
    "checklist-entrada-mercado": ("CHECKLIST ANTES DE ENTRAR", "Contexto, riesgo y estado mental"),
    "orb-nasdaq": ("ORB NASDAQ", "Entrada de apertura paso a paso"),
    "amd-ifvg": ("AMD + IFVG", "Acumulación, manipulación y distribución"),
    "apertura-0000-nueva-york": ("APERTURA 00:00 NY", "Abre, manipula y expande"),
    "plan-trader-rentable": ("EL PLAN CONTRARIO", "10 errores que frenan tu rentabilidad"),
    "guia-5-conceptos-trading": ("5 CONCEPTOS ESENCIALES", "La base para leer el precio"),
    "ifvg": ("INVERSE FVG", "La prueba del cambio de intención"),
    "data-tradinverso": ("DATA TRADINVERSO", "El centro de control del trader"),
    "metodo-c3": ("MÉTODO C3", "El sistema de trabajo de TRADINVERSO"),
    "programa-tradinverso": ("PROGRAMA TRADINVERSO", "Todo lo que incluye nuestro programa"),
    "test-objetividad-sistema": ("TEST DE OBJETIVIDAD", "Comprueba si tu sistema tiene reglas claras"),
    "claridad-trader": ("CLARIDAD PARA TU TRADING", "Descubre qué está frenando tus resultados"),
    "protocolo-mental-trader": ("PROTOCOLO MENTAL", "Frena el impulso. Ejecuta tu plan."),
    "rango-asiatico": ("RANGO ASIÁTICO", "Estructura, manipulación y ejecución"),
    "manipulacion-maximos-minimos": ("MÁXIMOS Y MÍNIMOS", "Toma de liquidez y confirmación"),
    "modelo-liquidez-estructura-fvg": ("LIQUIDEZ + ESTRUCTURA + FVG", "El modelo de compra en tres pasos"),
}


def build_card(slug, title, subtitle):
    image = Image.new("RGB", (1200, 630), "#ffffff")

    logo = Image.open(LOGO).convert("RGB")
    white = Image.new("RGB", logo.size, "#ffffff")
    content_box = ImageChops.difference(logo, white).getbbox()
    if content_box:
        logo = logo.crop(content_box)
    logo.thumbnail((580, 520), Image.Resampling.LANCZOS)
    x = (image.width - logo.width) // 2
    y = (image.height - logo.height) // 2
    image.paste(logo, (x, y))

    OUTPUT.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT / f"{slug}.png", optimize=True)


def main():
    for slug, (title, subtitle) in CARDS.items():
        build_card(slug, title, subtitle)
        print(OUTPUT / f"{slug}.png")


if __name__ == "__main__":
    main()
