import pytest

import eonlp
from eonlp.stopwords import (
    STOP_WORDS,
    cargar_vortoj,
    formas_correlativos,
    formas_numero,
    formas_pronombre,
    formas_verbo,
    is_stop,
)


def test_el_lexicon_de_la_guia_se_carga():
    vortoj = cargar_vortoj()
    assert len(vortoj) > 100
    assert all("vorto" in entrada and "kategorio" in entrada for entrada in vortoj)


@pytest.mark.parametrize("palabra", ["la", "kaj", "de", "en", "al", "por", "ke", "ne", "pli"])
def test_palabras_del_lexicon(palabra):
    assert is_stop(palabra)


@pytest.mark.parametrize("palabra", ["min", "mia", "miajn", "ŝin", "ilia", "sian", "nin"])
def test_formas_de_pronombres(palabra):
    assert is_stop(palabra)


@pytest.mark.parametrize("palabra", ["estas", "estis", "estos", "estus", "havas", "povis"])
def test_formas_de_verbos(palabra):
    assert is_stop(palabra)


@pytest.mark.parametrize("palabra", ["unu", "unua", "dua", "trian", "dek", "cent"])
def test_numeros_y_ordinales(palabra):
    assert is_stop(palabra)


@pytest.mark.parametrize("palabra", ["kiu", "tio", "ĉiuj", "tiujn", "kion", "kien", "neniam", "kiel", "ĉiom"])
def test_correlativos(palabra):
    assert is_stop(palabra)


@pytest.mark.parametrize("palabra", ["trajno", "aŭto", "aviadilo", "lokomotivo", "flugas", "rapida"])
def test_palabras_con_contenido_no_son_stop(palabra):
    assert not is_stop(palabra)


def test_no_distingue_mayusculas():
    assert is_stop("La") and is_stop("KAJ")


def test_puntuacion_no_es_stop():
    # La puntuación se marca aparte con token.is_punct (tema 2.2).
    assert not is_stop(".")


def test_generadores_de_formas():
    assert formas_pronombre("mi") == ["mi", "min", "mia", "miaj", "mian", "miajn"]
    assert formas_verbo("esti") == ["esti", "estas", "estis", "estos", "estus", "estu"]
    assert formas_numero("du") == ["du", "dua", "duaj", "duan", "duajn"]


def test_tabla_de_correlativos():
    formas = formas_correlativos()
    base = [f for f in formas if not f.endswith(("j", "n"))]
    assert len(base) == 45
    assert "tioj" not in formas        # los de -o nunca llevan -j
    assert "kiuj" in formas and "tiun" in formas


def test_tamano_razonable():
    assert 250 < len(STOP_WORDS) < 500


def test_integracion_con_el_doc():
    doc = eonlp.load()("La trajno estas tre rapida.")
    assert [token.is_stop for token in doc] == [True, False, True, True, False, False]
    assert doc[-1].is_punct
