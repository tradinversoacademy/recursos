from pathlib import Path
import math
import random

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "modelo-liquidez-ifvg-tradinverso.pdf"
LOGO = ROOT / "assets" / "img" / "tradinverso-logo.png"

W, H = A4
NAVY = HexColor("#061938")
BLUE = HexColor("#2F86F6")
SKY = HexColor("#E6F1FF")
ICE = HexColor("#F5F9FF")
INK = HexColor("#14233B")
MUTED = HexColor("#5F7089")
LINE = HexColor("#C9DCF5")
GREEN = HexColor("#2D9C71")
RED = HexColor("#E45353")
GOLD = HexColor("#F3B84A")

FONT_REG = "Helvetica"
FONT_BOLD = "Helvetica-Bold"


def register_fonts():
    font_dir = Path(r"C:\Windows\Fonts")
    regular = font_dir / "arial.ttf"
    bold = font_dir / "arialbd.ttf"
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("TVRegular", str(regular)))
        pdfmetrics.registerFont(TTFont("TVBold", str(bold)))
        global FONT_REG, FONT_BOLD
        FONT_REG, FONT_BOLD = "TVRegular", "TVBold"


def pstyle(size=11, color=INK, leading=None, align=TA_LEFT, bold=False):
    return ParagraphStyle(
        "tv",
        fontName=FONT_BOLD if bold else FONT_REG,
        fontSize=size,
        leading=leading or size * 1.38,
        textColor=color,
        alignment=align,
        spaceAfter=0,
        allowWidows=0,
        allowOrphans=0,
    )


def paragraph(c, text, x, y_top, width, size=11, color=INK, leading=None,
              align=TA_LEFT, bold=False):
    p = Paragraph(text, pstyle(size, color, leading, align, bold))
    _, h = p.wrap(width, H)
    p.drawOn(c, x, y_top - h)
    return h


def round_rect(c, x, y, w, h, radius=10, fill=white, stroke=LINE, sw=0.8):
    c.setLineWidth(sw)
    c.setStrokeColor(stroke)
    c.setFillColor(fill)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)


def label(c, text, x, y, fill=SKY, color=BLUE):
    c.setFont(FONT_BOLD, 8.5)
    tw = c.stringWidth(text, FONT_BOLD, 8.5)
    round_rect(c, x, y - 4, tw + 22, 23, 11, fill, fill, 0)
    c.setFillColor(color)
    c.drawString(x + 11, y + 3, text)


def add_logo(c, x, y, width):
    if LOGO.exists():
        img = ImageReader(str(LOGO))
        iw, ih = img.getSize()
        c.drawImage(img, x, y, width=width, height=width * ih / iw,
                    preserveAspectRatio=True, mask="auto")


def page_base(c, number, section):
    c.setFillColor(ICE)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.rect(0, 0, 7, H, fill=1, stroke=0)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.7)
    c.line(42, 38, W - 42, 38)
    c.setFillColor(MUTED)
    c.setFont(FONT_REG, 8)
    c.drawString(42, 23, section.upper())
    c.drawRightString(W - 42, 23, f"{number:02d}  |  TRADINVERSO")


def section_title(c, kicker, title, subtitle=None):
    label(c, kicker.upper(), 42, H - 63)
    y = H - 102
    h = paragraph(c, title, 42, y, W - 84, 28, NAVY, 32, bold=True)
    if subtitle:
        paragraph(c, subtitle, 42, y - h - 10, W - 84, 11.5, MUTED, 16)


def bullet(c, number, title, body, x, y_top, width):
    c.setFillColor(BLUE)
    c.circle(x + 14, y_top - 15, 14, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont(FONT_BOLD, 10)
    c.drawCentredString(x + 14, y_top - 18.5, str(number))
    paragraph(c, title, x + 39, y_top, width - 39, 11.5, NAVY, 15, bold=True)
    paragraph(c, body, x + 39, y_top - 20, width - 39, 9.4, MUTED, 13)


def candles(c, x, y, w, h, values, gap=None, liquidity=None, target=None):
    low = min(min(o, cl, lo, hi) for o, cl, lo, hi in values)
    high = max(max(o, cl, lo, hi) for o, cl, lo, hi in values)
    pad = (high - low) * 0.12 or 1
    low -= pad
    high += pad

    def sy(v):
        return y + (v - low) / (high - low) * h

    c.setStrokeColor(HexColor("#E2EAF5"))
    c.setLineWidth(0.5)
    for i in range(5):
        gy = y + h * i / 4
        c.line(x, gy, x + w, gy)

    if gap:
        start, end, v1, v2, color = gap
        cw = w / len(values)
        c.setFillColor(Color(color.red, color.green, color.blue, alpha=0.18))
        c.rect(x + start * cw, sy(min(v1, v2)), (end - start) * cw,
               abs(sy(v2) - sy(v1)), fill=1, stroke=0)

    cw = w / len(values)
    body_w = max(4, cw * 0.52)
    for i, (op, cl, lo, hi) in enumerate(values):
        cx = x + cw * (i + 0.5)
        color = GREEN if cl >= op else RED
        c.setStrokeColor(color)
        c.setLineWidth(1)
        c.line(cx, sy(lo), cx, sy(hi))
        c.setFillColor(color)
        by = min(sy(op), sy(cl))
        bh = max(2, abs(sy(cl) - sy(op)))
        c.rect(cx - body_w / 2, by, body_w, bh, fill=1, stroke=0)

    for item, color, text in (
        (liquidity, BLUE, "LIQUIDEZ"),
        (target, GOLD, "OBJETIVO"),
    ):
        if item is not None:
            ly = sy(item)
            c.setStrokeColor(color)
            c.setDash(4, 3)
            c.line(x, ly, x + w, ly)
            c.setDash()
            c.setFillColor(color)
            c.setFont(FONT_BOLD, 7)
            c.drawRightString(x + w, ly + 4, text)


def diagram_values(seed=5, count=18, start=100, drift=0.3):
    random.seed(seed)
    out = []
    last = start
    for i in range(count):
        move = random.uniform(-2.8, 2.8) + drift
        op = last + random.uniform(-0.7, 0.7)
        cl = op + move
        lo = min(op, cl) - random.uniform(0.4, 1.5)
        hi = max(op, cl) + random.uniform(0.4, 1.5)
        out.append((op, cl, lo, hi))
        last = cl
    return out


def draw_cover(c):
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.rect(0, 0, 11, H, fill=1, stroke=0)
    c.setFillColor(HexColor("#0B2B5F"))
    c.circle(W + 25, H - 120, 185, fill=1, stroke=0)
    c.setFillColor(Color(0.18, 0.52, 0.96, alpha=0.22))
    c.circle(W - 30, 80, 150, fill=1, stroke=0)

    add_logo(c, 48, H - 180, 105)
    label(c, "GUÍA OPERATIVA", 48, H - 224, HexColor("#16386C"), white)
    paragraph(c, "MODELO DE<br/>LIQUIDEZ E IFVG", 48, H - 285, W - 96,
              37, white, 42, bold=True)
    paragraph(c,
              "Cómo leer el contexto, confirmar la intención y gestionar "
              "una idea antes de ejecutar.",
              48, H - 405, W - 130, 15, HexColor("#C9D9F2"), 21)

    round_rect(c, 48, 104, W - 96, 122, 16, HexColor("#0D2B59"), HexColor("#214A81"), 1)
    paragraph(c, "<b>Idea central</b>", 68, 205, W - 136, 10, BLUE, 14)
    paragraph(c,
              "Una señal aislada no crea una operación. La oportunidad nace "
              "cuando liquidez, desplazamiento, confirmación y riesgo cuentan "
              "la misma historia.",
              68, 180, W - 136, 13, white, 19)
    c.setFillColor(HexColor("#AFC8EA"))
    c.setFont(FONT_REG, 9)
    c.drawString(48, 52, "Material educativo · No constituye asesoramiento financiero")
    c.setFillColor(white)
    c.setFont(FONT_BOLD, 9)
    c.drawRightString(W - 48, 52, "TRADINVERSO.COM")
    c.showPage()


def draw_map(c):
    page_base(c, 2, "Mapa de la guía")
    section_title(c, "Antes de empezar", "El proceso completo, de izquierda a derecha",
                  "La ejecución es el último paso. Primero construimos una narrativa verificable.")
    items = [
        ("01", "CONTEXTO", "Sesión, dirección probable y zonas relevantes."),
        ("02", "LIQUIDEZ", "Un nivel claro es barrido o atacado."),
        ("03", "INTENCIÓN", "Aparece desplazamiento y cambia el ritmo."),
        ("04", "CONFIRMACIÓN", "El IFVG valida el giro o la continuación."),
        ("05", "RIESGO", "Entrada, invalidación y objetivo están definidos."),
    ]
    y = H - 225
    for i, (num, title, body) in enumerate(items):
        fill = white if i % 2 == 0 else SKY
        round_rect(c, 58, y - 70, W - 116, 70, 10, fill, LINE)
        c.setFillColor(BLUE)
        c.setFont(FONT_BOLD, 20)
        c.drawString(76, y - 43, num)
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 11)
        c.drawString(126, y - 28, title)
        paragraph(c, body, 126, y - 38, W - 210, 9.5, MUTED, 13)
        y -= 84
    paragraph(c,
              "<b>Regla práctica:</b> si no puedes explicar por qué existe la "
              "operación en una frase, todavía no tienes una operación.",
              58, 126, W - 116, 11, NAVY, 16)
    c.showPage()


def draw_liquidity(c):
    page_base(c, 3, "Contexto y liquidez")
    section_title(c, "Paso 1", "La liquidez inicia la historia",
                  "Buscamos niveles visibles para muchos participantes, no líneas elegidas al azar.")
    round_rect(c, 42, 388, W - 84, 275, 14, white, LINE)
    vals = diagram_values(8, 22, 100, 0.25)
    # Force a sweep and rejection in the final candles.
    vals[-5:] = [
        (107, 109, 106, 110),
        (109, 111, 108, 112),
        (111, 113, 110, 114.2),
        (113, 108, 107, 115.5),
        (108, 105, 104, 109),
    ]
    candles(c, 64, 425, W - 128, 190, vals, liquidity=114.2)
    paragraph(c, "Barrido y rechazo", 64, 648, 220, 11, NAVY, 14, bold=True)
    c.setFillColor(RED)
    c.circle(W - 88, 586, 5, fill=1, stroke=0)
    c.setStrokeColor(RED)
    c.line(W - 88, 586, W - 123, 548)
    bullet(c, 1, "Localiza un nivel reconocible",
           "Máximos o mínimos iguales, extremos de sesión y swings evidentes.",
           52, 350, 240)
    bullet(c, 2, "Observa la reacción",
           "El barrido por sí solo no basta: necesitamos respuesta y desplazamiento.",
           304, 350, 240)
    round_rect(c, 52, 96, W - 104, 104, 12, SKY, SKY)
    paragraph(c, "<b>No confundas liquidez con dirección.</b>", 72, 180, W - 144,
              11.5, NAVY, 15)
    paragraph(c,
              "Que el precio tome un máximo no garantiza una caída. Solo crea "
              "el contexto para esperar pruebas de intención en sentido contrario.",
              72, 153, W - 144, 10.5, MUTED, 15)
    c.showPage()


def draw_ifvg(c):
    page_base(c, 4, "Confirmación IFVG")
    section_title(c, "Paso 2", "El IFVG confirma un cambio de intención",
                  "No lo tratamos como una entrada automática, sino como evidencia dentro del contexto.")
    round_rect(c, 42, 365, W - 84, 300, 14, white, LINE)
    vals = diagram_values(15, 20, 110, -0.15)
    vals[-8:] = [
        (108, 111, 107, 112), (111, 113, 110, 114),
        (113, 108, 107, 113.5), (108, 104, 103, 109),
        (104, 101, 100, 105), (101, 103, 100.5, 104),
        (103, 99, 98, 103.5), (99, 97, 96, 100),
    ]
    candles(c, 64, 405, W - 128, 205, vals,
            gap=(13, 18, 102.2, 104.4, RED), liquidity=113.7)
    c.setFillColor(RED)
    c.setFont(FONT_BOLD, 8)
    c.drawString(W - 182, 485, "ZONA IFVG")
    paragraph(c, "Secuencia de lectura", 52, 332, 220, 13, NAVY, 17, bold=True)
    bullet(c, 1, "Se toma liquidez", "El mercado visita una zona evidente.", 52, 300, 240)
    bullet(c, 2, "Aparece desplazamiento", "El precio acelera en sentido contrario.", 304, 300, 240)
    bullet(c, 3, "La ineficiencia cambia de función",
           "La zona deja de sostener el movimiento anterior y confirma la nueva intención.",
           52, 205, 240)
    bullet(c, 4, "Esperamos una ejecución lógica",
           "La entrada se decide por estructura, riesgo y reacción; no por el nombre de la zona.",
           304, 205, 240)
    c.showPage()


def draw_validity(c):
    page_base(c, 5, "Validación")
    section_title(c, "Paso 3", "Válido no significa perfecto",
                  "Una operación de calidad mantiene una invalidación clara antes de alcanzar el objetivo.")
    cards = [
        ("SETUP VÁLIDO", GREEN,
         "Liquidez tomada<br/>Desplazamiento limpio<br/>IFVG identificable<br/>Invalidación intacta"),
        ("SETUP DUDOSO", GOLD,
         "Nivel poco visible<br/>Impulso débil<br/>Zona ambigua<br/>Riesgo difícil de justificar"),
        ("SETUP INVÁLIDO", RED,
         "Entrada tardía<br/>Invalidación ya superada<br/>Objetivo sin recorrido<br/>Operación nacida del impulso"),
    ]
    x = 42
    for title, color, body in cards:
        round_rect(c, x, 380, 158, 263, 12, white, LINE)
        c.setFillColor(color)
        c.rect(x, 612, 158, 31, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont(FONT_BOLD, 9)
        c.drawCentredString(x + 79, 622, title)
        paragraph(c, body, x + 17, 582, 124, 10.2, INK, 31)
        x += 176
    round_rect(c, 42, 170, W - 84, 150, 14, NAVY, NAVY)
    paragraph(c, "La pregunta que evita entradas impulsivas", 65, 292,
              W - 130, 13, BLUE, 17, bold=True)
    paragraph(c,
              "Si el precio vuelve a cruzar mi invalidación, "
              "<b>¿qué parte concreta de mi análisis deja de ser cierta?</b>",
              65, 252, W - 130, 18, white, 25, align=TA_CENTER, bold=False)
    paragraph(c,
              "Si la respuesta es «ninguna», el stop está colocado por dinero, no por lógica.",
              65, 190, W - 130, 9.5, HexColor("#C7D8EF"), 14, align=TA_CENTER)
    c.showPage()


def draw_entry(c):
    page_base(c, 6, "Ejecución")
    section_title(c, "Paso 4", "La entrada sucede después de la confirmación",
                  "El objetivo no es adivinar el punto exacto, sino ejecutar una idea con asimetría.")
    round_rect(c, 42, 350, W - 84, 310, 14, white, LINE)
    vals = diagram_values(23, 23, 100, -0.2)
    vals[-10:] = [
        (101, 103, 100, 104), (103, 105, 102, 106),
        (105, 100, 99, 105.5), (100, 96, 95, 101),
        (96, 93, 92, 97), (93, 95, 92.5, 96),
        (95, 94, 93, 96), (94, 90, 89, 94.5),
        (90, 87, 86, 91), (87, 84, 83, 88),
    ]
    candles(c, 64, 390, W - 128, 215, vals,
            gap=(14, 18, 93.5, 96, RED), liquidity=105.2, target=85)
    c.setFillColor(NAVY)
    c.setFont(FONT_BOLD, 8)
    c.drawString(367, 474, "ENTRADA TRAS REACCIÓN")
    cols = [
        ("ENTRADA", "En el punto donde la confirmación permite definir el riesgo."),
        ("STOP", "Detrás del nivel que invalida la narrativa, no en una distancia arbitraria."),
        ("OBJETIVO", "En la siguiente liquidez con recorrido suficiente para justificar la operación."),
    ]
    x = 42
    for title, body in cols:
        round_rect(c, x, 128, 158, 160, 12, SKY, SKY)
        paragraph(c, title, x + 15, 263, 128, 10, BLUE, 14, bold=True)
        paragraph(c, body, x + 15, 231, 128, 9.7, MUTED, 14)
        x += 176
    c.showPage()


def draw_risk(c):
    page_base(c, 7, "Riesgo")
    section_title(c, "Protección", "El stop pertenece a la idea, no al miedo",
                  "Elegimos una invalidación que tenga sentido técnico y un tamaño que podamos asumir.")
    rows = [
        ("STOP ESTRUCTURAL", "Tras el swing o nivel cuya ruptura desmonta el escenario.",
         "Más espacio; suele reducir el tamaño de posición.", GREEN),
        ("STOP DE CONFIRMACIÓN", "Tras la vela o zona que activó la ejecución.",
         "Equilibrio entre protección y eficiencia.", BLUE),
        ("STOP AJUSTADO", "Muy próximo a la zona de entrada, solo con contexto excepcional.",
         "Mayor probabilidad de salida por ruido.", GOLD),
    ]
    y = 620
    for title, body, note, color in rows:
        round_rect(c, 42, y - 120, W - 84, 112, 12, white, LINE)
        c.setFillColor(color)
        c.rect(42, y - 120, 8, 112, fill=1, stroke=0)
        paragraph(c, title, 68, y - 28, 190, 11, NAVY, 15, bold=True)
        paragraph(c, body, 68, y - 55, 215, 9.5, MUTED, 13)
        paragraph(c, note, 320, y - 38, 215, 10.2, INK, 15)
        y -= 138
    round_rect(c, 42, 115, W - 84, 76, 12, NAVY, NAVY)
    paragraph(c,
              "<b>Antes de entrar:</b> riesgo monetario definido + nivel de invalidación "
              "definido + recorrido disponible.",
              65, 167, W - 130, 11, white, 16, align=TA_CENTER)
    c.showPage()


def draw_management(c):
    page_base(c, 8, "Gestión")
    section_title(c, "Durante el trade", "Gestionar no es tocar la operación sin parar",
                  "Cada movimiento del stop debe responder a información nueva, no a una emoción nueva.")
    steps = [
        ("A", "PLAN INICIAL", "Entrada, stop, objetivo y riesgo quedan escritos antes de ejecutar."),
        ("B", "PROTECCIÓN", "El precio confirma avance y alcanza un punto previsto para reducir riesgo."),
        ("C", "SALIDA", "Se alcanza el objetivo, se invalida la idea o aparece una salida planificada."),
    ]
    y = 605
    for letter, title, body in steps:
        c.setStrokeColor(LINE)
        c.setLineWidth(3)
        if letter != "C":
            c.line(78, y - 78, 78, y - 142)
        c.setFillColor(BLUE if letter != "C" else NAVY)
        c.circle(78, y - 31, 24, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont(FONT_BOLD, 13)
        c.drawCentredString(78, y - 36, letter)
        paragraph(c, title, 124, y - 10, 390, 11, NAVY, 15, bold=True)
        paragraph(c, body, 124, y - 39, 390, 10, MUTED, 14)
        y -= 158
    round_rect(c, 42, 104, W - 84, 90, 12, SKY, SKY)
    paragraph(c,
              "<b>Break even no siempre significa gestión correcta.</b> Mover el stop demasiado "
              "pronto puede convertir una buena lectura en una sucesión de salidas innecesarias.",
              64, 170, W - 128, 10.5, NAVY, 15)
    c.showPage()


def draw_timeframes(c):
    page_base(c, 9, "Temporalidades")
    section_title(c, "Contexto superior", "La temporalidad alta marca el destino",
                  "La temporalidad baja ayuda a ejecutar; no debería contradecir la narrativa principal.")
    round_rect(c, 42, 418, 245, 242, 14, white, LINE)
    round_rect(c, 308, 418, 245, 242, 14, white, LINE)
    paragraph(c, "TEMPORALIDAD ALTA", 61, 634, 205, 10, BLUE, 14, bold=True)
    paragraph(c, "¿Hacia dónde?", 61, 607, 205, 16, NAVY, 20, bold=True)
    candles(c, 61, 455, 205, 120, diagram_values(31, 15, 100, 0.45), target=111)
    paragraph(c, "TEMPORALIDAD BAJA", 327, 634, 205, 10, BLUE, 14, bold=True)
    paragraph(c, "¿Cómo participo?", 327, 607, 205, 16, NAVY, 20, bold=True)
    candles(c, 327, 455, 205, 120, diagram_values(37, 20, 100, 0.18),
            gap=(11, 16, 100, 102, BLUE))
    c.setStrokeColor(BLUE)
    c.setLineWidth(2)
    c.line(275, 539, 320, 539)
    c.line(311, 547, 320, 539)
    c.line(311, 531, 320, 539)
    bullet(c, 1, "Define el objetivo probable",
           "Liquidez pendiente, extremos relevantes o desequilibrios de temporalidad alta.",
           52, 365, 240)
    bullet(c, 2, "Espera el modelo en temporalidad baja",
           "Barrido, desplazamiento, IFVG y una invalidación que permita participar.",
           304, 365, 240)
    round_rect(c, 52, 113, W - 104, 96, 12, NAVY, NAVY)
    paragraph(c,
              "La precisión de una temporalidad baja no compensa una dirección "
              "mal planteada en temporalidad alta.",
              75, 181, W - 150, 13, white, 18, align=TA_CENTER, bold=True)
    c.showPage()


def draw_checklist(c):
    page_base(c, 10, "Checklist")
    section_title(c, "Antes de ejecutar", "Checklist de decisión",
                  "Marca cada punto. Si falta una pieza esencial, esperar también es una decisión.")
    items = [
        ("CONTEXTO", "Sé qué sesión opero y cuál es la narrativa principal."),
        ("LIQUIDEZ", "El precio ha atacado o barrido un nivel claro."),
        ("DESPLAZAMIENTO", "Existe una reacción con intención, no solo una vela aislada."),
        ("IFVG", "La zona confirma el cambio de función dentro de la estructura."),
        ("ENTRADA", "Tengo un punto de ejecución concreto y no persigo el precio."),
        ("INVALIDACIÓN", "Sé exactamente qué hecho técnico desmonta mi idea."),
        ("OBJETIVO", "Hay liquidez disponible y recorrido razonable."),
        ("RIESGO", "El tamaño de posición está calculado antes de entrar."),
        ("ESTADO MENTAL", "No estoy recuperando pérdidas ni operando por urgencia."),
    ]
    y = 635
    for title, body in items:
        round_rect(c, 52, y - 47, W - 104, 44, 8, white, LINE)
        c.setStrokeColor(BLUE)
        c.setLineWidth(1.5)
        c.roundRect(68, y - 34, 17, 17, 3, fill=0, stroke=1)
        c.setFillColor(NAVY)
        c.setFont(FONT_BOLD, 9)
        c.drawString(101, y - 22, title)
        c.setFillColor(MUTED)
        c.setFont(FONT_REG, 8.5)
        c.drawString(185, y - 22, body)
        y -= 56
    c.showPage()


def draw_close(c):
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.rect(0, 0, 8, H, fill=1, stroke=0)
    add_logo(c, 48, H - 176, 105)
    label(c, "CONCLUSIÓN", 48, H - 218, HexColor("#16386C"), white)
    paragraph(c, "LA VENTAJA ESTÁ<br/>EN EL PROCESO", 48, H - 278, W - 96,
              34, white, 40, bold=True)
    paragraph(c,
              "La liquidez aporta contexto. El desplazamiento muestra intención. "
              "El IFVG ayuda a confirmar. La gestión convierte una lectura en una "
              "decisión controlada.",
              48, H - 390, W - 112, 14, HexColor("#C9D9F2"), 21)
    round_rect(c, 48, 260, W - 96, 125, 14, HexColor("#0D2B59"), HexColor("#214A81"))
    paragraph(c,
              "No necesitas operar cada movimiento. Necesitas reconocer cuándo "
              "tus condiciones están presentes y protegerte cuando no lo están.",
              70, 352, W - 140, 16, white, 23, align=TA_CENTER, bold=True)
    paragraph(c, "Practica · Registra · Revisa · Mejora", 48, 204, W - 96,
              12, BLUE, 16, align=TA_CENTER, bold=True)
    c.setFillColor(HexColor("#BFD1EB"))
    c.setFont(FONT_REG, 8.5)
    c.drawString(48, 60, "Contenido educativo. El trading implica riesgo de pérdida.")
    c.setFillColor(white)
    c.setFont(FONT_BOLD, 9)
    c.drawRightString(W - 48, 60, "TRADINVERSO.COM")
    c.showPage()


def build():
    register_fonts()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=A4, pageCompression=1)
    c.setTitle("Modelo de liquidez e IFVG | TRADINVERSO")
    c.setAuthor("TRADINVERSO")
    draw_cover(c)
    draw_map(c)
    draw_liquidity(c)
    draw_ifvg(c)
    draw_validity(c)
    draw_entry(c)
    draw_risk(c)
    draw_management(c)
    draw_timeframes(c)
    draw_checklist(c)
    draw_close(c)
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    build()
