# Mineria-de-textos · eonlp

Práctica de Minería de Textos (CUNEF, 4º INF-A, 2026/2027): clasificación de textos en **esperanto** en tres categorías de vehículos: **coches**, **aviones** y **trenes**.

El resultado final es el cuaderno [`notebooks/clasificacion.ipynb`](notebooks/clasificacion.ipynb), **autocontenido**: genera (o carga) el dataset, incluye el modelo de NLP, entrena el clasificador, lo evalúa y clasifica páginas web.

Además hemos hecho la práctica como proyecto de software (apartado 9.1 del enunciado):

1. **`eonlp`**: el modelo de NLP del cuaderno publicado como librería instalable con `pip`, basada en reglas y hecha desde cero (sin spaCy, NLTK ni Stanza), con una API como la de spaCy, tests y documentación. El cuaderno comprueba que da el mismo resultado que su propio código.
2. **Dataset**: párrafos de Wikipedia en esperanto y el script que los descarga (el mismo código que la sección 1 del cuaderno).

## Equipo

| Nombre | GitHub | Parte principal |
|---|---|---|
| Eduardo Bernad Soria | [@eduardobernad33](https://github.com/eduardobernad33) | Repositorio, tokenizador, `Doc`/`Token`, lematizador |
| Gonzalo Olivares | [@Olivaressss](https://github.com/Olivaressss) | Dataset, etiquetador POS |
| Pedro Riveiro | [@PedroRiveiro](https://github.com/PedroRiveiro) | Stop-words |

## Estructura

```
src/eonlp/              librería: tokenizer, tagger, lemmatizer, stopwords, Doc/Token
tests/                  tests de cada módulo (pytest)
docs/                   documentación de la librería (API y reglas)
scripts/build_dataset.py  genera el dataset desde la API de Wikipedia
data/dataset.csv        dataset (text;class)
data/metadata.csv       artículo y revisión de Wikipedia de cada párrafo
notebooks/clasificacion.ipynb  cuaderno final (Fase 3)
```

## Cómo ejecutarlo

**Cuaderno**: abrir [`notebooks/clasificacion.ipynb`](notebooks/clasificacion.ipynb) en Google Colab y *Ejecutar todo*. Por defecto carga el dataset ya generado de este repositorio (con `GENERAR_DATASET = True` lo vuelve a descargar de Wikipedia, unos 5 min). Tarda menos de un minuto y no necesita GPU.

**Librería**:

```bash
pip install git+https://github.com/eduardobernad33/Mineria-de-textos.git
```

```python
import eonlp

nlp = eonlp.load()
doc = nlp("La rapidaj trajnoj veturas al Madrido.")
for token in doc:
    print(token.text, token.lemma_, token.pos_, token.is_stop)
for frase in doc.sents:
    print(frase.text)
```

**Dataset y tests** (en local):

```bash
pip install -r requirements.txt
pip install -e .
python scripts/build_dataset.py   # vuelve a generar data/dataset.csv (unos 5 min)
pytest
```

## Qué genera

- `data/dataset.csv`: 1052 párrafos de 151 artículos (coches 333, aviones 367, trenes 352). CSV UTF-8, separador `;`, columnas `text;class`. Cada artículo se descarga en una revisión fija, así que el resultado es reproducible.
- El cuaderno muestra:
  - el ruido del etiquetado (párrafos que heredan la clase de su artículo sin hablar de ella);
  - la comparación de modelos con validación cruzada: el mejor es la regresión logística con TF-IDF por clases (F1 macro 0,956);
  - la evaluación: accuracy y F1 macro de 0,929 en el test aleatorio y de 0,86 en la validación por artículo, con sus matrices de confusión;
  - la probabilidad de cada clase para cuatro páginas que no están en el dataset: tres artículos de Wikipedia y una noticia de Vikinovaĵoj.

## Forma de trabajo

Cada cambio entra por una rama y un Pull Request revisado por otro miembro del equipo. GitHub Actions ejecuta los tests en cada push.

## Fuentes y licencia

- Código: MIT.
- `src/eonlp/resources/vortoj.json`: de la guía de la práctica, [jparisu/nlp-esperantilo](https://github.com/jparisu/nlp-esperantilo) (Apache-2.0).
- Textos: [Wikipedia en esperanto](https://eo.wikipedia.org/), CC BY-SA 4.0.
