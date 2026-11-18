import eonlp
from eonlp.tokens import Doc, Span, Token


TEXTO = "La trajno alvenis. Ĝi estis rapida!"


def analizar(texto=TEXTO):
    return eonlp.load()(texto)


# --- Token -------------------------------------------------------------------

def test_token_atributos_basicos():
    token = Token("trajno", 1, 3)
    assert token.text == "trajno"
    assert token.i == 1
    assert token.idx == 3
    assert len(token) == 6
    assert str(token) == "trajno"


def test_token_tipo_de_caracteres():
    assert Token("trajno", 0, 0).is_alpha
    assert Token(".", 0, 0).is_punct
    assert not Token("trajno", 0, 0).is_punct
    assert Token("1950", 0, 0).is_digit
    assert Token("1.000", 0, 0).like_num
    assert not Token("A380", 0, 0).like_num


# --- Doc ---------------------------------------------------------------------

def test_doc_es_iterable_sobre_tokens():
    doc = analizar()
    assert [token.text for token in doc] == [
        "La", "trajno", "alvenis", ".", "Ĝi", "estis", "rapida", "!",
    ]
    assert all(isinstance(token, Token) for token in doc)


def test_doc_len_y_getitem():
    doc = analizar()
    assert len(doc) == 8
    assert doc[1].text == "trajno"
    assert doc[-1].text == "!"


def test_doc_slice_devuelve_span():
    doc = analizar()
    trozo = doc[0:2]
    assert isinstance(trozo, Span)
    assert trozo.text == "La trajno"


def test_doc_posiciones_de_los_tokens():
    doc = analizar()
    assert [token.i for token in doc] == list(range(len(doc)))
    for token in doc:
        assert doc.text[token.idx:token.idx + len(token)] == token.text


def test_doc_text_conserva_el_texto():
    assert analizar().text == TEXTO


# --- doc.sents (Span) --------------------------------------------------------

def test_doc_sents_como_en_spacy():
    doc = analizar()
    assert [frase.text for frase in doc.sents] == ["La trajno alvenis.", "Ĝi estis rapida!"]


def test_span_es_iterable_y_tiene_longitud():
    primera = analizar().sents[0]
    assert len(primera) == 4
    assert [token.text for token in primera] == ["La", "trajno", "alvenis", "."]
    assert primera[1].text == "trajno"


def test_doc_vacio():
    doc = analizar("")
    assert len(doc) == 0
    assert doc.sents == []


def test_doc_se_puede_crear_sin_frases():
    tokens = [Token("trajno", 0, 0)]
    doc = Doc("trajno", tokens)
    assert [frase.text for frase in doc.sents] == ["trajno"]


def test_doc_normaliza_el_texto_de_entrada():
    doc = analizar("La sxipo")
    assert doc[1].text == "ŝipo"
    assert doc.text == "La ŝipo"
