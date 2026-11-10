"""Etiquetador morfológico / POS basado en reglas (TODO: terminaciones -o, -a, -e, -i, -as...)."""


def tag(word: str) -> str:
    if not any(c.isalnum() for c in word):
        return "PUNCT"
    return "X"  # Placeholder
