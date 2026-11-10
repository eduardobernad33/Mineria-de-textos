"""Objetos Doc y Token (estructura del resultado, al estilo spaCy)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, List


@dataclass
class Token:
    text: str
    i: int
    lemma_: str = ""
    pos_: str = ""
    is_stop: bool = False
    is_punct: bool = False

    def __repr__(self) -> str:
        return self.text


@dataclass
class Doc:
    text: str
    tokens: List[Token] = field(default_factory=list)

    def __iter__(self) -> Iterator[Token]:
        return iter(self.tokens)

    def __len__(self) -> int:
        return len(self.tokens)

    def __getitem__(self, i):
        return self.tokens[i]
