# Galaxy Market Admin Dashboard

Ce projet est un tableau de bord d'administration pour Galaxy Market, construit avec Flask.

## Structure du projet

- `main.py` : Point d'entrée de l'application.
- `api_client.py` : Client pour communiquer avec l'API backend.
- `blueprints/` : Modules logiques de l'application (Auth, Dashboard, Users, etc.).
- `templates/` : Fichiers HTML Jinja2.
- `static/` : Fichiers CSS et JS.

## Installation

1. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

2. Lancez l'application :
   ```bash
   python main.py
   ```

3. Accédez au dashboard :
   `http://localhost:5000`

## Authentification

L'application utilise un Bearer Token JWT stocké en session. Connectez-vous via la page de login pour obtenir un token.
L'URL de base de l'API est `https://galaxy.mirhosty.com/api/admin`.
