# API de eonlp

## `eonlp.load()`

Devuelve el analizador (`Language`), equivalente a `spacy.load(...)`. Llamarlo con un texto devuelve un `Doc`.

```python
nlp = eonlp.load()
doc = nlp("La trajno alvenis.")
```

## `Doc`

Un texto analizado.

| Atributo / operación | Qué devuelve | Ejemplo |
|---|---|---|
| `doc.text` | Texto normalizado | `"La trajno alvenis."` |
| `for token in doc` | Los `Token`, en orden | |
| `len(doc)` | Número de tokens | `4` |
| `doc[1]` | Un `Token` | `trajno` |
| `doc[0:2]` | Un `Span` | `La trajno` |
| `doc.sents` | Lista de frases (`Span`) | `[La trajno alvenis.]` |

## `Span`

Un trozo de tokens seguidos; `doc.sents` devuelve una lista de `Span`.

| Atributo / operación | Qué devuelve |
|---|---|
| `span.text` | Texto original del trozo, con sus espacios |
| `for token in span`, `len(span)`, `span[0]` | Igual que en `Doc` |
| `span.start`, `span.end` | Posiciones del primer token y del siguiente al último |

## `Token`

Ejemplo con `doc = nlp("Ni vidis la rapidajn trajnojn.")` y `token = doc[4]`:

| Atributo | Qué es | Valor |
|---|---|---|
| `text` | Texto del token | `"trajnojn"` |
| `i` | Posición en el `Doc` | `4` |
| `idx` | Posición del primer carácter en `doc.text` | `21` |
| `lemma_` | Forma de diccionario | `"trajno"` |
| `pos_` | Categoría gramatical universal | `"NOUN"` |
| `is_stop` | Palabra vacía | `False` |
| `is_punct` | Signo de puntuación | `False` |
| `is_alpha` | Solo letras | `True` |
| `is_digit` | Solo cifras | `False` |
| `like_num` | Parece un número (`1950`, `3,5`, `1.000`) | `False` |

Etiquetas de `pos_`: `NOUN`, `PROPN`, `VERB`, `AUX`, `ADJ`, `ADV`, `PRON`, `DET`, `ADP`, `CCONJ`, `SCONJ`, `PART`, `NUM`, `INTJ`, `PUNCT` y `X` (desconocida).

## Funciones de cada módulo

Se pueden usar por separado, sin crear un `Doc`:

| Módulo | Función | Ejemplo |
|---|---|---|
| `eonlp.tokenizer` | `normalize(texto)` | `normalize("sxipo") → "ŝipo"` |
| | `tokenize(texto)` | lista de pares `(token, posición)` |
| | `split_sentences(tokens)` | lista de pares `(inicio, fin)` por frase |
| `eonlp.stopwords` | `is_stop(palabra)` | `is_stop("estas") → True` |
| | `STOP_WORDS` | conjunto de 337 palabras vacías |
| `eonlp.tagger` | `tag(palabra, inicio_frase=False)` | `tag("veturis") → "VERB"` |
| `eonlp.lemmatizer` | `lemmatize(palabra, pos="")` | `lemmatize("librojn") → "libro"` |
