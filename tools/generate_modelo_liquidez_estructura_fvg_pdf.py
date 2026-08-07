from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "modelo-liquidez-estructura-fvg.pdf"
CHART_IMAGE = ROOT / "assets" / "img" / "resources" / "modelo-liquidez-estructura-fvg.png"
LOGO = ROOT / "assets" / "img" / "tradinverso-logo.png"
W, H = A4

NAVY = HexColor("#06245C")
DARK = HexColor("#03173B")
BLUE = HexColor("#2D89FF")
SKY = HexColor("#5DB2FF")
ICE = HexColor("#EAF4FF")
INK = HexColor("#06152E")
MUTED = HexColor("#566578")
LINE = HexColor("#D9E6FB")
PAPER = HexColor("#F7FAFF")
GREEN = HexColor("#17B978")
RED = HexColor("#E24D5F")

MODEL = [
    (18, 30, 35, 14),
    (30, 42, 47, 28),
    (42, 55, 60, 39),
    (55, 49, 58, 45),
    (49, 58, 63, 47),
    (58, 52, 61, 48),
    (52, 60, 64, 50),
    (60, 46, 62, 34),
    (46, 63, 66, 43),
    (63, 78, 82, 60),
    (78, 90, 94, 75),
    (90, 80, 93, 74),
    (80, 102, 106, 78),
]


def wrap(text, font, size, max_width):
    lines = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if stringWidth(candidate, font, size) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def paragraph(c, text, x, y, width, size=9.5, leading=13, color=MUTED, font="Helvetica"):
    c.setFillColor(color)
    c.setFont(font, size)
    for line in wrap(text, font, size, width):
        c.drawString(x, y, line)
        y -= leading
    return y


def page_base(c, label, page):
    c.setFillColor(white)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.drawImage(str(LOGO), 38, H - 76, width=46, height=46, preserveAspectRatio=True, mask="auto")
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(96, H - 49, "TRADINVERSO")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7.5)
    c.drawString(96, H - 63, "TRADING CON DATA E IA")
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 8)
    c.drawRightString(W - 38, H - 52, label.upper())
    c.setStrokeColor(LINE)
    c.line(38, H - 88, W - 38, H - 88)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(38, 28, "Recurso educativo - davidrosell.fx")
    c.drawRightString(W - 38, 28, f"{page:02d}")


def page_title(c, kicker, title, subtitle):
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(38, H - 126, kicker.upper())
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 23)
    c.drawString(38, H - 160, title)
    paragraph(c, subtitle, 38, H - 186, W - 76, size=10, leading=14)


def pill(c, x, y, width, text, fill=ICE, text_color=BLUE):
    c.setFillColor(fill)
    c.roundRect(x, y, width, 26, 5, fill=1, stroke=0)
    c.setFillColor(text_color)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(x + width / 2, y + 9, text)


def step_box(c, x, y, width, number, title, text):
    c.setFillColor(PAPER)
    c.setStrokeColor(LINE)
    c.roundRect(x, y - 104, width, 104, 7, fill=1, stroke=1)
    c.setFillColor(BLUE)
    c.roundRect(x + 14, y - 39, 34, 26, 5, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawCentredString(x + 31, y - 30, number)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x + 58, y - 31, title)
    paragraph(c, text, x + 14, y - 59, width - 28, size=8.4, leading=11)


def note_box(c, y, title, text, accent=BLUE):
    c.setFillColor(ICE)
    c.roundRect(38, y - 78, W - 76, 78, 7, fill=1, stroke=0)
    c.setFillColor(accent)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(54, y - 25, title.upper())
    paragraph(c, text, 54, y - 47, W - 108, size=9.2, leading=12, color=INK)


def checklist_row(c, y, text):
    c.setFillColor(ICE)
    c.roundRect(38, y - 4, 22, 22, 4, fill=1, stroke=0)
    c.setStrokeColor(BLUE)
    c.rect(45, y + 3, 8, 8, fill=0, stroke=1)
    paragraph(c, text, 72, y + 4, W - 110, size=9.2, leading=12, color=INK)


def draw_candle(c, x, y, scale, candle_width, values):
    open_value, close_value, high_value, low_value = values
    bullish = close_value >= open_value
    color = GREEN if bullish else RED
    low = y + low_value * scale
    high = y + high_value * scale
    open_y = y + open_value * scale
    close_y = y + close_value * scale
    c.setStrokeColor(color)
    c.setLineWidth(1.4)
    c.line(x, low, x, high)
    c.setFillColor(color)
    c.rect(
        x - candle_width / 2,
        min(open_y, close_y),
        candle_width,
        max(abs(close_y - open_y), 3),
        fill=1,
        stroke=0,
    )


def chart(c, x, y, width, height, stage=3, risk=False):
    c.setFillColor(DARK)
    c.roundRect(x, y, width, height, 8, fill=1, stroke=0)
    for index in range(1, 6):
        c.setStrokeColor(HexColor("#16345F"))
        c.setLineWidth(0.45)
        grid_y = y + index * height / 6
        c.line(x + 18, grid_y, x + width - 18, grid_y)
    for index in range(1, 10):
        grid_x = x + index * width / 10
        c.line(grid_x, y + 18, grid_x, y + height - 18)

    scale = (height - 54) / 112
    candle_width = max(8, min(16, width / 34))
    gap = (width - 76) / 13
    start_x = x + 38
    visible = 8 if stage == 1 else 11 if stage == 2 else 13
    for index, values in enumerate(MODEL[:visible]):
        draw_candle(c, start_x + index * gap, y + 24, scale, candle_width, values)

    relevant_low = y + 24 + 46 * scale
    c.setStrokeColor(SKY)
    c.setDash(4, 3)
    c.line(start_x + 3.5 * gap, relevant_low, start_x + 8.2 * gap, relevant_low)
    c.setDash()
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(start_x + 3.5 * gap, relevant_low + 7, "MÍNIMO RELEVANTE")

    sweep_x = start_x + 7 * gap
    sweep_y = y + 24 + 34 * scale
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(sweep_x, sweep_y - 16, "1 · BARRIDA")
    c.setStrokeColor(RED)
    c.line(sweep_x, sweep_y - 10, sweep_x, sweep_y + 4)

    if stage >= 2:
        break_level = y + 24 + 64 * scale
        c.setStrokeColor(BLUE)
        c.setDash(4, 3)
        c.line(start_x + 5.5 * gap, break_level, start_x + 10.7 * gap, break_level)
        c.setDash()
        c.setFillColor(SKY)
        c.drawString(start_x + 8.2 * gap, break_level + 7, "2 · RUPTURA")

    if stage >= 3:
        fvg_low = y + 24 + 66 * scale
        fvg_high = y + 24 + 75 * scale
        fvg_x = start_x + 8.2 * gap
        fvg_width = 3.7 * gap
        c.setFillColor(Color(0.18, 0.54, 1, 0.24))
        c.rect(fvg_x, fvg_low, fvg_width, fvg_high - fvg_low, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(fvg_x + 6, fvg_high + 7, "3 · FVG")
        entry_x = start_x + 11 * gap
        entry_y = y + 24 + 76 * scale
        c.setStrokeColor(SKY)
        c.setLineWidth(1.4)
        c.line(entry_x + 18, entry_y + 23, entry_x + 3, entry_y + 5)
        c.line(entry_x + 3, entry_y + 5, entry_x + 9, entry_y + 7)
        c.line(entry_x + 3, entry_y + 5, entry_x + 5, entry_y + 12)
        c.setFillColor(SKY)
        c.drawString(entry_x + 20, entry_y + 24, "RETROCESO")

    if risk and stage >= 3:
        entry = y + 24 + 79 * scale
        stop = y + 24 + 70 * scale
        target = y + 24 + 106 * scale
        box_x = start_x + 11.8 * gap
        box_w = max(18, 0.9 * gap)
        c.setFillColor(Color(0.09, 0.73, 0.47, 0.24))
        c.rect(box_x, entry, box_w, target - entry, fill=1, stroke=0)
        c.setFillColor(Color(0.89, 0.30, 0.37, 0.28))
        c.rect(box_x, stop, box_w, entry - stop, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(box_x + box_w + 5, entry - 2, "ENTRADA")
        c.drawString(box_x + box_w + 5, stop - 2, "STOP")
        c.drawString(box_x + box_w + 5, target - 2, "OBJETIVO")


def load_font(size, bold=False):
    name = "arialbd.ttf" if bold else "arial.ttf"
    path = Path("C:/Windows/Fonts") / name
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def build_chart_image():
    CHART_IMAGE.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1600, 900), "#03173B")
    draw = ImageDraw.Draw(image, "RGBA")
    for x in range(80, 1521, 120):
        draw.line((x, 150, x, 820), fill="#16345F", width=1)
    for y in range(180, 821, 100):
        draw.line((80, y, 1520, y), fill="#16345F", width=1)

    title_font = load_font(46, True)
    small_font = load_font(21, True)
    label_font = load_font(24, True)
    draw.text((80, 54), "LIQUIDEZ + ESTRUCTURA + FVG", font=title_font, fill="#FFFFFF")
    draw.text((80, 112), "El modelo completo en una sola lectura", font=small_font, fill="#5DB2FF")

    chart_x, chart_y, chart_w, chart_h = 100, 210, 1360, 560
    scale = (chart_h - 55) / 112
    gap = (chart_w - 90) / 13
    start_x = chart_x + 42
    candle_width = 28

    def py(value):
        return chart_y + chart_h - 28 - value * scale

    for index, (open_value, close_value, high_value, low_value) in enumerate(MODEL):
        x = start_x + index * gap
        bullish = close_value >= open_value
        color = "#17B978" if bullish else "#E24D5F"
        draw.line((x, py(low_value), x, py(high_value)), fill=color, width=4)
        top = min(py(open_value), py(close_value))
        bottom = max(py(open_value), py(close_value))
        draw.rectangle((x - candle_width / 2, top, x + candle_width / 2, max(bottom, top + 5)), fill=color)

    relevant_low = py(46)
    draw.line((start_x + 3.5 * gap, relevant_low, start_x + 8.2 * gap, relevant_low), fill="#5DB2FF", width=3)
    draw.text((start_x + 3.5 * gap, relevant_low - 34), "MÍNIMO RELEVANTE", font=small_font, fill="#5DB2FF")

    sweep_x = start_x + 7 * gap
    sweep_y = py(34)
    draw.line((sweep_x, sweep_y + 8, sweep_x, sweep_y + 58), fill="#E24D5F", width=3)
    draw.text((sweep_x - 70, sweep_y + 66), "1 · BARRIDA", font=label_font, fill="#E24D5F")

    break_level = py(64)
    draw.line((start_x + 5.5 * gap, break_level, start_x + 10.7 * gap, break_level), fill="#2D89FF", width=3)
    draw.text((start_x + 7.8 * gap, break_level - 38), "2 · RUPTURA", font=label_font, fill="#5DB2FF")

    fvg_top = py(75)
    fvg_bottom = py(66)
    fvg_x = start_x + 8.2 * gap
    draw.rectangle((fvg_x, fvg_top, fvg_x + 3.7 * gap, fvg_bottom), fill=(45, 137, 255, 72))
    draw.text((fvg_x + 18, fvg_top - 38), "3 · FVG", font=label_font, fill="#FFFFFF")

    entry_x = start_x + 11 * gap
    entry_y = py(76)
    draw.line((entry_x + 55, entry_y - 55, entry_x + 8, entry_y - 6), fill="#5DB2FF", width=4)
    draw.polygon([(entry_x + 8, entry_y - 6), (entry_x + 17, entry_y - 26), (entry_x + 28, entry_y - 14)], fill="#5DB2FF")
    draw.text((entry_x + 62, entry_y - 80), "RETROCESO Y ENTRADA", font=small_font, fill="#5DB2FF")

    image.save(CHART_IMAGE, optimize=True)


def build():
    build_chart_image()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=A4)
    c.setTitle("Modelo de compra: liquidez, estructura y FVG - TRADINVERSO")
    c.setAuthor("TRADINVERSO")

    # Cover
    c.setFillColor(DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.rect(0, H - 18, W, 18, fill=1, stroke=0)
    c.setFillColor(white)
    c.roundRect(40, H - 118, 82, 82, 6, fill=1, stroke=0)
    c.drawImage(str(LOGO), 49, H - 109, width=64, height=64, preserveAspectRatio=True, mask="auto")
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, H - 170, "GUÍA VISUAL · NASDAQ")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 30)
    c.drawString(40, H - 218, "MODELO DE COMPRA")
    c.drawString(40, H - 258, "EN TRES PASOS")
    paragraph(
        c,
        "Manipulación de liquidez, cambio de estructura y retroceso al Fair Value Gap dentro de una misma lectura.",
        40,
        H - 306,
        W - 80,
        size=12,
        leading=17,
        color=Color(1, 1, 1, 0.76),
    )
    labels = [("01", "LIQUIDEZ"), ("02", "ESTRUCTURA"), ("03", "FVG")]
    box_w = (W - 96) / 3
    for index, (number, label) in enumerate(labels):
        x = 40 + index * (box_w + 8)
        c.setFillColor(NAVY)
        c.setStrokeColor(BLUE)
        c.roundRect(x, H - 464, box_w, 78, 5, fill=1, stroke=1)
        c.setFillColor(SKY)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(x + 14, H - 414, number)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x + 14, H - 443, label)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, 66, "TRADINVERSO")
    c.setFillColor(Color(1, 1, 1, 0.55))
    c.setFont("Helvetica", 8.5)
    c.drawString(40, 49, "Recurso educativo - davidrosell.fx")
    c.showPage()

    # Overview
    page_base(c, "El modelo", 2)
    page_title(
        c,
        "Una sola secuencia",
        "No persigas la entrada",
        "La entrada no empieza en el FVG. Empieza cuando el precio toma liquidez, cambia su comportamiento y deja una zona lógica para gestionar el riesgo.",
    )
    chart(c, 38, H - 515, W - 76, 280, stage=3)
    step_w = (W - 92) / 3
    step_box(c, 38, H - 550, step_w, "01", "Manipulación", "El precio barre un mínimo relevante y recupera la zona.")
    step_box(c, 46 + step_w, H - 550, step_w, "02", "Estructura", "El impulso alcista rompe un máximo interno con cierre.")
    step_box(c, 54 + 2 * step_w, H - 550, step_w, "03", "FVG", "Esperamos el retroceso al desequilibrio antes de ejecutar.")
    note_box(c, 112, "La idea central", "Cada paso filtra al anterior. Si falta liquidez, ruptura o una entrada gestionable, el modelo todavía no está completo.")
    c.showPage()

    # Liquidity
    page_base(c, "Paso 01 - Liquidez", 3)
    page_title(
        c,
        "Primero el combustible",
        "Espera la manipulación",
        "El precio debe barrer por debajo de un mínimo relevante. La toma de liquidez plantea el giro, pero todavía no confirma una compra.",
    )
    chart(c, 38, H - 520, W - 76, 280, stage=1)
    step_box(c, 38, H - 560, (W - 88) / 2, "A", "Qué buscamos", "Una mecha o desplazamiento por debajo del mínimo seguido de recuperación.")
    step_box(c, 50 + (W - 88) / 2, H - 560, (W - 88) / 2, "B", "Qué evitamos", "Comprar solo porque el precio tocó un nivel o parece barato.")
    note_box(c, 112, "No basta con barrer", "Si el precio continúa aceptando por debajo del mínimo, no existe recuperación ni intención alcista confirmada.", accent=RED)
    c.showPage()

    # Structure
    page_base(c, "Paso 02 - Estructura", 4)
    page_title(
        c,
        "Después de la barrida",
        "Confirma el cambio de estructura",
        "Los compradores deben demostrar fuerza rompiendo un máximo interno relevante. Buscamos desplazamiento y cierre, no una mecha aislada.",
    )
    chart(c, 38, H - 520, W - 76, 280, stage=2)
    step_box(c, 38, H - 560, (W - 88) / 2, "A", "Ruptura válida", "El precio supera el máximo con cuerpo, velocidad y continuidad.")
    step_box(c, 50 + (W - 88) / 2, H - 560, (W - 88) / 2, "B", "Lectura", "La secuencia deja un máximo más alto y cambia la microestructura.")
    note_box(c, 112, "La confirmación", "La ruptura muestra que la barrida no fue una simple pausa bajista: aparece una intención nueva que ya podemos seguir.")
    c.showPage()

    # FVG
    page_base(c, "Paso 03 - FVG", 5)
    page_title(
        c,
        "El filtro de ejecución",
        "Espera el retroceso al FVG",
        "El desplazamiento deja un espacio entre la primera y la tercera vela. Esa zona permite esperar una corrección en lugar de perseguir el impulso.",
    )
    chart(c, 38, H - 520, W - 76, 280, stage=3)
    step_box(c, 38, H - 560, (W - 88) / 2, "A", "Entrada", "El precio vuelve al FVG después de haber confirmado la ruptura estructural.")
    step_box(c, 50 + (W - 88) / 2, H - 560, (W - 88) / 2, "B", "Invalidación", "El stop se define bajo la manipulación o la referencia técnica del modelo.")
    note_box(c, 112, "No todo FVG sirve", "Un FVG aislado no es una señal. Aquí tiene valor porque aparece después de liquidez y cambio de estructura.")
    c.showPage()

    # Execution
    page_base(c, "Ejecución", 6)
    page_title(
        c,
        "Riesgo antes que resultado",
        "Entrada, stop y objetivo",
        "La estructura define la operación. El objetivo 1:3 es una referencia del ejemplo, no una obligación: solo se utiliza si el recorrido y la siguiente liquidez lo permiten.",
    )
    chart(c, 38, H - 480, W - 76, 240, stage=3, risk=True)
    items = [
        "Existe un mínimo relevante claramente definido.",
        "El precio lo ha barrido y ha recuperado la zona.",
        "La microestructura alcista se confirma con cierre y desplazamiento.",
        "El FVG nace del impulso y la entrada espera el retroceso.",
        "Entrada, stop, riesgo y objetivo están definidos antes de ejecutar.",
    ]
    y = H - 522
    for item in items:
        checklist_row(c, y, item)
        y -= 40

    c.setFillColor(DARK)
    c.roundRect(38, 55, W - 76, 80, 7, fill=1, stroke=0)
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(54, 112, "SIGUIENTE PASO")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(54, 89, "Descubre el sistema completo de TRADINVERSO")
    c.setFont("Helvetica", 9)
    c.drawString(54, 68, "Accede a la clase gratuita en clase.tradinverso.com")
    c.linkURL("https://clase.tradinverso.com/", (38, 55, W - 38, 135), relative=0)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 6.8)
    c.drawString(38, 43, "Contenido educativo. No constituye asesoramiento financiero ni garantiza resultados.")
    c.showPage()

    c.save()
    print(OUTPUT)
    print(CHART_IMAGE)


if __name__ == "__main__":
    build()
