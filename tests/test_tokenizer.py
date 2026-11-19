import pytest

from eonlp.tokenizer import normalize, split_sentences, tokenize


def textos(texto):
    """Solo el texto de cada token, sin su posición."""
    return [token for token, _ in tokenize(texto)]


# --- normalize ---------------------------------------------------------------

def test_normalize_une_letra_y_acento_combinado():
    compuesta = "ĉiu"          # "c" + acento circunflejo combinado
    assert normalize(compuesta) == "ĉiu"
    assert len(normalize(compuesta)) == 3


@pytest.mark.parametrize("entrada, esperado", [
    ("cxiu", "ĉiu"),
    ("sxipo", "ŝipo"),
    ("Gxi estas auxto", "Ĝi estas aŭto"),
    ("CXEFURBO", "ĈEFURBO"),
])
def test_normalize_sistema_x(entrada, esperado):
    assert normalize(entrada) == esperado


def test_normalize_no_cambia_x_si_el_texto_ya_tiene_acentos():
    assert normalize("Ĝi uzas Linux") == "Ĝi uzas Linux"


# --- tokenize ----------------------------------------------------------------

def test_tokenize_frase_simple():
    assert textos("La trajno veturas.") == ["La", "trajno", "veturas", "."]


def test_tokenize_devuelve_la_posicion_de_cada_token():
    texto = "La aŭto haltis."
    for token, posicion in tokenize(texto):
        assert texto[posicion:posicion + len(token)] == token


@pytest.mark.parametrize("texto, esperado", [
    ("Airbus A380", ["Airbus", "A380"]),                      # letras y números juntos
    ("la 29-an de aprilo", ["la", "29-an", "de", "aprilo"]),  # palabra con guion
    ("F-16 kaj B-52", ["F-16", "kaj", "B-52"]),
    ("3,5 metrojn", ["3,5", "metrojn"]),                      # decimal
    ("1.000 pasaĝeroj", ["1.000", "pasaĝeroj"]),              # miles
    ("en 1950.", ["en", "1950", "."]),                        # el punto final se separa
])
def test_tokenize_numeros_y_guiones(texto, esperado):
    assert textos(texto) == esperado


@pytest.mark.parametrize("texto, esperado", [
    ("aviadiloj, ekz. Boeing", ["aviadiloj", ",", "ekz.", "Boeing"]),
    ("trajnoj, aŭtoj k.t.p.", ["trajnoj", ",", "aŭtoj", "k.t.p."]),
    ("en la 20-a jc.", ["en", "la", "20-a", "jc."]),
])
def test_tokenize_abreviaturas_del_lexicon(texto, esperado):
    assert textos(texto) == esperado


def test_tokenize_longest_match_gana_la_abreviatura_mas_larga():
    assert textos("k.t.p.") == ["k.t.p."]


def test_tokenize_puntuacion():
    assert textos("(«Eurostar») ...") == ["(", "«", "Eurostar", "»", ")", "..."]


def test_tokenize_elision_del_articulo():
    assert textos("de l' mondo") == ["de", "l'", "mondo"]


def test_tokenize_letras_esperanto():
    assert textos("ŝipo ĉiuj ĝi ĥoro ĵaŭdo aŭto") == [
        "ŝipo", "ĉiuj", "ĝi", "ĥoro", "ĵaŭdo", "aŭto",
    ]


def test_tokenize_texto_vacio():
    assert tokenize("") == []


# --- split_sentences ---------------------------------------------------------

def test_split_sentences_dos_frases():
    tokens = ["Ĝi", "venis", ".", "Ni", "iris", "."]
    assert split_sentences(tokens) == [(0, 3), (3, 6)]


def test_split_sentences_signos_de_interrogacion_y_exclamacion():
    tokens = ["Ĉu", "vi", "venas", "?", "Jes", "!"]
    assert split_sentences(tokens) == [(0, 4), (4, 6)]


def test_split_sentences_no_corta_tras_una_inicial():
    tokens = textos("J. Smith konstruis la lokomotivon.")
    assert len(split_sentences(tokens)) == 1


def test_split_sentences_no_corta_en_abreviaturas():
    tokens = textos("Kelkaj aviadiloj, ekz. Concorde, estis rapidaj.")
    assert len(split_sentences(tokens)) == 1


def test_split_sentences_no_corta_si_sigue_minuscula():
    # "Xyz." no está en el lexicón, pero la palabra siguiente va en minúscula.
    tokens = ["Ili", "fondis", "Xyz", ".", "en", "1916", "."]
    assert split_sentences(tokens) == [(0, 7)]


def test_split_sentences_frase_real_con_abreviatura_co():
    tokens = textos("Ili fondis la kompanion Pacific Aero Products Co. en 1916. Poste venis Boeing.")
    assert len(split_sentences(tokens)) == 2


@pytest.mark.parametrize("abreviatura", ["Mk.", "Co.", "trad.", "i.a.", "inkl.", "a.n.e."])
def test_tokenize_abreviaturas_de_nombres_y_referencias(abreviatura):
    assert textos(f"vidu {abreviatura} 2") == ["vidu", abreviatura, "2"]


def test_split_sentences_ktp_al_final_de_frase():
    tokens = textos("Ekzistas trajnoj, aŭtoj k.t.p. Poste venis aviadiloj.")
    assert len(split_sentences(tokens)) == 2


def test_split_sentences_cierre_de_comillas_va_con_su_frase():
    tokens = ["Li", "diris", "«", "jes", ".", "»", "Poste", "li", "iris", "."]
    assert split_sentences(tokens) == [(0, 6), (6, 10)]


def test_split_sentences_frase_sin_punto_final():
    assert split_sentences(["La", "trajno"]) == [(0, 2)]


def test_split_sentences_sin_tokens():
    assert split_sentences([]) == []
