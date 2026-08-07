from __future__ import annotations

import argparse
import io
import os
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
LABEL = "www.tradinverso.com"
URL = "https://www.tradinverso.com/"
FOOTER_VERSION = "1"


def public_pdfs() -> list[Path]:
    folders = (ROOT / "output" / "pdf", ROOT / "recursos")
    return sorted(
        path
        for folder in folders
        if folder.exists()
        for path in folder.rglob("*.pdf")
    )


def footer_overlay(width: float, height: float) -> tuple[PdfReader, tuple[float, float, float, float]]:
    font_name = "Helvetica-Bold"
    font_size = 8
    text_width = stringWidth(LABEL, font_name, font_size)
    center_x = width / 2
    text_y = 12.5
    padding_x = 5

    stream = io.BytesIO()
    pdf = canvas.Canvas(stream, pagesize=(width, height))
    pdf.setFillColor(white)
    pdf.rect(
        center_x - text_width / 2 - padding_x,
        text_y - 2.5,
        text_width + padding_x * 2,
        font_size + 5,
        stroke=0,
        fill=1,
    )
    pdf.setFillColor(HexColor("#08295C"))
    pdf.setFont(font_name, font_size)
    pdf.drawCentredString(center_x, text_y, LABEL)
    pdf.save()
    stream.seek(0)

    rect = (
        center_x - text_width / 2 - padding_x,
        text_y - 2.5,
        center_x + text_width / 2 + padding_x,
        text_y + font_size + 2.5,
    )
    return PdfReader(stream), rect


def add_footer(path: Path) -> None:
    reader = PdfReader(str(path))
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)

    for page_number, page in enumerate(writer.pages):
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        overlay_reader, rect = footer_overlay(width, height)
        page.merge_page(overlay_reader.pages[0])
        writer.add_uri(page_number, URL, rect, border=[0, 0, 0])

    metadata = dict(reader.metadata or {})
    metadata["/TradinversoWebFooter"] = FOOTER_VERSION
    writer.add_metadata(metadata)

    temporary = path.with_name(path.stem + ".footer-tmp.pdf")
    with temporary.open("wb") as stream:
        writer.write(stream)

    verify = PdfReader(str(temporary))
    if len(verify.pages) != len(reader.pages):
        temporary.unlink(missing_ok=True)
        raise RuntimeError(f"Page count changed in {path}")

    for page_number, page in enumerate(verify.pages, start=1):
        links = []
        for reference in page.get("/Annots", []) or []:
            annotation = reference.get_object()
            action = annotation.get("/A")
            if action and action.get("/URI"):
                links.append(str(action.get("/URI")))
        if URL not in links:
            temporary.unlink(missing_ok=True)
            raise RuntimeError(f"Missing footer link in {path}, page {page_number}")

    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add the clickable TRADINVERSO website footer to public PDFs."
    )
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args()

    paths = [path.resolve() for path in args.paths] if args.paths else public_pdfs()
    for path in paths:
        add_footer(path)
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
