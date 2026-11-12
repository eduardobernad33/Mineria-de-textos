"""Genera el dataset de vehículos en Esperanto a partir de Wikipedia.

Uso (desde la raíz del repositorio):
    pip install -e ".[data]"
    python scripts/build_dataset.py

Salidas:
    data/dataset.csv   -> contrato de datos: UTF-8, separador ';', cabecera text;class
    data/metadata.csv  -> text;class;articulo;fuente (para partir train/test por artículo
                          y citar la revisión exacta de Wikipedia de cada párrafo)

Si algún artículo falla, se guarda data/dataset_parcial.csv y el script avisa.
Las revisiones de Wikipedia están fijadas (oldid) y la semilla es 42: el resultado es reproducible.
Textos: Wikipedia en esperanto, licencia CC BY-SA 4.0.
"""

# =============================================================================
# Texto original del cuaderno de Colab (portada)
# =============================================================================
# # Vehículos · Construcción del dataset
# **Minería de Textos · Fase 1 · Versión ampliada**
#
# Este cuaderno crea una tabla de párrafos en esperanto sobre coches, aviones y trenes.
# Cada fila tiene el párrafo original limpio y el tema que le corresponde.
#
# **En Colab:** abre este archivo y selecciona **Entorno de ejecución → Ejecutar
# todo**. Al terminar, la última celda indica el nombre del archivo guardado. Búscalo
# en el panel **Archivos** de la izquierda. Cada sección explica qué hace la celda de
# código que aparece debajo.

# =============================================================================
# ## 1. Elegir de dónde salen los textos
#
# La lista conserva los artículos del piloto y añade nuevas páginas de Wikipedia en
# esperanto. Al leer un artículo del grupo de coches, el programa pone la etiqueta
# **coches** a sus párrafos. Los identificadores de revisión permiten recuperar la
# misma versión de cada artículo. Un título nuevo se puede añadir a la lista para
# consultar su versión actual.
# =============================================================================

import random
import re
from urllib.parse import quote
import unicodedata
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ARTICULOS = {'coches': ['Aŭto',
            'Toyota Prius',
            'Trabant',
            'Elektra aŭtomobilo',
            'Ford Modelo T',
            'LADA Kalina',
            'LADA 110',
            'UAZ Patriot',
            'Austin FX4',
            'LADA Vesta',
            'Chevrolet Viva',
            'BS Nymph',
            'Senŝofora aŭto',
            'Tesla Model 3',
            'Porsche 911',
            'AMC Pacer',
            'Chrysler Crossfire',
            'Kombinaŭto',
            'Koncepta aŭtomobilo',
            'Volkswagen Tipo 1',
            'Bugatti Veyron',
            'Citroën DS',
            'Citroën Traction Avant',
            'Messerschmitt Kabinenroller',
            'BMW Isetta',
            'Goggomobil',
            'Renault Clio',
            'Benz Patent-Motorwagen',
            'Kvarciklo Ford',
            'Lancia Dilambda',
            'Fiat 500',
            'Renault 4',
            'Citroën'],
 'aviones': ['Aeroplano',
             'Airbus A380',
             'Concorde',
             'Flyer 1',
             'Supermarine Spitfire',
             'Aviadilo',
             'De Havilland Comet',
             'Boeing 737',
             'Boeing 777',
             'Boeing 767',
             'Boeing 707',
             'Airbus A330',
             'Airbus A300',
             'Lockheed C-130 Hercules',
             'General Dynamics F-16 Fighting Falcon',
             'Boeing B-52 Stratofortress',
             'North American P-51 Mustang',
             'Lockheed Martin F-35 Lightning II',
             'Lockheed Martin F-22 Raptor',
             'Airbus A350 XWB',
             'Bombaviadilo',
             'Ĉasaviadilo',
             'Militaviadilo',
             'Ultramalpeza aviadilo',
             'Biplano',
             'Antonov An-124',
             'Antonov An-225',
             'Junkers Ju 52',
             'McDonnell Douglas F-4 Phantom II',
             'Messerschmitt Bf 109',
             'Grumman F-14 Tomcat',
             'Flugo Air France 447',
             'Flugo 1549 de US Airways',
             'Boeing',
             'Airbus',
             'Douglas DC-3',
             'Boeing 747',
             'Boeing 727',
             'Boeing 787 Dreamliner',
             'Airbus A340',
             'Airbus A310',
             'Airbus A318',
             'Airbus A319',
             'Airbus A321',
             'McDonnell Douglas MD-11',
             'Douglas DC-8',
             'Lockheed L-1011 TriStar',
             'Tupolev Tu-144',
             'Komercaviadilo',
             'Glisilo',
             'Boeing B-17 Flying Fortress',
             'Boeing B-29 Superfortress',
             'McDonnell Douglas F-15 Eagle',
             'Alerono',
             'Fuzelaĝo',
             'Tupolev ANT-9',
             'Boeing 757',
             'Boeing 717',
             'Fokker 100',
             'Messerschmitt Me 262',
             'Iljuŝin Il-76',
             'Lockheed P-38 Lightning'],
 'trenes': ['Trajno',
            'Lokomotivo',
            'Vaporlokomotivo',
            'TGV',
            'Ŝinkanseno',
            'Grandrapida trajno',
            'Ŝvebotrajno',
            'Orient-ekspreso',
            'Dentorela fervojo',
            'Eurostar',
            'EuroCity',
            'InterCityExpress',
            'Intercités',
            'Alta Velocidad Española',
            'Railjet',
            'Z 5300',
            'Z 5600',
            'Z 20500',
            'MI 2N Altéo',
            'MI 2N Eole',
            'Z 20900',
            'Z 50000',
            'MI 09',
            'RER NG',
            'MF 01',
            'MF 77',
            'MF 88',
            'MP 89',
            'MP 51',
            'MF 19',
            'Bulgara ekspresa lokomotivo 1D1',
            'Lokomotivo de la serio Ѵ',
            'Serioj ER2 kaj ER9 de SZD',
            'Pendolino de Fiat Ferroviaria',
            'RegioJet',
            'Vaporlokomotivriparejo de Meiningen',
            'Trajneto de La Rhune',
            'Fervojo Stockton kaj Darlington',
            'Vaporlokomotivo 52 8055',
            'Serio O de SZD',
            '242 A1 de SNCF',
            'Kuŝvagono',
            'Kargotrajno',
            'Talgo',
            'Tramtrajno',
            'Trajnunuo',
            'Altrapida fervojo',
            'Rodalies de Catalunya',
            'Ŝinkansena linio Tōkaidō',
            'Fervojo de Sóller',
            'Vagono',
            'Metroo sur pneŭoj',
            'Dizellokomotivo',
            'Deutsche Reichsbahn',
            'DSB (Danske Statsbaner)',
            'Nubotrajno']}

REVISIONES = {'Aŭto': 9505405,
 'Toyota Prius': 9362619,
 'Trabant': 9362627,
 'Elektra aŭtomobilo': 9408222,
 'Ford Modelo T': 8983603,
 'LADA Kalina': 9510800,
 'LADA 110': 9510799,
 'UAZ Patriot': 9452491,
 'Austin FX4': 9464588,
 'LADA Vesta': 8772806,
 'Chevrolet Viva': 8765158,
 'BS Nymph': 7944756,
 'Senŝofora aŭto': 8754591,
 'Tesla Model 3': 9254165,
 'Porsche 911': 9263712,
 'AMC Pacer': 9505445,
 'Chrysler Crossfire': 8770022,
 'Kombinaŭto': 9098716,
 'Koncepta aŭtomobilo': 8273925,
 'Volkswagen Tipo 1': 9329132,
 'Bugatti Veyron': 6095433,
 'Citroën DS': 8920599,
 'Citroën Traction Avant': 9401856,
 'Messerschmitt Kabinenroller': 8363736,
 'BMW Isetta': 7944743,
 'Goggomobil': 8208341,
 'Renault Clio': 8425740,
 'Benz Patent-Motorwagen': 9391564,
 'Kvarciklo Ford': 8972419,
 'Lancia Dilambda': 8312758,
 'Fiat 500': 8175285,
 'Renault 4': 9428890,
 'Citroën': 9364516,
 'Aeroplano': 9419967,
 'Airbus A380': 9494683,
 'Concorde': 9473395,
 'Flyer 1': 9371993,
 'Supermarine Spitfire': 8930107,
 'Aviadilo': 9473384,
 'De Havilland Comet': 9493718,
 'Boeing 737': 8805074,
 'Boeing 777': 9263395,
 'Boeing 767': 9494682,
 'Boeing 707': 9494874,
 'Airbus A330': 8719032,
 'Airbus A300': 8785171,
 'Lockheed C-130 Hercules': 9118165,
 'General Dynamics F-16 Fighting Falcon': 9448264,
 'Boeing B-52 Stratofortress': 8856466,
 'North American P-51 Mustang': 9425695,
 'Lockheed Martin F-35 Lightning II': 9466633,
 'Lockheed Martin F-22 Raptor': 8330104,
 'Airbus A350 XWB': 9410816,
 'Bombaviadilo': 9175530,
 'Ĉasaviadilo': 8650686,
 'Militaviadilo': 9114551,
 'Ultramalpeza aviadilo': 8490419,
 'Biplano': 9360473,
 'Antonov An-124': 9146389,
 'Antonov An-225': 8873173,
 'Junkers Ju 52': 8933384,
 'McDonnell Douglas F-4 Phantom II': 8757602,
 'Messerschmitt Bf 109': 8363735,
 'Grumman F-14 Tomcat': 9065287,
 'Flugo Air France 447': 9435781,
 'Flugo 1549 de US Airways': 9435770,
 'Boeing': 9473361,
 'Airbus': 9473393,
 'Douglas DC-3': 8123220,
 'Boeing 747': 8450053,
 'Boeing 727': 6236153,
 'Boeing 787 Dreamliner': 8805075,
 'Airbus A340': 8718995,
 'Airbus A310': 8785172,
 'Airbus A318': 8748247,
 'Airbus A319': 9496119,
 'Airbus A321': 8718981,
 'McDonnell Douglas MD-11': 9494681,
 'Douglas DC-8': 9285675,
 'Lockheed L-1011 TriStar': 9473358,
 'Tupolev Tu-144': 8487662,
 'Komercaviadilo': 9473355,
 'Glisilo': 9089860,
 'Boeing B-17 Flying Fortress': 8461778,
 'Boeing B-29 Superfortress': 9419948,
 'McDonnell Douglas F-15 Eagle': 8429331,
 'Alerono': 9031506,
 'Fuzelaĝo': 9481613,
 'Tupolev ANT-9': 8487660,
 'Boeing 757': 9496120,
 'Boeing 717': 8719014,
 'Fokker 100': 8180465,
 'Messerschmitt Me 262': 8700457,
 'Iljuŝin Il-76': 8310601,
 'Lockheed P-38 Lightning': 9243777,
 'Trajno': 9502151,
 'Lokomotivo': 9502150,
 'Vaporlokomotivo': 9479913,
 'TGV': 8962726,
 'Ŝinkanseno': 9335000,
 'Grandrapida trajno': 8641100,
 'Ŝvebotrajno': 9439323,
 'Orient-ekspreso': 8924242,
 'Dentorela fervojo': 8817898,
 'Eurostar': 8948537,
 'EuroCity': 8540992,
 'InterCityExpress': 8948521,
 'Intercités': 9325682,
 'Alta Velocidad Española': 9224890,
 'Railjet': 9168853,
 'Z 5300': 7888273,
 'Z 5600': 7888349,
 'Z 20500': 7888282,
 'MI 2N Altéo': 7888274,
 'MI 2N Eole': 8539010,
 'Z 20900': 7888346,
 'Z 50000': 9327595,
 'MI 09': 9422089,
 'RER NG': 8453574,
 'MF 01': 7256380,
 'MF 77': 9482366,
 'MF 88': 8340227,
 'MP 89': 8571160,
 'MP 51': 8444463,
 'MF 19': 9326174,
 'Bulgara ekspresa lokomotivo 1D1': 9432779,
 'Lokomotivo de la serio Ѵ': 9068935,
 'Serioj ER2 kaj ER9 de SZD': 8898663,
 'Pendolino de Fiat Ferroviaria': 8787993,
 'RegioJet': 9451435,
 'Vaporlokomotivriparejo de Meiningen': 9272139,
 'Trajneto de La Rhune': 9504499,
 'Fervojo Stockton kaj Darlington': 9298642,
 'Vaporlokomotivo 52 8055': 8788195,
 'Serio O de SZD': 8784186,
 '242 A1 de SNCF': 9504449,
 'Kuŝvagono': 8301386,
 'Kargotrajno': 9127361,
 'Talgo': 8618426,
 'Tramtrajno': 8568570,
 'Trajnunuo': 9115441,
 'Altrapida fervojo': 8663881,
 'Rodalies de Catalunya': 9314068,
 'Ŝinkansena linio Tōkaidō': 9438116,
 'Fervojo de Sóller': 9241319,
 'Vagono': 9302945,
 'Metroo sur pneŭoj': 9326137,
 'Dizellokomotivo': 9459576,
 'Deutsche Reichsbahn': 9338050,
 'DSB (Danske Statsbaner)': 9151934,
 'Nubotrajno': 8630978}

# Se conservan todos los párrafos ya aprobados en el piloto.
ARTICULOS_PILOTO = ('Aŭto',
 'Toyota Prius',
 'Trabant',
 'Elektra aŭtomobilo',
 'Ford Modelo T',
 'Aeroplano',
 'Airbus A380',
 'Concorde',
 'Flyer 1',
 'Supermarine Spitfire',
 'Trajno',
 'Lokomotivo',
 'Vaporlokomotivo',
 'TGV',
 'Ŝinkanseno')
MAXIMO_POR_ARTICULO = 32



# =============================================================================
# ## 2. Descargar las páginas de Wikipedia
#
# El programa abre la página de cada artículo y conserva su texto principal. El número
# de revisión
# permite volver a consultar la versión usada. Esto evita que una edición posterior
# cambie el texto del
# dataset. Los enlaces de las fuentes se muestran en el paso 4.
#
# [Ayuda de MediaWiki sobre enlaces
# permanentes](https://www.mediawiki.org/wiki/Help:Permanent_link)
# =============================================================================

WIKIPEDIA = "https://eo.wikipedia.org"

sesion = requests.Session()
sesion.headers["User-Agent"] = "CUNEF-Vehiculos/0.2 (Practica docente de Mineria de Textos)"
reintentos = Retry(total=1, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
sesion.mount("https://", HTTPAdapter(max_retries=reintentos))

def descargar_articulo(titulo):
    revision = REVISIONES.get(titulo)
    if revision is None:
        nombre = quote(titulo.replace(" ", "_"), safe="")
        respuesta = sesion.get(f"{WIKIPEDIA}/wiki/{nombre}", timeout=(5, 15))
    else:
        respuesta = sesion.get(
            f"{WIKIPEDIA}/w/index.php",
            params={"title": titulo.replace(" ", "_"), "oldid": revision},
            timeout=(5, 15),
        )
    respuesta.raise_for_status()

    sopa = BeautifulSoup(respuesta.content, "html.parser")
    cuerpo = sopa.select_one("#mw-content-text .mw-parser-output")
    if cuerpo is None:
        raise ValueError("No se encontró el texto principal del artículo.")

    permanente = sopa.select_one("#t-permalink a")
    coincidencia = re.search(r"[?&]oldid=(\d+)", permanente.get("href", "")) if permanente else None
    if coincidencia is None:
        raise ValueError("No se pudo identificar la revisión del artículo.")
    revision_descargada = int(coincidencia.group(1))
    if revision is not None and revision_descargada != revision:
        raise ValueError("Wikipedia devolvió una revisión distinta de la solicitada.")

    enlace = f"{WIKIPEDIA}/w/index.php?oldid={revision_descargada}"
    return str(cuerpo), enlace


# =============================================================================
# ## 3. Separar y limpiar los párrafos
#
# Beautiful Soup lee la estructura de la página. Así podemos quedarnos con los
# párrafos y saltar tablas, fichas, listas, imágenes y referencias. Si una palabra
# tiene un enlace, conservamos la palabra y quitamos el enlace. Sustituimos los puntos y
# coma que estén dentro del texto por comas, porque el punto y coma se usa para separar
# las dos columnas del archivo.
#
# Para preparar el texto, descartamos bloques de menos de seis palabras, frases que solo
# presentan una lista y, en el artículo *Trajno*, la sección sobre otros significados
# de la palabra «tren». También excluimos pasajes concretos del artículo de coches
# eléctricos que tratan de trolebuses, furgonetas o carritos de golf. Estos filtros se
# aplican al descargar los artículos. Todavía puede quedar algún párrafo demasiado
# general que convenga revisar a mano.
#
# En las páginas más amplias, seleccionamos los bloques sobre vehículos. Limitamos a
# 32 párrafos por artículo nuevo para repartir el peso entre más fuentes. La
# selección usa siempre la misma semilla, 42, para poder repetirla.
# =============================================================================

SECCIONES_OMITIDAS = {
    "bildaro", "bibliografio", "eksteraj ligiloj", "fontoj", "galerio",
    "literaturo", "noto", "notoj", "referencoj", "vidu ankaŭ",
}
SECCIONES_POR_ARTICULO = {"Trajno": {"diversaj signifoj"}}
# Revisamos estos pasajes del piloto y los identificamos por su inicio.
INICIOS_OMITIDOS = {
    "Elektra aŭtomobilo": (
        "La 29-an de aprilo de 1882",
        "1990-aj jaroj: EV1",
        "En 1975 aŭ 1976 surbaze",
        "En 1980 oni ekpensis",
        "En 1983 sekvis kamioneto",
        "En 1999 laŭ la mendo de golfo-klubo",
        "En 2002 surbaze de LADA Golf",
        "En 2001-2002 la kompanio Bronto",
    ),
}
RUIDO = (
    "table, figure, figcaption, ul, ol, dl, blockquote, script, style, "
    ".infobox, .navbox, .thumb, .hatnote, .ambox, .reflist, .mw-editsection, "
    ".mw-ref, sup.reference, .mw-cite-backlink, .mw-ext-cite-error, "
    "[typeof~='mw:Extension/ref'], [typeof~='mw:Extension/references']"
)
ENCABEZADOS = {"h2", "h3", "h4", "h5", "h6"}

def extraer_parrafos(html, titulo):
    sopa = BeautifulSoup(html, "html.parser")
    raiz = sopa.select_one(".mw-parser-output") or sopa
    for elemento in raiz.select(RUIDO):
        if elemento.parent is not None:
            elemento.decompose()

    omitidas = SECCIONES_OMITIDAS | SECCIONES_POR_ARTICULO.get(titulo, set())
    nivel_omitido = None
    parrafos = []

    for nodo in raiz.find_all(sorted(ENCABEZADOS) + ["p"]):
        if nodo.name in ENCABEZADOS:
            nivel = int(nodo.name[1])
            if nivel_omitido is None or nivel <= nivel_omitido:
                titulo_seccion = nodo.get_text(" ", strip=True).casefold()
                nivel_omitido = nivel if titulo_seccion in omitidas else None
            continue
        if nivel_omitido is not None:
            continue

        for salto in nodo.find_all("br"):
            salto.replace_with(" ")
        texto = unicodedata.normalize("NFC", nodo.get_text())
        texto = re.sub(r"\[\s*\d+\s*\]", "", texto)
        texto = re.sub(r"(?:https?://|www\.)\S+", "", texto)
        texto = " ".join(texto.replace(";", ",").split())
        if len(texto.split()) < 6 or texto.endswith(":"):
            continue
        if texto.casefold().startswith(("vidu ankaŭ", "dosiero:", "arkivigite je")):
            continue
        if texto.startswith(INICIOS_OMITIDOS.get(titulo, ())):
            continue
        parrafos.append(texto)

    return parrafos

# En páginas amplias, conservamos los párrafos que describen vehículos o su uso.
TERMINOS_TREN = r"trajn|lokomotiv|vagon|ŝinkansen|tgv|materialo rul"
TERMINOS_AVION = r"aviadil|aeroplan|flugil|jetmotor|pilotaŭtomat|boeing\s+\d|airbus\s+a\d"
FUENTES_FERROVIARIAS_AMPLIAS = {
    "Fervoja transporto en Japanio", "Fervojo", "RegioJet", "Deutsche Reichsbahn",
    "DSB (Danske Statsbaner)", "RER de Francilio", "Transilien", "Metroo de Parizo",
    "Rodalies de Catalunya", "Londona Surgrundo", "Juna virina fervojo",
    "Fervoja akcidento de Balvano (1944)", "Fervoja akcidento en Studénka 2008",
    "Fervoja katastrofo de Eschede", "Listo de la serioj de Deutsche Reichsbahn",
    "Ŝinkansena linio Tōkaidō", "Fervoja muzeo Lužná u Rakovníka",
    "Nacia Fervoja Muzeo (Anglio)", "Stadler Rail",
}
FUENTES_AERONAUTICAS_AMPLIAS = {
    "Aviado", "Boeing", "Airbus", "Flugo Air France 447", "Flugo 370 de Malaysia Airlines",
    "Flugo 17 de Malaysia Airlines", "Flugo 9525 de Germanwings", "Flugo 1549 de US Airways",
}

def seleccionar_parrafos(parrafos, titulo):
    # Quitar etiquetas residuales que algunos artículos muestran como texto literal.
    parrafos = [
        " ".join(re.sub(r"</?[a-zA-Z][^<>]*>", "", p).split()) for p in parrafos
    ]
    if titulo in ARTICULOS_PILOTO:
        return parrafos

    if titulo == "Aviadilo":
        # En la revisión fijada, estos bloques tratan de historia y aviones de ala fija.
        intervalos = [(6, 17), (32, 37), (42, 43), (45, 54)]
        parrafos = [
            texto for numero, texto in enumerate(parrafos, start=1)
            if any(inicio <= numero <= fin for inicio, fin in intervalos)
        ]
    if titulo in FUENTES_FERROVIARIAS_AMPLIAS:
        parrafos = [p for p in parrafos if re.search(TERMINOS_TREN, p, re.IGNORECASE)]
    if titulo in FUENTES_AERONAUTICAS_AMPLIAS:
        parrafos = [p for p in parrafos if re.search(TERMINOS_AVION, p, re.IGNORECASE)]

    maximo = 15 if titulo == "Flugo Air France 447" else MAXIMO_POR_ARTICULO
    if len(parrafos) > maximo:
        indices = random.Random(42).sample(range(len(parrafos)), maximo)
        parrafos = [parrafos[i] for i in sorted(indices)]
    return parrafos



# =============================================================================
# ## 4. Poner el tema y comprobar los resultados
#
# Recorremos los artículos de cada grupo, añadimos el tema a cada párrafo y quitamos
# textos repetidos dentro de una clase. Si el mismo párrafo aparece con dos temas
# distintos, se aparta del dataset. El cuaderno muestra cuántos párrafos aporta cada
# artículo al resultado y avisa si una página falla.
#
# El resumen comprueba si las tres categorías superan los 300 párrafos. Aquí la
# etiqueta viene del artículo entero y el programa aplica reglas de limpieza, sin leer
# el significado de cada párrafo.
#
# (En este script, ese paso está dentro de main(), al final del fichero.)
# =============================================================================
# ---------------------------------------------------------------------------
# Medición del ruido
# ---------------------------------------------------------------------------
# La etiqueta de cada párrafo se hereda del artículo, así que hay párrafos genéricos
# ("Ĝi estis fondita en 1950") que no hablan del tema. Como estimación automática,
# contamos los párrafos que NO contienen ninguna raíz típica de su propia clase.
# Es un proxy: sobreestima el ruido (un párrafo puede ser específico sin usar estas
# raíces), así que conviene contrastarlo con una revisión manual de una muestra.
RAICES_CLASE = {
    "coches": r"aŭto|aŭtomobil|ŝofor|stirad|karoseri|kombinaŭt",
    "aviones": r"aviad|aeroplan|flug|pilot|aeroport|alerono|fuzelaĝ",
    "trenes": r"trajn|lokomotiv|fervoj|vagon|\brel|stacidom|metroo|ŝinkansen|tgv",
}


def medir_ruido(dataset):
    tabla = []
    for clase, raices in RAICES_CLASE.items():
        textos = dataset.loc[dataset["class"].eq(clase), "text"]
        sin_raiz = ~textos.str.contains(raices, case=False, regex=True)
        tabla.append((clase, len(textos), int(sin_raiz.sum()), 100 * sin_raiz.mean()))
    return pd.DataFrame(tabla, columns=["class", "parrafos", "sin_raiz_de_clase", "porcentaje"])


def muestra_para_revision_manual(dataset, n=50, semilla=42):
    """Muestra aleatoria por clase para etiquetar a mano como 'especifico' o 'generico'."""
    return dataset.groupby("class", group_keys=False).apply(
        lambda g: g.sample(min(n, len(g)), random_state=semilla)
    )


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------
CARPETA_DATOS = Path(__file__).resolve().parents[1] / "data"


def main():
    registros, fuentes, errores = [], [], []

    for clase, titulos in ARTICULOS.items():
        for titulo in titulos:
            try:
                html, enlace = descargar_articulo(titulo)
                parrafos = seleccionar_parrafos(extraer_parrafos(html, titulo), titulo)
                if not parrafos:
                    raise ValueError("No quedaron párrafos tras la limpieza.")
            except (requests.RequestException, ValueError) as error:
                # Un artículo que falla no detiene el script (requisito: sobrevivir a fallos web).
                errores.append((titulo, str(error)))
                print(f"Aviso · {titulo}: {error}")
                continue

            fuentes.append((clase, titulo, enlace))
            for texto in parrafos:
                registros.append((texto, clase, titulo, enlace))

    origen = pd.DataFrame(registros, columns=["text", "class", "articulo", "fuente"])
    # Un párrafo que aparece con dos clases distintas es ambiguo: se descarta.
    clases_por_texto = origen.groupby("text")["class"].transform("nunique")
    origen = origen.loc[clases_por_texto.eq(1)].drop_duplicates(["text", "class"])
    origen = origen.reset_index(drop=True)
    dataset = origen[["text", "class"]]

    if dataset.empty:
        raise SystemExit("No se recuperó ningún párrafo: no se guarda nada.")

    if dataset["text"].str.contains(r"[;\r\n]|https?://|<[/a-zA-Z]", regex=True).any():
        raise ValueError("Algún párrafo contiene separadores, enlaces o marcas de HTML.")

    completo = not errores and set(dataset["class"]) == set(ARTICULOS)
    CARPETA_DATOS.mkdir(parents=True, exist_ok=True)
    archivo = CARPETA_DATOS / ("dataset.csv" if completo else "dataset_parcial.csv")

    dataset.to_csv(archivo, sep=";", encoding="utf-8", index=False)
    comprobacion = pd.read_csv(archivo, sep=";", encoding="utf-8", keep_default_na=False)
    if not comprobacion.equals(dataset):
        raise ValueError("El CSV guardado no coincide con la tabla preparada.")
    origen.to_csv(CARPETA_DATOS / "metadata.csv", sep=";", encoding="utf-8", index=False)

    print("\nPárrafos por clase")
    print(dataset["class"].value_counts().to_string())
    print(f"Total · {len(dataset)} · Artículos con párrafos · {origen['articulo'].nunique()}")

    print("\nEstimación de ruido (párrafos sin ninguna raíz de su clase)")
    print(medir_ruido(dataset).to_string(index=False, float_format="%.1f"))

    print(f"\nGuardado · {archivo.relative_to(CARPETA_DATOS.parent)} · {len(dataset)} filas")
    if not completo:
        print(f"Resultado PARCIAL: {len(errores)} artículo(s) fallaron. Vuelve a ejecutar el script.")


if __name__ == "__main__":
    main()

# =============================================================================
# Notas originales del cuaderno: guardado y procedencia
# =============================================================================
# ## 5. Guardar vehiculos.csv
#
# Exportamos dos columnas llamadas **text** y **class**. Entre ambas va un punto y coma.
# Usamos **UTF-8** para conservar letras del esperanto como **ĉ**, **ŝ** y **ŭ**. El
# cuaderno vuelve a abrir el archivo para comprobar que se lee exactamente la tabla que
# acabamos de construir.
#
# Si algún artículo falla y se obtienen párrafos, el cuaderno guarda
# **vehiculos_parcial.csv** y muestra un aviso. Cuando se descargan todos los artículos,
# la salida se llama **vehiculos.csv**. Para bajarla en Colab, abre **Archivos**, busca
# el CSV y usa **Descargar** en su menú.
#
# ## Procedencia y revisión
#
# Los textos proceden de quienes contribuyen a **Wikipedia en esperanto**. El paso 4
# muestra los enlaces a las revisiones utilizadas. La adaptación consiste en seleccionar
# párrafos, limpiar marcas y añadir una etiqueta de tema. Al compartir el CSV,
# acompañadlo de este cuaderno para conservar la atribución y el enlace a la licencia.
# [Wikipedia en esperanto](https://eo.wikipedia.org/) · [CC BY-SA
# 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
#
# Esta versión amplía el piloto de 15 artículos. El enunciado recomienda superar los
# 300 párrafos por clase. Como la etiqueta procede del tema del artículo, conviene
# revisar una muestra de cada grupo antes de entrenar el clasificador.
#
# Nota: en este script el archivo se guarda como data/dataset.csv (no vehiculos.csv)
# para seguir el contrato de datos del repositorio.
