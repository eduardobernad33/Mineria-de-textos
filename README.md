# eonlp-veturiloj

Clasificación temática de textos en **Esperanto** — Práctica de Minería de Textos (CUNEF, 4º INF-A, 2026/2027).

Categorías: **aŭtomobiloj** (coches), **aviadiloj** (aviones), **trajnoj** (trenes).

## Equipo

| Nombre | Usuario GitHub | Responsabilidad principal |
|---|---|---|
| Eduardo Bernad Soria | @usuario1 | |
| Compañero 2 | @usuario2 | |
| Compañero 3 | @usuario3 | |

## Estructura del repositorio

```
eonlp-veturiloj/
├── src/eonlp/            # Librería NLP de Esperanto (basada en reglas, sin spaCy/NLTK)
│   ├── __init__.py       # API pública: eonlp.load()
│   ├── language.py       # Clase Language (pipeline tipo spaCy: nlp("texto") -> Doc)
│   ├── tokens.py         # Clases Doc y Token
│   ├── tokenizer.py      # Tokenizador
│   ├── lemmatizer.py     # Lematizador
│   ├── tagger.py         # Etiquetador morfológico / POS
│   └── stopwords.py      # Gestión de stop-words
├── tests/                # Pruebas unitarias (pytest)
├── scripts/
│   └── build_dataset.py  # Script reproducible que genera el dataset
├── data/
│   └── dataset.csv       # Dataset etiquetado (text;class)
├── notebooks/            # Cuaderno de entrenamiento y clasificación web (Colab)
├── docs/                 # Documentación de la librería
└── pyproject.toml        # Configuración del paquete instalable
```

## Instalación

```bash
pip install git+https://github.com/eduardobernad33/mineria-de-textos.git
```

## Uso (API similar a spaCy)

```python
import eonlp

nlp = eonlp.load()
doc = nlp("La rapidaj trajnoj veturas al Madrido.")
for token in doc:
    print(token.text, token.lemma_, token.pos_, token.is_stop)
```

## Dataset

Contrato de datos: CSV, UTF-8, separador `;`, cabecera `text;class`, un párrafo por fila, sin `;` en el texto, limpio de HTML, enlaces y referencias.

Regenerar el dataset:

```bash
python scripts/build_dataset.py
```

## Desarrollo

```bash
pip install -e ".[dev]"
pytest
```

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para el flujo de ramas y Pull Requests.
