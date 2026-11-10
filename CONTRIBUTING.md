# Cómo contribuir

## Reglas básicas

1. **Nadie hace push directo a `main`.** Todo cambio entra por Pull Request.
2. Cada PR lo revisa y aprueba **otro miembro del equipo** antes de hacer merge.
3. Una rama por tarea, con nombre descriptivo:
   - `feature/tokenizer`, `feature/lemmatizer`, `feature/dataset-script`
   - `fix/tokenizer-apostrofo`
   - `docs/readme`
4. Antes de abrir un PR: `pytest` debe pasar en local.

## Flujo de trabajo

```bash
git checkout main
git pull                              # traer lo último
git checkout -b feature/tokenizer     # nueva rama
# ... trabajar ...
git add .
git commit -m "feat(tokenizer): separar puntuación y números"
git push -u origin feature/tokenizer  # luego abrir el PR en GitHub
```

## Mensajes de commit

Formato: `tipo(ámbito): descripción en presente`

| Tipo | Uso |
|---|---|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de un error |
| `test` | Añadir o modificar tests |
| `docs` | Documentación |
| `data` | Cambios en el dataset o en el script que lo genera |
| `chore` | Configuración, dependencias, estructura |

Commits pequeños y frecuentes: el profesor evalúa la contribución equilibrada de los tres miembros.
