from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "guia-apertura-0000-nueva-york.pdf"
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
GREEN = HexColor("#E8F7F0")
RED = HexColor("#FFF0F0")


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


def paragraph(c, text, x, y, width, size=10, leading=14, color=MUTED, font="Helvetica"):
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
    c.drawRightString(W - 38, 28, f"{page:02d}")


def section_title(c, kicker, title, y):
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(38, y, kicker.upper())
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 23)
    c.drawString(38, y - 34, title)
    return y - 62


def phase(c, x, y, width, number, title, body):
    c.setFillColor(PAPER)
    c.setStrokeColor(LINE)
    c.roundRect(x, y, width, 128, 6, fill=1, stroke=1)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x + 16, y + 102, number)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(x + 16, y + 76, title)
    paragraph(c, body, x + 16, y + 55, width - 32, size=9.2, leading=12.5)


def note(c, title, body, y, fill=ICE):
    c.setFillColor(fill)
    c.roundRect(38, y - 70, W - 76, 70, 6, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(54, y - 23, title.upper())
    paragraph(c, body, 54, y - 43, W - 108, size=9.2, leading=12, color=INK)


def checklist_row(c, y, text):
    c.setFillColor(ICE)
    c.roundRect(38, y - 5, 20, 20, 4, fill=1, stroke=0)
    c.setStrokeColor(BLUE)
    c.rect(44, y + 1, 8, 8, fill=0, stroke=1)
    paragraph(c, text, 70, y + 1, W - 108, size=9.4, leading=12.5, color=INK)


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=A4)
    c.setTitle("Apertura 00:00 de Nueva York - TRADINVERSO")
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
    c.drawString(40, H - 172, "MODELO TEMPORAL - SESIÓN DE LONDRES")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 31)
    c.drawString(40, H - 222, "APERTURA 00:00")
    c.drawString(40, H - 262, "DE NUEVA YORK")
    paragraph(
        c,
        "Una referencia simple para construir el sesgo, esperar la manipulación y ejecutar la expansión con confirmación.",
        40,
        H - 307,
        W - 80,
        size=12,
        leading=17,
        color=Color(1, 1, 1, 0.76),
    )
    labels = [("01", "ABRE"), ("02", "MANIPULA"), ("03", "EXPANDE")]
    box_w = (W - 96) / 3
    for index, (number, label) in enumerate(labels):
        x = 40 + index * (box_w + 8)
        c.setFillColor(NAVY)
        c.setStrokeColor(BLUE)
        c.roundRect(x, H - 455, box_w, 76, 5, fill=1, stroke=1)
        c.setFillColor(SKY)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(x + 14, H - 405, number)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x + 14, H - 432, label)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, 66, "TRADINVERSO")
    c.setFillColor(Color(1, 1, 1, 0.55))
    c.setFont("Helvetica", 8.5)
    c.drawString(40, 49, "Recurso educativo - davidrosell.fx")
    c.showPage()

    # Page 2
    page_base(c, "Apertura 00:00 NY", 2)
    y = section_title(c, "01 - Configuración", "Marca la referencia correctamente", H - 126)
    paragraph(
        c,
        "La línea nace en el precio de apertura de la vela de las 00:00 de Nueva York. Trabaja en 5 minutos y proyecta la referencia hasta la sesión de Londres.",
        38,
        y,
        W - 76,
        size=10.5,
        leading=15,
    )
    note(
        c,
        "Zona horaria",
        "Configura el gráfico en America/New_York. El horario local puede desplazarse cuando cambia el horario de verano.",
        H - 235,
    )
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 17)
    c.drawString(38, H - 335, "Power of 3 ligado al tiempo")
    gap = 12
    card_w = (W - 76 - gap * 2) / 3
    phase(c, 38, H - 495, card_w, "01", "Abre", "La apertura fija el punto desde el que empieza la lectura temporal.")
    phase(c, 38 + card_w + gap, H - 495, card_w, "02", "Manipula", "La primera parte del ciclo puede capturar liquidez hacia un lado.")
    phase(c, 38 + (card_w + gap) * 2, H - 495, card_w, "03", "Expande", "Tras confirmar intención, buscamos el desarrollo hacia el lado contrario.")
    note(
        c,
        "Lectura superior",
        "Cuando esta secuencia aparece con contexto, estás leyendo el Power of 3 de una vela de temporalidad superior.",
        H - 535,
        fill=PAPER,
    )
    note(
        c,
        "Regla",
        "La línea construye contexto. Nunca convierte una posición del precio en una entrada automática.",
        H - 625,
        fill=ICE,
    )
    c.showPage()

    # Page 3
    page_base(c, "Sesgo y entrada", 3)
    y = section_title(c, "02 - Dirección", "Construye el sesgo en Londres", H - 126)
    c.setFillColor(RED)
    c.roundRect(38, y - 105, (W - 88) / 2, 105, 6, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(54, y - 28, "PRECIO SOBRE LA LÍNEA")
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(54, y - 58, "Prioriza ventas")
    paragraph(c, "Espera confirmación bajista.", 54, y - 80, (W - 130) / 2, size=9, color=MUTED)
    x2 = 50 + (W - 88) / 2
    c.setFillColor(GREEN)
    c.roundRect(x2, y - 105, (W - 88) / 2, 105, 6, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x2 + 16, y - 28, "PRECIO BAJO LA LÍNEA")
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(x2 + 16, y - 58, "Prioriza compras")
    paragraph(c, "Espera confirmación alcista.", x2 + 16, y - 80, (W - 130) / 2, size=9, color=MUTED)

    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 17)
    c.drawString(38, H - 350, "Protocolo de entrada")
    rows = [
        ("A", "Esperar Londres", "No anticipes la entrada antes del momento operativo."),
        ("B", "Confirmar intención", "Busca un CISD u otra confirmación objetiva de tu sistema."),
        ("C", "Definir el riesgo", "Stop técnico y riesgo calculado antes de ejecutar."),
        ("D", "Validar el recorrido", "No fuerces 1:2 si una barrera limita el objetivo."),
    ]
    row_y = H - 388
    for letter, action, criterion in rows:
        c.setFillColor(BLUE)
        c.roundRect(38, row_y - 46, 42, 42, 4, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(59, row_y - 30, letter)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(94, row_y - 19, action)
        paragraph(c, criterion, 94, row_y - 36, W - 132, size=8.8, leading=11)
        row_y -= 58

    note(
        c,
        "Ejemplo",
        "Precio sobre la línea en Londres | prioridad ventas | CISD bajista | entrada con stop técnico y recorrido libre.",
        H - 650,
    )
    c.showPage()

    # Page 4
    page_base(c, "Checklist", 4)
    y = section_title(c, "03 - Decisión", "Checklist antes de entrar", H - 126)
    items = [
        "He marcado la apertura de las 00:00 en horario de Nueva York.",
        "Estoy dentro de la sesión que contempla mi plan.",
        "El precio está claramente situado respecto a la referencia.",
        "Mi dirección coincide con el sesgo priorizado.",
        "Tengo una confirmación objetiva, no una intuición.",
        "El stop está colocado en un punto técnico.",
        "Existe recorrido antes de la siguiente barrera relevante.",
        "El riesgo está dentro de mi límite diario.",
        "Acepto perder esta operación sin modificar el plan.",
    ]
    check_y = y - 8
    for item in items:
        checklist_row(c, check_y, item)
        check_y -= 43

    note(
        c,
        "Regla final",
        "La referencia construye el contexto. La confirmación autoriza la entrada. La gestión del riesgo protege el proceso.",
        180,
        fill=ICE,
    )
    paragraph(
        c,
        "Material educativo. No constituye asesoramiento financiero ni garantiza resultados. Haz backtesting y utiliza únicamente un riesgo que puedas asumir.",
        38,
        76,
        W - 76,
        size=8,
        leading=11,
        color=MUTED,
    )
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    build()
