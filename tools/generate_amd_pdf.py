from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "guia-amd-tradinverso.pdf"
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

RANGO_URL = "https://tradinversoacademy.github.io/recursos/recursos/rango-asiatico/"
AMD_IFVG_URL = "https://tradinversoacademy.github.io/recursos/recursos/amd-ifvg/"


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


def session_card(c, y, tag, session, title, body):
    c.setFillColor(PAPER)
    c.setStrokeColor(LINE)
    c.roundRect(38, y - 118, W - 76, 118, 7, fill=1, stroke=1)
    c.setFillColor(BLUE)
    c.roundRect(54, y - 42, 74, 26, 5, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 9.5)
    c.drawCentredString(91, y - 34, session)
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(140, y - 33, tag)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(54, y - 68, title)
    paragraph(c, body, 54, y - 88, W - 130, size=9.3, leading=12.5, color=MUTED)


def confirmation_card(c, x, y, w, number, title, body):
    c.setFillColor(PAPER)
    c.setStrokeColor(LINE)
    c.roundRect(x, y - 172, w, 172, 7, fill=1, stroke=1)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x + 16, y - 30, number)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 13.5)
    c.drawString(x + 16, y - 52, title)
    paragraph(c, body, x + 16, y - 72, w - 32, size=8.8, leading=11.8, color=MUTED)


def check_item(c, y, number, text):
    c.setFillColor(ICE)
    c.roundRect(38, y - 5, 20, 20, 4, fill=1, stroke=0)
    c.setStrokeColor(BLUE)
    c.rect(44, y + 1, 8, 8, fill=0, stroke=1)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(70, y + 3, number)
    paragraph(c, text, 95, y + 3, W - 133, size=9.2, leading=12, color=INK)


def video_row(c, y, kicker, title, body, url):
    c.setFillColor(PAPER)
    c.setStrokeColor(LINE)
    c.roundRect(38, y - 96, W - 76, 96, 7, fill=1, stroke=1)
    c.setFillColor(DARK)
    c.roundRect(54, y - 78, 96, 58, 5, fill=1, stroke=0)
    c.setFillColor(white)
    play = c.beginPath()
    play.moveTo(94, y - 59)
    play.lineTo(94, y - 39)
    play.lineTo(112, y - 49)
    play.close()
    c.drawPath(play, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(168, y - 28, kicker.upper())
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(168, y - 46, title)
    paragraph(c, body, 168, y - 62, W - 226, size=8.8, leading=11.5, color=MUTED)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(168, y - 86, "VER EL VIDEO  >")
    c.linkURL(url, (38, y - 96, W - 38, y), relative=0)


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=A4)
    c.setTitle("AMD: acumulación, manipulación y distribución - TRADINVERSO")
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
    c.drawString(40, H - 170, "EL CICLO DE LAS SESIONES")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 31)
    c.drawString(40, H - 220, "AMD: ACUMULACIÓN,")
    c.drawString(40, H - 260, "MANIPULACIÓN Y DISTRIBUCIÓN")
    paragraph(
        c,
        "Cada sesión tiene un propósito. Asia construye el rango, Londres captura la liquidez y Nueva York da el movimiento real del día. Predecible, sistemático y repetible.",
        40,
        H - 306,
        W - 80,
        size=12,
        leading=17,
        color=Color(1, 1, 1, 0.76),
    )
    labels = [("ASIA", "ACUMULA"), ("LONDRES", "MANIPULA"), ("NUEVA YORK", "DISTRIBUYE")]
    box_w = (W - 96) / 3
    for index, (session, label) in enumerate(labels):
        x = 40 + index * (box_w + 8)
        c.setFillColor(NAVY)
        c.setStrokeColor(BLUE)
        c.roundRect(x, H - 455, box_w, 76, 5, fill=1, stroke=1)
        c.setFillColor(SKY)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(x + 14, H - 405, session)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawString(x + 14, H - 432, label)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, 66, "TRADINVERSO")
    c.setFillColor(Color(1, 1, 1, 0.55))
    c.setFont("Helvetica", 8.5)
    c.drawString(40, 49, "Recurso educativo - davidrosell.fx")
    c.showPage()

    # Page 2 - El ciclo
    page_base(c, "El ciclo", 2)
    page_title(
        c,
        "01 - Tres sesiones, tres propósitos",
        "Así se construye el día",
        "El mercado repite la misma secuencia sesión tras sesión. Entender qué hace cada una te dice qué esperar y, sobre todo, qué no anticipar.",
    )
    session_card(
        c,
        H - 225,
        "FASE DE ACUMULACIÓN",
        "ASIA",
        "Abre y consolida",
        "Asia no hace grandes movimientos. Construye un rango acumulando órdenes entre un máximo y un mínimo. Esos dos extremos concentran la liquidez que usará la siguiente sesión.",
    )
    session_card(
        c,
        H - 365,
        "FASE DE MANIPULACIÓN",
        "LONDRES",
        "Barre el rango y captura liquidez",
        "Cuando abre Londres, barre el máximo o el mínimo de Asia para capturar la liquidez acumulada. Esa barrida crea el combustible del movimiento real y prepara la expansión.",
    )
    session_card(
        c,
        H - 505,
        "FASE DE DISTRIBUCIÓN",
        "NUEVA YORK",
        "El movimiento direccional del día",
        "Con la liquidez capturada y la intención confirmada, Nueva York distribuye. Ahí ocurre el verdadero desplazamiento direccional que buscamos operar.",
    )
    c.setFillColor(DARK)
    c.roundRect(38, H - 716, W - 76, 82, 7, fill=1, stroke=0)
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(54, H - 661, "IDEA CENTRAL")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(54, H - 686, "La manipulación no es la entrada. Es la señal.")
    paragraph(c, "Te dice dónde puede empezar el movimiento real. La entrada llega después, con confirmación.", 54, H - 706, W - 108, size=9.3, leading=12, color=Color(1, 1, 1, 0.76))
    c.showPage()

    # Page 3 - La señal
    page_base(c, "La señal", 3)
    page_title(
        c,
        "02 - Leer la manipulación",
        "De la barrida a la señal",
        "No todas las rupturas del rango asiático son una manipulación. Buscamos una secuencia concreta antes de plantear cualquier escenario.",
    )
    steps = [
        ("01", "Marca el rango de Asia", "Traza el máximo y el mínimo de la sesión asiática. Son tus dos referencias de liquidez para el resto del día."),
        ("02", "Espera la barrida", "Londres debe atravesar uno de los extremos y capturar la liquidez. Una simple llegada al nivel no es una señal."),
        ("03", "Exige el rechazo", "Tras la barrida, el precio debe mostrar rechazo y volver hacia el interior del rango. Si sigue desplazándose sin recuperar, no hay manipulación: hay expansión en contra."),
        ("04", "Plantea el escenario", "Con la manipulación confirmada, el sesgo apunta al lado contrario de la barrida. Ahora toca esperar la confirmación de entrada."),
    ]
    y = H - 230
    for number, title, body in steps:
        c.setFillColor(BLUE)
        c.roundRect(38, y - 8, 30, 24, 5, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawCentredString(53, y, number)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(84, y, title)
        y = paragraph(c, body, 84, y - 17, W - 140, size=9.3, leading=12.5) - 24
    c.setFillColor(ICE)
    c.roundRect(38, y - 66, W - 76, 74, 7, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(54, y - 18, "REGLA TRADINVERSO")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 13.5)
    c.drawString(54, y - 40, "Sin manipulación no hay señal. Sin confirmación no hay entrada.")
    paragraph(c, "La barrida plantea el escenario; solo la confirmación permite ejecutarlo con invalidación clara.", 54, y - 58, W - 108, size=9)
    c.showPage()

    # Page 4 - Confirmaciones
    page_base(c, "Confirmaciones", 4)
    page_title(
        c,
        "03 - Las confirmaciones que ejecuto",
        "La entrada llega con la confirmación",
        "Después de la manipulación, espera a que el precio demuestre el cambio de intención en temporalidad baja. Estas son las confirmaciones que uso en este modelo.",
    )
    card_w = (W - 100) / 3
    confirmation_card(
        c,
        38,
        H - 225,
        card_w,
        "01",
        "IFVG",
        "Se forma un Fair Value Gap y el precio lo atraviesa en sentido contrario. Cuando cierra al otro lado, el desequilibrio queda invertido y confirma el cambio de intención.",
    )
    confirmation_card(
        c,
        38 + card_w + 12,
        H - 225,
        card_w,
        "02",
        "CISD",
        "Cambio en la entrega del precio: tras la barrida, el precio recupera estructura y empieza a entregarse en la dirección contraria a la manipulación.",
    )
    confirmation_card(
        c,
        38 + (card_w + 12) * 2,
        H - 225,
        card_w,
        "03",
        "Vela envolvente",
        "Una envolvente con desplazamiento tras la toma de liquidez valida el rechazo del nivel y deja una invalidación técnica clara.",
    )
    c.setFillColor(PAPER)
    c.setStrokeColor(LINE)
    c.roundRect(38, H - 560, W - 76, 130, 7, fill=1, stroke=1)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(54, H - 455, "GESTIÓN DE LA OPERACIÓN")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 13.5)
    c.drawString(54, H - 477, "Riesgo definido antes del clic")
    paragraph(
        c,
        "La invalidación va en el punto técnico que anula la idea: el extremo de la manipulación o la zona de la confirmación. Calcula el tamaño con esa distancia y valida que exista recorrido real hacia el objetivo, sin liquidez ni estructura relevante que lo bloquee. Como mínimo, una relación riesgo-beneficio de 1:1.",
        54,
        H - 497,
        W - 130,
        size=9.3,
        leading=12.5,
    )
    c.setFillColor(DARK)
    c.roundRect(38, H - 700, W - 76, 82, 7, fill=1, stroke=0)
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(54, H - 645, "RECUERDA")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(54, H - 670, "Una confirmación objetiva, no una intuición.")
    paragraph(c, "Si tienes que convencerte de que la señal está ahí, no está. La confirmación se ve o no existe.", 54, H - 690, W - 108, size=9.3, leading=12, color=Color(1, 1, 1, 0.76))
    c.showPage()

    # Page 5 - Checklist + vídeos
    page_base(c, "Ejecución", 5)
    page_title(
        c,
        "04 - Checklist y aplicación real",
        "Antes de ejecutar, repasa",
        "Marca cada punto antes de comprometer capital. Si falta uno, la mejor operación puede ser no entrar.",
    )
    items = [
        ("01", "El rango de Asia está marcado: máximo y mínimo."),
        ("02", "Londres ha barrido uno de los extremos y capturado liquidez."),
        ("03", "El precio ha mostrado rechazo tras la barrida."),
        ("04", "Tengo una confirmación objetiva: IFVG, CISD o envolvente."),
        ("05", "La invalidación está en un punto técnico y asumo su riesgo."),
        ("06", "Existe recorrido real hacia el objetivo, mínimo 1:1."),
        ("07", "Acepto perder esta operación sin modificar el plan."),
    ]
    y = H - 240
    for number, text in items:
        check_item(c, y, number, text)
        y -= 40

    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(38, y - 12, "APLICADO EN GRÁFICO — DOS OPERATIVAS REALES")
    video_row(
        c,
        y - 28,
        "Acumulación y manipulación",
        "Manipulación del rango asiático",
        "Cómo leemos el rango de Asia con estructura y contexto, y cómo se manipula antes del movimiento.",
        RANGO_URL,
    )
    video_row(
        c,
        y - 136,
        "Confirmación y distribución",
        "AMD + IFVG en Nasdaq",
        "Sesión real: barrida de liquidez, confirmación con IFVG y distribución hacia el objetivo.",
        AMD_IFVG_URL,
    )
    c.showPage()

    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    build()
