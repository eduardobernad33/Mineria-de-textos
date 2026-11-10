"""Gestión de stop-words (TODO: cargar resources/vortoj.json)."""

STOP_WORDS: set = {"la", "kaj", "de", "en", "estas", "al", "ke", "por"}


def is_stop(word: str) -> bool:
    return word.lower() in STOP_WORDS
