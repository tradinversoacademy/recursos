"""Guía del modelo de la vela diaria anterior: máximo, mínimo y 50%.

Reutiliza el estilo de la guía de los FVG.
"""

from pathlib import Path

from reportlab.lib.colors import Color, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from generate_tipos_fvg_pdf import (
    BLUE, DARK, GREEN, ICE, INK, LINE, LOGO, MUTED, NAVY, PAPER, RED, SKY,
    checklist_row, page_base, page_title, paragraph,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "vela-diaria-anterior.pdf"
W, H = A4

# Vela diaria anterior: máximo 100, mínimo 60, 50% en 80.
MAXIMO, MINIMO, MITAD = 100, 60, 80
VELA_DIARIA = (66, 96, 100, 60)

# Velas de 15 minutos del día siguiente (apertura, cierre, máximo, mínimo).
# El precio está por encima del 50%, barre el máximo, cierra dentro y se va
# primero al 50% y después al mínimo.
VELAS_VENTA = [
    (86, 89, 90, 85),
    (89, 87, 91, 86),
    (87, 92, 93, 86),
    (92, 95, 96, 91),
    (95, 97, 98, 94),
    (97, 96, 103, 95),   # barre el máximo y cierra dentro
    (98, 91, 99, 90),
    (91, 88, 93, 86),
    (88, 92, 94, 87),    # retroceso al FVG
    (92, 85, 93, 84),
    (85, 80, 86, 78),    # objetivo 1: el 50%
    (80, 73, 81, 72),
    (73, 66, 74, 64),
    (66, 61, 67, 59),    # objetivo 2: el mínimo
]
BARRIDO = 5
FVG = (93, 95, 7)        # (abajo, arriba, vela desde la que se dibuja)
ENTRADA = 93
STOP = 104


def espejo(precio):
    return 160 - precio


def vela_diaria_chart(c, x, y, width, height, venta=True, pasos=True):
    """Vela diaria a la izquierda y el día siguiente en 15 minutos a la derecha."""
    if venta:
        velas = VELAS_VENTA
        diaria = VELA_DIARIA
        fvg_bajo, fvg_alto, fvg_desde = FVG
        entrada, stop = ENTRADA, STOP
        tp1, tp2 = MITAD, MINIMO
    else:
        velas = [(espejo(o), espejo(c_), espejo(l), espejo(h)) for o, c_, h, l in VELAS_VENTA]
        o, c_, h, l = VELA_DIARIA
        diaria = (espejo(o), espejo(c_), espejo(l), espejo(h))
        fvg_bajo, fvg_alto, fvg_desde = espejo(FVG[1]), espejo(FVG[0]), FVG[2]
        entrada, stop = espejo(ENTRADA), espejo(STOP)
        tp1, tp2 = MITAD, MAXIMO

    c.setFillColor(PAPER)
    c.setStrokeColor(LINE)
    c.roundRect(x, y - height, width, height, 7, fill=1, stroke=1)

    pad_top, pad_bottom = 22, 30
    alto = height - pad_top - pad_bottom
    base = y - height + pad_bottom
    precios = [v[2] for v in velas] + [v[3] for v in velas] + [stop]
    suelo = min(precios) - 3
    rango = max(precios) + 3 - suelo

    def py(precio):
        return base + ((precio - suelo) / rango) * alto

    diaria_x = x + 40
    sep_x = x + 82
    zona_x = sep_x + 10
    zona_w = width - (zona_x - x) - 96
    paso = zona_w / len(velas)
    ancho = min(8, paso * 0.55)

    def vx(indice):
        return zona_x + paso * (indice + 0.5)

    # Mitad superior e inferior de la vela anterior.
    c.setFillColor(Color(RED.red, RED.green, RED.blue, 0.05))
    c.rect(sep_x, py(MITAD), zona_x + zona_w - sep_x, py(MAXIMO) - py(MITAD), fill=1, stroke=0)
    c.setFillColor(Color(GREEN.red, GREEN.green, GREEN.blue, 0.05))
    c.rect(sep_x, py(MINIMO), zona_x + zona_w - sep_x, py(MITAD) - py(MINIMO), fill=1, stroke=0)

    # La vela diaria.
    o, c_, h, l = diaria
    color = GREEN if c_ >= o else RED
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.6)
    c.line(diaria_x, py(l), diaria_x, py(h))
    c.rect(diaria_x - 11, py(min(o, c_)), 22, py(max(o, c_)) - py(min(o, c_)), fill=1, stroke=0)
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", 6.5)
    c.drawCentredString(diaria_x, y - height + 12, "AYER (D1)")

    c.setStrokeColor(MUTED)
    c.setLineWidth(0.7)
    c.setDash(2, 3)
    c.line(sep_x, y - height + 22, sep_x, y - 12)
    c.setDash()
    c.setFillColor(MUTED)
    c.drawString(sep_x + 6, y - height + 12, "HOY (15 MIN)")

    # Niveles de la vela anterior.
    for precio, texto, color in (
        (MAXIMO, "MÁXIMO", NAVY),
        (MITAD, "50%", BLUE),
        (MINIMO, "MÍNIMO", NAVY),
    ):
        c.setStrokeColor(color)
        c.setLineWidth(1.2 if precio == MITAD else 0.9)
        c.setDash(5, 3)
        c.line(diaria_x + 12, py(precio), zona_x + zona_w, py(precio))
        c.setDash()
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(zona_x + zona_w + 6, py(precio) - 2.5, texto)
        if pasos and precio in (tp1, tp2):
            c.setFillColor(GREEN)
            c.setFont("Helvetica-Bold", 6.3)
            c.drawString(zona_x + zona_w + 6, py(precio) - 11.5, "OBJETIVO 1" if precio == tp1 else "OBJETIVO 2")

    if pasos:
        inicio = vx(fvg_desde) - paso * 0.5
        c.setFillColor(Color(BLUE.red, BLUE.green, BLUE.blue, 0.2))
        c.rect(inicio, py(fvg_bajo), zona_x + zona_w - inicio, py(fvg_alto) - py(fvg_bajo), fill=1, stroke=0)
        c.setStrokeColor(RED)
        c.setLineWidth(0.9)
        c.line(vx(BARRIDO) - paso * 0.5, py(stop), zona_x + zona_w, py(stop))
        c.setFillColor(RED)
        c.setFont("Helvetica-Bold", 6.5)
        c.drawString(zona_x + zona_w + 6, py(stop) + (3 if venta else -9), "STOP")
        c.setFillColor(BLUE)
        c.drawString(zona_x + zona_w + 6, (py(fvg_bajo) + py(fvg_alto)) / 2 - 2.3, "ENTRADA FVG")

    for indice, (apertura, cierre, alto_v, bajo_v) in enumerate(velas):
        cx = vx(indice)
        color = GREEN if cierre >= apertura else RED
        c.setStrokeColor(color)
        c.setFillColor(color)
        c.setLineWidth(1.1)
        c.line(cx, py(bajo_v), cx, py(alto_v))
        abajo = py(min(apertura, cierre))
        c.rect(cx - ancho / 2, abajo, ancho, max(py(max(apertura, cierre)) - abajo, 1.6), fill=1, stroke=0)

    if pasos:
        apertura, cierre, alto_v, bajo_v = velas[BARRIDO]
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 7)
        if venta:
            c.drawRightString(vx(BARRIDO) - 7, py(alto_v) - 9, "BARRIDO")
        else:
            c.drawRightString(vx(BARRIDO) - 7, py(bajo_v) + 4, "BARRIDO")


def niveles_chart(c, x, y, width, height):
    """La vela diaria con sus tres niveles y sus dos mitades."""
    c.setFillColor(PAPER)
    c.setStrokeColor(LINE)
    c.roundRect(x, y - height, width, height, 7, fill=1, stroke=1)
    pad = 26
    alto = height - pad * 2
    base = y - height + pad

    def py(precio):
        return base + ((precio - 56) / 48) * alto

    vx = x + 120
    zona_fin = x + width - 150
    c.setFillColor(Color(RED.red, RED.green, RED.blue, 0.07))
    c.rect(vx + 30, py(MITAD), zona_fin - vx - 30, py(MAXIMO) - py(MITAD), fill=1, stroke=0)
    c.setFillColor(Color(GREEN.red, GREEN.green, GREEN.blue, 0.07))
    c.rect(vx + 30, py(MINIMO), zona_fin - vx - 30, py(MITAD) - py(MINIMO), fill=1, stroke=0)

    o, c_, h, l = VELA_DIARIA
    c.setStrokeColor(GREEN)
    c.setFillColor(GREEN)
    c.setLineWidth(2)
    c.line(vx, py(l), vx, py(h))
    c.rect(vx - 22, py(o), 44, py(c_) - py(o), fill=1, stroke=0)

    for precio, texto, nota, color in (
        (MAXIMO, "MÁXIMO", "liquidez de arriba", NAVY),
        (MITAD, "50%", "el equilibrio de la vela", BLUE),
        (MINIMO, "MÍNIMO", "liquidez de abajo", NAVY),
    ):
        c.setStrokeColor(color)
        c.setLineWidth(1.4 if precio == MITAD else 1)
        c.setDash(5, 3)
        c.line(vx + 24, py(precio), zona_fin, py(precio))
        c.setDash()
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(zona_fin + 10, py(precio) + 1, texto)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 7.5)
        c.drawString(zona_fin + 10, py(precio) - 10, nota)

    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString((vx + 30 + zona_fin) / 2, py(90) - 3, "MITAD DE ARRIBA: SOLO BUSCAS VENTAS")
    c.setFillColor(GREEN)
    c.drawCentredString((vx + 30 + zona_fin) / 2, py(70) - 3, "MITAD DE ABAJO: SOLO BUSCAS COMPRAS")
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(vx, y - height + 10, "VELA DIARIA ANTERIOR")


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


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=A4)
    c.setTitle("El modelo de la vela diaria - TRADINVERSO")
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
    c.drawString(40, H - 170, "MÁXIMO - MÍNIMO - 50% - 15 MINUTOS")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 30)
    c.drawString(40, H - 220, "EL MODELO DE LA")
    c.drawString(40, H - 260, "VELA DIARIA")
    c.setFont("Helvetica-Bold", 19)
    c.drawString(40, H - 294, "TRES NIVELES Y UNA REGLA")
    paragraph(
        c,
        "El máximo, el mínimo y el 50% de la vela de ayer te dicen qué buscar hoy, dónde entrar, dónde salir y, sobre todo, cuándo no operar.",
        40, H - 338, W - 80, size=11.5, leading=16, color=Color(1, 1, 1, 0.76),
    )
    etiquetas = [("01", "MARCA LOS NIVELES"), ("02", "ESPERA EL BARRIDO"), ("03", "OBJETIVO: EL 50%")]
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

    # Página 2 - Los tres niveles
    page_base(c, "Los tres niveles", 2)
    page_title(
        c,
        "01 - En el gráfico diario",
        "Máximo, mínimo y 50% de ayer",
        "Antes de abrir el gráfico de 15 minutos, marca tres niveles de la vela diaria anterior. Son los únicos que necesitas para este modelo.",
    )
    niveles_chart(c, 38, H - 222, W - 76, 250)
    pasos = [
        ("El máximo y el mínimo", "Son los extremos que casi todo el mundo tiene marcados. Por encima del máximo y por debajo del mínimo se acumulan los stops: es la liquidez que el precio va a buscar."),
        ("El 50%", "La mitad exacta entre el máximo y el mínimo: (máximo + mínimo) / 2. Es el equilibrio de la vela y divide el día en una mitad de arriba y una de abajo."),
        ("La mitad en la que está el precio", "Si cotiza por encima del 50%, solo buscas ventas en el máximo. Si cotiza por debajo, solo compras en el mínimo. Nunca las dos cosas el mismo día."),
    ]
    yy = H - 496
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
    nota(c, "IDEA CENTRAL", "El 50% es a la vez el filtro y el objetivo.",
         "Te dice qué lado buscar y hasta dónde suele volver el precio después del barrido.")
    c.showPage()

    # Página 3 - La venta
    page_base(c, "La venta", 3)
    page_title(
        c,
        "02 - Por encima del 50%",
        "Barre el máximo y vuelve dentro",
        "El precio está en la mitad de arriba, supera el máximo de ayer, recoge los stops y una vela de 15 minutos cierra otra vez dentro de la vela anterior. Ahí empieza la venta.",
    )
    vela_diaria_chart(c, 38, H - 222, W - 76, 290, venta=True)
    cajas(c, [
        ("CONTEXTO", "El precio está por encima del 50%",
         "Antes del barrido, el precio cotiza en la mitad de arriba de la vela anterior. Si está por debajo del 50%, este setup no existe."),
        ("GATILLO", "Barrido del máximo y cierre dentro",
         "Una mecha supera el máximo de ayer y la vela de 15 minutos cierra por debajo de él. Si cierra fuera y se mantiene, no es un barrido: es una ruptura."),
        ("OBJETIVOS", "Primero el 50%, después el mínimo",
         "El objetivo 1 es el 50% de la vela anterior. El objetivo 2, su mínimo: la liquidez del otro lado."),
    ], H - 528, 64)
    c.showPage()

    # Página 4 - La compra
    page_base(c, "La compra", 4)
    page_title(
        c,
        "03 - Por debajo del 50%",
        "Barre el mínimo y vuelve dentro",
        "Es el mismo modelo dado la vuelta. El precio está en la mitad de abajo, pierde el mínimo de ayer, recoge los stops y una vela de 15 minutos cierra otra vez dentro. Ahí empieza la compra.",
    )
    vela_diaria_chart(c, 38, H - 222, W - 76, 290, venta=False)
    cajas(c, [
        ("CONTEXTO", "El precio está por debajo del 50%",
         "Antes del barrido, el precio cotiza en la mitad de abajo de la vela anterior. Si está por encima del 50%, este setup no existe."),
        ("GATILLO", "Barrido del mínimo y cierre dentro",
         "Una mecha pierde el mínimo de ayer y la vela de 15 minutos cierra por encima de él. Si cierra fuera y se mantiene, es una ruptura y no se compra."),
        ("OBJETIVOS", "Primero el 50%, después el máximo",
         "El objetivo 1 es el 50% de la vela anterior. El objetivo 2, su máximo: la liquidez del otro lado."),
    ], H - 528, 64)
    c.showPage()

    # Página 5 - Ejecución
    page_base(c, "Ejecución", 5)
    page_title(
        c,
        "04 - De la idea a la orden",
        "Entrada, stop y gestión",
        "El cierre de la vela dentro del rango te da la idea. La entrada llega cuando el precio confirma el giro, con el riesgo definido antes de entrar.",
    )
    cajas(c, [
        ("ENTRADA", "En el retroceso al FVG",
         "Después del cierre dentro, el giro suele dejar un fair value gap. Esperas el retroceso a ese hueco y entras con confirmación: una vela envolvente o un IFVG en temporalidad baja. Nunca en límite antes del cierre de la vela de 15."),
        ("STOP", "Detrás del extremo del barrido",
         "En la venta, por encima del máximo que hizo la mecha. En la compra, por debajo del mínimo. Si el precio vuelve a superarlo, la lectura era falsa y sales."),
        ("RECORRIDO", "El 50% tiene que pagar el riesgo",
         "Mide la distancia de tu entrada al 50%. Si es menor que la distancia al stop, el objetivo 1 no llega ni a 1:1 y la operación no compensa. No la tomes."),
        ("GESTIÓN", "Parcial en el 50%",
         "Al llegar al 50% puedes cerrar una parte y llevar el stop a la entrada. El resto va a buscar el otro extremo de la vela anterior sin arriesgar la operación."),
    ], H - 236, 92)
    nota(c, "NO ANTICIPES", "Tocar el máximo no es barrerlo.",
         "Hasta que la vela de 15 minutos no cierra dentro, no sabes si es un barrido o el inicio de una ruptura.")
    c.showPage()

    # Página 6 - Cuándo no operar
    page_base(c, "Cuándo no operar", 6)
    page_title(
        c,
        "05 - Los días sin setup",
        "Saber cuándo no entrar",
        "La mitad del modelo es filtrar. Estos son los casos en los que no hay operación aunque el precio se mueva cerca de los niveles.",
    )
    cajas(c, [
        ("50%", "El precio está alrededor del 50%",
         "Cruza el equilibrio arriba y abajo sin decidirse. No tienes lado claro, y además tu objetivo 1 está justo donde estás. No se opera."),
        ("RUPTURA", "Cierra fuera y se mantiene",
         "Si la vela de 15 minutos cierra por encima del máximo (o por debajo del mínimo) y las siguientes se sostienen fuera, el mercado está expandiendo. No se opera en contra."),
        ("IMPULSO", "Llega al nivel de un solo tirón",
         "Si el precio viene de la otra mitad, cruza el 50% y barre el extremo en el mismo impulso, no estaba en esa mitad antes del barrido. El contexto no se cumple: no se opera."),
        ("YA LLEGÓ", "El precio ya está en el 50%",
         "Si te has perdido el giro y el precio ya ha llegado al equilibrio, la operación se ha ido. Mañana hay otra vela."),
    ], H - 236, 86, tonos=[RED, NAVY, BLUE, DARK])
    nota(c, "REGLA", "Si no está claro en qué mitad está el precio, no hay operación.",
         "El modelo funciona porque elige un solo lado. Si dudas de cuál es, el día ya te ha dado la respuesta.", oscuro=False)
    c.showPage()

    # Página 7 - Checklist
    page_base(c, "Checklist", 7)
    page_title(
        c,
        "06 - Checklist",
        "Antes de entrar",
        "Marca cada condición. Si falta una, todavía no hay operación.",
    )
    items = [
        ("01", "Tengo marcados el máximo, el mínimo y el 50% de la vela diaria anterior."),
        ("02", "Sé en qué mitad está el precio y solo busco el setup de ese lado."),
        ("03", "El precio no está pegado al 50% ni cruzándolo arriba y abajo."),
        ("04", "Hay barrido: la mecha supera el máximo o pierde el mínimo de ayer."),
        ("05", "La vela de 15 minutos ha cerrado otra vez dentro de la vela anterior."),
        ("06", "Hay retroceso al fair value gap y confirmación para entrar."),
        ("07", "El stop está detrás del extremo del barrido."),
        ("08", "La distancia al 50% es al menos igual que la distancia al stop."),
        ("09", "Sé qué hago en el 50%: parcial y stop a la entrada."),
    ]
    yy = H - 245
    for numero, texto in items:
        checklist_row(c, yy, numero, texto)
        yy -= 44
    nota(c, "REGLA FINAL", "Tres niveles, un lado, un objetivo.",
         "Cuanto más simple es el modelo, más fácil es saber cuándo lo estás rompiendo.", y0=88, alto=84)
    c.showPage()

    # Página 8 - Registro y siguiente paso
    page_base(c, "Tu proceso", 8)
    page_title(
        c,
        "07 - Integración",
        "Convierte el modelo en datos",
        "Apunta cada día, operes o no. En veinte sesiones sabrás cuántas veces el precio volvió al 50% después del barrido y cuántas llegó al otro extremo.",
    )
    campos = [
        ("Mitad del precio", "Por encima / por debajo / en el 50%"),
        ("Barrido", "Máximo / Mínimo / No hubo"),
        ("Cierre de la vela de 15", "Dentro / Fuera"),
        ("Objetivo alcanzado", "Ninguno / 50% / Otro extremo"),
        ("Resultado", "R conseguido"),
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
