"""Guía del Volume Profile: montañas, valles y cómo usamos el SVP.

Reutiliza el estilo de la guía de los FVG.
"""

import math
from pathlib import Path

from reportlab.lib.colors import Color, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from generate_tipos_fvg_pdf import (
    BLUE, DARK, GREEN, ICE, INK, LINE, LOGO, MUTED, NAVY, PAPER, RED, SKY,
    checklist_row, page_base, page_title, paragraph,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "volume-profile.pdf"
W, H = A4
GRIS = Color(0.62, 0.68, 0.76)

# Perfil de ejemplo: una montaña grande arriba (80), otra más pequeña abajo (52)
# y un valle entre las dos. El POC y el área de valor se calculan como lo hace
# la plataforma: desde el POC se añade cada vez el lado con más volumen hasta
# llegar al 70% del total.
FILAS = list(range(40, 101, 2))


def volumen(precio):
    return (100 * math.exp(-((precio - 80) / 6) ** 2)
            + 45 * math.exp(-((precio - 52) / 5) ** 2) + 1)


VOLUMENES = [volumen(p) for p in FILAS]


def area_de_valor(porcentaje=0.7):
    poc = max(range(len(FILAS)), key=lambda i: VOLUMENES[i])
    bajo = alto = poc
    total = sum(VOLUMENES)
    acumulado = VOLUMENES[poc]
    while acumulado < total * porcentaje:
        arriba = VOLUMENES[alto + 1] if alto + 1 < len(FILAS) else -1
        abajo = VOLUMENES[bajo - 1] if bajo > 0 else -1
        if arriba >= abajo:
            alto += 1
            acumulado += arriba
        else:
            bajo -= 1
            acumulado += abajo
    return poc, bajo, alto


POC, VA_BAJO, VA_ALTO = area_de_valor()
PRECIO_POC = FILAS[POC]
PRECIO_VAL = FILAS[VA_BAJO]
PRECIO_VAH = FILAS[VA_ALTO]


def histograma(c, x_derecha, ancho_max, py, alto_fila, etiquetas=True):
    """Dibuja el perfil hacia la izquierda desde x_derecha."""
    maximo = max(VOLUMENES)
    for i, (precio, vol) in enumerate(zip(FILAS, VOLUMENES)):
        ancho = ancho_max * vol / maximo
        if i == POC:
            color = NAVY
        elif VA_BAJO <= i <= VA_ALTO:
            color = Color(BLUE.red, BLUE.green, BLUE.blue, 0.55)
        else:
            color = GRIS
        c.setFillColor(color)
        c.rect(x_derecha - ancho, py(precio) - alto_fila * 0.42, ancho, alto_fila * 0.84, fill=1, stroke=0)


def anatomia_chart(c, x, y, width, height):
    c.setFillColor(PAPER)
    c.setStrokeColor(LINE)
    c.roundRect(x, y - height, width, height, 7, fill=1, stroke=1)
    pad = 22
    base = y - height + pad
    alto = height - pad * 2

    def py(precio):
        return base + (precio - 38) / 64 * alto

    x_derecha = x + width - 170
    histograma(c, x_derecha, 230, py, alto / 32)

    # Área de valor sombreada a lo ancho.
    c.setFillColor(Color(BLUE.red, BLUE.green, BLUE.blue, 0.06))
    c.rect(x + 16, py(PRECIO_VAL), x_derecha - x - 16, py(PRECIO_VAH) - py(PRECIO_VAL), fill=1, stroke=0)

    for precio, texto, nota, color in (
        (PRECIO_VAH, "VAH", "techo del área de valor", BLUE),
        (PRECIO_POC, "POC", "el precio con más volumen", NAVY),
        (PRECIO_VAL, "VAL", "suelo del área de valor", BLUE),
    ):
        c.setStrokeColor(color)
        c.setLineWidth(1.3 if texto == "POC" else 1)
        c.setDash(5, 3)
        c.line(x + 16, py(precio), x_derecha + 10, py(precio))
        c.setDash()
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x_derecha + 18, py(precio) + 1, texto)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 7.5)
        c.drawString(x_derecha + 18, py(precio) - 10, nota)

    # Montañas y valle.
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(NAVY)
    c.drawString(x + 28, py(86) + 2, "MONTAÑA (NODO DE ALTO VOLUMEN)")
    c.drawString(x + 28, py(52) + 14, "MONTAÑA (NODO DE ALTO VOLUMEN)")
    c.setFillColor(RED)
    c.drawString(x + 28, py(66) - 3, "VALLE (NODO DE BAJO VOLUMEN)")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7.5)
    c.drawString(x + 28, py(86) - 9, "mucha negociación: el precio se frena")
    c.drawString(x + 28, py(52) + 3, "mucha negociación: el precio se frena")
    c.drawString(x + 28, py(66) - 14, "casi nadie negoció: el precio corre")
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(x + 16, y - height + 8, "70% DEL VOLUMEN = ÁREA DE VALOR (EN AZUL)")


# Velas del movimiento del Reel: el precio se frena dentro de la montaña,
# pierde su borde, cruza el valle muy rápido y se frena en la siguiente.
VELAS_VALLE = [
    (80, 82, 84, 78), (82, 79, 83, 77), (79, 81, 82, 76), (81, 78, 83, 77),
    (78, 80, 81, 76), (80, 77, 81, 75),
    (77, 72, 78, 71), (72, 64, 73, 63), (64, 57, 65, 56),
    (57, 55, 58, 53), (55, 56, 57, 52), (56, 53, 57, 51), (53, 55, 56, 52),
]


def montana_valle_chart(c, x, y, width, height):
    c.setFillColor(PAPER)
    c.setStrokeColor(LINE)
    c.roundRect(x, y - height, width, height, 7, fill=1, stroke=1)
    pad = 22
    base = y - height + pad
    alto = height - pad * 2

    def py(precio):
        return base + (precio - 38) / 64 * alto

    x_derecha = x + width - 16
    ancho_perfil = 110
    histograma(c, x_derecha, ancho_perfil, py, alto / 32)

    zona_x = x + 18
    zona_w = width - ancho_perfil - 56
    paso = zona_w / len(VELAS_VALLE)
    ancho = min(10, paso * 0.5)

    def vx(i):
        return zona_x + paso * (i + 0.5)

    # Bandas de las dos montañas y del valle.
    for bajo, alto_b, color in ((75, 85, BLUE), (49, 57, BLUE)):
        c.setFillColor(Color(color.red, color.green, color.blue, 0.07))
        c.rect(zona_x, py(bajo), zona_w, py(alto_b) - py(bajo), fill=1, stroke=0)
    c.setFillColor(Color(RED.red, RED.green, RED.blue, 0.05))
    c.rect(zona_x, py(58), zona_w, py(74) - py(58), fill=1, stroke=0)

    for i, (o, cl, h, l) in enumerate(VELAS_VALLE):
        color = GREEN if cl >= o else RED
        c.setStrokeColor(color)
        c.setFillColor(color)
        c.setLineWidth(1.1)
        c.line(vx(i), py(l), vx(i), py(h))
        abajo = py(min(o, cl))
        c.rect(vx(i) - ancho / 2, abajo, ancho, max(py(max(o, cl)) - abajo, 1.6), fill=1, stroke=0)

    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(NAVY)
    c.drawString(zona_x + 4, py(85) + 5, "1 · DENTRO DE LA MONTAÑA: AÚN NO")
    c.setFillColor(RED)
    c.drawString(vx(8) + 10, py(68), "2 · ENTRA EN EL VALLE: LA SEÑAL")
    c.setFillColor(NAVY)
    c.drawString(vx(5), py(49) - 12, "3 · SIGUIENTE MONTAÑA: SE FRENA")


# Reacciones a los niveles del SVP durante una sesión (VAH 76, POC 70, VAL 62).
VAH_S, POC_S, VAL_S = 76, 70, 62
VELAS_SESION = [
    (70, 73, 74, 69), (73, 75, 77, 72), (75, 72, 76, 71),          # 1 respeta el VAH
    (72, 68, 73, 67), (68, 64, 69, 63), (64, 63, 65, 61),          # baja al VAL
    (63, 66, 67, 62), (66, 70, 71, 65), (70, 74, 75, 69),          # 2 respeta el VAL
    (74, 80, 81, 73), (80, 85, 86, 79),                            # 3 rompe con fuerza
    (85, 81, 86, 80), (81, 78, 82, 76), (78, 83, 84, 77),          # 4 vuelve y lo respeta
    (83, 87, 88, 82),
]


def sesion_chart(c, x, y, width, height):
    c.setFillColor(PAPER)
    c.setStrokeColor(LINE)
    c.roundRect(x, y - height, width, height, 7, fill=1, stroke=1)
    pad = 24
    base = y - height + pad
    alto = height - pad * 2

    def py(precio):
        return base + (precio - 57) / 34 * alto

    zona_x = x + 18
    zona_w = width - 110
    paso = zona_w / len(VELAS_SESION)
    ancho = min(10, paso * 0.5)

    def vx(i):
        return zona_x + paso * (i + 0.5)

    c.setFillColor(Color(BLUE.red, BLUE.green, BLUE.blue, 0.06))
    c.rect(zona_x, py(VAL_S), zona_w, py(VAH_S) - py(VAL_S), fill=1, stroke=0)
    for precio, texto, color in ((VAH_S, "VAH", BLUE), (POC_S, "POC", NAVY), (VAL_S, "VAL", BLUE)):
        c.setStrokeColor(color)
        c.setLineWidth(1.2 if texto == "POC" else 1)
        c.setDash(5, 3)
        c.line(zona_x, py(precio), zona_x + zona_w, py(precio))
        c.setDash()
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(zona_x + zona_w + 8, py(precio) - 3, texto)

    for i, (o, cl, h, l) in enumerate(VELAS_SESION):
        color = GREEN if cl >= o else RED
        c.setStrokeColor(color)
        c.setFillColor(color)
        c.setLineWidth(1.1)
        c.line(vx(i), py(l), vx(i), py(h))
        abajo = py(min(o, cl))
        c.rect(vx(i) - ancho / 2, abajo, ancho, max(py(max(o, cl)) - abajo, 1.6), fill=1, stroke=0)

    def marca(i, n, arriba):
        o, cl, h, l = VELAS_SESION[i]
        cy = py(h) + 12 if arriba else py(l) - 14
        c.setFillColor(DARK)
        c.circle(vx(i), cy, 7, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(vx(i), cy - 3, str(n))

    marca(1, 1, True)
    marca(5, 2, False)
    marca(10, 3, True)
    marca(12, 4, False)
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(zona_x, y - height + 9, "SVP DIARIO · NASDAQ (FUTUROS) · GRÁFICO DE 15 MINUTOS")


def cajas(c, items, yy, alto_caja, tonos=None):
    for indice, (tag, titulo, texto) in enumerate(items):
        tono = tonos[indice] if tonos else BLUE
        c.setFillColor(PAPER)
        c.setStrokeColor(LINE)
        c.roundRect(38, yy - alto_caja, W - 76, alto_caja, 7, fill=1, stroke=1)
        c.setFillColor(tono)
        c.roundRect(38, yy - alto_caja, 104, alto_caja, 7, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawCentredString(90, yy - alto_caja / 2 - 3, tag)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 12.5)
        c.drawString(158, yy - 28, titulo)
        paragraph(c, texto, 158, yy - 47, W - 212, size=9, leading=12.2)
        yy -= alto_caja + 12
    return yy


def nota(c, kicker, titulo, texto, oscuro=True, y0=62, alto=76):
    c.setFillColor(DARK if oscuro else ICE)
    c.roundRect(38, y0, W - 76, alto, 7, fill=1, stroke=0)
    c.setFillColor(SKY if oscuro else BLUE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(54, y0 + alto - 22, kicker)
    c.setFillColor(white if oscuro else INK)
    c.setFont("Helvetica-Bold", 12.5)
    c.drawString(54, y0 + alto - 43, titulo)
    paragraph(c, texto, 54, y0 + alto - 61, W - 108, size=9, leading=12,
              color=Color(1, 1, 1, 0.76) if oscuro else MUTED)


def ajustes_tabla(c, x, y, titulo, filas):
    ancho = (W - 76 - 14) / 2
    c.setFillColor(DARK)
    c.roundRect(x, y - 28, ancho, 28, 6, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(x + 12, y - 18, titulo)
    yy = y - 28
    for i, (ajuste, valor) in enumerate(filas):
        c.setFillColor(PAPER if i % 2 == 0 else white)
        c.setStrokeColor(LINE)
        c.rect(x, yy - 26, ancho, 26, fill=1, stroke=1)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8.3)
        c.drawString(x + 12, yy - 17, ajuste)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 8.6)
        c.drawRightString(x + ancho - 12, yy - 17, valor)
        yy -= 26
    return yy


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=A4)
    c.setTitle("Volume Profile y SVP - TRADINVERSO")
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
    c.drawString(40, H - 170, "VOLUME PROFILE - SVP - POC - VAH - VAL")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 30)
    c.drawString(40, H - 220, "MONTAÑAS Y VALLES")
    c.drawString(40, H - 260, "DEL VOLUMEN")
    c.setFont("Helvetica-Bold", 19)
    c.drawString(40, H - 294, "CÓMO USAMOS EL VOLUME PROFILE")
    paragraph(
        c,
        "Dónde se frena el precio, dónde corre y cómo usamos el SVP en Nasdaq para encontrar puntos de reacción antes de que lleguen.",
        40, H - 338, W - 80, size=11.5, leading=16, color=Color(1, 1, 1, 0.76),
    )
    etiquetas = [("01", "MONTAÑAS Y VALLES"), ("02", "POC, VAH Y VAL"), ("03", "EL SVP EN 15 MIN")]
    box_w = (W - 96) / 3
    for indice, (numero, etiqueta) in enumerate(etiquetas):
        bx = 40 + indice * (box_w + 8)
        c.setFillColor(NAVY)
        c.setStrokeColor(BLUE)
        c.roundRect(bx, H - 470, box_w, 76, 5, fill=1, stroke=1)
        c.setFillColor(SKY)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(bx + 14, H - 420, numero)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawString(bx + 14, H - 447, etiqueta)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, 66, "TRADINVERSO")
    c.setFillColor(Color(1, 1, 1, 0.55))
    c.setFont("Helvetica", 8.5)
    c.drawString(40, 49, "Recurso educativo - davidrosell.fx")
    c.showPage()

    # Página 2 - Qué es
    page_base(c, "Qué es", 2)
    page_title(
        c,
        "01 - Volumen por precio",
        "El volumen tumbado de lado",
        "Las barras de volumen de siempre dicen cuánto se negoció en cada vela. El Volume Profile dice cuánto se negoció en cada precio. Ese cambio te enseña dónde está el mercado a gusto y dónde no.",
    )
    anatomia_chart(c, 38, H - 222, W - 76, 290)
    pasos = [
        ("POC", "El precio donde más volumen se ha negociado. Es el punto de equilibrio del periodo y el precio suele volver a él."),
        ("Área de valor, VAH y VAL", "La zona alrededor del POC donde se concentra el 70% del volumen. Su techo es el VAH y su suelo el VAL. Dentro, el precio está a gusto; fuera, busca otro sitio."),
        ("Montañas y valles", "Una montaña es una zona con mucho volumen: el precio se frena. Un valle es una zona con muy poco: el precio la cruza rápido."),
    ]
    yy = H - 538
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
        yy -= 62
    nota(c, "IDEA CENTRAL", "El volumen no te dice la dirección: te dice dónde reacciona el precio.",
         "Por eso es una ayuda para planificar, no una señal de entrada por sí sola.", y0=50, alto=70)
    c.showPage()

    # Página 3 - Montañas y valles
    page_base(c, "Montañas y valles", 3)
    page_title(
        c,
        "02 - Dónde se frena y dónde corre",
        "Espera a que salga de la montaña",
        "Si el precio está dentro de una montaña, la respuesta no es ni largo ni corto, al menos todavía. La señal llega cuando sale de la montaña y entra en el valle.",
    )
    montana_valle_chart(c, 38, H - 222, W - 76, 270)
    cajas(c, [
        ("MONTAÑA", "Mucha negociación: el precio se frena",
         "Ahí se construyeron grandes posiciones. El mercado se ralentiza para negociar esos precios, y una vela que parece bajista o alcista dentro de la montaña no te dice nada todavía."),
        ("VALLE", "Casi nadie negoció: el precio corre",
         "Cuando el precio entra en un valle, no hay nadie que lo frene. Se mueve rápido hasta la siguiente montaña, que suele ser el objetivo natural del movimiento."),
        ("LECTURA", "La salida de la montaña es la señal",
         "No entras porque el precio esté en la montaña. Entras cuando la abandona y entra en el valle, con la siguiente montaña como referencia para el objetivo."),
    ], H - 506, 78)
    c.showPage()

    # Página 4 - Los dos perfiles
    page_base(c, "Cómo lo configuramos", 4)
    page_title(
        c,
        "03 - Los dos perfiles que usamos",
        "El de la semana y el del día",
        "Usamos dos perfiles en TradingView. El de la semana da referencias amplias; el SVP diario es el que más influye cuando trabajas en 15 minutos, porque se basa en la misma sesión.",
    )
    mitad = (W - 76 - 14) / 2
    yy_a = ajustes_tabla(c, 38, H - 236, "PERFIL SEMANAL (RANGO FIJO)", [
        ("Dónde se marca", "Gráfico diario"),
        ("Desde", "Mismo día de la semana anterior"),
        ("Disposición de filas", "Ticks por fila"),
        ("Tamaño de fila", "5"),
        ("Volumen", "Total"),
        ("Volumen del área de valor", "70%"),
    ])
    ajustes_tabla(c, 38 + mitad + 14, H - 236, "SVP DIARIO (SESSION VOLUME PROFILE)", [
        ("Dónde se usa", "15 minutos, solo Nasdaq"),
        ("Sesiones", "Todas (All)"),
        ("Volumen", "Total"),
        ("Volumen del área de valor", "70%"),
        ("Tamaño de fila", "100"),
        ("Extender POC", "No (demasiado ruido)"),
    ])
    yy = yy_a - 22
    cajas(c, [
        ("SEMANAL", "Referencias lejanas",
         "En el diario, márcalo desde el mismo día de la semana anterior: si hoy es miércoles, desde el miércoles pasado. Sus niveles muchas veces quedan lejos del precio; cuando el precio se acerca, puede reaccionar."),
        ("SVP", "Un perfil por cada sesión de 24 horas",
         "En 15 minutos dibuja un perfil por día y sus niveles se van moviendo durante la sesión. Funciona con el volumen real de futuros: úsalo en el futuro del Nasdaq, no en un CFD."),
        ("LAYOUT", "En 15 minutos, no en 1",
         "Funciona igual en 1 minuto, pero ahí es donde ejecutamos y no queremos más líneas. Lo dejamos en el gráfico de 15 y lo miramos cuando el precio se acerca."),
    ], yy, 84, tonos=[NAVY, BLUE, DARK])
    c.showPage()

    # Página 5 - Cómo lo leemos
    page_base(c, "Cómo lo leemos", 5)
    page_title(
        c,
        "04 - VAH, POC y VAL en la sesión",
        "Puntos donde el precio se da la vuelta",
        "Tratamos el VAH, el POC y el VAL como si fueran el máximo y el mínimo de una sesión: puntos de reversión, o de toma de liquidez y continuación hacia el otro lado.",
    )
    sesion_chart(c, 38, H - 222, W - 76, 250)
    pasos = [
        ("Respeta el VAH", "El precio llega al techo del área de valor y se gira. Ahí no compras: es un punto de reacción."),
        ("Respeta el VAL", "Cae hasta el suelo del área de valor y vuelve a girarse. Dentro del área, el precio está a gusto."),
        ("Lo rompe con fuerza", "Cuando sale del área de valor con fuerza, tiene vía libre hasta el siguiente punto relevante de liquidez."),
        ("Vuelve y lo respeta", "El nivel roto se convierte en referencia: el precio vuelve, lo respeta y continúa."),
    ]
    yy = H - 498
    for indice, (titulo, texto) in enumerate(pasos):
        c.setFillColor(DARK)
        c.circle(51, yy - 11, 11, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(51, yy - 14, str(indice + 1))
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(76, yy - 15, titulo)
        paragraph(c, texto, 76, yy - 31, W - 114, size=9, leading=12)
        yy -= 54
    nota(c, "MONTAÑAS EN EL PERFIL", "Una montaña de volumen también es una zona.",
         "Márcala como tal para buscar el objetivo, colocar el stop o esperar una reacción.", oscuro=False, y0=50, alto=70)
    c.showPage()

    # Página 6 - Su lugar en la operativa
    page_base(c, "Su lugar en la operativa", 6)
    page_title(
        c,
        "05 - Una ayuda más, no la principal",
        "La liquidez manda; el volumen suma",
        "El Volume Profile no es indispensable. Lo usamos pocas veces y nunca solo. Su trabajo es sumar confluencia a los niveles que ya importan.",
    )
    cajas(c, [
        ("PRIMERO", "Los puntos de liquidez",
         "Máximos y mínimos de Asia y de Londres, del día anterior (PDH y PDL) y de la semana anterior (PWH y PWL). Son mucho más importantes que cualquier nivel del perfil."),
        ("DESPUÉS", "VAH, POC y VAL como confluencia",
         "Si un nivel del perfil coincide con un punto de liquidez, la zona gana peso. Si está solo, es una referencia más, no un motivo para entrar."),
        ("PARA QUÉ", "Saber cuándo esperar",
         "Te ayuda a ver si conviene esperar porque el precio puede girarse en un nivel cercano, y a evitar algún stop loss que, sin tenerlo en cuenta, te habrías comido."),
        ("CUÁNDO NO", "Si el nivel queda lejos",
         "Los niveles del perfil semanal muchas veces quedan lejos del precio. Hasta que el precio no se acerca, no influyen en la operación."),
    ], H - 236, 86, tonos=[DARK, BLUE, NAVY, RED])
    nota(c, "REGLA TRADINVERSO", "Primero liquidez, después volumen.",
         "Si tienes que elegir entre un nivel de liquidez y uno del perfil, el de liquidez gana siempre.", y0=50, alto=70)
    c.showPage()

    # Página 7 - Checklist
    page_base(c, "Checklist", 7)
    page_title(
        c,
        "06 - Checklist",
        "Antes de usar el perfil",
        "Repásalo cuando el precio se acerque a un nivel del Volume Profile.",
    )
    items = [
        ("01", "Tengo el SVP diario en el gráfico de 15 minutos del futuro del Nasdaq, no en el de ejecución."),
        ("02", "Sé dónde están el VAH, el POC y el VAL de la sesión, y las montañas cercanas."),
        ("03", "Tengo marcados antes los puntos de liquidez: Asia, Londres, PDH, PDL, PWH y PWL."),
        ("04", "Sé si el precio está dentro de una montaña (esperar) o entrando en un valle (puede correr)."),
        ("05", "El nivel del perfil coincide con un punto de liquidez, o lo tomo solo como referencia."),
        ("06", "Si el precio sale del área de valor con fuerza, no me pongo en contra."),
        ("07", "Uso las montañas para situar el objetivo y el stop, no para entrar sin confirmación."),
        ("08", "Si el nivel queda lejos del precio, no influye todavía en la operación."),
    ]
    yy = H - 245
    for numero, texto in items:
        checklist_row(c, yy, numero, texto)
        yy -= 46
    nota(c, "REGLA FINAL", "El volumen te dice dónde mirar, no cuándo entrar.",
         "La entrada sigue siendo la de tu estrategia, con su confirmación y su riesgo definido.", y0=88, alto=84)
    c.showPage()

    # Página 8 - Siguiente paso
    page_base(c, "Siguiente paso", 8)
    page_title(
        c,
        "07 - Ponlo en práctica",
        "Mira cómo reacciona antes de usarlo",
        "Durante veinte sesiones, apunta cada vez que el precio toque un nivel del perfil: si reaccionó, si lo rompió y si coincidía con un punto de liquidez.",
    )
    campos = [
        ("Nivel tocado", "VAH / POC / VAL / Montaña"),
        ("Coincidía con liquidez", "Sí / No (cuál)"),
        ("Qué hizo el precio", "Reaccionó / Lo rompió"),
        ("Tras romperlo", "Corrió / Volvió y respetó"),
        ("Sesión", "Asia / Londres / Nueva York"),
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
