from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
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
PAPER = HexColor("#F5F9FF")


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


def paragraph(c, text, x, y, width, size=10.5, leading=15, color=MUTED, font="Helvetica"):
    c.setFillColor(color)
    c.setFont(font, size)
    for line in wrap(text, font, size, width):
        c.drawString(x, y, line)
        y -= leading
    return y


def header(c, label, page):
    c.setFillColor(white)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.drawImage(str(LOGO), 38, H - 82, width=50, height=50, preserveAspectRatio=True, mask="auto")
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(101, H - 53, "TRADINVERSO")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(101, H - 67, "TRADING CON DATA E IA")
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 8)
    c.drawRightString(W - 38, H - 57, label.upper())
    c.setStrokeColor(LINE)
    c.line(38, H - 92, W - 38, H - 92)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawRightString(W - 38, 28, f"{page:02d}")


def title_block(c, title, subtitle):
    c.setFillColor(DARK)
    c.roundRect(38, H - 270, W - 76, 148, 6, fill=1, stroke=0)
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(62, H - 151, "GUÍA OPERATIVA")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 30)
    c.drawString(62, H - 193, title)
    paragraph(c, subtitle, 62, H - 222, W - 124, size=11, leading=16, color=Color(1, 1, 1, 0.76))


def phase_card(c, x, y, width, number, title, body):
    c.setFillColor(PAPER)
    c.setStrokeColor(LINE)
    c.roundRect(x, y, width, 132, 6, fill=1, stroke=1)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x + 16, y + 106, number)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(x + 16, y + 80, title)
    paragraph(c, body, x + 16, y + 58, width - 32, size=9.3, leading=13)


def fact_row(c, x, y, label, value, width):
    c.setStrokeColor(LINE)
    c.line(x, y - 8, x + width, y - 8)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8.5)
    c.drawString(x, y + 8, label)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawRightString(x + width, y + 8, value)


def checklist(c, x, y, items, width):
    for item in items:
        c.setFillColor(ICE)
        c.setStrokeColor(LINE)
        c.roundRect(x, y - 4, 18, 18, 4, fill=1, stroke=0)
        paragraph(c, item, x + 29, y + 1, width - 29, size=9.5, leading=13, color=INK)
        y -= 42


def footer_note(c):
    c.setFillColor(DARK)
    c.roundRect(38, 50, W - 76, 58, 6, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(54, 84, "RECUERDA")
    paragraph(
        c,
        "Contenido educativo. Define siempre el riesgo antes de entrar. Ningún modelo garantiza resultados.",
        54,
        68,
        W - 108,
        size=8.5,
        leading=12,
        color=Color(1, 1, 1, 0.75),
    )


def build_amd(path):
    c = canvas.Canvas(str(path), pagesize=A4)
    c.setTitle("AMD + IFVG - Guía operativa TRADINVERSO")

    header(c, "AMD + IFVG", 1)
    title_block(
        c,
        "AMD + IFVG",
        "De la acumulación a la distribución usando la inversión de un Fair Value Gap como confirmación.",
    )
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(38, H - 305, "La secuencia en cuatro fases")
    gap = 14
    card_w = (W - 76 - gap) / 2
    phase_card(c, 38, H - 465, card_w, "01", "Acumulación", "El precio construye un rango antes de la sesión y concentra liquidez en sus extremos.")
    phase_card(c, 38 + card_w + gap, H - 465, card_w, "02", "Manipulación", "La apertura barre un nivel relevante. En el ejemplo, el máximo de Londres.")
    phase_card(c, 38, H - 615, card_w, "03", "Creación del IFVG", "Un FVG alcista se rompe en sentido contrario y el cierre aporta confirmación bajista.")
    phase_card(c, 38 + card_w + gap, H - 615, card_w, "04", "Distribución", "El precio acepta la nueva dirección y desarrolla el desplazamiento hacia el objetivo.")
    footer_note(c)
    c.showPage()

    header(c, "AMD + IFVG", 2)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 25)
    c.drawString(38, H - 138, "Desglose de la entrada")
    paragraph(c, "Datos tomados del ejemplo explicado en el vídeo.", 38, H - 162, W - 76)

    facts_y = H - 215
    facts = [
        ("Contexto", "Acumulación previa"),
        ("Liquidez", "Máximo de Londres"),
        ("Confirmación", "Cierre a través del IFVG"),
        ("Protección", "IFVG + vela envolvente"),
        ("Objetivo", "50% del ORB"),
        ("Relación mostrada", "1,7R"),
    ]
    for label, value in facts:
        fact_row(c, 38, facts_y, label, value, W - 76)
        facts_y -= 48

    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(38, H - 520, "Checklist antes de ejecutar")
    checklist(
        c,
        38,
        H - 565,
        [
            "¿Existe una acumulación reconocible antes de la sesión?",
            "¿La manipulación barre liquidez en un nivel con sentido?",
            "¿El precio ha cerrado a través del FVG en dirección contraria?",
            "¿La invalidación y el objetivo están definidos antes de entrar?",
        ],
        W - 76,
    )
    footer_note(c)
    c.save()


def build_orb(path):
    c = canvas.Canvas(str(path), pagesize=A4)
    c.setTitle("ORB Nasdaq - Guía operativa TRADINVERSO")

    header(c, "ORB NASDAQ", 1)
    title_block(
        c,
        "ORB NASDAQ",
        "Una lectura del rango inicial de la Apertura de Nueva York para esperar ruptura, confirmación y una entrada con riesgo definido.",
    )
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(38, H - 305, "El modelo en tres decisiones")
    phase_card(c, 38, H - 465, 160, "01", "Marca el rango", "Señala el máximo y el mínimo de los primeros cinco minutos de la sesión.")
    phase_card(c, 217, H - 465, 160, "02", "Espera", "La ruptura aislada no basta. Busca aceptación, rechazo o retroceso.")
    phase_card(c, 396, H - 465, 160, "03", "Ejecuta", "Entra solo si hay confirmación, invalidación clara y recorrido suficiente.")

    c.setFillColor(ICE)
    c.roundRect(38, H - 620, W - 76, 118, 6, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(56, H - 532, "IDEA CENTRAL")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(56, H - 558, "No persigas la primera ruptura")
    paragraph(
        c,
        "El ORB ofrece una referencia, no una orden automática. El retroceso a un FVG o una vela de confirmación puede separar una ruptura con intención de un movimiento impulsivo sin continuidad.",
        56,
        H - 580,
        W - 112,
        size=9.5,
        leading=13,
    )
    footer_note(c)
    c.showPage()

    header(c, "ORB NASDAQ", 2)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 25)
    c.drawString(38, H - 138, "Mapa rápido de la operación")
    paragraph(c, "Repásalo antes de la apertura y descarta la entrada si faltan filtros.", 38, H - 162, W - 76)

    c.setFillColor(PAPER)
    c.setStrokeColor(LINE)
    c.roundRect(38, H - 415, W - 76, 210, 6, fill=1, stroke=1)
    facts = [
        ("Rango", "Primeros 5 minutos"),
        ("Señal", "Ruptura + confirmación"),
        ("Entrada", "Retroceso al FVG"),
        ("Invalida", "Tras la estructura protegida"),
        ("Objetivo", "Liquidez o nivel de sesión"),
    ]
    y = H - 245
    for label, value in facts:
        fact_row(c, 56, y, label, value, W - 112)
        y -= 36

    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(38, H - 465, "Checklist ORB")
    checklist(
        c,
        38,
        H - 510,
        [
            "¿Está marcado correctamente el rango de apertura?",
            "¿La ruptura muestra intención y no solo una mecha?",
            "¿Existe retroceso o confirmación antes de entrar?",
            "¿El stop responde a estructura y el objetivo ofrece recorrido?",
            "¿La entrada sigue vigente o el precio ya se ha escapado?",
        ],
        W - 76,
    )
    footer_note(c)
    c.save()


def main():
    amd_path = ROOT / "recursos" / "amd-ifvg" / "guia-amd-ifvg.pdf"
    orb_path = ROOT / "recursos" / "orb-nasdaq" / "guia-orb-nasdaq.pdf"
    build_amd(amd_path)
    build_orb(orb_path)
    print(amd_path)
    print(orb_path)


if __name__ == "__main__":
    main()
