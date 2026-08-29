from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "tipos-fair-value-gap.pdf"
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
GAP = Color(45 / 255, 137 / 255, 255 / 255, 0.16)


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


# Cada vela en unidades de precio: (apertura, cierre, maximo, minimo).
# La primera y la segunda son iguales en los tres casos: lo que cambia
# es la tercera y lo que el precio hace despues.
ARRANQUE = [
    (10, 20, 24, 8),
    (22, 52, 55, 21),
]

CASOS = {
    "breakaway": {
        "velas": ARRANQUE + [
            (52, 74, 76, 50),
            (74, 88, 91, 72),
            (87, 96, 99, 85),
        ],
        "gap": (24, 50),
        "nota": "El precio no vuelve",
        "marca": (2, "ENTRADA"),
    },
    "clasico": {
        "velas": ARRANQUE + [
            (52, 60, 63, 46),
            (60, 44, 61, 40),
            (44, 32, 45, 28),
            (32, 58, 60, 30),
        ],
        "gap": (24, 46),
        "nota": "Retesteo y envolvente",
        "marca": (5, "ENTRADA"),
    },
    "rechazo": {
        "velas": ARRANQUE + [
            (52, 38, 56, 36),
            (38, 26, 39, 24),
            (26, 14, 27, 12),
        ],
        "gap": (24, 36),
        "nota": "Se invierte: IFVG",
        "marca": (4, "IFVG"),
    },
    "anatomia": {
        "velas": ARRANQUE + [(52, 66, 69, 46)],
        "gap": (24, 46),
        "nota": "",
        "marca": None,
    },
}


def fvg_chart(c, x, y, width, height, caso, numerar=False):
    """Dibuja el hueco y lo que el precio hace despues en cada caso."""
    datos = CASOS[caso]
    velas = datos["velas"]

    c.setFillColor(PAPER)
    c.setStrokeColor(LINE)
    c.roundRect(x, y - height, width, height, 7, fill=1, stroke=1)

    zona_x = x + 22
    zona_w = width - 150
    pad = 34
    alto = height - pad * 2
    base = y - height + pad

    # Cada caso recorre un rango de precio distinto: se escala al suyo para
    # que el grafico llene la caja en vez de quedarse en una franja.
    minimo_visto = min(vela[3] for vela in velas)
    maximo_visto = max(vela[2] for vela in velas)
    margen = (maximo_visto - minimo_visto) * 0.08
    suelo = minimo_visto - margen
    rango = max((maximo_visto + margen) - suelo, 1)

    def py(precio):
        return base + ((precio - suelo) / rango) * alto

    # Banda del desequilibrio, de lado a lado.
    gap_bajo, gap_alto = datos["gap"]
    c.setFillColor(GAP)
    c.rect(zona_x, py(gap_bajo), zona_w, py(gap_alto) - py(gap_bajo), fill=1, stroke=0)
    c.setStrokeColor(BLUE)
    c.setLineWidth(0.7)
    c.setDash(3, 3)
    c.line(zona_x, py(gap_bajo), zona_x + zona_w, py(gap_bajo))
    c.line(zona_x, py(gap_alto), zona_x + zona_w, py(gap_alto))
    c.setDash()
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(zona_x + 4, py(gap_alto) + 4, "FAIR VALUE GAP")

    paso = zona_w / (len(velas) + 0.6)
    ancho = min(14, paso * 0.52)

    for indice, (apertura, cierre, maximo, minimo) in enumerate(velas):
        cx = zona_x + paso * (indice + 0.7)
        alcista = cierre >= apertura
        color = GREEN if alcista else RED
        c.setStrokeColor(color)
        c.setFillColor(color)
        c.setLineWidth(1.3)
        c.line(cx, py(minimo), cx, py(maximo))
        abajo = py(min(apertura, cierre))
        c.rect(cx - ancho / 2, abajo, ancho, max(py(max(apertura, cierre)) - abajo, 2), fill=1, stroke=0)

        if numerar and indice < 3:
            c.setFillColor(MUTED)
            c.setFont("Helvetica-Bold", 8)
            c.drawCentredString(cx, y - height + 12, str(indice + 1))

        marca = datos["marca"]
        if marca and marca[0] == indice:
            c.setFillColor(NAVY)
            c.setFont("Helvetica-Bold", 7.5)
            etiqueta_y = max(y - height + 12, py(minimo) - 18)
            c.drawCentredString(cx, etiqueta_y, marca[1])
            c.setStrokeColor(NAVY)
            c.setLineWidth(0.8)
            c.line(cx, etiqueta_y + 10, cx, py(minimo) - 3)

    if datos["nota"]:
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawString(x + width - 122, y - 40, datos["nota"])


def checklist_row(c, y, number, text):
    c.setFillColor(ICE)
    c.roundRect(38, y - 5, 22, 22, 4, fill=1, stroke=0)
    c.setStrokeColor(BLUE)
    c.rect(45, y + 2, 8, 8, fill=0, stroke=1)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(72, y + 4, number)
    paragraph(c, text, 98, y + 4, W - 136, size=9.2, leading=12, color=INK)


def caso_page(c, page, etiqueta, kicker, titulo, subtitulo, caso, bloques, cierre_titulo, cierre_texto, oscuro=True):
    page_base(c, etiqueta, page)
    page_title(c, kicker, titulo, subtitulo)
    fvg_chart(c, 38, H - 235, W - 76, 200, caso)

    y = H - 455
    for indice, (nombre, texto) in enumerate(bloques):
        c.setFillColor(PAPER)
        c.setStrokeColor(LINE)
        c.roundRect(38, y - 78, W - 76, 78, 7, fill=1, stroke=1)
        c.setFillColor(BLUE)
        c.roundRect(54, y - 36, 30, 24, 5, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(69, y - 29, f"0{indice + 1}")
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(96, y - 29, nombre)
        paragraph(c, texto, 54, y - 50, W - 120, size=9.2, leading=12)
        y -= 92

    fondo = DARK if oscuro else ICE
    c.setFillColor(fondo)
    c.roundRect(38, 88, W - 76, 98, 7, fill=1, stroke=0)
    c.setFillColor(SKY if oscuro else BLUE)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(54, 158, "LA CLAVE")
    c.setFillColor(white if oscuro else INK)
    c.setFont("Helvetica-Bold", 14.5)
    c.drawString(54, 133, cierre_titulo)
    paragraph(
        c,
        cierre_texto,
        54,
        112,
        W - 108,
        size=9.3,
        leading=12.5,
        color=Color(1, 1, 1, 0.76) if oscuro else MUTED,
    )
    c.showPage()


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=A4)
    c.setTitle("Los 3 tipos de fair value gap - TRADINVERSO")
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
    c.drawString(40, H - 170, "FAIR VALUE GAP - CONTINUACIÓN - CONFIRMACIÓN")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 30)
    c.drawString(40, H - 220, "LOS 3 TIPOS DE")
    c.drawString(40, H - 260, "FAIR VALUE GAP")
    c.setFont("Helvetica-Bold", 19)
    c.drawString(40, H - 294, "LA TERCERA VELA ES LA QUE DECIDE")
    paragraph(
        c,
        "Todos se dibujan igual: tres velas y un hueco. Lo que cambia es la fuerza de la tercera vela, y con ella dónde está la entrada.",
        40,
        H - 338,
        W - 80,
        size=11.5,
        leading=16,
        color=Color(1, 1, 1, 0.76),
    )
    etiquetas = [("01", "BREAKAWAY"), ("02", "EL DE SIEMPRE"), ("03", "EL QUE NO VALE")]
    box_w = (W - 96) / 3
    for indice, (numero, etiqueta) in enumerate(etiquetas):
        x = 40 + indice * (box_w + 8)
        c.setFillColor(NAVY)
        c.setStrokeColor(BLUE)
        c.roundRect(x, H - 470, box_w, 76, 5, fill=1, stroke=1)
        c.setFillColor(SKY)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(x + 14, H - 420, numero)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x + 14, H - 447, etiqueta)
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
        "Tres velas y un hueco",
        "El fair value gap es el espacio que la vela del medio deja sin cubrir entre los extremos de la primera y la tercera. Ese hueco es un desequilibrio: precio por el que se pasó sin negociar.",
    )
    fvg_chart(c, 38, H - 240, W - 76, 210, "anatomia", numerar=True)
    c.setFillColor(ICE)
    c.roundRect(38, 262, W - 76, 88, 7, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(54, 326, "LO QUE CAMBIA")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(54, 303, "El dibujo es idéntico en los tres casos.")
    paragraph(
        c,
        "Lo único que los separa es la fuerza de la tercera vela: si empuja a favor, si solo frena o si empuja en contra. De ahí salen tres formas distintas de operarlo.",
        54,
        283,
        W - 108,
        size=9.2,
        leading=12,
    )
    c.setFillColor(DARK)
    c.roundRect(38, 108, W - 76, 130, 7, fill=1, stroke=0)
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(54, 210, "ANTES DE SEGUIR")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 15.5)
    c.drawString(54, 184, "Dos huecos pegados se trabajan como uno solo.")
    paragraph(
        c,
        "Cuando aparecen dos fair value gaps seguidos, uno encima del otro, se juntan en una única zona en lugar de tratarlos por separado.",
        54,
        162,
        W - 108,
        size=9.5,
        leading=13,
        color=Color(1, 1, 1, 0.76),
    )
    c.showPage()

    # Página 3 - Breakaway
    caso_page(
        c,
        3,
        "Breakaway",
        "02 - El primero",
        "Breakaway gap: no te va a esperar",
        "La tercera vela sale disparada a favor del movimiento. Es el hueco con más fuerza de los tres y, la mayoría de las veces, el precio no vuelve a buscarlo.",
        "breakaway",
        [
            ("Cómo se reconoce", "La tercera vela cierra con cuerpo grande en la dirección del hueco. No hay duda ni freno: es continuación pura."),
            ("Dónde está la entrada", "Si vas agresivo, en el propio hueco: sabes que el precio no va a volver. Si vas conservador, deja la orden algo más atrás por si retrocede, asumiendo que puedes quedarte fuera."),
        ],
        "Esperar el retesteo aquí es quedarse fuera.",
        "Es el único de los tres donde la paciencia te cuesta la operación en lugar de protegerte. Todo depende del contexto en el que estés trabajando.",
    )

    # Página 4 - El de siempre
    caso_page(
        c,
        4,
        "El de siempre",
        "03 - El segundo",
        "El fair value gap de toda la vida",
        "La tercera vela frena, pero sin un cuerpo grande en contra. Ni continuación clara ni rechazo. El precio suele volver a retestear el hueco antes de seguir.",
        "clasico",
        [
            ("Cómo se reconoce", "La tercera vela no acompaña con fuerza ni empuja en contra. Es el caso más discrecional de los tres y el que más se ve en el gráfico."),
            ("Dónde está la entrada", "Dejas que el precio vuelva al hueco y esperas. La entrada llega cuando una vela envolvente confirma que ahí ha frenado de verdad."),
        ],
        "Que el precio toque el hueco no es una señal.",
        "Llegar a la zona no confirma nada. La envolvente sí: te cuesta algo de recorrido y te da una invalidación clara detrás de la vela.",
    )

    # Página 5 - El que no vale
    caso_page(
        c,
        5,
        "El que no vale",
        "04 - El tercero",
        "Cuando la tercera vela rechaza",
        "El hueco se dibuja igual, pero la tercera vela cierra con cuerpo en contra. Eso avisa de que no hay continuación detrás del movimiento.",
        "rechazo",
        [
            ("Cómo se reconoce", "Vela de rechazo justo encima del hueco, con cuerpo claro en el sentido opuesto. El desequilibrio existe, pero nadie lo está defendiendo."),
            ("Qué se hace con él", "No se opera a favor. Se espera: cuando el precio lo atraviesa y lo cierra en contra, ese hueco se invierte y se convierte en un inverse fair value gap que sí da entrada en la otra dirección."),
        ],
        "El fallo de un hueco es la señal del siguiente.",
        "Un fair value gap roto no es una zona muerta: pasa a ser una referencia invertida y, con contexto, una entrada en continuación en el sentido contrario.",
    )

    # Página 6 - La regla
    page_base(c, "La regla", 6)
    page_title(
        c,
        "05 - Ejecución",
        "Nunca entres en límite",
        "Es la parte que más se repite y la que más caro sale. Dejar la orden puesta en el hueco es cómodo, pero no hay nada que confirme que el precio vaya a frenar ahí.",
    )
    items = [
        ("01", "He identificado cuál de los tres casos tengo delante antes de pensar en entrar."),
        ("02", "He mirado la tercera vela: fuerza a favor, freno o cuerpo en contra."),
        ("03", "El hueco encaja con el contexto y la dirección en la que ya estaba trabajando."),
        ("04", "Si es el de siempre, he esperado el retesteo y no he entrado al tocar la zona."),
        ("05", "Tengo una vela envolvente que confirma el freno, no solo el precio en la zona."),
        ("06", "Si son dos huecos pegados, los estoy trabajando como una sola zona."),
        ("07", "La invalidación está definida antes de ejecutar, no después."),
        ("08", "Acepto perder algo de ratio a cambio de entrar con confirmación."),
        ("09", "Si el hueco se rompe en contra, lo dejo ir y busco la inversión en vez de insistir."),
    ]
    y = H - 245
    for numero, texto in items:
        checklist_row(c, y, numero, texto)
        y -= 44
    c.setFillColor(DARK)
    c.roundRect(38, 88, W - 76, 88, 7, fill=1, stroke=0)
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(54, 148, "REGLA FINAL")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(54, 124, "Sin envolvente, no hay entrada.")
    paragraph(
        c,
        "Perder una operación por esperar cuesta menos que entrar en una zona que todavía no ha demostrado nada.",
        54,
        104,
        W - 108,
        size=9.2,
        leading=12,
        color=Color(1, 1, 1, 0.76),
    )
    c.showPage()

    # Página 7 - Integración
    page_base(c, "Tu proceso", 7)
    page_title(
        c,
        "06 - Integración",
        "Convierte la lectura en datos",
        "Distinguir los tres casos solo sirve si después compruebas cuál de ellos te funciona a ti. Registra el tipo de hueco en cada operación y en veinte trades tendrás la respuesta.",
    )
    campos = [
        ("Tipo de hueco", "Breakaway / Clásico / Rechazado"),
        ("Tercera vela", "A favor / Freno / En contra"),
        ("Entrada", "Directa / Envolvente / Inversión"),
        ("Contexto", "Zona y dirección de trabajo"),
        ("Resultado", "R y calidad de ejecución"),
        ("Aprendizaje", "Qué repetir o corregir"),
    ]
    y = H - 245
    for etiqueta, pista in campos:
        c.setFillColor(PAPER)
        c.setStrokeColor(LINE)
        c.roundRect(38, y - 43, W - 76, 43, 5, fill=1, stroke=1)
        c.setFillColor(BLUE)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(52, y - 26, etiqueta.upper())
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8.5)
        c.drawRightString(W - 52, y - 26, pista)
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
