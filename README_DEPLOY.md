MursCommerciaux — Déploiement Streamlit (One-click)

Contenu
-------
Ce dépôt contient une application Streamlit prête à être déployée sur Streamlit Cloud.
Fichiers clefs:
- app.py                : application principale Streamlit
- parsers.py            : parseurs par site (heuristiques)
- requirements.txt      : dépendances
- sample_seeds.txt      : exemples d'URLs
- LICENSE               : MIT (pour usage perso)
- README_DEPLOY.md      : ce fichier

Déploiement (3 étapes simples)
1) Crée un compte GitHub (https://github.com) si tu n'en as pas.
2) Crée un nouveau dépôt et upload tout le contenu de ce dossier (ou clique sur "Upload files" et envoie le .zip).
3) Va sur https://share.streamlit.io, connecte ton compte GitHub et choisis le dépôt & la branche. Clique "Deploy".

Résultat: tu obtiens un lien public du type: https://share.streamlit.io/<ton-utilisateur>/<ton-repo>/main/app.py
Tu pourras ensuite partager le lien, et chaque mise à jour du repo déclenchera un nouveau déploiement.

Notes
-----
- Respecte les robots.txt et CGU des sites scrappés.
- Les parseurs fournis sont heuristiques et nécessiteront souvent des ajustements site-par-site.
- Si tu veux, je peux t'aider à adapter les parseurs à 2–3 sites prioritaires (fournis les URLs d'exemples).
