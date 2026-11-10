"""eonlp — Librería NLP basada en reglas para Esperanto.

API pública (similar a spaCy):

    import eonlp
    nlp = eonlp.load()
    doc = nlp("La trajno estas rapida.")
"""

from eonlp.language import Language
from eonlp.tokens import Doc, Token

__version__ = "0.1.0"
__all__ = ["load", "Language", "Doc", "Token", "__version__"]


def load() -> Language:
    """Devuelve un pipeline de Esperanto listo para usar (equivalente a spacy.load)."""
    return Language()
