# Reglas de cada módulo

La morfología del Esperanto no tiene excepciones: cada palabra es una **raíz** más **terminaciones** que marcan su categoría y su flexión. Por eso un sistema basado en reglas funciona bien. Las reglas siguen la gramática de la [guía de la práctica](https://github.com/jparisu/nlp-esperantilo).

## 1. Tokenizador (`tokenizer.py`)

**Normalización.** Una letra como `ĉ` puede llegar como un carácter o como `c` + acento combinado; Unicode NFC deja siempre uno solo (tema 1.3). Si el texto no tiene acentos, se convierte el sistema x (`cx → ĉ`, `ux → ŭ`).

**Tokenización.** Siguiendo el tema 2.2, primero se consulta un **lexicón** de casos especiales con la regla de la **coincidencia más larga** (*longest-match*): abreviaturas como `k.t.p.`, `ekz.` o `t.e.`, para que su punto no corte la frase. Después, expresiones regulares (tema 1.3) para:

| Caso | Ejemplo | Tokens |
|---|---|---|
| Números con separador | `3,5` `1.000` | `3,5` · `1.000` |
| Palabras con guion | `29-an` `F-16` | `29-an` · `F-16` |
| Artículo con elisión | `de l' mondo` | `de` · `l'` · `mondo` |
| Signos | `(«TGV»)` | `(` · `«` · `TGV` · `»` · `)` |

**Frases.** Una frase termina en `.`, `!`, `?` o `...`, salvo detrás de una inicial (`J. Smith`) o antes de una palabra en minúscula (en esperanto la frase siguiente empieza con mayúscula).

## 2. Stop-words (`stopwords.py`)

El léxico de la guía (`vortoj.json`) guarda **raíces, no formas**. Las formas que faltan se generan con cuatro reglas:

| Regla | Ejemplo |
|---|---|
| Pronombres: acusativo y posesivo | `mi → min, mia, miaj, mian, miajn` |
| Verbos: terminaciones de tiempo | `esti → estas, estis, estos, estus, estu` |
| Números: ordinales | `unu → unua`, `du → dua` |
| Correlativos: tabla 5 × 9 | `kiu, tio, ĉiuj, tiujn, kien...` (45 palabras y sus formas) |

Resultado: 337 palabras vacías, el 40 % de las palabras del dataset. La puntuación se marca aparte, con `is_punct`.

## 3. Etiquetador (`tagger.py`)

Etiquetas universales, como en spaCy. Reglas en orden, de la más segura a la más general:

| # | Regla | Ejemplo |
|---|---|---|
| 1 | Signos y números | `.` → PUNCT, `1950` → NUM |
| 2 | Palabras gramaticales del léxico | `la` → DET, `en` → ADP, `estas` → AUX, `kiu` → PRON |
| 3 | Prefijo + palabra del léxico | `malpli` = `mal-` + `pli` → ADV |
| 4 | Nombres propios | `TGV`, `A380`; mayúscula en mitad de frase: `Parizo` → PROPN |
| 5 | **Terminación** tras quitar `-j` y `-n` | `-o` NOUN · `-a` ADJ · `-e` ADV · `-i -as -is -os -us -u` VERB |
| 6 | Ninguna | `hatchback` → X |

Limitación: cada palabra se etiqueta sin mirar las de al lado. En `tiujn librojn`, `tiujn` sale PRON aunque ahí hace de determinante.

## 4. Lematizador (`lemmatizer.py`)

Devuelve la **forma de diccionario**. Es **lematización y no stemming** (tema 2.2): `librojn → libro` (una palabra real), no `libr-` (la raíz). Por eso se conservan los afijos: `instruistinoj → instruistino`.

| Categoría | Regla | Ejemplo |
|---|---|---|
| Pronombres, correlativos, ordinales | Tabla generada con las reglas de las stop-words | `min → mi`, `tiujn → tiu`, `unuan → unua` |
| VERB, AUX | Terminación de tiempo → `-i` | `kantis → kanti`, `estas → esti` |
| NOUN, ADJ | Quitar `-n` y `-j` | `librojn → libro`, `rapidajn → rapida` |
| PROPN | Quitar acusativo, conservar mayúscula | `Parizon → Parizo` |
| Resto | Sin cambios (en minúsculas) | `tre`, `en`, `1950` |

Sobre el dataset, el vocabulario pasa de 11.622 formas distintas a 9.265 lemas (−20 %): `trajno`, `trajnoj`, `trajnon` y `trajnojn` cuentan como una sola palabra al vectorizar.

Limitación: los participios (`leganta`, `legita`) se tratan como adjetivos; la guía tampoco los cubre.
