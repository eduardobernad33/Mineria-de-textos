# Recursos de eonlp

| Fichero | Origen | Licencia |
|---|---|---|
| `vortoj.json` | Copiado sin cambios de la guía oficial de la práctica, [jparisu/nlp-esperantilo](https://github.com/jparisu/nlp-esperantilo) (`resources/esperanto/vortoj.json`). Lista de stop-words basada en [stopwords-iso/stopwords-eo](https://github.com/stopwords-iso/stopwords-eo). | Apache-2.0 |

`vortoj.json` guarda **raíces, no formas**: `stopwords.py` genera a partir de ellas
las formas que faltan (acusativos y posesivos de los pronombres, verbos conjugados
y los 45 correlativos), siguiendo la gramática de la guía.
