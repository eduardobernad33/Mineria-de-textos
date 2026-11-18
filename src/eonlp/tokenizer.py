"""Tokenizador basado en reglas para Esperanto.

Tres pasos, siguiendo el tema 2.2 (NLP) de la asignatura:

1. normalize: dejar el texto en una forma única (Unicode NFC y sistema x).
2. tokenize: dividir el texto en tokens (palabras, números y signos).
3. split_sentences: agrupar los tokens en frases.

Como en los apuntes, el tokenizador consulta primero un pequeño lexicón de casos
especiales (abreviaturas como "ekz." o "k.t.p.") y aplica la regla de la
coincidencia más larga (longest-match). Lo demás se separa con expresiones
regulares (tema 1.3).
"""

import re
import unicodedata

# ---------------------------------------------------------------------------
# 1. Normalización
# ---------------------------------------------------------------------------

# Sistema x: forma de escribir en ASCII las letras con acento circunflejo cuando
# el teclado no las tiene (cx = ĉ, gx = ĝ...). En esperanto no existe la letra x,
# así que "cx" siempre significa "ĉ".
SISTEMA_X = {
    "cx": "ĉ", "gx": "ĝ", "hx": "ĥ", "jx": "ĵ", "sx": "ŝ", "ux": "ŭ",
    "Cx": "Ĉ", "Gx": "Ĝ", "Hx": "Ĥ", "Jx": "Ĵ", "Sx": "Ŝ", "Ux": "Ŭ",
    "CX": "Ĉ", "GX": "Ĝ", "HX": "Ĥ", "JX": "Ĵ", "SX": "Ŝ", "UX": "Ŭ",
}
LETRAS_CON_ACENTO = "ĉĝĥĵŝŭĈĜĤĴŜŬ"


def normalize(text: str) -> str:
    """Devuelve el texto en una forma única para que la misma palabra se escriba igual.

    - Unicode NFC: una letra como "ĉ" puede venir como un solo carácter o como
      "c" + acento combinado. NFC deja siempre un único carácter.
    - Sistema x: convierte "cx" en "ĉ", "ux" en "ŭ", etc. Solo se aplica si el
      texto no tiene ya letras con acento, para no estropear palabras extranjeras
      de un texto normal (por ejemplo "Linux").

    Args:
        text: texto en esperanto.

    Returns:
        El texto normalizado.

    Examples:
        >>> normalize("La sxipo estas cxe la haveno")
        'La ŝipo estas ĉe la haveno'
    """
    text = unicodedata.normalize("NFC", text)
    if not any(letra in text for letra in LETRAS_CON_ACENTO):
        for ascii_x, letra in SISTEMA_X.items():
            text = text.replace(ascii_x, letra)
    return text


# ---------------------------------------------------------------------------
# 2. Tokenización
# ---------------------------------------------------------------------------

# Lexicón de abreviaturas: llevan punto, pero el punto forma parte de la palabra
# y no termina la frase. Se guardan también con la primera letra en mayúscula
# por si empiezan una frase.
ABREVIATURAS = [
    # esperanto
    "k.t.p.", "ktp.", "k.c.", "kc.", "ekz.", "t.e.", "t.n.", "i.a.", "vd.", "inkl.",
    "trad.", "p.K.", "a.K.", "a.n.e.", "n.e.", "jc.", "ĉ.", "pp.", "p.", "n.",
    # nombres propios y referencias que aparecen en artículos de vehículos
    "Mk.", "Co.", "Ref.", "Nr.", "St.",
]
ABREVIATURAS = ABREVIATURAS + [a[0].upper() + a[1:] for a in ABREVIATURAS]

# Longest-match: se ordenan de más larga a más corta para que "k.t.p." gane a "p.".
_ABREVIATURAS_ORDENADAS = sorted(set(ABREVIATURAS), key=len, reverse=True)

# Cada alternativa del patrón es una regla. Se prueban en orden, de la más
# específica a la más general:
PATRON_TOKEN = re.compile(
    "|".join(re.escape(abreviatura) for abreviatura in _ABREVIATURAS_ORDENADAS)
    + r"|\d+(?:[.,]\d+)+"     # números con separador: 1.000, 3,5
    + r"|[Ll]['’]"            # artículo con elisión: "de l' mondo" = "de la mondo"
    + r"|\w+(?:-\w+)*"        # palabras, también con guion: 29-an, F-16, s-ro
    + r"|\.\.\.|…"            # puntos suspensivos
    + r"|[^\w\s]"             # cualquier otro signo, de uno en uno: . , ; ( ) « »
)


def tokenize(text: str) -> list:
    """Divide un texto en tokens.

    Args:
        text: texto ya normalizado.

    Returns:
        Lista de pares (token, posición), donde la posición es el índice del
        primer carácter del token dentro del texto.

    Examples:
        >>> [t for t, _ in tokenize("La trajno, ekz. TGV, veturas 320 km/h.")]
        ['La', 'trajno', ',', 'ekz.', 'TGV', ',', 'veturas', '320', 'km', '/', 'h', '.']
    """
    return [(m.group(), m.start()) for m in PATRON_TOKEN.finditer(text)]


# ---------------------------------------------------------------------------
# 3. División en frases
# ---------------------------------------------------------------------------

FINALES_DE_FRASE = {".", "!", "?", "...", "…"}
# Signos que, justo después del punto, todavía pertenecen a la misma frase.
CIERRES = {")", "]", "»", "”", '"', "'"}
# Abreviaturas que muchas veces cierran una frase ("...k.t.p. Poste...").
ABREVIATURAS_FINALES = {"k.t.p.", "ktp."}


def _es_inicial(token: str) -> bool:
    """True si el token es una sola letra mayúscula, como la "J" de "J. Smith"."""
    return len(token) == 1 and token.isupper()


def split_sentences(tokens: list) -> list:
    """Agrupa los tokens en frases.

    Una frase termina en ".", "!", "?" o "...", salvo que el punto vaya detrás de
    una inicial ("J. Smith") o delante de una palabra en minúscula. Las
    abreviaturas del lexicón no cortan la frase, excepto "k.t.p." si la palabra
    siguiente empieza por mayúscula.

    Args:
        tokens: lista con el texto de cada token.

    Returns:
        Lista de pares (inicio, fin) con las posiciones de los tokens de cada
        frase; "fin" no se incluye, como en los slices de Python.

    Examples:
        >>> split_sentences(["Ĝi", "venis", ".", "Ni", "iris", "."])
        [(0, 3), (3, 6)]
    """
    limites = []
    inicio = 0
    i = 0
    while i < len(tokens):
        token = tokens[i]
        es_final = token in FINALES_DE_FRASE
        if token == "." and i > 0 and _es_inicial(tokens[i - 1]):
            es_final = False
        # En esperanto la frase siguiente empieza en mayúscula: si después del
        # punto viene una palabra en minúscula, el punto era de una abreviatura.
        if token == "." and i + 1 < len(tokens) and tokens[i + 1][0].islower():
            es_final = False
        if token in ABREVIATURAS_FINALES and i + 1 < len(tokens) and tokens[i + 1][0].isupper():
            es_final = True

        if es_final:
            # Las comillas o paréntesis que cierran van con la frase anterior.
            while i + 1 < len(tokens) and tokens[i + 1] in CIERRES:
                i += 1
            limites.append((inicio, i + 1))
            inicio = i + 1
        i += 1

    if inicio < len(tokens):
        limites.append((inicio, len(tokens)))
    return limites
