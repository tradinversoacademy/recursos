"""Genera la tabla de recursos para el bot de setting.

La lista de recursos sale de assets/js/resources.js (única fuente de verdad) y
el dolor y la solución de cada uno se escriben aquí. Si se añade un recurso al
catálogo y no se le escribe su texto, el script falla a propósito: así la hoja
del setter no se queda a medias sin que nadie se entere.

    python tools/build_lista_setters.py        # escribe output/lista-setters.tsv

Después se pega el contenido en la hoja "Lista de recursos de la biblioteca":
https://docs.google.com/spreadsheets/d/1pb4Dp4-uBAG4JrOeycL9u3_PxOqgCh1vPFMxl6cWANA/edit
"""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOGO = ROOT / "assets" / "js" / "resources.js"
SALIDA = ROOT / "output" / "lista-setters.tsv"
BASE = "https://tradinversoacademy.github.io/recursos/recursos/"

CABECERA = ["Recurso", "Qué dolor aborda", "Qué solución da", "Enlace"]

# slug: (dolor del lead, lo que se lleva)
TEXTOS = {
    "judas-swing": (
        "Entra en el primer movimiento de la apertura y el precio se gira justo después. Siente que el mercado va a por su stop.",
        "Le explica el Judas Swing con un ejemplo en mercado real: cómo reconocer la manipulación de las 9:30, esperar el giro y entrar hacia la liquidez del lado contrario.",
    ),
    "tipos-fair-value-gap": (
        "Opera fair value gaps, unos le funcionan y otros no, y cuando deja la orden puesta el precio le pasa por encima.",
        "Le enseña los tres tipos de FVG, cómo distinguirlos mirando la tercera vela y dónde está la entrada en cada caso. Vídeo y guía en PDF.",
    ),
    "mechas-velas": (
        "No sabe leer las velas y se pierde entre indicadores para decidir si entrar o no.",
        "Le enseña a leer las mechas y, sobre todo, en qué zonas del gráfico significan algo y en cuáles son ruido.",
    ),
    "backtesting-orb": (
        "Cree que su estrategia funciona pero no tiene un solo dato que lo respalde, así que salta de una a otra.",
        "Le da el vídeo del backtesting del ORB en Nasdaq y una plantilla de Google Sheets para registrar sus operaciones y ver sus números reales.",
    ),
    "amd": (
        "Opera a cualquier hora sin saber qué está haciendo el precio en cada sesión.",
        "Le explica el ciclo de acumulación, manipulación y distribución entre Asia, Londres y Nueva York, con las confirmaciones de entrada.",
    ),
    "amd-ifvg": (
        "Entiende la teoría pero no sabe cómo se aplica en una sesión real, de principio a fin.",
        "Le da una sesión completa en Nasdaq explicada paso a paso, de la liquidez a la ejecución, en una guía de 11 páginas.",
    ),
    "manipulacion-maximos-minimos": (
        "Le saltan los stops justo antes de que el precio se vaya a su favor, una y otra vez.",
        "Le explica por qué el precio va a buscar sus stops, en qué niveles se acumula la liquidez y cómo entrar al lado contrario del barrido.",
    ),
    "modelo-liquidez-estructura-fvg": (
        "Conoce conceptos sueltos pero no sabe en qué orden se usan dentro de una misma operación.",
        "Le da un modelo de compra completo: barrida de liquidez, cambio de estructura y FVG, explicados dentro del mismo ejemplo.",
    ),
    "guia-5-conceptos-trading": (
        "Está empezando y se pierde con tanto concepto y tanta nomenclatura.",
        "Le explica desde cero los cinco conceptos con los que se lee el precio: FVG, IFVG, liquidez, estructura y cambio de estructura. Es el mejor primer envío.",
    ),
    "ifvg": (
        "Entra en los giros demasiado pronto y se come el movimiento en contra.",
        "Le enseña cómo un fair value gap invertido confirma el cambio de intención antes de buscar la entrada.",
    ),
    "orb-nasdaq": (
        "Quiere una estrategia concreta, con una hora fija, en lugar de más teoría.",
        "Le da la operativa ORB en la apertura de Nueva York: rango inicial, confirmación y gestión del riesgo.",
    ),
    "rango-asiatico": (
        "Opera de madrugada o en sesión europea sin ninguna referencia clara.",
        "Le enseña a usar el rango asiático: contexto, manipulación y ejecución con el riesgo definido.",
    ),
    "apertura-0000-nueva-york": (
        "No sabe con qué sesgo empezar el día y acaba improvisando en la apertura de Londres.",
        "Le da la apertura de las 00:00 de Nueva York como referencia para preparar la sesión. Solo por enlace directo: no aparece en la biblioteca.",
    ),
    "data-tradinverso": (
        "Ya opera con un método pero lo lleva todo en la cabeza o en notas sueltas y no mide nada.",
        "Le enseña DATA: journal técnico y emocional, gestión de cuentas y trading plan en una sola herramienta.",
    ),
    "test-objetividad-sistema": (
        "Dice que ya tiene un sistema, pero en realidad improvisa y cambia las reglas sobre la marcha.",
        "Le da un test de diez preguntas que termina con un veredicto sobre si su sistema es objetivo. Muy útil para abrir conversación.",
    ),
    "claridad-trader": (
        "Lleva tiempo atascado y cambia de estrategia cada pocas semanas.",
        "Le da un diagnóstico en vídeo de qué está frenando de verdad sus resultados antes de volver a cambiar de estrategia.",
    ),
    "checklist-entrada-mercado": (
        "Entra por impulso y después no sabe justificar por qué tomó esa operación.",
        "Le da un checklist de contexto, riesgo, entrada y estado mental para pasar antes de arriesgar dinero.",
    ),
    "protocolo-mental-trader": (
        "Se sabe las reglas pero las rompe en caliente: revenge trading, sobreoperar, mover el stop.",
        "Le da un protocolo para frenar el impulso y ejecutar con control cuando hay presión.",
    ),
    "plan-trader-rentable": (
        "Lleva mucho tiempo sin avanzar y no sabe qué está haciendo mal.",
        "Le señala los diez errores que tiene que dejar de repetir para proteger su proceso.",
    ),
    "metodo-c3": (
        "Ya ha consumido varios recursos y pregunta cómo trabajamos.",
        "Le explica el Método C3: el sistema paso a paso con el que el alumno construye un proceso consistente.",
    ),
    "programa-tradinverso": (
        "Lead caliente que pregunta precio, qué incluye o cómo se entra.",
        "Le detalla todo lo que incluye el programa: formación, acompañamiento, directos, comunidad y tecnología.",
    ),
}


def cargar_catalogo():
    fuente = CATALOGO.read_text(encoding="utf-8")
    cuerpo = re.search(r"window\.TRADINVERSO_RESOURCES\s*=\s*(\[.*?\]);", fuente, re.S).group(1)
    lineas = [re.sub(r'^(\s*)(\w+):', r'\1"\2":', linea) for linea in cuerpo.splitlines()]
    return json.loads(re.sub(r",(\s*[}\]])", r"\1", "\n".join(lineas)))


def main():
    catalogo = cargar_catalogo()
    faltan = [r["slug"] for r in catalogo if r["slug"] not in TEXTOS]
    if faltan:
        raise SystemExit(
            "Sin dolor/solución escritos para: " + ", ".join(faltan)
            + "\nAñádelos en TEXTOS antes de actualizar la hoja del setter."
        )

    # Los dos del programa van al final: son para lead caliente, no para nutrir.
    ordenados = sorted(catalogo, key=lambda r: r["category"] == "programa")

    filas = [CABECERA]
    for recurso in ordenados:
        dolor, solucion = TEXTOS[recurso["slug"]]
        filas.append([recurso["title"], dolor, solucion, BASE + recurso["slug"] + "/"])

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    texto = "\n".join("\t".join(celda for celda in fila) for fila in filas)
    SALIDA.write_text(texto, encoding="utf-8", newline="\n")
    print(SALIDA)
    print(f"{len(filas) - 1} recursos")


if __name__ == "__main__":
    main()
