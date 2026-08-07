from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "manipulacion-maximos-minimos-dia-anterior.pdf"
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
GREEN = HexColor("#0C8A6A")
RED = HexColor("#D64A60")


def wrap(text, font, size, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
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


def step_card(c, x, y, width, height, number, title, text):
    c.setFillColor(PAPER)
    c.setStrokeColor(LINE)
    c.roundRect(x, y - height, width, height, 7, fill=1, stroke=1)
    c.setFillColor(BLUE)
    c.roundRect(x + 16, y - 44, 34, 28, 5, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(x + 33, y - 35, number)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(x + 62, y - 36, title)
    paragraph(c, text, x + 16, y - 69, width - 32, size=9, leading=12)


def confirmation_card(c, y, tag, title, definition, valid_when):
    c.setFillColor(PAPER)
    c.setStrokeColor(LINE)
    c.roundRect(38, y - 132, W - 76, 132, 7, fill=1, stroke=1)
    c.setFillColor(NAVY)
    c.roundRect(54, y - 46, 66, 30, 5, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(87, y - 36, tag)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(138, y - 37, title)
    paragraph(c, definition, 54, y - 68, W - 108, size=9.2, leading=12)
    c.setFillColor(ICE)
    c.roundRect(54, y - 117, W - 108, 30, 5, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(65, y - 99, "VALIDA CUANDO")
    paragraph(c, valid_when, 142, y - 99, W - 196, size=8.2, leading=10, color=INK)


def candle(c, x, open_y, close_y, high_y, low_y, bullish):
    color = GREEN if bullish else RED
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.4)
    c.line(x + 5, low_y, x + 5, high_y)
    bottom = min(open_y, close_y)
    height = max(abs(close_y - open_y), 3)
    c.rect(x, bottom, 10, height, fill=1, stroke=0)


def liquidity_chart(c, x, y, width, height, bearish=True):
    c.setFillColor(PAPER)
    c.setStrokeColor(LINE)
    c.roundRect(x, y - height, width, height, 7, fill=1, stroke=1)
    line_y = y - 58 if bearish else y - height + 58
    c.setStrokeColor(BLUE)
    c.setLineWidth(1.2)
    c.line(x + 18, line_y, x + width - 18, line_y)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(x + 20, line_y + 7, "MÁXIMO ANTERIOR" if bearish else "MÍNIMO ANTERIOR")

    xs = [x + 46, x + 78, x + 110, x + 142, x + 174, x + 206]
    if bearish:
        values = [
            (line_y - 36, line_y - 18, line_y - 10, line_y - 45, True),
            (line_y - 18, line_y - 5, line_y + 5, line_y - 28, True),
            (line_y - 6, line_y + 16, line_y + 29, line_y - 12, True),
            (line_y + 15, line_y - 7, line_y + 22, line_y - 18, False),
            (line_y - 6, line_y - 31, line_y + 2, line_y - 40, False),
            (line_y - 30, line_y - 48, line_y - 22, line_y - 58, False),
        ]
    else:
        values = [
            (line_y + 36, line_y + 18, line_y + 45, line_y + 10, False),
            (line_y + 18, line_y + 5, line_y + 28, line_y - 5, False),
            (line_y + 6, line_y - 16, line_y + 12, line_y - 29, False),
            (line_y - 15, line_y + 7, line_y + 18, line_y - 22, True),
            (line_y + 6, line_y + 31, line_y + 40, line_y - 2, True),
            (line_y + 30, line_y + 48, line_y + 58, line_y + 22, True),
        ]
    for px, values_for_candle in zip(xs, values):
        candle(c, px, *values_for_candle)

    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x + width - 178, y - height + 25, "Búsqueda: VENTA" if bearish else "Búsqueda: COMPRA")


def checklist_row(c, y, number, text):
    c.setFillColor(ICE)
    c.roundRect(38, y - 5, 22, 22, 4, fill=1, stroke=0)
    c.setStrokeColor(BLUE)
    c.rect(45, y + 2, 8, 8, fill=0, stroke=1)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(72, y + 4, number)
    paragraph(c, text, 98, y + 4, W - 136, size=9.2, leading=12, color=INK)


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=A4)
    c.setTitle("Manipulación de máximos y mínimos del día anterior - TRADINVERSO")
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
    c.drawString(40, H - 170, "LIQUIDEZ - ESTRUCTURA - CONFIRMACIÓN")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 30)
    c.drawString(40, H - 220, "MANIPULACIÓN DE")
    c.drawString(40, H - 260, "MÁXIMOS Y MÍNIMOS")
    c.setFont("Helvetica-Bold", 19)
    c.drawString(40, H - 294, "DEL DÍA ANTERIOR")
    paragraph(
        c,
        "Un modelo mecánico para esperar la toma de liquidez y ejecutar únicamente cuando el precio confirma el cambio de intención.",
        40,
        H - 338,
        W - 80,
        size=11.5,
        leading=16,
        color=Color(1, 1, 1, 0.76),
    )
    labels = [("01", "MARCA"), ("02", "ESPERA"), ("03", "CONFIRMA")]
    box_w = (W - 96) / 3
    for index, (number, label) in enumerate(labels):
        x = 40 + index * (box_w + 8)
        c.setFillColor(NAVY)
        c.setStrokeColor(BLUE)
        c.roundRect(x, H - 470, box_w, 76, 5, fill=1, stroke=1)
        c.setFillColor(SKY)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(x + 14, H - 420, number)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawString(x + 14, H - 447, label)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, 66, "TRADINVERSO")
    c.setFillColor(Color(1, 1, 1, 0.55))
    c.setFont("Helvetica", 8.5)
    c.drawString(40, 49, "Recurso educativo - davidrosell.fx")
    c.showPage()

    # Page 2
    page_base(c, "El modelo", 2)
    page_title(
        c,
        "01 - Contexto",
        "El modelo en cuatro pasos",
        "No necesitas un indicador para localizar el máximo y el mínimo del día anterior. Solo una referencia diaria consistente y paciencia para esperar la reacción.",
    )
    card_width = (W - 88) / 2
    step_card(c, 38, H - 235, card_width, 160, "01", "Marca los extremos", "Al empezar la sesión, traza manualmente el máximo y el mínimo del día anterior ya completado.")
    step_card(c, 50 + card_width, H - 235, card_width, 160, "02", "Espera la barrida", "El precio debe superar uno de los niveles. Una simple llegada al extremo todavía no plantea el giro.")
    step_card(c, 38, H - 415, card_width, 160, "03", "Lee la intención", "Después de la toma de liquidez, busca desplazamiento y cambio de estructura en temporalidad baja.")
    step_card(c, 50 + card_width, H - 415, card_width, 160, "04", "Define el riesgo", "Ejecuta solo con invalidación clara y un objetivo que permita al menos una relación riesgo-beneficio de 1:1.")
    c.setFillColor(DARK)
    c.roundRect(38, 105, W - 76, 105, 7, fill=1, stroke=0)
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(54, 181, "IDEA CENTRAL")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(54, 154, "El nivel no es una entrada. Es una zona de decisión.")
    paragraph(c, "La operación aparece solo cuando la liquidez ha sido tomada y el precio demuestra intención de volver.", 54, 131, W - 108, size=9.5, leading=13, color=Color(1, 1, 1, 0.76))
    c.showPage()

    # Page 3
    page_base(c, "Confirmaciones", 3)
    page_title(
        c,
        "02 - Temporalidad baja",
        "Tres formas de confirmar el giro",
        "El cambio de estructura es la base. FVG, IFVG y vela envolvente son herramientas para validar que el desplazamiento contrario tiene intención real.",
    )
    confirmation_card(c, H - 235, "FVG", "Desequilibrio con desplazamiento", "El impulso contrario rompe la microestructura y deja un hueco entre velas.", "el FVG nace dentro del movimiento que cambia la estructura, no antes.")
    confirmation_card(c, H - 383, "IFVG", "Cambio de control", "Un FVG previo es atravesado y cerrado en sentido contrario, convirtiéndose en una zona inversa.", "la inversión se produce después de la barrida y acompaña el giro.")
    confirmation_card(c, H - 531, "VELA", "Envolvente decisiva", "Una vela cierra con fuerza por debajo de la última vela alcista para vender, o por encima de la última bajista para comprar.", "el cierre rompe la referencia interna y no se limita a dejar una mecha.")
    c.setFillColor(ICE)
    c.roundRect(38, 80, W - 76, 90, 7, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(54, 143, "TEMPORALIDAD")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(54, 120, "Usa una temporalidad baja que puedas ejecutar de forma consistente.")
    paragraph(c, "Cinco minutos es una referencia práctica. Bajar más solo tiene sentido si tus reglas y tus datos lo justifican.", 54, 99, W - 108, size=8.8, leading=11)
    c.showPage()

    # Page 4
    page_base(c, "Compra y venta", 4)
    page_title(
        c,
        "03 - Lectura direccional",
        "El modelo en compra y venta",
        "Cuando el precio barre el máximo anterior buscamos una confirmación bajista. Cuando barre el mínimo anterior buscamos la confirmación alcista equivalente.",
    )
    liquidity_chart(c, 38, H - 235, W - 76, 210, bearish=True)
    liquidity_chart(c, 38, H - 465, W - 76, 210, bearish=False)
    c.setFillColor(DARK)
    c.roundRect(38, 68, W - 76, 83, 7, fill=1, stroke=0)
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(54, 126, "NO ANTICIPES")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(54, 104, "Si el precio continúa fuera del nivel, no hay giro confirmado.")
    paragraph(c, "Esperar también es parte del modelo.", 54, 85, W - 108, size=9, color=Color(1, 1, 1, 0.72))
    c.showPage()

    # Page 5
    page_base(c, "Ejecución", 5)
    page_title(
        c,
        "04 - Checklist",
        "Antes de ejecutar",
        "Marca cada condición. Si falta contexto, confirmación o invalidación, todavía no existe una operación completa.",
    )
    items = [
        ("01", "He marcado el máximo y el mínimo del día anterior ya completado."),
        ("02", "El precio ha barrido uno de los extremos, no solo lo ha tocado."),
        ("03", "Existe rechazo o recuperación del nivel después de la barrida."),
        ("04", "La microestructura ha cambiado con un desplazamiento claro."),
        ("05", "Tengo una confirmación: FVG, IFVG o vela envolvente."),
        ("06", "La entrada y la invalidación están definidas antes de ejecutar."),
        ("07", "El riesgo es asumible y no lo he aumentado por confianza o urgencia."),
        ("08", "El objetivo ofrece como mínimo una relación riesgo-beneficio de 1:1."),
        ("09", "Sé qué condición cancela la idea y no moveré el stop para evitarla."),
    ]
    y = H - 245
    for number, text in items:
        checklist_row(c, y, number, text)
        y -= 44
    c.setFillColor(ICE)
    c.roundRect(38, 90, W - 76, 84, 7, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(54, 150, "REGLA FINAL")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(54, 126, "Sin confirmación, no hay trade.")
    paragraph(c, "Perder una oportunidad cuesta menos que ejecutar una operación que no cumple el modelo.", 54, 106, W - 108, size=9)
    c.showPage()

    # Page 6
    page_base(c, "Tu proceso", 6)
    page_title(
        c,
        "05 - Integración",
        "Convierte el modelo en datos",
        "La toma de liquidez del día anterior es una de las estructuras que trabajamos dentro del sistema TRADINVERSO. Su valor aparece cuando se ejecuta con reglas y se registra.",
    )
    fields = [
        ("Nivel atacado", "Máximo anterior / Mínimo anterior"),
        ("Confirmación", "FVG / IFVG / Envolvente"),
        ("Temporalidad", "Contexto y ejecución"),
        ("Riesgo", "% o cantidad fija"),
        ("Resultado", "R y calidad de ejecución"),
        ("Aprendizaje", "Qué repetir o corregir"),
    ]
    y = H - 245
    for label, hint in fields:
        c.setFillColor(PAPER)
        c.setStrokeColor(LINE)
        c.roundRect(38, y - 43, W - 76, 43, 5, fill=1, stroke=1)
        c.setFillColor(BLUE)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(52, y - 26, label.upper())
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8.5)
        c.drawRightString(W - 52, y - 26, hint)
        y -= 56
    c.setFillColor(DARK)
    c.roundRect(38, 88, W - 76, 148, 7, fill=1, stroke=0)
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(54, 207, "SIGUIENTE PASO")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(54, 177, "Accede a la masterclass gratuita")
    paragraph(c, "Descubre cómo unimos estructura, gestión, psicología y DATA dentro de un sistema objetivo.", 54, 151, W - 108, size=10, leading=14, color=Color(1, 1, 1, 0.76))
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(54, 116, "CLASE.TRADINVERSO.COM")
    c.showPage()

    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    build()
