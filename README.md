# Mineria-de-textos · eonlp

Clasificación temática de textos en **Esperanto** — Práctica de Minería de Textos (CUNEF, 4º INF-A, 2026/2027).

Tres categorías de vehículos: **coches** (*aŭtoj*), **aviones** (*aviadiloj*) y **trenes** (*trajnoj*).

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/eduardobernad33/Mineria-de-textos/blob/main/notebooks/clasificacion.ipynb)
[![Tests](https://github.com/eduardobernad33/Mineria-de-textos/actions/workflows/tests.yml/badge.svg)](https://github.com/eduardobernad33/Mineria-de-textos/actions/workflows/tests.yml)

El repositorio tiene dos partes:

1. **`eonlp`**: una librería de procesamiento de lenguaje natural para Esperanto, basada en reglas y construida desde cero (sin spaCy, NLTK ni Stanza), con una API como la de spaCy.
2. **El clasificador**: un dataset de párrafos de Wikipedia en esperanto y un cuaderno que lo vectoriza con `eonlp`, entrena un modelo y clasifica páginas web.

## Equipo

| Nombre | GitHub | Responsabilidad principal |
|---|---|---|
| Eduardo Bernad Soria | [@eduardobernad33](https://github.com/eduardobernad33) | Repositorio, tokenizador y objetos `Doc`/`Token`, lematizador |
| Gonzalo Olivares | [@Olivaressss](https://github.com/Olivaressss) | Dataset (Fase 1), etiquetador POS |
| Pedro Riveiro | [@PedroRiveiro](https://github.com/PedroRiveiro) | Stop-words |

## Instalación

```bash
pip install git+https://github.com/eduardobernad33/Mineria-de-textos.git
```

Para instalar exactamente la versión de la entrega: `pip install git+https://github.com/eduardobernad33/Mineria-de-textos.git@v0.1.0`.

La librería no tiene dependencias externas.

## Uso (API como la de spaCy)

```python
import eonlp

nlp = eonlp.load()
doc = nlp("La rapidaj trajnoj veturas al Madrido.")

for token in doc:
    print(token.text, token.lemma_, token.pos_, token.is_stop, token.is_punct)

for frase in doc.sents:
    print(frase.text)
```

Resultado:

| text | lemma_ | pos_ | is_stop | is_punct |
|---|---|---|---|---|
| `La` | `la` | DET | True | False |
| `rapidaj` | `rapida` | ADJ | False | False |
| `trajnoj` | `trajno` | NOUN | False | False |
| `veturas` | `veturi` | VERB | False | False |
| `al` | `al` | ADP | True | False |
| `Madrido` | `Madrido` | PROPN | False | False |
| `.` | `.` | PUNCT | False | True |

Documentación completa en [`docs/`](docs/index.md): [API](docs/api.md) y [reglas de cada módulo](docs/reglas.md).

## Estructura del repositorio

```
Mineria-de-textos/
├── src/eonlp/                # Librería NLP de Esperanto
│   ├── __init__.py           # API pública: eonlp.load()
│   ├── language.py           # Pipeline: nlp("texto") -> Doc
│   ├── tokens.py             # Clases Doc, Span (frase) y Token
│   ├── tokenizer.py          # Normalización, tokenización y división en frases
│   ├── stopwords.py          # Palabras vacías (is_stop)
│   ├── tagger.py             # Categoría gramatical (pos_)
│   ├── lemmatizer.py         # Forma de diccionario (lemma_)
│   └── resources/
│       └── vortoj.json       # Léxico de la guía de la práctica (Apache-2.0)
├── tests/                    # Un fichero de pruebas por módulo (pytest)
├── scripts/
│   └── build_dataset.py      # Genera el dataset desde la API de Wikipedia
├── data/
│   ├── dataset.csv           # Dataset: text;class
│   └── metadata.csv          # Artículo y revisión de Wikipedia de cada párrafo
├── notebooks/
│   └── clasificacion.ipynb   # Cuaderno de clasificación (Fase 3)
├── docs/                     # Documentación de la librería
└── pyproject.toml            # Paquete instalable con pip
```

## Dataset

1052 párrafos de 151 artículos de Wikipedia en esperanto: **coches 333 · aviones 367 · trenes 352**.

- Contrato de datos: CSV UTF-8, separador `;`, cabecera `text;class`, un párrafo por fila, sin `;`, HTML, enlaces ni referencias.
- Reproducible: cada artículo se descarga en una revisión fija (`oldid`) mediante la API de Wikipedia, y las selecciones aleatorias usan la semilla 42.
- Cada párrafo hereda la etiqueta de su artículo, lo que introduce ruido; el script lo estima (párrafos sin ninguna raíz típica de su clase).

Regenerarlo:

```bash
pip install -e ".[data]"
python scripts/build_dataset.py
```

## Resultados

Cuaderno: [`notebooks/clasificacion.ipynb`](notebooks/clasificacion.ipynb), ejecutable en Google Colab en menos de un minuto (CPU). Instala la librería y descarga el dataset de la versión `v0.1.0`.

**Vectorización** (implementada a mano, temas 2.3 y 2.4): lemas de `eonlp` sin stop-words, puntuación ni números; vocabulario de los 1000 lemas más frecuentes del entrenamiento; BoW normalizada y TF-IDF por clases, `IDF(t) = 1 − log_|C|(nº de clases que contienen t)`.

**Selección de modelo** (validación cruzada de 5 particiones sobre el entrenamiento, F1 macro):

| Modelo | BoW | TF-IDF por clases |
|---|---|---|
| **Regresión logística** | 0.936 | **0.956** |
| Naive Bayes | 0.911 | 0.918 |
| Árbol de decisión | 0.875 | 0.868 |
| KNN (k=5) | 0.840 | 0.831 |

**Evaluación** del modelo elegido (regresión logística + TF-IDF por clases):

| Partición de test | Accuracy | F1 macro |
|---|---|---|
| Aleatoria estratificada (20 %) | 0.929 | 0.929 |
| Por artículo (20 % de los artículos de cada clase) | 0.852 | 0.852 |

La partición por artículo es más exigente: el modelo no ha visto ningún párrafo de esos artículos, como ocurre con una página web nueva.

**Ruido del etiquetado**: el 13,3 % de los párrafos se asigna a otra clase cuando el modelo no ha visto su artículo (coches 14,1 %, aviones 9,8 %, trenes 16,2 %). Son sobre todo párrafos genéricos (fechas, empresas, cifras) que no hablan de su vehículo.

**Páginas web** (Vikipedio, fuera del dataset, descargadas respetando `robots.txt`):

| Página | coches | aviones | trenes |
|---|---|---|---|
| Aŭtomobilo-revokoj de Toyota 2009-2010 | **59.4 %** | 21.7 % | 18.9 % |
| Flughaveno Frankfurto | 21.0 % | **48.5 %** | 30.5 % |
| Majaa Trajno | 8.1 % | 8.5 % | **83.4 %** |

## Desarrollo

```bash
pip install -e ".[dev]"
pytest
```

Cada cambio entra por una rama y un Pull Request revisado por otro miembro del equipo. Ver [CONTRIBUTING.md](CONTRIBUTING.md).

## Licencia y fuentes

- Código: MIT ([LICENSE](LICENSE)).
- `src/eonlp/resources/vortoj.json`: copiado de la guía de la práctica, [jparisu/nlp-esperantilo](https://github.com/jparisu/nlp-esperantilo) (Apache-2.0).
- Textos del dataset: [Wikipedia en esperanto](https://eo.wikipedia.org/), licencia [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
