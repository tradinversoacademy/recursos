from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "guia-5-conceptos-esenciales-trading.pdf"
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
GREEN = HexColor("#1B9C68")
RED = HexColor("#D95362")


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
    c.saveState()
    c.drawImage(str(LOGO), 38, H - 76, width=46, height=46, preserveAspectRatio=True, mask="auto")
    c.restoreState()
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


def candle(c, x, low, high, open_price, close_price, width=22):
    bullish = close_price >= open_price
    color = BLUE if bullish else NAVY
    c.setStrokeColor(color)
    c.setLineWidth(2)
    c.line(x, low, x, high)
    body_low = min(open_price, close_price)
    body_height = max(abs(close_price - open_price), 3)
    c.setFillColor(color if bullish else white)
    c.rect(x - width / 2, body_low, width, body_height, fill=1, stroke=1)


def chart_frame(c, x, y, width, height, label):
    c.setFillColor(PAPER)
    c.setStrokeColor(LINE)
    c.roundRect(x, y, width, height, 7, fill=1, stroke=1)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x + 16, y + height - 24, label.upper())
    for index in range(1, 4):
        grid_y = y + 20 + index * ((height - 56) / 4)
        c.setStrokeColor(HexColor("#E7EFFB"))
        c.setLineWidth(0.6)
        c.line(x + 16, grid_y, x + width - 16, grid_y)


def rule_box(c, y, title, body, accent=BLUE):
    c.setFillColor(ICE)
    c.roundRect(38, y - 76, W - 76, 76, 7, fill=1, stroke=0)
    c.setFillColor(accent)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(54, y - 24, title.upper())
    paragraph(c, body, 54, y - 45, W - 108, size=9.3, leading=12, color=INK)


def key_row(c, y, number, title, text):
    c.setFillColor(BLUE)
    c.roundRect(38, y - 32, 34, 28, 5, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(55, y - 22, number)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(86, y - 16, title)
    paragraph(c, text, 86, y - 32, W - 124, size=8.8, leading=11)


def checklist_row(c, y, text):
    c.setFillColor(ICE)
    c.roundRect(38, y - 5, 20, 20, 4, fill=1, stroke=0)
    c.setStrokeColor(BLUE)
    c.rect(44, y + 1, 8, 8, fill=0, stroke=1)
    paragraph(c, text, 70, y + 3, W - 108, size=9.2, leading=12, color=INK)


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=A4)
    c.setTitle("Los 5 conceptos esenciales del trading - TRADINVERSO")
    c.setAuthor("TRADINVERSO")

    # Cover
    c.setFillColor(DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.rect(0, H - 18, W, 18, fill=1, stroke=0)
    c.setFillColor(white)
    c.roundRect(40, H - 118, 82, 82, 6, fill=1, stroke=0)
    c.saveState()
    c.drawImage(str(LOGO), 49, H - 109, width=64, height=64, preserveAspectRatio=True, mask="auto")
    c.restoreState()
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, H - 170, "GUÍA ESENCIAL DE LECTURA DEL PRECIO")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 30)
    c.drawString(40, H - 218, "LOS 5 CONCEPTOS")
    c.drawString(40, H - 257, "ESENCIALES DEL TRADING")
    paragraph(
        c,
        "FVG, IFVG, liquidez y estructura explicados con gráficos sencillos y una lectura conjunta.",
        40,
        H - 304,
        W - 80,
        size=12,
        leading=17,
        color=Color(1, 1, 1, 0.76),
    )
    labels = ["FVG", "IFVG", "LIQUIDEZ", "ESTRUCTURA", "CAMBIO"]
    box_w = (W - 112) / 5
    for index, label in enumerate(labels):
        x = 40 + index * (box_w + 8)
        c.setFillColor(BLUE if index in (1, 4) else NAVY)
        c.setStrokeColor(BLUE)
        c.roundRect(x, H - 450, box_w, 68, 5, fill=1, stroke=1)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawCentredString(x + box_w / 2, H - 423, label)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, 66, "TRADINVERSO")
    c.setFillColor(Color(1, 1, 1, 0.55))
    c.setFont("Helvetica", 8.5)
    c.drawString(40, 49, "Recurso educativo - davidrosell.fx")
    c.showPage()

    # Overview
    page_base(c, "Mapa de lectura", 2)
    page_title(
        c,
        "Antes de estudiar cada concepto",
        "Las cinco piezas forman una lectura",
        "No necesitas acumular términos. Necesitas comprender qué pregunta responde cada concepto y cómo se relaciona con los demás.",
    )
    flow = [
        ("01", "Liquidez", "¿Dónde pueden estar acumuladas las órdenes?"),
        ("02", "Estructura", "¿Qué dirección mantiene el precio?"),
        ("03", "Cambio", "¿Ha aparecido una nueva intención?"),
        ("04", "FVG / IFVG", "¿Qué zona deja o invierte el desplazamiento?"),
        ("05", "Objetivo", "¿Dónde está la siguiente liquidez relevante?"),
    ]
    y = H - 245
    for index, (number, title, text) in enumerate(flow):
        c.setFillColor(PAPER)
        c.setStrokeColor(LINE)
        c.roundRect(38, y - 58, W - 76, 58, 6, fill=1, stroke=1)
        c.setFillColor(BLUE)
        c.roundRect(52, y - 43, 38, 28, 5, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(71, y - 33, number)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(106, y - 27, title)
        paragraph(c, text, 210, y - 27, W - 264, size=9, leading=11)
        if index < len(flow) - 1:
            c.setFillColor(BLUE)
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(W / 2, y - 73, "↓")
        y -= 82
    rule_box(
        c,
        128,
        "Regla de contexto",
        "Un concepto aislado no es una entrada. La operación gana calidad cuando liquidez, estructura, intención y riesgo cuentan la misma historia.",
    )
    c.showPage()

    # FVG
    page_base(c, "Concepto 01 - FVG", 3)
    page_title(
        c,
        "01 - Fair Value Gap",
        "El desequilibrio que deja el impulso",
        "Un FVG aparece cuando el precio se desplaza con tanta velocidad que queda un espacio entre la primera y la tercera vela de una secuencia de tres.",
    )
    chart_frame(c, 38, H - 520, W - 76, 275, "Ejemplo visual - FVG alcista")
    base = H - 480
    candle(c, 150, base, base + 85, base + 20, base + 62, 28)
    candle(c, 270, base + 48, base + 190, base + 58, base + 168, 34)
    candle(c, 390, base + 112, base + 208, base + 128, base + 180, 28)
    c.setFillColor(Color(0.18, 0.54, 1, 0.18))
    c.rect(164, base + 85, 212, 27, fill=1, stroke=0)
    c.setStrokeColor(BLUE)
    c.setDash(4, 3)
    c.line(164, base + 85, 376, base + 85)
    c.line(164, base + 112, 376, base + 112)
    c.setDash()
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(407, base + 95, "FVG")
    key_row(c, H - 558, "A", "Qué indica", "Un desplazamiento con desequilibrio y urgencia en una dirección.")
    key_row(c, H - 606, "B", "Cómo se utiliza", "Como zona de interés cuando el precio corrige; nunca como entrada automática.")
    key_row(c, H - 654, "C", "Qué debe acompañarlo", "Contexto, liquidez, estructura e invalidación técnica.")
    rule_box(c, 112, "Idea sencilla", "El precio puede volver a equilibrar la zona, pero no tiene la obligación de llenarla por completo.")
    c.showPage()

    # IFVG
    page_base(c, "Concepto 02 - IFVG", 4)
    page_title(
        c,
        "02 - Inverse Fair Value Gap",
        "Cuando el desequilibrio cambia de función",
        "Un IFVG aparece cuando un FVG pierde su función original, el precio lo atraviesa con intención y la zona puede actuar en el sentido contrario.",
    )
    chart_frame(c, 38, H - 520, W - 76, 275, "Ejemplo visual - inversión de un FVG")
    base = H - 475
    c.setFillColor(Color(0.18, 0.54, 1, 0.16))
    c.rect(105, base + 94, 360, 30, fill=1, stroke=0)
    c.setStrokeColor(BLUE)
    c.setDash(4, 3)
    c.line(105, base + 94, 465, base + 94)
    c.line(105, base + 124, 465, base + 124)
    c.setDash()
    candles = [
        (125, 55, 140, 70, 125),
        (190, 90, 165, 130, 108),
        (255, 50, 132, 112, 66),
        (320, 18, 95, 72, 34),
        (385, 28, 118, 44, 105),
        (450, 65, 130, 112, 78),
    ]
    for x, low, high, op, close in candles:
        candle(c, x, base + low, base + high, base + op, base + close, 24)
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(273, base + 20, "Ruptura con intención")
    c.setFillColor(BLUE)
    c.drawString(397, base + 133, "Retesteo IFVG")
    key_row(c, H - 558, "A", "Qué cambia", "La zona deja de defender el movimiento original.")
    key_row(c, H - 606, "B", "Qué confirma", "Un posible cambio de intención cuando existe desplazamiento y estructura.")
    key_row(c, H - 654, "C", "Cómo lo usamos", "Como confirmación y contexto; después esperamos una entrada con lógica propia.")
    rule_box(c, 112, "No confundas", "No todo FVG atravesado es un IFVG útil. La ruptura necesita intención, contexto y una lectura estructural coherente.")
    c.showPage()

    # Liquidity
    page_base(c, "Concepto 03 - Liquidez", 5)
    page_title(
        c,
        "03 - Manipulación de liquidez",
        "El precio barre y recupera",
        "Los máximos y mínimos visibles pueden concentrar órdenes. Una manipulación aparece cuando el precio los supera y recupera rápidamente la zona.",
    )
    chart_frame(c, 38, H - 520, W - 76, 275, "Ejemplo visual - barrido de un máximo")
    base = H - 475
    level = base + 125
    c.setStrokeColor(RED)
    c.setDash(5, 3)
    c.line(80, level, 500, level)
    c.setDash()
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawRightString(500, level + 9, "Máximo anterior / liquidez")
    candles = [
        (110, 42, 110, 58, 96),
        (165, 70, 124, 101, 84),
        (220, 68, 126, 88, 118),
        (275, 92, 184, 117, 104),
        (330, 48, 122, 102, 62),
        (385, 22, 72, 59, 36),
    ]
    for x, low, high, op, close in candles:
        candle(c, x, base + low, base + high, base + op, base + close, 24)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(250, base + 193, "Barrido")
    c.setFillColor(RED)
    c.drawString(345, base + 30, "Rechazo")
    key_row(c, H - 558, "A", "Dónde buscarla", "En máximos, mínimos y zonas que el mercado puede identificar con claridad.")
    key_row(c, H - 606, "B", "Qué observar", "Barrido, rechazo y recuperación; no basta con tocar el nivel.")
    key_row(c, H - 654, "C", "Qué evita", "Confundir una falsa continuación con una reversión confirmada.")
    rule_box(c, 112, "Importante", "Un barrido por sí solo tampoco confirma una entrada. Espera intención y cambio estructural.")
    c.showPage()

    # Structure
    page_base(c, "Concepto 04 - Estructura", 6)
    page_title(
        c,
        "04 - Estructura de mercado",
        "La secuencia que define el contexto",
        "La estructura organiza los máximos y mínimos del precio. Nos ayuda a entender qué dirección mantiene el control y dónde puede existir liquidez.",
    )
    panel_w = (W - 88) / 2
    chart_frame(c, 38, H - 505, panel_w, 250, "Estructura alcista")
    chart_frame(c, 50 + panel_w, H - 505, panel_w, 250, "Estructura bajista")

    left_points = [(65, 40), (105, 98), (145, 67), (190, 145), (230, 104)]
    left_x = 38
    left_y = H - 485
    c.setStrokeColor(BLUE)
    c.setLineWidth(3)
    for a, b in zip(left_points, left_points[1:]):
        c.line(left_x + a[0], left_y + a[1], left_x + b[0], left_y + b[1])
    labels = [(105, 98, "HH"), (145, 67, "HL"), (190, 145, "HH"), (230, 104, "HL")]
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 8)
    for x, y, label in labels:
        c.drawCentredString(left_x + x, left_y + y + 10, label)

    right_points = [(55, 155), (100, 98), (145, 128), (190, 60), (230, 92)]
    right_x = 50 + panel_w
    right_y = H - 485
    c.setStrokeColor(NAVY)
    for a, b in zip(right_points, right_points[1:]):
        c.line(right_x + a[0], right_y + a[1], right_x + b[0], right_y + b[1])
    labels = [(100, 98, "LL"), (145, 128, "LH"), (190, 60, "LL"), (230, 92, "LH")]
    c.setFillColor(NAVY)
    for x, y, label in labels:
        c.drawCentredString(right_x + x, right_y + y + 10, label)

    key_row(c, H - 548, "A", "Alcista", "Máximos más altos y mínimos más altos.")
    key_row(c, H - 596, "B", "Bajista", "Máximos más bajos y mínimos más bajos.")
    key_row(c, H - 644, "C", "Función", "Define contexto y señala niveles estructurales donde puede descansar liquidez.")
    rule_box(c, 112, "Evita el ruido", "Define primero la temporalidad que estás leyendo. Una estructura puede ser alcista en M5 y bajista en H1.")
    c.showPage()

    # Change of structure
    page_base(c, "Concepto 05 - Cambio", 7)
    page_title(
        c,
        "05 - Cambio de estructura",
        "La ruptura que revela nueva intención",
        "Cuando el precio rompe un máximo o mínimo estructural con desplazamiento, deja de comportarse como antes y puede buscar el siguiente nivel de liquidez.",
    )
    chart_frame(c, 38, H - 520, W - 76, 275, "Ejemplo visual - cambio alcista")
    base = H - 475
    level = base + 122
    c.setStrokeColor(NAVY)
    c.setDash(5, 3)
    c.line(80, level, 500, level)
    c.setDash()
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(82, level + 9, "Máximo estructural")
    candles = [
        (110, 52, 118, 98, 66),
        (165, 36, 88, 68, 48),
        (220, 44, 106, 58, 96),
        (275, 80, 148, 95, 136),
        (330, 112, 205, 126, 188),
        (395, 160, 228, 180, 210),
    ]
    for x, low, high, op, close in candles:
        candle(c, x, base + low, base + high, base + op, base + close, 24)
    c.setFillColor(Color(0.18, 0.54, 1, 0.18))
    c.rect(287, base + 148, 94, 22, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(285, base + 214, "Desplazamiento")
    c.drawString(300, base + 154, "FVG")
    key_row(c, H - 558, "A", "Qué debe romper", "Un máximo o mínimo relevante para la estructura que estás leyendo.")
    key_row(c, H - 606, "B", "Cómo debe hacerlo", "Con intención, velocidad y cierre; mejor si deja desequilibrio.")
    key_row(c, H - 654, "C", "Qué buscamos después", "Una corrección hacia una zona relevante y una entrada con invalidación.")
    rule_box(c, 112, "No anticipes", "Una mecha que supera el nivel y vuelve no equivale a un cambio estructural confirmado.")
    c.showPage()

    # Final
    page_base(c, "Lectura completa", 8)
    page_title(
        c,
        "Los cinco conceptos en orden",
        "Checklist antes de construir una idea",
        "Utiliza esta secuencia para evitar entradas basadas en una sola zona o en una intuición aislada.",
    )
    items = [
        "He localizado la liquidez relevante y sé por qué puede atraer al precio.",
        "Tengo definida la estructura y la temporalidad que estoy leyendo.",
        "Ha ocurrido una manipulación o limpieza con reacción clara.",
        "Existe un cambio de estructura con desplazamiento y cierre.",
        "El FVG o IFVG aparece en una zona coherente con la nueva intención.",
        "La entrada, el stop y el objetivo están definidos antes de ejecutar.",
        "El recorrido hasta la siguiente liquidez compensa el riesgo asumido.",
    ]
    y = H - 250
    for item in items:
        checklist_row(c, y, item)
        y -= 48

    c.setFillColor(DARK)
    c.roundRect(38, 104, W - 76, 142, 8, fill=1, stroke=0)
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(54, 219, "SIGUIENTE PASO")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 17)
    c.drawString(54, 191, "Accede a nuestra masterclass gratuita")
    paragraph(
        c,
        "Descubre cómo utilizamos estos conceptos dentro de un sistema sencillo, objetivo y acompañado.",
        54,
        169,
        W - 108,
        size=9.5,
        leading=13,
        color=Color(1, 1, 1, 0.76),
    )
    c.setFillColor(BLUE)
    c.roundRect(54, 120, 210, 30, 5, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(159, 131, "CLASE.TRADINVERSO.COM")
    c.linkURL("https://clase.tradinverso.com/", (54, 120, 264, 150), relative=0)
    c.showPage()

    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    build()
