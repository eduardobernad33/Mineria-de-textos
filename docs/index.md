# Documentación de eonlp

`eonlp` es una librería de procesamiento de lenguaje natural para Esperanto, basada en reglas y construida desde cero. Su API imita la de spaCy, vista en el tema 2.2 de la asignatura.

## Inicio rápido

```python
import eonlp

nlp = eonlp.load()
doc = nlp("Boeing konstruis la unuan aviadilon en 1916. Ĝi flugis al Seatlo.")

for frase in doc.sents:
    print(frase.text)
# Boeing konstruis la unuan aviadilon en 1916.
# Ĝi flugis al Seatlo.

for token in doc:
    print(token.text, token.lemma_, token.pos_, token.is_stop)
```

## Qué pasa al llamar a `nlp(texto)`

```
texto
  │
  ├─ 1. normalize        Unicode NFC y sistema x (sxipo -> ŝipo)       tokenizer.py
  ├─ 2. tokenize         palabras, números y signos                     tokenizer.py
  ├─ 3. split_sentences  frases (doc.sents)                             tokenizer.py
  ├─ 4. tag              categoría gramatical (token.pos_)              tagger.py
  ├─ 5. lemmatize        forma de diccionario (token.lemma_)            lemmatizer.py
  └─ 6. is_stop          palabra vacía (token.is_stop)                  stopwords.py
  │
  ▼
Doc  (secuencia de Token, dividida en frases Span)                     tokens.py
```

El etiquetado va antes que la lematización porque el lema depende de la categoría: un verbo cambia su terminación por `-i` (`kantis → kanti`), mientras que un sustantivo solo pierde `-j` y `-n` (`librojn → libro`).

## Páginas

- [API](api.md): clases `Doc`, `Span` y `Token`, y funciones de cada módulo.
- [Reglas](reglas.md): qué reglas aplica cada módulo, con ejemplos y su relación con el temario.

## Fuentes

- Gramática del Esperanto y léxico `vortoj.json`: guía oficial de la práctica, [jparisu/nlp-esperantilo](https://github.com/jparisu/nlp-esperantilo).
- Conceptos de NLP (token, stop-word, lematización frente a stemming, etiquetas POS universales): temas 2.1 y 2.2 de la asignatura.
