"""Clase Language: pipeline tipo spaCy. Uso: nlp = Language(); doc = nlp("teksto")."""

from eonlp.lemmatizer import lemmatize
from eonlp.stopwords import is_stop
from eonlp.tagger import tag
from eonlp.tokenizer import tokenize
from eonlp.tokens import Doc, Token


class Language:
    def __call__(self, text: str) -> Doc:
        tokens = []
        for i, word in enumerate(tokenize(text)):
            pos = tag(word)
            tokens.append(Token(text=word, i=i, lemma_=lemmatize(word), pos_=pos,
                                is_stop=is_stop(word), is_punct=(pos == "PUNCT")))
        return Doc(text=text, tokens=tokens)
