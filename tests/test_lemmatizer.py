import pytest

import eonlp
from eonlp.lemmatizer import LEMAS_GRAMATICALES, lemma_verbo, lemmatize, quitar_flexion


def lemas(texto):
    return [(token.text, token.lemma_) for token in eonlp.load()(texto) if not token.is_punct]


# --- Sustantivos y adjetivos: se quitan -n y -j --------------------------------

@pytest.mark.parametrize("palabra, esperado", [
    ("trajno", "trajno"), ("trajnoj", "trajno"), ("trajnon", "trajno"), ("trajnojn", "trajno"),
    ("rapida", "rapida"), ("rapidaj", "rapida"), ("rapidan", "rapida"), ("rapidajn", "rapida"),
    ("29-an", "29-a"),
])
def test_sustantivos_y_adjetivos(palabra, esperado):
    assert lemmatize(palabra) == esperado


# --- Verbos: la terminación de tiempo o modo pasa a -i -------------------------

@pytest.mark.parametrize("palabra, esperado", [
    ("veturas", "veturi"), ("veturis", "veturi"), ("veturos", "veturi"),
    ("veturus", "veturi"), ("veturu", "veturi"), ("veturi", "veturi"),
    ("estas", "esti"), ("havis", "havi"),
])
def test_verbos(palabra, esperado):
    assert lemmatize(palabra) == esperado


# --- Palabras gramaticales --------------------------------------------------------

@pytest.mark.parametrize("palabra, esperado", [
    ("min", "mi"), ("ŝin", "ŝi"), ("ilin", "ili"),
    ("mia", "mia"), ("miaj", "mia"), ("miajn", "mia"),
    ("kiu", "kiu"), ("kiuj", "kiu"), ("tiujn", "tiu"), ("kion", "kio"), ("kien", "kie"),
    ("unuan", "unua"), ("duaj", "dua"), ("tri", "tri"),
    ("l'", "la"),
])
def test_palabras_gramaticales(palabra, esperado):
    assert lemmatize(palabra) == esperado


@pytest.mark.parametrize("palabra", ["la", "en", "kaj", "ne", "tre", "rapide", "1950", "."])
def test_palabras_que_no_cambian(palabra):
    assert lemmatize(palabra) == palabra


def test_tabla_gramatical_incluye_los_correlativos():
    assert LEMAS_GRAMATICALES["neniujn"] == "neniu"
    assert LEMAS_GRAMATICALES["ĉies"] == "ĉies"


# --- Mayúsculas y nombres propios ------------------------------------------------

def test_lema_en_minusculas():
    assert lemmatize("Trajnoj", "NOUN") == "trajno"


def test_nombres_propios_conservan_la_mayuscula():
    assert lemmatize("Parizon", "PROPN") == "Parizo"
    assert lemmatize("Boeing", "PROPN") == "Boeing"
    assert lemmatize("TGV", "PROPN") == "TGV"


# --- Lematización frente a stemming (tema 2.2) ------------------------------------

def test_conserva_los_afijos():
    # El lema es la palabra de diccionario, no la raíz: no se quitan -ist-, -in-.
    assert lemmatize("instruistinoj") == "instruistino"
    assert lemmatize("pasaĝeraviadiloj") == "pasaĝeraviadilo"


def test_funciones_auxiliares():
    assert quitar_flexion("librojn") == "libro"
    assert lemma_verbo("kantos") == "kanti"


# --- Integración con el Doc: ejemplos de la gramática de la guía -----------------

def test_ejemplo_de_la_guia():
    assert lemas("La juna instruistino legas interesan libron.") == [
        ("La", "la"), ("juna", "juna"), ("instruistino", "instruistino"),
        ("legas", "legi"), ("interesan", "interesa"), ("libron", "libro"),
    ]


def test_segundo_ejemplo_de_la_guia():
    assert lemas("Ĉiuj miaj amikoj legas tiujn librojn.") == [
        ("Ĉiuj", "ĉiu"), ("miaj", "mia"), ("amikoj", "amiko"),
        ("legas", "legi"), ("tiujn", "tiu"), ("librojn", "libro"),
    ]


def test_la_frase_inicial_usa_la_categoria_del_etiquetador():
    doc = eonlp.load()("Trajnoj veturas al Parizo.")
    assert [token.lemma_ for token in doc] == ["trajno", "veturi", "al", "Parizo", "."]
