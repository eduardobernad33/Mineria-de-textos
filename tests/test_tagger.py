import pytest

import eonlp
from eonlp.tagger import LEXICON, tag


def etiquetas(texto):
    return [(token.text, token.pos_) for token in eonlp.load()(texto)]


# --- Regla central: la terminación marca la categoría --------------------------

@pytest.mark.parametrize("palabra, esperado", [
    ("trajno", "NOUN"), ("trajnoj", "NOUN"), ("trajnon", "NOUN"), ("trajnojn", "NOUN"),
    ("rapida", "ADJ"), ("rapidaj", "ADJ"), ("rapidan", "ADJ"), ("rapidajn", "ADJ"),
    ("rapide", "ADV"),
    ("veturi", "VERB"), ("veturas", "VERB"), ("veturis", "VERB"),
    ("veturos", "VERB"), ("veturus", "VERB"), ("veturu", "VERB"),
])
def test_terminaciones(palabra, esperado):
    assert tag(palabra) == esperado


# --- Palabras gramaticales (léxico de la guía) ---------------------------------

@pytest.mark.parametrize("palabra, esperado", [
    ("la", "DET"), ("l'", "DET"),
    ("en", "ADP"), ("al", "ADP"), ("de", "ADP"), ("por", "ADP"),
    ("kaj", "CCONJ"), ("sed", "CCONJ"), ("ke", "SCONJ"), ("se", "SCONJ"),
    ("mi", "PRON"), ("min", "PRON"), ("mia", "DET"), ("miajn", "DET"),
    ("estas", "AUX"), ("estis", "AUX"), ("havas", "VERB"), ("povis", "VERB"),
    ("tri", "NUM"), ("unua", "ADJ"), ("dua", "ADJ"),
    ("ne", "PART"), ("ankaŭ", "ADV"),
])
def test_lexicon(palabra, esperado):
    assert tag(palabra) == esperado


@pytest.mark.parametrize("palabra, esperado", [
    ("kio", "PRON"), ("kiu", "PRON"), ("tiujn", "PRON"),
    ("kia", "DET"), ("ties", "DET"),
    ("kie", "ADV"), ("kiam", "ADV"), ("tiel", "ADV"), ("neniom", "ADV"), ("kien", "ADV"),
])
def test_correlativos(palabra, esperado):
    assert tag(palabra) == esperado


def test_lexicon_tiene_los_45_correlativos():
    from eonlp.stopwords import PREFIJOS_CORRELATIVOS, TERMINACIONES_CORRELATIVOS
    for prefijo in PREFIJOS_CORRELATIVOS:
        for final in TERMINACIONES_CORRELATIVOS:
            assert prefijo + final in LEXICON


# --- Afijos, abreviaturas, unidades y números ----------------------------------

@pytest.mark.parametrize("palabra, esperado", [
    ("malpli", "ADV"),      # mal- + pli
    ("ekde", "ADP"),        # ek- + de
    ("almenaŭ", "ADV"),     # adverbio primitivo en -aŭ
    ("ekz.", "ADV"),
    ("km", "NOUN"),
])
def test_afijos_abreviaturas_y_unidades(palabra, esperado):
    assert tag(palabra) == esperado


@pytest.mark.parametrize("palabra", ["1950", "3,5", "1.000", "0-4-0", "16⅔"])
def test_numeros(palabra):
    assert tag(palabra) == "NUM"


@pytest.mark.parametrize("signo", [".", ",", "(", "«", "..."])
def test_puntuacion(signo):
    assert tag(signo) == "PUNCT"


# --- Nombres propios ------------------------------------------------------------

@pytest.mark.parametrize("palabra", ["TGV", "SNCF", "A380", "F-16", "B-52"])
def test_siglas_y_modelos(palabra):
    assert tag(palabra) == "PROPN"


def test_mayuscula_en_medio_de_la_frase_es_nombre_propio():
    assert tag("Parizo") == "PROPN"
    assert tag("Boeing") == "PROPN"


def test_mayuscula_al_inicio_de_frase_usa_la_terminacion():
    assert tag("Trajnoj", inicio_frase=True) == "NOUN"
    assert tag("Boeing", inicio_frase=True) == "PROPN"     # sin terminación esperanta


def test_palabra_extranjera_es_x():
    assert tag("hatchback") == "X"


# --- Integración con el Doc: ejemplos de la gramática de la guía ----------------

def test_ejemplo_de_la_guia():
    assert etiquetas("La juna instruistino legas interesan libron.") == [
        ("La", "DET"), ("juna", "ADJ"), ("instruistino", "NOUN"), ("legas", "VERB"),
        ("interesan", "ADJ"), ("libron", "NOUN"), (".", "PUNCT"),
    ]


def test_frase_del_dataset():
    assert etiquetas("Boeing konstruis la aviadilon en Usono.") == [
        ("Boeing", "PROPN"), ("konstruis", "VERB"), ("la", "DET"), ("aviadilon", "NOUN"),
        ("en", "ADP"), ("Usono", "PROPN"), (".", "PUNCT"),
    ]


def test_inicio_de_cada_frase_tras_comillas():
    doc = eonlp.load()("«Trajnoj veturas.» Aŭtoj ankaŭ.")
    assert doc[1].pos_ == "NOUN"        # "Trajnoj" empieza la frase, tras «
    assert doc[5].pos_ == "NOUN"        # "Aŭtoj" empieza la segunda frase
