"""Tokenizador basado en reglas (versión inicial: palabras y puntuación)."""

import re
from typing import List

# Palabras (incluye letras esperanto ĉĝĥĵŝŭ) o cualquier signo no espacio.
_TOKEN_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)


def tokenize(text: str) -> List[str]:
    return _TOKEN_RE.findall(text)
