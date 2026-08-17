from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "mechas-velas.pdf"
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


def candle(c, x, open_y, close_y, high_y, low_y, bullish, width=10):
    """Vela pequeña para los gráficos de contexto."""
    color = GREEN if bullish else RED
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.4)
    c.line(x + width / 2, low_y, x + width / 2, high_y)
    bottom = min(open_y, close_y)
    height = max(abs(close_y - open_y), 3)
    c.rect(x, bottom, width, height, fill=1, stroke=0)


def anatomy_diagram(c, x, y, width, height):
    """Vela grande anotada: mecha superior, cuerpo y mecha inferior."""
    c.setFillColor(PAPER)
    c.setStrokeColor(LINE)
    c.roundRect(x, y - height, width, height, 7, fill=1, stroke=1)

    cx = x + 92
    body_w = 34
    low_y = y - height + 34
    open_y = low_y + 44
    close_y = open_y + 104
    high_y = close_y + 36

    c.setStrokeColor(GREEN)
    c.setFillColor(GREEN)
    c.setLineWidth(2.6)
    c.line(cx, low_y, cx, high_y)
    c.rect(cx - body_w / 2, open_y, body_w, close_y - open_y, fill=1, stroke=0)

    label_x = cx + 74
    annotations = [
        ((high_y + close_y) / 2, "MECHA SUPERIOR", "Hasta aquí llegó el precio, pero no se quedó ahí."),
        ((close_y + open_y) / 2, "CUERPO", "El recorrido real: de la apertura al cierre."),
        ((open_y + low_y) / 2, "MECHA INFERIOR", "El extremo de abajo que también fue rechazado."),
    ]
    c.setLineWidth(0.9)
    for line_y, title, text in annotations:
        c.setStrokeColor(BLUE)
        c.setDash(2, 2)
        c.line(cx + body_w / 2 + 8, line_y, label_x - 10, line_y)
        c.setDash()
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawString(label_x, line_y + 4, title)
        paragraph(c, text, label_x, line_y - 9, width - (label_x - x) - 20, size=8.6, leading=11)

    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", 7)
    c.drawRightString(cx - body_w / 2 - 8, high_y - 2, "MÁXIMO")
    c.drawRightString(cx - body_w / 2 - 8, close_y - 2, "CIERRE")
    c.drawRightString(cx - body_w / 2 - 8, open_y - 2, "APERTURA")
    c.drawRightString(cx - body_w / 2 - 8, low_y - 2, "MÍNIMO")


def zone_chart(c, x, y, width, height, support=True):
    """El precio llega a una zona relevante y deja una mecha de rechazo."""
    c.setFillColor(PAPER)
    c.setStrokeColor(LINE)
    c.roundRect(x, y - height, width, height, 7, fill=1, stroke=1)

    zone_y = y - height + 62 if support else y - 62
    c.setStrokeColor(BLUE)
    c.setLineWidth(1.2)
    c.setDash(4, 3)
    c.line(x + 18, zone_y, x + width - 150, zone_y)
    c.setDash()
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(x + 20, zone_y + (7 if support else -14), "SOPORTE" if support else "RESISTENCIA")

    xs = [x + 54, x + 88, x + 122, x + 156, x + 190]
    if support:
        # El precio cae hacia el soporte y la última vela lo perfora y se recupera.
        values = [
            (zone_y + 78, zone_y + 58, zone_y + 86, zone_y + 50, False),
            (zone_y + 58, zone_y + 38, zone_y + 64, zone_y + 30, False),
            (zone_y + 38, zone_y + 20, zone_y + 44, zone_y + 12, False),
            (zone_y + 20, zone_y + 44, zone_y + 50, zone_y - 26, True),
            (zone_y + 44, zone_y + 74, zone_y + 82, zone_y + 38, True),
        ]
    else:
        # El precio sube hacia la resistencia y la última vela la perfora y se gira.
        values = [
            (zone_y - 78, zone_y - 58, zone_y - 50, zone_y - 86, True),
            (zone_y - 58, zone_y - 38, zone_y - 30, zone_y - 64, True),
            (zone_y - 38, zone_y - 20, zone_y - 12, zone_y - 44, True),
            (zone_y - 20, zone_y - 44, zone_y + 26, zone_y - 50, False),
            (zone_y - 44, zone_y - 74, zone_y - 38, zone_y - 82, False),
        ]
    for px, values_for_candle in zip(xs, values):
        candle(c, px, *values_for_candle)

    tone = GREEN if support else RED
    c.setFillColor(tone)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x + width - 138, y - 34, "BUSCAS COMPRA" if support else "BUSCAS VENTA")
    paragraph(
        c,
        "La mecha perfora el nivel, recoge los stops y el precio vuelve dentro antes del cierre."
        if support
        else "La mecha supera el nivel, recoge los stops y el precio vuelve dentro antes del cierre.",
        x + width - 138,
        y - 52,
        120,
        size=8,
        leading=10.5,
    )


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
    c.setTitle("Como leer las mechas de las velas - TRADINVERSO")
    c.setAuthor("TRADINVERSO")

    # Portada
    c.setFillColor(DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.rect(0, H - 18, W, 18, fill=1, stroke=0)
    c.setFillColor(white)
    c.roundRect(40, H - 118, 82, 82, 6, fill=1, stroke=0)
    c.drawImage(str(LOGO), 49, H - 109, width=64, height=64, preserveAspectRatio=True, mask="auto")
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, H - 170, "LECTURA DE VELAS - RECHAZO - CONFIRMACIÓN")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 30)
    c.drawString(40, H - 220, "CÓMO LEER LAS")
    c.drawString(40, H - 260, "MECHAS DE LAS VELAS")
    c.setFont("Helvetica-Bold", 19)
    c.drawString(40, H - 294, "QUIÉN TIENE EL CONTROL DEL MERCADO")
    paragraph(
        c,
        "Qué significa una mecha larga arriba o abajo, por qué solo importa cuando aparece en una zona relevante y cómo usarla para confirmar una entrada.",
        40,
        H - 338,
        W - 80,
        size=11.5,
        leading=16,
        color=Color(1, 1, 1, 0.76),
    )
    labels = [("01", "ZONA"), ("02", "RECHAZO"), ("03", "EJECUCIÓN")]
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

    # Página 2 - Anatomía
    page_base(c, "Anatomía", 2)
    page_title(
        c,
        "01 - Qué estás mirando",
        "La mecha es el precio que no aguantó",
        "Cada vela guarda cuatro datos: apertura, máximo, mínimo y cierre. El cuerpo enseña el recorrido real; las mechas enseñan hasta dónde se intentó llegar y no se pudo sostener.",
    )
    anatomy_diagram(c, 38, H - 240, W - 76, 230)
    c.setFillColor(ICE)
    c.roundRect(38, 250, W - 76, 82, 7, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(54, 308, "PROPORCIÓN")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 12.5)
    c.drawString(54, 286, "Lo que importa es la mecha comparada con el cuerpo.")
    paragraph(
        c,
        "Una mecha corta es ruido normal. Una mecha que mide varias veces el cuerpo indica que ese extremo fue rechazado con fuerza.",
        54,
        266,
        W - 108,
        size=9,
        leading=12,
    )
    c.setFillColor(DARK)
    c.roundRect(38, 108, W - 76, 118, 7, fill=1, stroke=0)
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(54, 198, "EL CASO CONTRARIO")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 15.5)
    c.drawString(54, 172, "Una vela sin mechas no tuvo discusión.")
    paragraph(
        c,
        "Si la apertura y el cierre coinciden con el máximo y el mínimo, nadie puso a prueba ningún extremo: un lado tuvo el control durante todo el periodo.",
        54,
        150,
        W - 108,
        size=9.5,
        leading=13,
        color=Color(1, 1, 1, 0.76),
    )
    c.showPage()

    # Página 3 - Las dos lecturas
    page_base(c, "Las dos lecturas", 3)
    page_title(
        c,
        "02 - Quién ganó la pelea",
        "Arriba y abajo se leen al revés",
        "La mecha señala el lado que perdió. Si sobresale por abajo, los vendedores no aguantaron. Si sobresale por arriba, fueron los compradores los que se quedaron sin fuerza.",
    )
    readings = [
        (
            GREEN,
            "MECHA LARGA ABAJO",
            "Ganaron los compradores",
            "Durante un tiempo los vendedores tuvieron el control y hundieron el precio. Después entraron los compradores con más fuerza y lo devolvieron arriba antes de que la vela cerrara.",
            "Señal de posible giro alcista.",
        ),
        (
            RED,
            "MECHA LARGA ARRIBA",
            "Ganaron los vendedores",
            "El precio subió con fuerza, pero los vendedores entraron y lo devolvieron abajo con más fuerza todavía. Es resistencia a la compra: los compradores están perdiendo fuelle.",
            "Señal de posible giro bajista.",
        ),
    ]
    y = H - 240
    for tone, tag, title, text, footer in readings:
        c.setFillColor(PAPER)
        c.setStrokeColor(LINE)
        c.roundRect(38, y - 170, W - 76, 170, 7, fill=1, stroke=1)
        c.setFillColor(tone)
        c.roundRect(38, y - 170, 6, 170, 3, fill=1, stroke=0)
        c.setFillColor(tone)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(62, y - 32, tag)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 17)
        c.drawString(62, y - 58, title)
        paragraph(c, text, 62, y - 82, W - 240, size=9.4, leading=12.6)
        c.setFillColor(tone)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(62, y - 146, footer)

        # Vela de ejemplo a la derecha: el cuerpo se aparta del lado de la mecha larga.
        cx = W - 108
        if tone is GREEN:
            high_y, close_y, open_y, low_y = y - 32, y - 46, y - 92, y - 156
        else:
            high_y, open_y, close_y, low_y = y - 32, y - 96, y - 142, y - 156
        c.setStrokeColor(tone)
        c.setFillColor(tone)
        c.setLineWidth(2.4)
        c.line(cx, low_y, cx, high_y)
        bottom = min(open_y, close_y)
        c.rect(cx - 13, bottom, 26, abs(close_y - open_y), fill=1, stroke=0)
        y -= 186

    c.setFillColor(ICE)
    c.roundRect(38, 132, W - 76, 82, 7, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(54, 190, "ANTES DE LEERLA")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 12.5)
    c.drawString(54, 168, "La vela tiene que haber cerrado.")
    paragraph(
        c,
        "Mientras la vela sigue abierta, eso que parece una mecha larga puede acabar convertido en cuerpo. Sin cierre no hay lectura.",
        54,
        148,
        W - 108,
        size=9,
        leading=12,
    )
    c.showPage()

    # Página 4 - Dónde importa
    page_base(c, "Dónde importa", 4)
    page_title(
        c,
        "03 - La clave",
        "Una mecha en mitad de la nada no dice nada",
        "El gráfico está lleno de mechas largas y la mayoría son ruido. Lo que convierte una mecha en información es el sitio donde aparece.",
    )
    zones = [
        ("SOPORTE", "Soportes y resistencias marcados", "Niveles que el precio ya respetó antes. Una mecha de rechazo ahí confirma que el nivel sigue defendido."),
        ("LIQUIDEZ", "Máximos y mínimos de referencia", "El extremo del día anterior o de la sesión. Si el precio los barre y deja mecha, ha ido a por los stops y se ha dado la vuelta."),
        ("TU MODELO", "Zonas donde ya esperabas reacción", "El rango de apertura, el rango asiático, un FVG. La mecha te confirma que la reacción llegó."),
    ]
    tones = [BLUE, HexColor("#1F6FD6"), NAVY]
    y = H - 240
    for (tag, title, text), tone in zip(zones, tones):
        c.setFillColor(PAPER)
        c.setStrokeColor(LINE)
        c.roundRect(38, y - 92, W - 76, 92, 7, fill=1, stroke=1)
        c.setFillColor(tone)
        c.roundRect(38, y - 92, 104, 92, 7, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(90, y - 50, tag)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(160, y - 38, title)
        paragraph(c, text, 160, y - 58, W - 220, size=9.4, leading=12.6)
        y -= 108

    c.setFillColor(DARK)
    c.roundRect(38, 110, W - 76, 132, 7, fill=1, stroke=0)
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(54, 214, "EL EJEMPLO DE SIEMPRE")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 15.5)
    c.drawString(54, 186, "Estás en un soporte y aparece una mecha de rechazo.")
    paragraph(
        c,
        "Ahí sí tienes contexto para ejecutar tu entrada: el nivel te dice dónde mirar y la mecha te dice que en ese nivel hubo pelea y quién la ganó. La misma mecha a mitad de camino no te aporta nada.",
        54,
        162,
        W - 108,
        size=9.5,
        leading=13,
        color=Color(1, 1, 1, 0.76),
    )
    c.showPage()

    # Página 5 - Compra y venta
    page_base(c, "Compra y venta", 5)
    page_title(
        c,
        "04 - Lectura direccional",
        "La mecha en la zona, en los dos sentidos",
        "En un soporte buscamos la mecha que perfora por abajo y vuelve dentro. En una resistencia, la que supera por arriba y vuelve dentro. La dirección la marca el lado del rechazo.",
    )
    zone_chart(c, 38, H - 235, W - 76, 200, support=True)
    zone_chart(c, 38, H - 455, W - 76, 200, support=False)
    c.setFillColor(DARK)
    c.roundRect(38, 78, W - 76, 92, 7, fill=1, stroke=0)
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(54, 142, "NO ANTICIPES")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 12.5)
    c.drawString(54, 118, "Si el precio se queda fuera del nivel, no hubo rechazo.")
    paragraph(
        c,
        "Una mecha que perfora y no recupera la zona no es un giro: es una ruptura. Esperar también es parte del modelo.",
        54,
        98,
        W - 108,
        size=9,
        leading=12,
        color=Color(1, 1, 1, 0.72),
    )
    c.showPage()

    # Página 6 - Checklist
    page_base(c, "Ejecución", 6)
    page_title(
        c,
        "05 - Checklist",
        "Antes de ejecutar",
        "Marca cada condición. Si falta la zona, el cierre de la vela o la invalidación, todavía no hay una operación completa.",
    )
    items = [
        ("01", "La zona estaba marcada antes de que el precio llegara a ella."),
        ("02", "Es una zona con peso: soporte, resistencia o liquidez de referencia."),
        ("03", "La vela ha cerrado. No estoy leyendo una mecha a medio formar."),
        ("04", "La mecha es claramente más larga que el cuerpo de la vela."),
        ("05", "El rechazo va en el sentido que mi modelo esperaba en esa zona."),
        ("06", "El stop está al otro lado de la mecha, no dentro de ella."),
        ("07", "El objetivo ofrece como mínimo una relación riesgo-beneficio de 1:1."),
        ("08", "No estoy entrando solo porque la mecha me parece bonita."),
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
    c.drawString(54, 126, "La mecha no es la señal. Es la confirmación.")
    paragraph(
        c,
        "Es una ayuda más dentro de un modelo con reglas, no un modelo por sí sola.",
        54,
        106,
        W - 108,
        size=9,
    )
    c.showPage()

    # Página 7 - Integración
    page_base(c, "Tu proceso", 7)
    page_title(
        c,
        "06 - Integración",
        "Convierte la lectura en datos",
        "La mecha de rechazo es una confirmación más dentro del sistema TRADINVERSO. Su valor aparece cuando se ejecuta con reglas y se registra operación a operación.",
    )
    fields = [
        ("Zona", "Soporte / Resistencia / Liquidez"),
        ("Tipo de mecha", "Superior / Inferior"),
        ("Proporción", "Mecha frente a cuerpo"),
        ("Temporalidad", "Contexto y ejecución"),
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
    c.drawString(54, 177, "Accede a la clase gratuita")
    paragraph(
        c,
        "Una estrategia sencilla que te dice dónde comprar, dónde vender y cuándo no operar.",
        54,
        151,
        W - 108,
        size=10,
        leading=14,
        color=Color(1, 1, 1, 0.76),
    )
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(54, 116, "CLASE.TRADINVERSO.COM")
    c.showPage()

    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    build()
