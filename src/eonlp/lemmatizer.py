"""Lematizador basado en reglas para Esperanto.

El lema es la forma de diccionario de una palabra (tema 2.2): la que buscarías en
un diccionario. Lematizar no es lo mismo que hacer stemming:

    stemming:      librojn -> libr     (solo la raíz, aunque no sea una palabra)
    lematización:  librojn -> libro    (la palabra de diccionario)

Como la morfología del esperanto no tiene excepciones, basta con las reglas de la
gramática de la guía. Se aplican según la categoría que ya puso el etiquetador:

1. Palabras gramaticales (pronombres, correlativos, ordinales): se buscan en una
   tabla generada con las mismas reglas que las stop-words.
       min -> mi    miajn -> mia    tiujn -> tiu    kion -> kio    unuan -> unua
2. Verbos: la terminación de tiempo o modo se cambia por -i.
       kantis -> kanti    estas -> esti    veturu -> veturi
3. Sustantivos y adjetivos: se quitan -n (acusativo) y -j (plural).
       librojn -> libro    rapidajn -> rapida
4. Nombres propios: se quita el acusativo y se conserva la mayúscula.
       Parizon -> Parizo
5. Lo demás (adverbios, preposiciones, números, signos...) no cambia, solo se
   pasa a minúsculas.

Los afijos no se quitan: "instruistino" (instru-ist-in-o, profesora) es su propio
lema, porque es una palabra distinta de "instrui" (enseñar).
"""

from eonlp.stopwords import (
    PREFIJOS_CORRELATIVOS,
    TERMINACIONES_CORRELATIVOS,
    cargar_vortoj,
    formas_numero,
    formas_pronombre,
)
from eonlp.tagger import tag

TERMINACIONES_VERBO = ("as", "is", "os", "us", "u", "i")


def crear_lemas_gramaticales():
    """Diccionario forma -> lema para pronombres, correlativos y ordinales."""
    lemas = {}
    for entrada in cargar_vortoj():
        palabra = entrada["vorto"]
        if entrada["kategorio"] == "pronomo":
            # mi, min -> mi    mia, miaj, mian, miajn -> mia
            for forma in formas_pronombre(palabra):
                lemas[forma] = palabra if forma in (palabra, palabra + "n") else palabra + "a"
        elif entrada["kategorio"] == "nombro":
            # unu -> unu    unua, unuaj, unuan, unuajn -> unua
            for forma in formas_numero(palabra):
                lemas[forma] = palabra if forma == palabra else palabra + "a"

    # kiu, kiuj, kiun, kiujn -> kiu    kio, kion -> kio    kie, kien -> kie
    for prefijo in PREFIJOS_CORRELATIVOS:
        for final in TERMINACIONES_CORRELATIVOS:
            correlativo = prefijo + final
            for extra in ["", "j", "n", "jn"]:
                lemas[correlativo + extra] = correlativo

    lemas["l'"] = "la"
    return lemas


LEMAS_GRAMATICALES = crear_lemas_gramaticales()


def quitar_flexion(palabra):
    """Quita el acusativo (-n) y después el plural (-j): librojn -> libro."""
    if palabra.endswith("n") and len(palabra) > 2:
        palabra = palabra[:-1]
    if palabra.endswith("j") and len(palabra) > 2:
        palabra = palabra[:-1]
    return palabra


def lemma_verbo(palabra):
    """Cambia la terminación de tiempo o modo por -i: kantis -> kanti."""
    for final in TERMINACIONES_VERBO:
        if palabra.endswith(final):
            return palabra[: -len(final)] + "i"
    return palabra


def lemmatize(word, pos=""):
    """Devuelve el lema (forma de diccionario) de una palabra.

    Args:
        word: el texto del token.
        pos: su categoría gramatical (NOUN, VERB...). Si no se indica, se calcula
            con el etiquetador.

    Returns:
        El lema, en minúsculas salvo en los nombres propios.

    Examples:
        >>> [lemmatize(p) for p in ["librojn", "kantis", "rapidajn", "min", "tiujn"]]
        ['libro', 'kanti', 'rapida', 'mi', 'tiu']
    """
    if not pos:
        pos = tag(word)
    palabra = word.lower()

    if palabra in LEMAS_GRAMATICALES:
        return LEMAS_GRAMATICALES[palabra]
    if pos in ("VERB", "AUX"):
        return lemma_verbo(palabra)
    if pos in ("NOUN", "ADJ"):
        return quitar_flexion(palabra)
    if pos == "PROPN":
        # Parizon -> Parizo, pero Boeing, TGV o A380 se quedan igual.
        if word.endswith(("on", "ojn", "oj")):
            return quitar_flexion(word)
        return word
    return palabra
