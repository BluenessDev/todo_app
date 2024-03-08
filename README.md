# Documentation du projet Toudou

Votre projet Toudou est organisé en plusieurs modules principaux, chacun ayant un rôle spécifique dans l'application.

## `src/toudou/models.py`

Ce fichier contient les définitions des modèles de données utilisés dans votre application, ainsi que les fonctions pour interagir avec la base de données. Il utilise SQLAlchemy pour définir et manipuler les modèles.

## `src/toudou/views.py`

Ce fichier contient les définitions des commandes CLI et des routes de l'application web. Il utilise le module `click` pour définir les commandes CLI et `Flask` pour l'application web.

## `src/toudou/templates/index.html`

Ce fichier est un template HTML utilisé par l'application web pour afficher la page d'accueil. Il utilise le moteur de templates Jinja2 fourni par Flask.

## `src/Tests/test_models.py`

Ce fichier contient les tests unitaires pour les fonctions définies dans `models.py`. Il utilise le module `unittest` de Python pour définir et exécuter les tests.

## Structure du projet

Voici une représentation de la structure du projet :

```
.
├── src
│   ├── toudou
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── templates
│   │   │   ├── index.html
│   ├── Tests
│   │   ├── test_models.py
├── README.md
```

## Comment exécuter le code

Pour exécuter le code, vous pouvez utiliser l'IDE PyCharm. Ouvrez le projet dans PyCharm, puis exécutez `views.py` en utilisant le terminal avec la commande ```pdm run toudou``` suivi de la commande que vous souhaitez exécuter. Si vous souhaitez demarrer l'application web, utilisez la commande ```pdm run flask --app toudou.views --debug run``` dans le terminal. Si vous souhaitez exécuter les tests, utilisez la commande ```pdm run python -m unittest Tests.test_models``` dans le terminal.