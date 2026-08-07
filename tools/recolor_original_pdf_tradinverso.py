from pathlib import Path
import re
import sys
import tempfile

import numpy as np
from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError
from pypdf.generic import DecodedStreamObject, NameObject
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


BRAND_BLUE = (47, 134, 246)
SOURCE_RED = (179, 0, 0)


def recolor_stream(stream):
    data = stream.get_data()
    pattern = rb"(?<![\d.])0\.702\s+0\s+0\s+(rg|RG)"
    data = re.sub(pattern, rb"0.184 0.525 0.965 \1", data)
    try:
        stream.set_data(data)
    except PdfReadError:
        return stream
    return stream


def recolor_resources(resources, seen):
    if not resources:
        return
    resources = resources.get_object()
    for group_name in ("/XObject", "/Pattern"):
        group = resources.get(group_name)
        if not group:
            continue
        group = group.get_object()
        for name, reference in list(group.items()):
            obj = reference.get_object()
            marker = id(obj)
            if marker in seen:
                continue
            seen.add(marker)
            subtype = obj.get("/Subtype")
            is_content_stream = group_name == "/Pattern" or subtype == "/Form"
            if is_content_stream and hasattr(obj, "get_data"):
                obj = recolor_stream(obj)
                group[name] = obj
            if is_content_stream:
                recolor_resources(obj.get("/Resources"), seen)


def replace_vector_red(page):
    contents = page.get_contents()
    if contents:
        data = contents.get_data()
        pattern = rb"(?<![\d.])0\.702\s+0\s+0\s+(rg|RG)"
        data = re.sub(pattern, rb"0.184 0.525 0.965 \1", data)
        stream = DecodedStreamObject()
        stream.set_data(data)
        page[NameObject("/Contents")] = stream
    recolor_resources(page.get("/Resources"), set())
    return page


def recolor_editorial_red(source_path, output_path):
    image = Image.open(source_path).convert("RGB")
    arr = np.asarray(image).copy()
    red = arr[:, :, 0].astype(np.int16)
    green = arr[:, :, 1].astype(np.int16)
    blue = arr[:, :, 2].astype(np.int16)

    # The source theme uses a dark red. This mask includes antialiased edges
    # while avoiding normal green/black candlesticks and neutral page elements.
    mask = (
        (red > 85)
        & (red > green * 1.55)
        & (red > blue * 1.55)
        & ((red - np.maximum(green, blue)) > 45)
    )
    strength = np.clip(red / SOURCE_RED[0], 0.35, 1.45)
    for channel, target in enumerate(BRAND_BLUE):
        arr[:, :, channel][mask] = np.clip(target * strength[mask], 0, 255)

    Image.fromarray(arr.astype(np.uint8), "RGB").save(output_path, quality=96)


def image_page_pdf(image_path, page_size, output_path):
    width, height = page_size
    c = canvas.Canvas(str(output_path), pagesize=(width, height), pageCompression=1)
    c.drawImage(
        ImageReader(str(image_path)),
        0,
        0,
        width=width,
        height=height,
        preserveAspectRatio=False,
        mask="auto",
    )
    c.showPage()
    c.save()


def build(source_pdf, rendered_page_three, output_pdf):
    source_pdf = Path(source_pdf)
    rendered_page_three = Path(rendered_page_three)
    output_pdf = Path(output_pdf)
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(str(source_pdf))
    writer = PdfWriter()

    with tempfile.TemporaryDirectory() as temp:
        temp = Path(temp)
        recolored_png = temp / "page-03-blue.png"
        recolored_pdf = temp / "page-03-blue.pdf"
        recolor_editorial_red(rendered_page_three, recolored_png)

        page_three = reader.pages[2]
        image_page_pdf(
            recolored_png,
            (float(page_three.mediabox.width), float(page_three.mediabox.height)),
            recolored_pdf,
        )
        raster_page = PdfReader(str(recolored_pdf)).pages[0]

        processed_pages = []
        for index, page in enumerate(reader.pages):
            processed_pages.append(
                raster_page if index == 2 else replace_vector_red(page)
            )
        for page in processed_pages:
            writer.add_page(page)

        if reader.metadata:
            metadata = {
                key: value
                for key, value in reader.metadata.items()
                if isinstance(key, str) and isinstance(value, str)
            }
            writer.add_metadata(metadata)

        writer.add_metadata(
            {
                "/Title": "Análisis completo de la estrategia - Colores TRADINVERSO",
                "/Producer": "TRADINVERSO",
            }
        )
        with output_pdf.open("wb") as handle:
            writer.write(handle)

    print(output_pdf)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit(
            "Uso: recolor_original_pdf_tradinverso.py original.pdf pagina-03.png salida.pdf"
        )
    build(sys.argv[1], sys.argv[2], sys.argv[3])
