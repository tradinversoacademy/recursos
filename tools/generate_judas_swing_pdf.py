"""Guía del Judas Swing. Reutiliza el estilo de la guía de los FVG."""

from pathlib import Path

from reportlab.lib.colors import Color, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from generate_tipos_fvg_pdf import (
    BLUE, DARK, GREEN, ICE, INK, LINE, LOGO, MUTED, NAVY, PAPER, RED, SKY,
    checklist_row, page_base, page_title, paragraph,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "judas-swing.pdf"
W, H = A4

# Velas (apertura, cierre, máximo, mínimo). Antes de las 9:30 el precio deja
# un máximo arriba (el objetivo) y un mínimo de vela abajo. En la apertura
# barre ese mínimo, recoge los stops y se va a por el máximo.
VELAS_COMPRA = [
    (64, 60, 71, 58),
    (60, 55, 62, 53),
    (55, 50, 57, 48),
    (50, 48, 52, 45),
    # 9:30
    (48, 40, 49, 38),
    (40, 36, 42, 33),
    (36, 45, 46, 35),
    (45, 56, 57, 44),
    (56, 64, 66, 55),
    (64, 70, 72, 63),
]
APERTURA = 4       # índice de la primera vela de las 9:30
MINIMO = 45        # el mínimo de vela que se barre
OBJETIVO = 71      # la liquidez del lado contrario
TRAMPA = 5         # vela que marca el extremo de la manipulación
GIRO = 6           # vela que confirma el giro


def espejo(velas):
    """El caso de venta es el de compra dado la vuelta."""
    return [(110 - o, 110 - c, 110 - l, 110 - h) for o, c, h, l in velas]


def judas_chart(c, x, y, width, height, compra=True):
    velas = VELAS_COMPRA if compra else espejo(VELAS_COMPRA)
    nivel = MINIMO if compra else 110 - MINIMO
    objetivo = OBJETIVO if compra else 110 - OBJETIVO

    c.setFillColor(PAPER)
    c.setStrokeColor(LINE)
    c.roundRect(x, y - height, width, height, 7, fill=1, stroke=1)

    zona_x = x + 22
    zona_w = width - 170
    pad = 30
    alto = height - pad * 2
    base = y - height + pad
    minimo = min(v[3] for v in velas)
    maximo = max(v[2] for v in velas)
    margen = (maximo - minimo) * 0.1
    suelo = minimo - margen
    rango = (maximo + margen) - suelo

    def py(precio):
        return base + ((precio - suelo) / rango) * alto

    paso = zona_w / (len(velas) + 0.4)
    ancho = min(13, paso * 0.5)

    def vx(indice):
        return zona_x + paso * (indice + 0.7)

    # Línea vertical de la apertura de Nueva York.
    ax = (vx(APERTURA - 1) + vx(APERTURA)) / 2
    c.setStrokeColor(MUTED)
    c.setLineWidth(0.8)
    c.setDash(2, 3)
    c.line(ax, base - 12, ax, y - 14)
    c.setDash()
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(ax + 5, y - 20, "9:30 APERTURA NY")

    # Niveles: el que se barre y el objetivo.
    for precio, etiqueta, color in (
        (nivel, "MÍNIMO DE VELA" if compra else "MÁXIMO DE VELA", RED if compra else GREEN),
        (objetivo, "OBJETIVO: LIQUIDEZ", BLUE),
    ):
        c.setStrokeColor(color)
        c.setLineWidth(1)
        c.setDash(4, 3)
        c.line(zona_x, py(precio), zona_x + zona_w, py(precio))
        c.setDash()
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(zona_x + zona_w + 6, py(precio) - 2.5, etiqueta)

    for indice, (apertura, cierre, alto_v, bajo_v) in enumerate(velas):
        cx = vx(indice)
        color = GREEN if cierre >= apertura else RED
        c.setStrokeColor(color)
        c.setFillColor(color)
        c.setLineWidth(1.3)
        c.line(cx, py(bajo_v), cx, py(alto_v))
        abajo = py(min(apertura, cierre))
        c.rect(cx - ancho / 2, abajo, ancho, max(py(max(apertura, cierre)) - abajo, 2), fill=1, stroke=0)

    # Marcas de la trampa y del giro.
    def marca(indice, texto, arriba):
        cx = vx(indice)
        apertura, cierre, alto_v, bajo_v = velas[indice]
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 7.5)
        if arriba:
            ty = min(y - 20, py(alto_v) + 14)
            c.drawCentredString(cx, ty, texto)
        else:
            ty = max(y - height + 8, py(bajo_v) - 16)
            c.drawCentredString(cx, ty, texto)

    marca(TRAMPA, "TRAMPA", arriba=not compra)
    marca(GIRO, "GIRO", arriba=compra)

    c.setFillColor(GREEN if compra else RED)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(x + width - 150, y - height + 18, "BUSCAS COMPRA" if compra else "BUSCAS VENTA")


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=A4)
    c.setTitle("El Judas Swing de las 9:30 - TRADINVERSO")
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
    c.drawString(40, H - 170, "APERTURA DE NUEVA YORK - MANIPULACIÓN - GIRO")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 30)
    c.drawString(40, H - 220, "EL JUDAS SWING")
    c.drawString(40, H - 260, "DE LAS 9:30")
    c.setFont("Helvetica-Bold", 19)
    c.drawString(40, H - 294, "LA TRAMPA DE LA APERTURA")
    paragraph(
        c,
        "El mercado te enseña un movimiento para que lo sigas y después se va hacia el lado contrario. Qué mirar, cómo confirmar el giro y cómo operarlo.",
        40, H - 338, W - 80, size=11.5, leading=16, color=Color(1, 1, 1, 0.76),
    )
    etiquetas = [("01", "LA TRAMPA"), ("02", "EL GIRO"), ("03", "EL OBJETIVO")]
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
        "01 - La traición",
        "El primer movimiento te engaña",
        "El nombre viene de Judas Iscariote, el discípulo que traicionó a Jesús. En la apertura pasa lo mismo: el mercado enseña una dirección, hace que todos crean que va a seguir y se va al lado contrario.",
    )
    judas_chart(c, 38, H - 238, W - 76, 230, compra=True)
    pasos = [
        ("El cebo", "A las 9:30 el precio arranca con fuerza hacia un lado. Parece el inicio del movimiento del día."),
        ("Todos entran detrás", "Los que persiguen la ruptura entran a favor y los que ya estaban al otro lado tienen el stop justo ahí."),
        ("Se da la vuelta", "Recoge esos stops y hace el movimiento real hacia el lado contrario."),
    ]
    yy = H - 490
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
        yy -= 64
    c.setFillColor(DARK)
    c.roundRect(38, 70, W - 76, 84, 7, fill=1, stroke=0)
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(54, 130, "IDEA CENTRAL")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 13.5)
    c.drawString(54, 108, "No operes el movimiento de las 9:30: opera lo que viene después.")
    paragraph(c, "La manipulación es la señal. El movimiento real empieza cuando la trampa se cierra.",
              54, 88, W - 108, size=9.2, leading=12, color=Color(1, 1, 1, 0.76))
    c.showPage()

    # Página 3 - Qué mirar
    page_base(c, "Qué mirar", 3)
    page_title(
        c,
        "02 - La lectura",
        "Tres cosas que mirar en la apertura",
        "Reconocer un Judas Swing no depende de adivinar el giro. Depende de saber dónde están los objetivos y cuánto está durando la manipulación.",
    )
    claves = [
        ("OTRO LADO", "Qué hay al otro lado de la manipulación",
         "Da igual que el precio manipule en una zona de temporalidad alta. Lo que importa es lo que queda justo detrás. Si lo único que hay es el mínimo de una vela, ese pudo ser el último sitio al que el mercado necesitaba llegar antes del movimiento real."),
        ("DURACIÓN", "Cuánto dura la manipulación",
         "Una trampa es rápida: recoge los stops y se gira. Si se alarga y el precio sigue desplazándose sin recuperar, ya no es una trampa. Es el movimiento del día y no se opera en contra."),
        ("OBJETIVO", "Dónde está el objetivo",
         "El movimiento real va a por la liquidez del lado contrario: máximos o mínimos que siguen intactos. Cuanto más obvio es el objetivo, más fácil es reconocer hacia dónde quiere ir el mercado."),
    ]
    tonos = [BLUE, NAVY, DARK]
    yy = H - 240
    for (tag, titulo, texto), tono in zip(claves, tonos):
        c.setFillColor(PAPER)
        c.setStrokeColor(LINE)
        c.roundRect(38, yy - 118, W - 76, 118, 7, fill=1, stroke=1)
        c.setFillColor(tono)
        c.roundRect(38, yy - 118, 104, 118, 7, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(90, yy - 63, tag)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 13.5)
        c.drawString(160, yy - 30, titulo)
        paragraph(c, texto, 160, yy - 50, W - 216, size=9.2, leading=12.4)
        yy -= 134
    c.setFillColor(ICE)
    c.roundRect(38, 84, W - 76, 74, 7, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(54, 134, "RESUMEN")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 12.5)
    c.drawString(54, 112, "Objetivo claro + manipulación corta = trampa probable.")
    paragraph(c, "Objetivo difuso o manipulación que no se gira = mejor no tocarlo.", 54, 94, W - 108, size=9, leading=12)
    c.showPage()

    # Página 4 - Compra y venta
    page_base(c, "Compra y venta", 4)
    page_title(
        c,
        "03 - Los dos sentidos",
        "Entras al lado contrario de la trampa",
        "Si la apertura manipula hacia abajo, buscas la compra hacia la liquidez de arriba. Si manipula hacia arriba, buscas la venta hacia la liquidez de abajo.",
    )
    judas_chart(c, 38, H - 232, W - 76, 205, compra=True)
    judas_chart(c, 38, H - 452, W - 76, 205, compra=False)
    c.setFillColor(DARK)
    c.roundRect(38, 70, W - 76, 88, 7, fill=1, stroke=0)
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(54, 134, "NO ANTICIPES")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 12.5)
    c.drawString(54, 112, "Barrer el nivel no es girarse.")
    paragraph(c, "Si el precio sigue desplazándose sin recuperar el nivel, no hay Judas Swing: hay tendencia. Esperar también es operar.",
              54, 92, W - 108, size=9, leading=12, color=Color(1, 1, 1, 0.76))
    c.showPage()

    # Página 5 - Ejecución
    page_base(c, "Ejecución", 5)
    page_title(
        c,
        "04 - De la trampa a la entrada",
        "Espera, confirma y ejecuta",
        "Reconocer la trampa no es suficiente. La entrada llega cuando el precio demuestra que se ha dado la vuelta de verdad.",
    )
    fases = [
        ("ESPERA", "Deja que la apertura haga su primer movimiento",
         "No entras en él. Antes de las 9:30 ya tienes marcado qué liquidez hay a cada lado: máximos y mínimos de vela, del pre-market o del día anterior."),
        ("CONFIRMA", "El giro tiene que verse",
         "Cambio de estructura con desplazamiento en temporalidad baja y una confirmación: un IFVG, un fair value gap que nace del giro o una vela envolvente. Sin eso, no hay entrada."),
        ("EJECUTA", "Stop detrás de la trampa, objetivo enfrente",
         "La invalidación es el extremo de la manipulación: si el precio lo supera, la lectura era falsa. El objetivo es la liquidez del lado contrario, con al menos una relación 1:1."),
    ]
    yy = H - 238
    for tag, titulo, texto in fases:
        c.setFillColor(PAPER)
        c.setStrokeColor(LINE)
        c.roundRect(38, yy - 112, W - 76, 112, 7, fill=1, stroke=1)
        c.setFillColor(BLUE)
        c.roundRect(54, yy - 38, 86, 24, 5, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(97, yy - 30, tag)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(154, yy - 30, titulo)
        paragraph(c, texto, 54, yy - 60, W - 108, size=9.3, leading=12.6)
        yy -= 128
    c.setFillColor(ICE)
    c.roundRect(38, 84, W - 76, 74, 7, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(54, 134, "SI TE LO PIERDES")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 12.5)
    c.drawString(54, 112, "No persigas el giro cuando ya se ha ido.")
    paragraph(c, "Si la confirmación llega lejos de la trampa, el riesgo ya no compensa. Mañana hay otra apertura.",
              54, 94, W - 108, size=9, leading=12)
    c.showPage()

    # Página 6 - Checklist
    page_base(c, "Checklist", 6)
    page_title(
        c,
        "05 - Checklist",
        "Antes de entrar",
        "Marca cada condición. Si falta el objetivo, la confirmación o la invalidación, todavía no hay operación.",
    )
    items = [
        ("01", "Antes de las 9:30 tengo marcada la liquidez de arriba y la de abajo."),
        ("02", "No he entrado en el primer movimiento de la apertura."),
        ("03", "El precio ha barrido un nivel claro: mínimo o máximo de vela, del pre-market o del día anterior."),
        ("04", "La manipulación ha sido rápida: recoge los stops y se gira."),
        ("05", "Hay cambio de estructura con desplazamiento hacia el otro lado."),
        ("06", "Tengo una confirmación: IFVG, fair value gap o vela envolvente."),
        ("07", "El stop está detrás del extremo de la manipulación."),
        ("08", "El objetivo es la liquidez contraria y ofrece al menos 1:1."),
        ("09", "Si el precio supera el extremo de la trampa, salgo sin mover el stop."),
    ]
    yy = H - 245
    for numero, texto in items:
        checklist_row(c, yy, numero, texto)
        yy -= 44
    c.setFillColor(DARK)
    c.roundRect(38, 88, W - 76, 84, 7, fill=1, stroke=0)
    c.setFillColor(SKY)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(54, 146, "REGLA FINAL")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 13.5)
    c.drawString(54, 122, "El primer movimiento de la apertura no es el del día.")
    paragraph(c, "Quien persigue el arranque de las 9:30 es la liquidez que el mercado necesitaba.",
              54, 102, W - 108, size=9.2, leading=12, color=Color(1, 1, 1, 0.76))
    c.showPage()

    # Página 7 - Integración
    page_base(c, "Tu proceso", 7)
    page_title(
        c,
        "06 - Integración",
        "Convierte la trampa en datos",
        "Registra cada apertura, la operes o no. En veinte sesiones sabrás cuántas veces hubo trampa, cuánto duró y cuántas llegaron al objetivo.",
    )
    campos = [
        ("Dirección de la trampa", "Hacia arriba / Hacia abajo"),
        ("Nivel barrido", "Vela / Pre-market / Día anterior"),
        ("Duración", "Minutos hasta el giro"),
        ("Confirmación", "IFVG / FVG / Envolvente"),
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
