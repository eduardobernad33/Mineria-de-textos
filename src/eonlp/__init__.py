"""eonlp: librería de procesamiento de lenguaje natural basada en reglas para Esperanto.

API pública, igual que la de spaCy vista en clase:

    import eonlp
    nlp = eonlp.load()
    doc = nlp("La trajno alvenis. Ĝi estis rapida.")
    for token in doc:
        print(token.text, token.lemma_, token.pos_, token.is_stop)
    for frase in doc.sents:
        print(frase.text)
"""

from eonlp.language import Language
from eonlp.tokens import Doc, Span, Token

__version__ = "0.1.0"
__all__ = ["load", "Language", "Doc", "Span", "Token", "__version__"]


def load():
    """Devuelve el analizador de esperanto listo para usar (equivale a spacy.load)."""
    return Language()
