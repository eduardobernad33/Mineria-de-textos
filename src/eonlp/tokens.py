"""Objetos del resultado del análisis: Token, Span y Doc.

Siguen la misma idea que spaCy, vista en clase (tema 2.2):

    doc = nlp("La trajno alvenis. Ĝi estis rapida.")
    for token in doc:                 # un Doc es una secuencia de Tokens
        print(token.text, token.lemma_, token.pos_, token.is_stop)
    for frase in doc.sents:           # y se puede dividir en frases (Span)
        print(frase.text)

Son clases normales con métodos especiales (__len__, __getitem__, __iter__...),
como se explica en el tema 0.1 (Python, clases).
"""


class Token:
    """Una unidad del texto: una palabra, un número o un signo de puntuación.

    Atributos:
        text: el texto del token tal y como aparece en el documento.
        i: posición del token dentro del Doc (0, 1, 2...).
        idx: posición del primer carácter del token dentro del texto del Doc.
        lemma_: forma base de la palabra (la rellena el lematizador).
        pos_: categoría gramatical con etiquetas universales: NOUN, VERB, ADJ...
            (la rellena el etiquetador).
        is_stop: True si es una palabra vacía (la rellena el módulo de stop-words).
        is_punct: True si es un signo de puntuación.
        is_alpha: True si está formado solo por letras.
        is_digit: True si está formado solo por dígitos.
        like_num: True si representa un número (1950, 3,5, 1.000).
    """

    def __init__(self, text: str, i: int, idx: int) -> None:
        self.text = text
        self.i = i
        self.idx = idx
        # Los rellenan los módulos de la Fase 2 (lematizador, etiquetador, stop-words).
        self.lemma_ = text
        self.pos_ = ""
        self.is_stop = False
        # Se deducen directamente del texto con métodos de str (tema 1.3).
        self.is_alpha = text.isalpha()
        self.is_digit = text.isdigit()
        self.like_num = text.replace(".", "").replace(",", "").isdigit()
        self.is_punct = not any(caracter.isalnum() for caracter in text)

    def __len__(self) -> int:
        """Número de caracteres del token."""
        return len(self.text)

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return self.text


class Span:
    """Un trozo de un Doc formado por tokens seguidos (por ejemplo, una frase).

    Atributos:
        doc: el Doc al que pertenece.
        start: posición del primer token del trozo.
        end: posición siguiente al último token (como en los slices de Python).
    """

    def __init__(self, doc: "Doc", start: int, end: int) -> None:
        self.doc = doc
        self.start = start
        self.end = end

    @property
    def text(self) -> str:
        """Texto original del trozo, con sus espacios."""
        if self.start >= self.end:
            return ""
        primero = self.doc[self.start]
        ultimo = self.doc[self.end - 1]
        return self.doc.text[primero.idx: ultimo.idx + len(ultimo.text)]

    def _tokens(self) -> list:
        return self.doc.tokens[self.start:self.end]

    def __iter__(self):
        return iter(self._tokens())

    def __len__(self) -> int:
        return self.end - self.start

    def __getitem__(self, posicion: int) -> Token:
        return self._tokens()[posicion]

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return self.text


class Doc:
    """Un texto analizado: la secuencia de sus tokens y sus frases.

    Atributos:
        text: el texto original.
        tokens: lista de Tokens en orden.
        sents: lista de frases, cada una como un Span.
    """

    def __init__(self, text: str, tokens: list, limites_frases: list = None) -> None:
        """Crea el Doc.

        Args:
            text: el texto original.
            tokens: lista de Tokens.
            limites_frases: lista de pares (inicio, fin) con las posiciones de los
                tokens de cada frase. Si no se indica, todo el texto es una frase.
        """
        self.text = text
        self.tokens = tokens
        if limites_frases is None:
            limites_frases = [(0, len(tokens))] if tokens else []
        self._limites_frases = limites_frases

    @property
    def sents(self) -> list:
        """Frases del documento, cada una como un Span (igual que doc.sents en spaCy)."""
        return [Span(self, inicio, fin) for inicio, fin in self._limites_frases]

    def __iter__(self):
        return iter(self.tokens)

    def __len__(self) -> int:
        """Número de tokens."""
        return len(self.tokens)

    def __getitem__(self, posicion):
        """doc[3] devuelve un Token y doc[1:4] devuelve un Span."""
        if isinstance(posicion, slice):
            inicio, fin, _ = posicion.indices(len(self.tokens))
            return Span(self, inicio, fin)
        return self.tokens[posicion]

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return self.text
