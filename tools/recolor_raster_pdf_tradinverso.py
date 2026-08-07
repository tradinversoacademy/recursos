from pathlib import Path
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


BRAND_BLUE = (47, 134, 246)
ROOT = Path(__file__).resolve().parents[1]
TRADINVERSO_LOGO = ROOT / "assets" / "img" / "tradinverso-logo.png"


def transparent_symbol():
    logo = Image.open(TRADINVERSO_LOGO).convert("RGBA")
    symbol = logo.crop((75, 20, 965, 690))
    data = np.asarray(symbol).copy()
    white_pixels = (
        (data[:, :, 0] > 242)
        & (data[:, :, 1] > 242)
        & (data[:, :, 2] > 242)
    )
    data[:, :, 3][white_pixels] = 0
    return Image.fromarray(data)


def replace_brand_marks(image, page_number):
    width, height = image.size
    draw = ImageDraw.Draw(image)
    logo = Image.open(TRADINVERSO_LOGO).convert("RGB")

    if page_number == 1:
        card_size = int(width * 0.30)
        left = (width - card_size) // 2
        top = int(height * 0.025)
        draw.rounded_rectangle(
            (left, top, left + card_size, top + card_size),
            radius=int(card_size * 0.055),
            fill=(250, 252, 255),
            outline=(202, 221, 244),
            width=max(2, int(width * 0.0014)),
        )
        inset = int(card_size * 0.045)
        logo = logo.resize(
            (card_size - inset * 2, card_size - inset * 2),
            Image.Resampling.LANCZOS,
        )
        image.paste(logo, (left + inset, top + inset))
        return image

    arr = np.asarray(image)
    y_limit = int(height * 0.16)
    blue = (
        (arr[:y_limit, :, 2] > 170)
        & (arr[:y_limit, :, 0] < 105)
        & (arr[:y_limit, :, 1] > 75)
        & (arr[:y_limit, :, 1] < 205)
    )
    ys, xs = np.where(blue)
    if len(xs) < 20:
        return image

    header_top = int(ys.min())
    header_only = ys < header_top + int(height * 0.06)
    ys = ys[header_only]
    xs = xs[header_only]
    min_x, max_x = int(xs.min()), int(xs.max())
    min_y, max_y = int(ys.min()), int(ys.max())
    pill_height = max_y - min_y
    center_y = (min_y + max_y) // 2
    center_x = int(min_x + pill_height * 0.86)
    icon_size = max(42, int(pill_height * 0.47))
    cover_size = int(pill_height * 0.65)
    sample_x = min(width - 1, int(min_x + pill_height * 0.34))
    fill = tuple(int(v) for v in arr[center_y, sample_x])
    draw.rounded_rectangle(
        (
            center_x - cover_size // 2,
            center_y - cover_size // 2,
            center_x + cover_size // 2,
            center_y + cover_size // 2,
        ),
        radius=int(cover_size * 0.22),
        fill=fill,
    )
    symbol = transparent_symbol()
    symbol.thumbnail((icon_size, icon_size), Image.Resampling.LANCZOS)
    image.paste(
        symbol,
        (center_x - symbol.width // 2, center_y - symbol.height // 2),
        symbol,
    )
    return image


def replace_handle(image, page_number):
    if page_number not in (1, 14):
        return image

    width, height = image.size
    if page_number == 1:
        text_y = int(height * 0.949)
    else:
        text_y = int(height * 0.818)

    font_path = Path(r"C:\Windows\Fonts\arial.ttf")
    font_size = int(height * (0.018 if page_number == 1 else 0.0165))
    font = ImageFont.truetype(str(font_path), font_size)
    draw = ImageDraw.Draw(image)
    text = "@davidrosell.fx"
    bounds = draw.textbbox((0, 0), text, font=font)
    text_width = bounds[2] - bounds[0]
    text_height = bounds[3] - bounds[1]
    pill_width = text_width + int(width * 0.07)
    pill_height = text_height + int(height * 0.018)
    draw.rounded_rectangle(
        (
            (width - pill_width) / 2,
            text_y - pill_height / 2,
            (width + pill_width) / 2,
            text_y + pill_height / 2,
        ),
        radius=int(pill_height * 0.42),
        fill=(248, 250, 253),
        outline=(202, 221, 244),
        width=max(2, int(width * 0.0012)),
    )
    draw.text(
        ((width - text_width) / 2, text_y - text_height / 2 - bounds[1]),
        text,
        font=font,
        fill=(132, 137, 145),
    )
    return image


def recolor_page(source, destination, page_number):
    image = Image.open(source).convert("RGB")
    arr = np.asarray(image).copy()
    red = arr[:, :, 0].astype(np.int16)
    green = arr[:, :, 1].astype(np.int16)
    blue = arr[:, :, 2].astype(np.int16)

    mask = (
        (red > 80)
        & (red > green * 1.38)
        & (red > blue * 1.38)
        & ((red - np.maximum(green, blue)) > 35)
    )

    intensity = np.clip(red / 179.0, 0.28, 1.42)
    for channel, target in enumerate(BRAND_BLUE):
        arr[:, :, channel][mask] = np.clip(target * intensity[mask], 0, 255)

    result = Image.fromarray(arr.astype(np.uint8), "RGB")
    result = replace_brand_marks(result, page_number)
    result = replace_handle(result, page_number)
    result.save(
        destination, "JPEG", quality=95, subsampling=0, optimize=False
    )


def build(source_pdf, rendered_directory, output_pdf):
    source_pdf = Path(source_pdf)
    rendered_directory = Path(rendered_directory)
    output_pdf = Path(output_pdf)
    pages = sorted(rendered_directory.glob("page-*.png"))
    if not pages:
        raise RuntimeError("No se encontraron páginas renderizadas.")

    original = PdfReader(str(source_pdf))
    page_width = float(original.pages[0].mediabox.width)
    page_height = float(original.pages[0].mediabox.height)
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        recolored = []
        for number, page in enumerate(pages, 1):
            target = temp_dir / f"page-{number:02d}.jpg"
            recolor_page(page, target, number)
            recolored.append(target)

        pdf = canvas.Canvas(
            str(output_pdf),
            pagesize=(page_width, page_height),
            pageCompression=1,
        )
        pdf.setTitle("Análisis completo de la estrategia - TRADINVERSO")
        pdf.setAuthor("TRADINVERSO")
        for page in recolored:
            pdf.drawImage(
                ImageReader(str(page)),
                0,
                0,
                width=page_width,
                height=page_height,
                preserveAspectRatio=False,
            )
            pdf.showPage()
        pdf.save()

    print(output_pdf)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit(
            "Uso: recolor_raster_pdf_tradinverso.py original.pdf carpeta_paginas salida.pdf"
        )
    build(sys.argv[1], sys.argv[2], sys.argv[3])
