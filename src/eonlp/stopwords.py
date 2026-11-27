"""Palabras vacías (stop-words) del esperanto.

Las palabras vacías son las que aparecen muchísimo pero aportan poco al tema de un
texto: artículos, preposiciones, pronombres, conjunciones... (tema 2.2). Para
clasificar un texto se suelen quitar antes de vectorizarlo.

La lista sale del léxico de la guía oficial de la práctica,
resources/vortoj.json (palabras con "ignorinda": true). Ese léxico guarda
raíces, no formas: tiene "mi" pero no "min" ni "mia", y "esti" pero no "estas".
Por eso aquí se generan las formas que faltan con tres reglas de la gramática:

1. Pronombres: acusativo (+n) y posesivo (+a, +aj, +an, +ajn).  mi -> min, mia...
2. Verbos: las terminaciones verbales.                          esti -> estas, estis...
3. Números: ordinales a partir de los cardinales (+a).          unu -> unua, dua...
4. Correlativos: la tabla de 5 prefijos x 9 terminaciones.      kiu, tio, ĉiuj...
"""

import json
from pathlib import Path

ARCHIVO_VORTOJ = Path(__file__).parent / "resources" / "vortoj.json"

# Terminaciones verbales: infinitivo, presente, pasado, futuro, condicional, imperativo.
TERMINACIONES_VERBO = ["i", "as", "is", "os", "us", "u"]

# Tabla de correlativos: 5 prefijos x 9 terminaciones = 45 palabras.
PREFIJOS_CORRELATIVOS = ["ki", "ti", "i", "ĉi", "neni"]
TERMINACIONES_CORRELATIVOS = ["o", "u", "a", "es", "e", "am", "al", "el", "om"]


def cargar_vortoj(archivo=ARCHIVO_VORTOJ):
    """Lee el léxico de la guía (JSON, tema 1.4) y devuelve la lista de palabras.

    Cada palabra es un diccionario con, entre otras, las claves "vorto" (la
    palabra), "kategorio" (su categoría) e "ignorinda" (si es palabra vacía).
    """
    with open(archivo, encoding="utf-8") as fichero:
        return json.load(fichero)["vortoj"]


def formas_pronombre(pronombre):
    """mi -> mi, min, mia, miaj, mian, miajn."""
    return [pronombre + final for final in ["", "n", "a", "aj", "an", "ajn"]]


def formas_verbo(infinitivo):
    """esti -> esti, estas, estis, estos, estus, estu."""
    raiz = infinitivo[:-1]
    return [raiz + final for final in TERMINACIONES_VERBO]


def formas_numero(cardinal):
    """unu -> unu, unua, unuaj, unuan, unuajn (el ordinal es el cardinal + -a)."""
    return [cardinal + final for final in ["", "a", "aj", "an", "ajn"]]


def formas_correlativos():
    """Las 45 palabras de la tabla y sus formas con -j / -n.

    Según la gramática de la guía: los de -u y -a toman -j y -n (kiuj, tiujn),
    los de -o solo -n (kion) y los de -e solo -n de dirección (kien).
    """
    formas = []
    for prefijo in PREFIJOS_CORRELATIVOS:
        for final in TERMINACIONES_CORRELATIVOS:
            palabra = prefijo + final
            formas.append(palabra)
            if final in ("u", "a"):
                formas += [palabra + "j", palabra + "n", palabra + "jn"]
            elif final in ("o", "e"):
                formas.append(palabra + "n")
    return formas


def crear_stop_words(vortoj):
    """Construye el conjunto completo de palabras vacías a partir del léxico."""
    stop_words = set()
    for entrada in vortoj:
        if not entrada.get("ignorinda"):
            continue
        palabra = entrada["vorto"]
        if entrada["kategorio"] == "pronomo":
            stop_words.update(formas_pronombre(palabra))
        elif entrada["kategorio"] == "verboformo":
            stop_words.update(formas_verbo(palabra))
        elif entrada["kategorio"] == "nombro":
            stop_words.update(formas_numero(palabra))
        else:
            stop_words.add(palabra)
    stop_words.update(formas_correlativos())
    return stop_words


STOP_WORDS = crear_stop_words(cargar_vortoj())


def is_stop(word):
    """True si la palabra es una palabra vacía (sin distinguir mayúsculas).

    Examples:
        >>> is_stop("La"), is_stop("estas"), is_stop("tiujn"), is_stop("trajno")
        (True, True, True, False)
    """
    return word.lower() in STOP_WORDS
