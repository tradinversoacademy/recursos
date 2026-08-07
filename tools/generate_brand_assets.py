from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "img"
SOURCE = ASSETS / "tradinverso-brand-card.png"
HEADER_LOGO = ASSETS / "tradinverso-logo.png"
ICON = ASSETS / "tradinverso-icon.png"


def crop_relative(image: Image.Image, box: tuple[float, float, float, float]) -> Image.Image:
    width, height = image.size
    return image.crop(
        (
            round(width * box[0]),
            round(height * box[1]),
            round(width * box[2]),
            round(height * box[3]),
        )
    )


def build_header_logo(source: Image.Image) -> None:
    logo = crop_relative(source, (0.045, 0.075, 0.955, 0.695))
    logo.thumbnail((1200, 760), Image.Resampling.LANCZOS)
    logo.save(HEADER_LOGO, optimize=True)


def build_icon(source: Image.Image) -> None:
    mark = crop_relative(source, (0.17, 0.075, 0.83, 0.56))
    mark.thumbnail((218, 218), Image.Resampling.LANCZOS)

    icon = Image.new("RGB", (256, 256), "white")
    x = (icon.width - mark.width) // 2
    y = (icon.height - mark.height) // 2
    icon.paste(mark, (x, y))
    icon.save(ICON, optimize=True)


def main() -> None:
    source = Image.open(SOURCE).convert("RGB")
    build_header_logo(source)
    build_icon(source)
    print(HEADER_LOGO)
    print(ICON)


if __name__ == "__main__":
    main()
