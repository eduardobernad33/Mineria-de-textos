import eonlp


def test_load_returns_pipeline():
    nlp = eonlp.load()
    doc = nlp("La trajno estas rapida.")
    assert [t.text for t in doc] == ["La", "trajno", "estas", "rapida", "."]


def test_stopwords_and_punct():
    doc = eonlp.load()("La aviadilo flugas.")
    assert doc[0].is_stop
    assert doc[-1].is_punct
