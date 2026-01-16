# Versions des dépendances

**Dernière mise à jour** : 16 janvier 2026

## Production

| Package | Version | Description |
|---------|---------|-------------|
| Django | 5.2.10 | Framework web Python |
| psycopg2-binary | 2.9.11 | Driver PostgreSQL |
| gunicorn | 23.0.0 | Serveur WSGI Python |
| whitenoise | 6.11.0 | Serveur fichiers statiques |
| python-decouple | 3.8 | Gestion variables d'environnement |

## Développement

| Package | Version | Description |
|---------|---------|-------------|
| pytest | 8.3.4 | Framework de tests |
| pytest-django | 4.9.0 | Plugin pytest pour Django |
| pytest-cov | 6.0.0 | Couverture de code |
| black | 25.1.0 | Formatter Python |
| ruff | 0.8.8 | Linter Python rapide |
| mypy | 1.14.0 | Type checker Python |
| django-debug-toolbar | 4.5.0 | Barre de debug Django |
| django-extensions | 3.2.3 | Extensions utiles Django |

## Environnement

- **Python** : 3.10+ (testé avec 3.10.13)
- **PostgreSQL** : 15+ recommandé
- **OS** : macOS, Linux, Windows

## Mise à jour

Pour mettre à jour toutes les dépendances :

```bash
# Production
pip install --upgrade -r requirements.txt

# Développement
pip install --upgrade -r requirements-dev.txt
```

## Vérification des versions

```bash
# Vérifier version Django
python -m django --version

# Lister toutes les dépendances
pip list

# Vérifier les mises à jour disponibles
pip list --outdated
```

## Compatibilité Django 5.2

Django 5.2 introduit :
- Support Python 3.10, 3.11, 3.12, 3.13
- Améliorations de performance
- Nouvelles fonctionnalités ORM
- Améliorations sécurité

Voir : https://docs.djangoproject.com/en/5.2/releases/5.2/

## Notes

- **WhiteNoise 6.11.0** : Meilleure compression des fichiers statiques
- **Gunicorn 23.0.0** : Support Python 3.13, améliorations performance
- **psycopg2-binary 2.9.11** : Corrections de bugs, stabilité améliorée

---

*Toutes les versions sont les dernières stables au 16 janvier 2026*
