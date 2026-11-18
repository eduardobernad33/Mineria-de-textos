"""Clase Language: la tubería (pipeline) de análisis, al estilo de spaCy.

    nlp = Language()            # o eonlp.load()
    doc = nlp("La trajno alvenis.")

Pasos al llamar a nlp(texto):
    1. normalizar el texto        (tokenizer.normalize)
    2. dividirlo en tokens        (tokenizer.tokenize)
    3. agruparlos en frases       (tokenizer.split_sentences)
    4. lema, categoría y stop-word de cada token (lemmatizer, tagger, stopwords)
"""

from eonlp.lemmatizer import lemmatize
from eonlp.stopwords import is_stop
from eonlp.tagger import tag
from eonlp.tokenizer import normalize, split_sentences, tokenize
from eonlp.tokens import Doc, Token


class Language:
    """Analizador de textos en esperanto. Llamarlo con un texto devuelve un Doc."""

    def __call__(self, text: str) -> Doc:
        """Analiza un texto.

        Args:
            text: texto en esperanto.

        Returns:
            Un Doc con los tokens analizados y sus frases.
        """
        texto = normalize(text)
        tokens = [
            Token(contenido, i, posicion)
            for i, (contenido, posicion) in enumerate(tokenize(texto))
        ]
        limites_frases = split_sentences([token.text for token in tokens])

        for token in tokens:
            token.lemma_ = lemmatize(token.text)
            token.pos_ = tag(token.text)
            token.is_stop = is_stop(token.text)

        return Doc(texto, tokens, limites_frases)
