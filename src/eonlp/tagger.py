"""Etiquetador de categorías gramaticales (POS) basado en reglas.

Asigna a cada token una etiqueta universal, las mismas que usa spaCy (tema 2.2):
NOUN, VERB, AUX, ADJ, ADV, PRON, DET, ADP, CCONJ, SCONJ, PART, NUM, INTJ,
PROPN, PUNCT y X (desconocida).

Se aplican las reglas en este orden, de la más segura a la más general:

1. Signos y números: PUNCT y NUM.
2. Palabras gramaticales (clases cerradas): se buscan en el léxico de la guía
   (vortoj.json), con las formas que genera el módulo de stop-words
   (pronombres, verbos auxiliares, ordinales y correlativos).
   También abreviaturas (ekz. = ekzemple) y unidades (km, kg).
3. Palabras gramaticales con prefijo (sección "Afijos" de la guía): malpli es
   mal- + pli, así que lleva la etiqueta de pli (ADV); ekde = ek- + de (ADP).
4. Nombres propios: siglas (TGV), nombres con cifras (A380, F-16) y palabras en
   mayúscula que no empiezan la frase (Boeing, Parizo).
5. Terminación de la palabra, la regla central de la gramática de la guía: la
   vocal final marca la categoría, después de quitar -j (plural) y -n (acusativo).
       -o -> NOUN    -a -> ADJ    -e -> ADV    -i -as -is -os -us -u -> VERB
   Además, -aŭ es la terminación de muchos adverbios primitivos (almenaŭ).
6. Si nada encaja: X.
"""

from eonlp.stopwords import (
    PREFIJOS_CORRELATIVOS,
    TERMINACIONES_CORRELATIVOS,
    cargar_vortoj,
    formas_numero,
    formas_pronombre,
    formas_verbo,
)

# Categorías del léxico de la guía -> etiquetas universales.
CATEGORIA_A_POS = {
    "artikolo": "DET",
    "prepozicio": "ADP",
    "konjunkcio": "CCONJ",
    "pronomo": "PRON",
    "adverbo": "ADV",
    "partikulo": "PART",
    "verboformo": "VERB",
    "nombro": "NUM",
    "interjekcio": "INTJ",
    "ĝentilaĵo": "INTJ",
    "titolo": "NOUN",
}
# Conjunciones que introducen una oración subordinada ("ke" = que, "se" = si...).
SUBORDINANTES = {"ke", "se", "ĉar", "kvankam", "kvazaŭ"}
# "esti" (ser, estar) funciona como verbo auxiliar.
AUXILIARES = {"esti"}

TERMINACIONES_VERBO = ("as", "is", "os", "us", "i", "u")
PREFIJOS = ("mal", "ek")
# Abreviaturas del tokenizador, con la categoría de la palabra completa.
ABREVIATURAS = {
    "ekz.": "ADV", "t.e.": "ADV", "ĉ.": "ADV", "ktp.": "ADV", "k.t.p.": "ADV",
    "i.a.": "ADV", "inkl.": "ADV", "vd.": "VERB",
}
# Unidades de medida frecuentes en los artículos de vehículos.
UNIDADES = {"km", "m", "cm", "mm", "kg", "t", "h", "s", "kw", "kv", "kvt", "ĉp", "l"}
# Correlativos según su terminación: cosa/persona -> pronombre, clase/posesión ->
# determinante, lugar/tiempo/razón/manera/cantidad -> adverbio.
POS_CORRELATIVO = {
    "o": "PRON", "u": "PRON", "a": "DET", "es": "DET",
    "e": "ADV", "am": "ADV", "al": "ADV", "el": "ADV", "om": "ADV",
}


def crear_lexicon() -> dict:
    """Diccionario palabra -> etiqueta para todas las palabras gramaticales."""
    lexicon = {}
    for entrada in cargar_vortoj():
        palabra = entrada["vorto"]
        categoria = entrada["kategorio"]
        pos = CATEGORIA_A_POS[categoria]

        if categoria == "konjunkcio" and palabra in SUBORDINANTES:
            lexicon[palabra] = "SCONJ"
        elif categoria == "pronomo":
            # mi, min -> PRON; mia, miaj, mian, miajn (posesivos) -> DET
            for forma in formas_pronombre(palabra):
                lexicon[forma] = "PRON" if forma in (palabra, palabra + "n") else "DET"
        elif categoria == "verboformo":
            for forma in formas_verbo(palabra):
                lexicon[forma] = "AUX" if palabra in AUXILIARES else "VERB"
        elif categoria == "nombro":
            # unu -> NUM; unua, unuaj, unuan, unuajn (ordinales) -> ADJ
            for forma in formas_numero(palabra):
                lexicon[forma] = "NUM" if forma == palabra else "ADJ"
        else:
            lexicon[palabra] = pos

    for prefijo in PREFIJOS_CORRELATIVOS:
        for final, pos in POS_CORRELATIVO.items():
            palabra = prefijo + final
            for extra in ["", "j", "n", "jn"]:
                lexicon[palabra + extra] = pos

    lexicon["l'"] = "DET"           # artículo con elisión
    lexicon.update(ABREVIATURAS)
    for unidad in UNIDADES:
        lexicon[unidad] = "NOUN"
    return lexicon


LEXICON = crear_lexicon()


def _es_numero(word: str) -> bool:
    """Sin letras y con alguna cifra: 1950, 3,5, 1.000, 0-4-0, 16⅔."""
    return not any(c.isalpha() for c in word) and any(c.isnumeric() for c in word)


def _por_prefijo(palabra: str) -> str:
    """malpli -> la etiqueta de pli; ekde -> la de de."""
    for prefijo in PREFIJOS:
        resto = palabra[len(prefijo):]
        if palabra.startswith(prefijo) and resto in LEXICON:
            return LEXICON[resto]
    return ""


def _es_nombre_propio(word: str, inicio_frase: bool) -> bool:
    tiene_letras = any(c.isalpha() for c in word)
    tiene_cifras = any(c.isdigit() for c in word)
    if tiene_letras and tiene_cifras and word[0].isupper():      # A380, F-16, B-52
        return True
    if len(word) > 1 and word.isupper():                          # TGV, SNCF
        return True
    return word[0].isupper() and not inicio_frase                 # Boeing, Parizo


def _por_terminacion(word: str) -> str:
    """Categoría según la terminación (regla de la gramática de la guía)."""
    palabra = word.lower()
    if len(palabra) < 3:
        return ""
    if palabra.endswith(TERMINACIONES_VERBO):
        return "VERB"
    if palabra.endswith("n"):           # acusativo: librojn -> libroj
        palabra = palabra[:-1]
    if palabra.endswith("j"):           # plural: libroj -> libro
        palabra = palabra[:-1]
    if palabra.endswith("o"):
        return "NOUN"
    if palabra.endswith("a"):
        return "ADJ"
    if palabra.endswith(("e", "aŭ")):
        return "ADV"
    return ""


def tag(word: str, inicio_frase: bool = False) -> str:
    """Devuelve la categoría gramatical universal de una palabra.

    Args:
        word: el texto del token.
        inicio_frase: True si es la primera palabra de la frase. Sirve para no
            tomar por nombre propio una palabra que lleva mayúscula solo por
            empezar la frase.

    Returns:
        Una etiqueta universal: NOUN, VERB, ADJ, ADV, PRON, DET, ADP...

    Examples:
        >>> [tag(p) for p in ["la", "trajno", "rapida", "veturas", "tre", "rapide", "."]]
        ['DET', 'NOUN', 'ADJ', 'VERB', 'ADV', 'ADV', 'PUNCT']
    """
    if not any(c.isalnum() for c in word):
        return "PUNCT"
    if _es_numero(word):
        return "NUM"

    minuscula = word.lower()
    if minuscula in LEXICON:
        return LEXICON[minuscula]
    if _por_prefijo(minuscula):
        return _por_prefijo(minuscula)
    if _es_nombre_propio(word, inicio_frase):
        return "PROPN"

    por_terminacion = _por_terminacion(word)
    if por_terminacion:
        return por_terminacion
    if word[0].isupper():               # mayúscula al inicio de frase y sin terminación
        return "PROPN"                  # esperanta: Boeing, Airbus...
    return "X"
