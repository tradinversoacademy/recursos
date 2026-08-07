from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "plan-contrario-trader-rentable.pdf"
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
RED = HexColor("#FFF0F2")
GREEN = HexColor("#EAF8F2")


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


def principle(c, y, number, title, wrong, right, action):
    c.setFillColor(PAPER)
    c.setStrokeColor(LINE)
    c.roundRect(38, y - 142, W - 76, 142, 7, fill=1, stroke=1)
    c.setFillColor(BLUE)
    c.roundRect(54, y - 44, 38, 30, 5, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(73, y - 34, number)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(106, y - 35, title)

    c.setFillColor(RED)
    c.roundRect(54, y - 91, 225, 34, 5, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(65, y - 70, "ERROR CONTRARIO")
    paragraph(c, wrong, 65, y - 83, 203, size=8, leading=10, color=MUTED)

    c.setFillColor(GREEN)
    c.roundRect(291, y - 91, 250, 34, 5, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(302, y - 70, "REGLA RENTABLE")
    paragraph(c, right, 302, y - 83, 228, size=8, leading=10, color=MUTED)

    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(54, y - 113, "ACCIÓN")
    paragraph(c, action, 103, y - 113, W - 157, size=8.6, leading=11, color=INK)


def checklist(c, y, number, text):
    c.setFillColor(ICE)
    c.roundRect(38, y - 5, 20, 20, 4, fill=1, stroke=0)
    c.setStrokeColor(BLUE)
    c.rect(44, y + 1, 8, 8, fill=0, stroke=1)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(70, y + 3, number)
    paragraph(c, text, 95, y + 3, W - 133, size=9.2, leading=12, color=INK)


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=A4)
    c.setTitle("El plan contrario del trader rentable - TRADINVERSO")
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
    c.drawString(40, H - 170, "MENTALIDAD - DISCIPLINA - DATA")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 31)
    c.drawString(40, H - 220, "EL PLAN CONTRARIO")
    c.drawString(40, H - 260, "DEL TRADER RENTABLE")
    paragraph(
        c,
        "10 errores que debes dejar de repetir para ejecutar tu sistema con criterio, control y consistencia.",
        40,
        H - 306,
        W - 80,
        size=12,
        leading=17,
        color=Color(1, 1, 1, 0.76),
    )
    labels = [("01", "PROCESO"), ("02", "DISCIPLINA"), ("03", "RESPONSABILIDAD")]
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
        c.setFont("Helvetica-Bold", 10.5)
        c.drawString(x + 14, H - 432, label)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, 66, "TRADINVERSO")
    c.setFillColor(Color(1, 1, 1, 0.55))
    c.setFont("Helvetica", 8.5)
    c.drawString(40, 49, "Recurso educativo - davidrosell.fx")
    c.showPage()

    # Page 2
    page_base(c, "Mentalidad", 2)
    page_title(
        c,
        "01 - Identidad y expectativas",
        "No necesitas tener razón",
        "Un trader rentable separa su autoestima del resultado de una operación. Su trabajo es ejecutar una ventaja, no demostrar que sabe hacia dónde irá el mercado.",
    )
    principle(c, H - 235, "01", "Busca ganar, no acertar", "Defiende una idea para demostrar que tenía razón.", "Acepta estar equivocado sin romper el plan.", "Antes de entrar, escribe qué invalidaría tu idea y respétalo.")
    principle(c, H - 393, "02", "El plan va antes que el dinero", "Piensa primero en cuánto puede ganar.", "Evalúa primero si la operación cumple el proceso.", "Puntúa la calidad de la ejecución antes de mirar el resultado.")
    principle(c, H - 551, "03", "Un trade no define tu valor", "Mide su capacidad por la última pérdida o ganancia.", "Evalúa series de operaciones y comportamientos.", "Revisa tu sistema cada 20 operaciones, nunca por una sola.")
    c.showPage()

    # Page 3
    page_base(c, "Disciplina", 3)
    page_title(
        c,
        "02 - Proceso repetible",
        "Más disciplina, menos estrategia",
        "Cambiar de sistema no arregla una ejecución impulsiva. Primero necesitas reglas claras, datos fiables y paciencia para repetirlas.",
    )
    principle(c, H - 235, "04", "Disciplina antes que novedad", "Busca otra estrategia cuando atraviesa una mala racha.", "Mantiene reglas estables y corrige la ejecución.", "Durante 20 operaciones no cambies reglas; registra desviaciones.")
    principle(c, H - 393, "05", "Lo anota todo", "Recuerda solo las operaciones que más le impactaron.", "Conoce cuándo gana, cuándo pierde y por qué.", "Registra setup, riesgo, emoción, error y resultado de cada trade.")
    principle(c, H - 551, "06", "Sin setup, no hay trade", "Opera por aburrimiento, miedo a perderse el movimiento o necesidad.", "Acepta días sin operar si no aparece su ventaja.", "Define tres condiciones obligatorias. Si falta una, no ejecutes.")
    c.showPage()

    # Page 4
    page_base(c, "Riesgo y ejecución", 4)
    page_title(
        c,
        "03 - Control operativo",
        "Decide el riesgo antes de hacer clic",
        "La improvisación aparece cuando la operación ya está abierta. El trader rentable deja resueltos tamaño, invalidación y gestión antes de exponerse.",
    )
    principle(c, H - 235, "07", "Siempre conoce su riesgo", "Ajusta el tamaño según la confianza o la necesidad del día.", "Usa un riesgo definido y asumible por operación.", "Calcula tamaño y pérdida máxima antes de colocar la orden.")
    principle(c, H - 393, "08", "Ejecuta y suelta", "Mira el gráfico constantemente y modifica el plan por cada vela.", "Gestiona solo en los puntos previstos por su sistema.", "Define cuándo puedes intervenir y elimina decisiones intermedias.")
    c.setFillColor(ICE)
    c.roundRect(38, H - 650, W - 76, 86, 7, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(54, H - 590, "REGLA DE CONTROL")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(54, H - 616, "Si no puedes asumir el stop, el riesgo es demasiado alto.")
    paragraph(c, "La tranquilidad después de entrar se construye antes de entrar.", 54, H - 637, W - 108, size=9.3)
    c.showPage()

    # Page 5
    page_base(c, "Pérdidas y responsabilidad", 5)
    page_title(
        c,
        "04 - Madurez del trader",
        "Perder deja de dar miedo",
        "No porque desaparezcan las pérdidas, sino porque existe un sistema que las contempla y un riesgo que permite seguir ejecutando.",
    )
    principle(c, H - 235, "09", "Confía en una muestra real", "Evita perder y abandona el sistema tras varios stops.", "Acepta la pérdida prevista dentro de su ventaja.", "Calcula rachas normales y define cuándo revisar el sistema.")
    principle(c, H - 393, "10", "Asume la responsabilidad", "Culpa al mercado, al broker o a la estrategia.", "Busca qué decisión propia puede medir y mejorar.", "Tras cada sesión, separa resultado, ejecución y error.")
    c.setFillColor(DARK)
    c.roundRect(38, H - 665, W - 76, 110, 7, fill=1, stroke=0)
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(54, H - 585, "IDEA CENTRAL")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 17)
    c.drawString(54, H - 614, "El problema no siempre fue el mercado.")
    paragraph(c, "La mejora empieza cuando detectas el error que repites y construyes una regla que lo impida.", 54, H - 638, W - 108, size=10, leading=14, color=Color(1, 1, 1, 0.76))
    c.showPage()

    # Page 6
    page_base(c, "Plan de corrección", 6)
    page_title(
        c,
        "05 - Revisión personal",
        "Tu plan para dejar de operar al contrario",
        "Marca cada afirmación que ya cumples de forma consistente. No la marques por intención: solo cuenta si tus datos lo demuestran.",
    )
    items = [
        ("01", "Acepto la invalidación sin mover el stop para tener razón."),
        ("02", "Evalúo el proceso antes que el resultado económico."),
        ("03", "Una pérdida no cambia mi autoestima ni mi siguiente decisión."),
        ("04", "Mantengo reglas estables durante una muestra suficiente."),
        ("05", "Registro todas mis operaciones y sé dónde está mi ventaja."),
        ("06", "Puedo pasar un día sin operar si mi setup no aparece."),
        ("07", "Conozco el riesgo exacto antes de abrir cada posición."),
        ("08", "No modifico la gestión fuera de los puntos definidos."),
        ("09", "Asumo las pérdidas normales de mi sistema."),
        ("10", "Identifico mis errores sin culpar al mercado."),
    ]
    y = H - 245
    for number, text in items:
        checklist(c, y, number, text)
        y -= 42

    c.setFillColor(DARK)
    c.roundRect(38, 84, W - 76, 84, 7, fill=1, stroke=0)
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(54, 143, "ACCIÓN DE ESTA SEMANA")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(54, 121, "Elige el primer punto que no puedes marcar.")
    paragraph(c, "Convierte ese error en una regla medible y aplícala durante tus próximas 20 operaciones.", 54, 102, W - 108, size=9, leading=12, color=Color(1, 1, 1, 0.75))
    c.showPage()

    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    build()
