"""Guía del ORB en tres temporalidades. Reutiliza el estilo de la guía de los FVG."""

from pathlib import Path

from reportlab.lib.colors import Color, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from generate_tipos_fvg_pdf import (
    BLUE, DARK, GREEN, ICE, INK, LINE, LOGO, MUTED, NAVY, PAPER, RED, SKY,
    checklist_row, page_base, page_title, paragraph,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "orb-temporalidades.pdf"
W, H = A4

# Velas de 5 minutos desde las 9:30 (apertura, cierre, máximo, mínimo).
# Sobre el mismo gráfico se dibujan los tres rangos: la primera vela (5 min),
# las tres primeras (15 min) y las seis primeras (30 min).
VELAS = [
    (50, 55, 57, 48),   # 9:30
    (55, 58, 60, 53),   # 9:35
    (58, 49, 59, 45),   # 9:40
    (49, 46, 50, 42),   # 9:45
    (46, 54, 55, 44),   # 9:50
    (54, 59, 63, 53),   # 9:55
    (59, 68, 69, 58),   # 10:00
    (68, 65, 70, 63),   # 10:05
    (65, 72, 74, 64),   # 10:10
    (72, 77, 79, 71),   # 10:15
    (77, 75, 80, 73),   # 10:20
    (75, 81, 83, 74),   # 10:25
]
HORAS = ["9:30", "9:35", "9:40", "9:45", "9:50", "9:55", "10:00", "10:05", "10:10", "10:15", "10:20", "10:25"]

# (velas que forman el rango, etiqueta, color)
RANGOS = [
    (6, "VELA DE 30 MIN", NAVY),
    (3, "VELA DE 15 MIN", BLUE),
    (1, "VELA DE 5 MIN", GREEN),
]

CONFIGURACIONES = [
    {
        "vela": "30 MIN",
        "rango": "9:30 - 10:00",
        "ejecucion": "5 minutos",
        "titulo": "Vela de 30 minutos, ejecución en 5",
        "texto": "El rango se forma con la primera media hora de Nueva York. Es el más amplio y el más tranquilo, y se puede operar de dos formas: la ruptura, como siempre, o el rechazo.",
        "color": NAVY,
    },
    {
        "vela": "15 MIN",
        "rango": "9:30 - 9:45",
        "ejecucion": "1 o 5 minutos",
        "titulo": "Vela de 15 minutos, ejecución en 1 o en 5",
        "texto": "El punto intermedio. El rango se cierra a las 9:45 y puedes ejecutar en 5 minutos para ir más tranquilo o en 1 minuto para afinar la entrada.",
        "color": BLUE,
    },
    {
        "vela": "5 MIN",
        "rango": "9:30 - 9:35",
        "ejecucion": "1 minuto",
        "titulo": "Vela de 5 minutos, ejecución en 1",
        "texto": "La que usamos en TRADINVERSO. El rango está listo a las 9:35 y la ejecución en 1 minuto permite entradas precisas, pero exige estar delante de la pantalla en la apertura.",
        "color": GREEN,
    },
]


# Vela de 30: las seis primeras velas de 5 minutos forman el rango (máximo 70,
# mínimo 50). Después, o el precio rompe y se acepta fuera (ruptura) o sale,
# no se acepta y vuelve dentro (rechazo).
RANGO_30 = [
    (58, 62, 64, 55),
    (62, 56, 63, 52),
    (56, 66, 68, 55),
    (66, 60, 67, 50),
    (60, 67, 70, 59),
    (67, 63, 68, 61),
]
CASOS_30 = {
    "ruptura": {
        "velas": RANGO_30 + [
            (63, 72, 73, 62),
            (72, 81, 82, 71),
            (81, 79, 83, 77),
            (79, 76, 80, 75),
            (76, 84, 85, 75),
            (84, 90, 91, 83),
        ],
        "fvg": (73, 77, 7),
        "entrada": 77,
        "stop": 69,
        "objetivo": 93,
        "marca": (7, "RUPTURA"),
        "nota": "COMPRA EN EL FVG",
        "compra": True,
    },
    "rechazo": {
        "velas": RANGO_30 + [
            (68, 73, 75, 67),
            (73, 62, 74, 61),
            (62, 58, 64, 56),
            (58, 65, 66, 57),
            (65, 57, 66, 55),
            (57, 48, 58, 46),
            (48, 44, 50, 42),
        ],
        "fvg": (64, 67, 7),
        "entrada": 64,
        "stop": 76,
        "objetivo": 40,
        "marca": (6, "RECHAZO"),
        "nota": "VENTA EN EL FVG",
        "compra": False,
    },
}


def vela30_chart(c, x, y, width, height, caso):
    datos = CASOS_30[caso]
    velas = datos["velas"]
    c.setFillColor(PAPER)
    c.setStrokeColor(LINE)
    c.roundRect(x, y - height, width, height, 7, fill=1, stroke=1)

    zona_x = x + 14
    zona_w = width - 92
    pad_top, pad_bottom = 18, 26
    alto = height - pad_top - pad_bottom
    base = y - height + pad_bottom
    precios = [v[2] for v in velas] + [v[3] for v in velas] + [datos["stop"], datos["objetivo"]]
    suelo = min(precios) - 2
    rango = max(precios) + 2 - suelo

    def py(precio):
        return base + ((precio - suelo) / rango) * alto

    paso = zona_w / len(velas)
    ancho = min(9, paso * 0.5)

    def vx(indice):
        return zona_x + paso * (indice + 0.5)

    # Rango de la vela de 30.
    x1 = zona_x + paso * 6
    c.setFillColor(Color(NAVY.red, NAVY.green, NAVY.blue, 0.07))
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.1)
    c.rect(zona_x + 2, py(50), x1 - zona_x - 4, py(70) - py(50), fill=1, stroke=1)
    c.setDash(3, 3)
    c.setLineWidth(0.8)
    for nivel in (70, 50):
        c.line(x1, py(nivel), zona_x + zona_w, py(nivel))
    c.setDash()
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 6.5)
    c.drawString(zona_x + 4, py(50) - 10, "RANGO 30 MIN")

    # Fair value gap.
    bajo_fvg, alto_fvg, desde = datos["fvg"]
    inicio = vx(desde) - paso * 0.5
    c.setFillColor(Color(BLUE.red, BLUE.green, BLUE.blue, 0.18))
    c.rect(inicio, py(bajo_fvg), zona_x + zona_w - inicio, py(alto_fvg) - py(bajo_fvg), fill=1, stroke=0)

    # Entrada, stop y objetivo.
    for precio, texto, color in (
        (datos["entrada"], "ENTRADA FVG", BLUE),
        (datos["stop"], "STOP", RED),
        (datos["objetivo"], "OBJETIVO 2:1", GREEN),
    ):
        c.setStrokeColor(color)
        c.setLineWidth(0.9)
        c.line(inicio, py(precio), zona_x + zona_w, py(precio))
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 6.5)
        c.drawString(zona_x + zona_w + 5, py(precio) - 2.3, texto)

    for indice, (apertura, cierre, alto_v, bajo_v) in enumerate(velas):
        cx = vx(indice)
        color = GREEN if cierre >= apertura else RED
        c.setStrokeColor(color)
        c.setFillColor(color)
        c.setLineWidth(1.1)
        c.line(cx, py(bajo_v), cx, py(alto_v))
        abajo = py(min(apertura, cierre))
        c.rect(cx - ancho / 2, abajo, ancho, max(py(max(apertura, cierre)) - abajo, 2), fill=1, stroke=0)

    indice, texto = datos["marca"]
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 7)
    c.drawRightString(vx(indice) - 7, py(velas[indice][2]) - 3, texto)

    c.setFillColor(GREEN if datos["compra"] else RED)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawRightString(x + width - 10, y - height + 9, datos["nota"])


def rangos_chart(c, x, y, width, height):
    c.setFillColor(PAPER)
    c.setStrokeColor(LINE)
    c.roundRect(x, y - height, width, height, 7, fill=1, stroke=1)

    zona_x = x + 18
    zona_w = width - 150
    pad_top, pad_bottom = 22, 34
    alto = height - pad_top - pad_bottom
    base = y - height + pad_bottom
    minimo = min(v[3] for v in VELAS)
    maximo = max(v[2] for v in VELAS)
    margen = (maximo - minimo) * 0.08
    suelo = minimo - margen
    rango = (maximo + margen) - suelo

    def py(precio):
        return base + ((precio - suelo) / rango) * alto

    paso = zona_w / len(VELAS)
    ancho = min(12, paso * 0.5)

    def vx(indice):
        return zona_x + paso * (indice + 0.5)

    # Los tres rangos, del más grande al más pequeño.
    etiqueta_y = []
    for n, etiqueta, color in RANGOS:
        alto_r = max(v[2] for v in VELAS[:n])
        bajo_r = min(v[3] for v in VELAS[:n])
        x0 = zona_x + 2
        x1 = zona_x + paso * n - 2
        c.setFillColor(Color(color.red, color.green, color.blue, 0.08))
        c.setStrokeColor(color)
        c.setLineWidth(1.2)
        c.rect(x0, py(bajo_r), x1 - x0, py(alto_r) - py(bajo_r), fill=1, stroke=1)
        # Máximo y mínimo del rango prolongados a la derecha.
        c.setDash(3, 3)
        c.setLineWidth(0.8)
        for nivel in (alto_r, bajo_r):
            c.line(x1, py(nivel), zona_x + zona_w, py(nivel))
        c.setDash()
        etiqueta_y.append((py(alto_r), etiqueta, color))

    # Etiquetas a la derecha, separadas para que no se pisen.
    ultima = None
    for ty, etiqueta, color in sorted(etiqueta_y, reverse=True):
        if ultima is not None and ultima - ty < 13:
            ty = ultima - 13
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(zona_x + zona_w + 8, ty - 2.5, etiqueta)
        ultima = ty

    for indice, (apertura, cierre, alto_v, bajo_v) in enumerate(VELAS):
        cx = vx(indice)
        color = GREEN if cierre >= apertura else RED
        c.setStrokeColor(color)
        c.setFillColor(color)
        c.setLineWidth(1.2)
        c.line(cx, py(bajo_v), cx, py(alto_v))
        abajo = py(min(apertura, cierre))
        c.rect(cx - ancho / 2, abajo, ancho, max(py(max(apertura, cierre)) - abajo, 2), fill=1, stroke=0)

    c.setFillColor(MUTED)
    c.setFont("Helvetica", 6.8)
    for indice, hora in enumerate(HORAS):
        if indice % 3 == 0:
            c.drawCentredString(vx(indice), y - height + 14, hora)


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=A4)
    c.setTitle("El ORB en 3 temporalidades - TRADINVERSO")
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
    c.drawString(40, H - 170, "APERTURA DE NUEVA YORK - 9:30 - NASDAQ")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 30)
    c.drawString(40, H - 220, "EL ORB EN 3")
    c.drawString(40, H - 260, "TEMPORALIDADES")
    c.setFont("Helvetica-Bold", 19)
    c.drawString(40, H - 294, "LA MISMA ESTRATEGIA, TU HORARIO")
    paragraph(
        c,
        "Vela de 30, de 15 o de 5 minutos. Cambia el tamaño del rango y la temporalidad en la que ejecutas; las entradas y las reglas son exactamente las mismas.",
        40, H - 338, W - 80, size=11.5, leading=16, color=Color(1, 1, 1, 0.76),
    )
    box_w = (W - 96) / 3
    for indice, config in enumerate(CONFIGURACIONES):
        bx = 40 + indice * (box_w + 8)
        c.setFillColor(NAVY)
        c.setStrokeColor(BLUE)
        c.roundRect(bx, H - 470, box_w, 76, 5, fill=1, stroke=1)
        c.setFillColor(SKY)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(bx + 14, H - 420, f"VELA DE {config['vela']}")
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawString(bx + 14, H - 447, f"Ejecución en {config['ejecucion']}")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, 66, "TRADINVERSO")
    c.setFillColor(Color(1, 1, 1, 0.55))
    c.setFont("Helvetica", 8.5)
    c.drawString(40, 49, "Recurso educativo - davidrosell.fx")
    c.showPage()

    # Página 2 - La idea
    page_base(c, "La idea", 2)
    page_title(
        c,
        "01 - Un mismo gráfico",
        "Tres formas de marcar el rango",
        "El ORB parte siempre de la apertura de Nueva York a las 9:30 (15:30 en España). Lo único que decides es cuántos minutos de esa apertura usas para marcar el rango.",
    )
    rangos_chart(c, 38, H - 232, W - 76, 250)
    pasos = [
        ("La vela marca el rango", "El máximo y el mínimo de la primera vela de 5, 15 o 30 minutos son tus referencias. Hasta que esa vela no cierra, no hay nada que hacer."),
        ("Cuanto más grande, más tarde", "Un rango de 30 minutos no está listo hasta las 10:00. Uno de 5 minutos está listo a las 9:35. Más espera a cambio de una referencia más amplia."),
        ("La ejecución baja de temporalidad", "Una vez marcado el rango, la entrada se busca en una temporalidad más baja: 5 minutos, 1 minuto o cualquiera de las dos."),
    ]
    yy = H - 510
    for indice, (titulo, texto) in enumerate(pasos):
        c.setFillColor(BLUE)
        c.roundRect(38, yy - 22, 26, 22, 5, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(51, yy - 15, f"0{indice + 1}")
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 12.5)
        c.drawString(76, yy - 15, titulo)
        paragraph(c, texto, 76, yy - 32, W - 114, size=9.2, leading=12)
        yy -= 66
    c.setFillColor(DARK)
    c.roundRect(38, 62, W - 76, 74, 7, fill=1, stroke=0)
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(54, 114, "IDEA CENTRAL")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(54, 94, "Cambia el rango, no la estrategia.")
    paragraph(c, "Las entradas, la confirmación, el stop y el objetivo son los mismos en las tres.",
              54, 76, W - 108, size=9.2, leading=12, color=Color(1, 1, 1, 0.76))
    c.showPage()

    # Página 3 - Las tres configuraciones
    page_base(c, "Las 3 configuraciones", 3)
    page_title(
        c,
        "02 - Elige la tuya",
        "Vela de rango y temporalidad de ejecución",
        "Cada combinación tiene el mismo modelo de entrada. Lo que cambia es a qué hora está listo el rango y en qué gráfico buscas la ejecución.",
    )
    yy = H - 236
    for config in CONFIGURACIONES:
        alto_card = 132
        c.setFillColor(PAPER)
        c.setStrokeColor(LINE)
        c.roundRect(38, yy - alto_card, W - 76, alto_card, 7, fill=1, stroke=1)
        c.setFillColor(config["color"])
        c.roundRect(38, yy - alto_card, 118, alto_card, 7, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(97, yy - 40, "VELA DE")
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(97, yy - 68, config["vela"])
        c.setFont("Helvetica", 8)
        c.drawCentredString(97, yy - 90, config["rango"])
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(174, yy - 30, config["titulo"])
        paragraph(c, config["texto"], 174, yy - 50, W - 230, size=9.2, leading=12.4)
        c.setFillColor(ICE)
        c.roundRect(174, yy - alto_card + 14, 190, 22, 5, fill=1, stroke=0)
        c.setFillColor(BLUE)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(184, yy - alto_card + 22, f"EJECUCIÓN EN {config['ejecucion'].upper()}")
        yy -= alto_card + 16
    c.setFillColor(ICE)
    c.roundRect(38, 62, W - 76, 74, 7, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(54, 114, "CÓMO LO HACEMOS NOSOTROS")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 12.5)
    c.drawString(54, 94, "Vela de 5 minutos y ejecución en 1 minuto.")
    paragraph(c, "Es la configuración del vídeo. Las otras dos funcionan con las mismas reglas.", 54, 76, W - 108, size=9, leading=12)
    c.showPage()

    # Página 4 - Las dos formas de la vela de 30
    page_base(c, "Vela de 30 minutos", 4)
    page_title(
        c,
        "03 - Vela de 30 minutos",
        "Dos formas de operarla",
        "Con el rango de la primera media hora puedes operar la ruptura, igual que siempre, o el rechazo: el precio sale del rango, no se acepta fuera y entras en dirección contraria, hacia dentro del rango.",
    )
    mitad = (W - 76 - 14) / 2
    for indice, (caso, titulo) in enumerate((("ruptura", "01 - LA RUPTURA"), ("rechazo", "02 - EL RECHAZO"))):
        bx = 38 + indice * (mitad + 14)
        c.setFillColor(BLUE)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(bx, H - 236, titulo)
        vela30_chart(c, bx, H - 246, mitad, 250, caso)
    bloques = [
        ("RUPTURA", "Como siempre",
         "El precio rompe el máximo o el mínimo y se acepta fuera del rango. Esperas el retroceso al FVG en 5 minutos y entras a favor de la ruptura."),
        ("RECHAZO", "Al lado contrario",
         "El precio sale del rango pero no se acepta fuera: vuelve a entrar con fuerza y deja un FVG en dirección contraria. Entras en el retesteo de ese FVG, hacia dentro del rango."),
        ("RIESGO", "Stop y objetivo",
         "En el rechazo, el stop va por encima del extremo que hizo el precio fuera del rango (por debajo, si el rechazo es en el mínimo). El objetivo, al menos 2:1."),
    ]
    yy = H - 512
    for tag, titulo, texto in bloques:
        c.setFillColor(PAPER)
        c.setStrokeColor(LINE)
        c.roundRect(38, yy - 70, W - 76, 70, 7, fill=1, stroke=1)
        c.setFillColor(BLUE)
        c.roundRect(54, yy - 34, 86, 22, 5, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(97, yy - 26, tag)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(154, yy - 27, titulo)
        paragraph(c, texto, 154, yy - 44, W - 210, size=8.8, leading=11.6)
        yy -= 78
    c.setFillColor(DARK)
    c.roundRect(38, 42, W - 76, 50, 7, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11.5)
    c.drawString(54, 72, "Salir del rango no es romperlo.")
    paragraph(c, "Si el precio no se acepta fuera, lo que tienes es un rechazo, y se opera al revés.",
              54, 55, W - 108, size=9, leading=12, color=Color(1, 1, 1, 0.76))
    c.showPage()

    # Página 5 - Lo que no cambia
    page_base(c, "Lo que no cambia", 5)
    page_title(
        c,
        "04 - Las mismas reglas",
        "El modelo de entrada es idéntico",
        "Da igual la vela que elijas: la ruptura se entra igual que en el vídeo. Marca el rango, espera la ruptura con confirmación y ejecuta con el riesgo definido.",
    )
    reglas = [
        ("RANGO", "Marca el máximo y el mínimo", "De la vela que hayas elegido: 5, 15 o 30 minutos desde las 9:30. No marques nada hasta que la vela haya cerrado."),
        ("SEÑAL", "Ruptura con confirmación", "La ruptura aislada no basta. Necesitas que el precio demuestre intención: aceptación fuera del rango, no solo una mecha."),
        ("ENTRADA", "Retroceso al FVG", "En tu temporalidad de ejecución, esperas el retroceso al fair value gap que deja la ruptura y entras con confirmación."),
        ("STOP", "Detrás de la estructura protegida", "La invalidación está donde la idea deja de tener sentido, no a una distancia fija."),
        ("OBJETIVO", "Liquidez o nivel de sesión", "Máximos y mínimos sin tocar o niveles de la sesión. Si no hay recorrido suficiente, no hay operación."),
    ]
    yy = H - 236
    for tag, titulo, texto in reglas:
        c.setFillColor(PAPER)
        c.setStrokeColor(LINE)
        c.roundRect(38, yy - 82, W - 76, 82, 7, fill=1, stroke=1)
        c.setFillColor(BLUE)
        c.roundRect(54, yy - 36, 86, 22, 5, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(97, yy - 28, tag)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 12.5)
        c.drawString(154, yy - 29, titulo)
        paragraph(c, texto, 154, yy - 48, W - 210, size=9, leading=12)
        yy -= 94
    c.setFillColor(DARK)
    c.roundRect(38, 62, W - 76, 74, 7, fill=1, stroke=0)
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(54, 114, "NO PERSIGAS LA PRIMERA RUPTURA")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 12.5)
    c.drawString(54, 94, "El ORB te da una referencia, no una orden automática.")
    paragraph(c, "Sin confirmación no hay entrada, sea cual sea la temporalidad.",
              54, 76, W - 108, size=9, leading=12, color=Color(1, 1, 1, 0.76))
    c.showPage()

    # Página 6 - Cómo elegir
    page_base(c, "Cómo elegir", 6)
    page_title(
        c,
        "05 - Encaja la estrategia en tu día",
        "Qué cambia al elegir una u otra",
        "No hay una configuración mejor que otra: hay una que encaja con tu horario, con tu experiencia y con cuánto tiempo puedes estar delante de la pantalla.",
    )
    filas = [
        ("", "Vela de 30", "Vela de 15", "Vela de 5"),
        ("Rango listo a las", "10:00", "9:45", "9:35"),
        ("Ejecución", "5 minutos", "1 o 5 minutos", "1 minuto"),
        ("Tamaño del rango", "El más amplio", "Intermedio", "El más estrecho"),
        ("Stop", "Más amplio", "Intermedio", "Más ajustado"),
        ("Ritmo", "Más tiempo para decidir", "Equilibrado", "Exige reacción rápida"),
    ]
    col_x = [38, 178, 300, 422]
    col_w = [140, 122, 122, W - 38 - 422]
    yy = H - 240
    for indice, fila in enumerate(filas):
        alto_f = 34
        if indice == 0:
            c.setFillColor(DARK)
        else:
            c.setFillColor(PAPER if indice % 2 else white)
        c.setStrokeColor(LINE)
        c.rect(38, yy - alto_f, W - 76, alto_f, fill=1, stroke=1)
        for col, texto in enumerate(fila):
            if indice == 0:
                c.setFillColor(white)
                c.setFont("Helvetica-Bold", 9.5)
            elif col == 0:
                c.setFillColor(BLUE)
                c.setFont("Helvetica-Bold", 8.5)
            else:
                c.setFillColor(INK)
                c.setFont("Helvetica", 9)
            c.drawString(col_x[col] + 12, yy - 21, texto)
        yy -= alto_f
    consejos = [
        ("Elige una y no la cambies a mitad de sesión", "Si hoy marcas la vela de 15, no pases a la de 5 porque la de 15 todavía no ha roto. Eso es buscar una entrada, no seguir un plan."),
        ("Si estás empezando, ve más despacio", "La vela de 30 con ejecución en 5 te da más tiempo para leer el gráfico y cometer menos errores de ejecución."),
        ("Mide la tuya", "Haz backtesting de la configuración que elijas antes de arriesgar dinero. Los datos te dirán si encaja contigo."),
    ]
    yy -= 26
    for titulo, texto in consejos:
        c.setFillColor(BLUE)
        c.circle(46, yy - 10, 3.5, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 11.5)
        c.drawString(58, yy - 14, titulo)
        paragraph(c, texto, 58, yy - 30, W - 96, size=9.2, leading=12)
        yy -= 64
    c.setFillColor(ICE)
    c.roundRect(38, 62, W - 76, 84, 7, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(54, 124, "PLANTILLA GRATUITA")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 12.5)
    c.drawString(54, 103, "Mide tu configuración con la plantilla de backtesting del ORB.")
    paragraph(c, "La tienes en la biblioteca: tradinversoacademy.github.io/recursos", 54, 84, W - 108, size=9, leading=12)
    c.showPage()

    # Página 7 - Checklist
    page_base(c, "Checklist", 7)
    page_title(
        c,
        "06 - Checklist",
        "Antes de la apertura",
        "Repásalo cada día antes de las 9:30. Si falta la confirmación, el stop o el objetivo, todavía no hay operación.",
    )
    items = [
        ("01", "He decidido antes de la apertura qué vela de rango voy a usar: 5, 15 o 30 minutos."),
        ("02", "Sé en qué temporalidad voy a ejecutar y no la voy a cambiar durante la sesión."),
        ("03", "He esperado a que cierre la vela de rango antes de marcar el máximo y el mínimo."),
        ("04", "La ruptura muestra intención: aceptación fuera del rango, no solo una mecha."),
        ("05", "Con la vela de 30, si opero el rechazo: el precio ha vuelto dentro del rango y ha dejado un FVG en contra."),
        ("06", "Hay retroceso al fair value gap y confirmación en mi temporalidad de ejecución."),
        ("07", "El stop está detrás de la estructura protegida."),
        ("08", "El objetivo es liquidez o un nivel de sesión con recorrido suficiente."),
        ("09", "Si el precio ya se ha escapado, no persigo la entrada."),
        ("10", "Registro la operación con la configuración que he usado."),
    ]
    yy = H - 245
    for numero, texto in items:
        checklist_row(c, yy, numero, texto)
        yy -= 42
    c.setFillColor(DARK)
    c.roundRect(38, 88, W - 76, 84, 7, fill=1, stroke=0)
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(54, 146, "REGLA FINAL")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 13.5)
    c.drawString(54, 122, "La temporalidad la eliges tú. Las reglas, no.")
    paragraph(c, "Una estrategia se vuelve rentable cuando la ejecutas igual cada día, no cuando la adaptas a cada apertura.",
              54, 102, W - 108, size=9.2, leading=12, color=Color(1, 1, 1, 0.76))
    c.showPage()

    # Página 8 - Siguiente paso
    page_base(c, "Tu proceso", 8)
    page_title(
        c,
        "07 - Integración",
        "Convierte tu configuración en datos",
        "Registra cada apertura con la vela de rango que has usado. En veinte sesiones sabrás si tu configuración encaja contigo o si necesitas otra.",
    )
    campos = [
        ("Vela de rango", "5 / 15 / 30 minutos"),
        ("Ejecución", "1 / 5 minutos"),
        ("Tipo de entrada", "Ruptura / Rechazo (vela de 30)"),
        ("Confirmación", "Retroceso al FVG / Sin confirmación"),
        ("Resultado", "R y si llegó al objetivo"),
        ("Aprendizaje", "Qué repetir o corregir"),
    ]
    yy = H - 245
    for etiqueta, pista in campos:
        c.setFillColor(PAPER)
        c.setStrokeColor(LINE)
        c.roundRect(38, yy - 43, W - 76, 43, 5, fill=1, stroke=1)
        c.setFillColor(BLUE)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(52, yy - 26, etiqueta.upper())
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8.5)
        c.drawRightString(W - 52, yy - 26, pista)
        yy -= 56
    c.setFillColor(DARK)
    c.roundRect(38, 88, W - 76, 148, 7, fill=1, stroke=0)
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(54, 207, "SIGUIENTE PASO")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(54, 177, "Accede a la clase gratuita")
    paragraph(c, "Una estrategia sencilla que te dice dónde comprar, dónde vender y cuándo no operar.",
              54, 151, W - 108, size=10, leading=14, color=Color(1, 1, 1, 0.76))
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(54, 116, "CLASE.TRADINVERSO.COM")
    c.showPage()

    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    build()
