# Jenny - Application de Chat IA Confidentielle

## Description
Jenny est une application web de chat IA thérapeutique et confidentielle, conçue pour offrir des conversations intimes et analytiques. L'IA utilise des modèles avancés pour répondre de manière empathique, avec des fonctionnalités d'upload d'images et d'audios, une interface moderne, et des paramètres de sécurité ajustés.

## Fonctionnalités
- **Chat IA** : Conversations avec Jenny, IA thérapeutique utilisant Google Gemini 2.5 Flash.
- **Uploads** : Possibilité d'uploader des images et des audios directement dans le chat.
- **Interface Moderne** : Design sombre avec Tailwind CSS, avatar de Jenny, indicateur de frappe animé.
- **Sécurité** : Paramètres de sécurité ajustés pour permettre des discussions sensibles.
- **Historique** : Sauvegarde des conversations par utilisateur dans une base de données SQLite.

## Technologies Utilisées
- **Backend** : Flask (Python), SQLAlchemy, Google Generative AI.
- **Frontend** : HTML, CSS (Tailwind), JavaScript.
- **Base de Données** : SQLite.
- **IA** : Google Gemini 2.5 Flash.

## Installation et Configuration

### Prérequis
- Python 3.8+
- Pip
- Clé API Google Generative AI

### Étapes
1. **Cloner ou télécharger le projet** :
   ```
   git clone <repo-url>
   cd tchat
   ```

2. **Installer les dépendances** :
   ```
   pip install -r backend/requirements.txt
   ```

3. **Configurer l'API** :
   - Obtenir une clé API sur [Google AI Studio](https://aistudio.google.com/).
   - Activer l'API Generative AI dans Google Cloud Console.
   - Modifier `google_cle.txt` et `app/config.py` avec votre clé.

4. **Lancer l'application** :
   ```
   python run.py
   ```
   - Accéder à http://127.0.0.1:5000/

## Structure du Projet
- `run.py` : Point d'entrée de l'application.
- `app/` : Code backend Flask.
  - `routes.py` : Routes API et logique de chat.
  - `models.py` : Modèles de base de données.
  - `config.py` : Configuration.
- `frontend/` : Interface utilisateur.
  - `index.html` : Page principale.
  - `style.css` : Styles personnalisés.
  - `script.js` : Logique frontend.
- `images/` : Images pour les avatars et uploads.
- `uploads/` : Dossier pour les fichiers uploadés.
- `instance/` : Base de données SQLite.

## Utilisation
- Ouvrir l'application dans un navigateur.
- Commencer une conversation avec Jenny.
- Uploader des images ou audios via les boutons dédiés.
- Les réponses de Jenny sont générées par l'IA avec un focus sur l'empathie et l'analyse.

## Dépannage
- **Erreur API** : Vérifier la clé API et l'activation de l'API Generative AI.
- **Modèles non trouvés** : Utiliser le script `test_key.py` pour lister les modèles disponibles.
- **Uploads** : Assurer que les dossiers `images/` et `uploads/` existent.

## Licence
Ce projet est open-source. Utilisez-le à vos risques et périls.

## Contact
Pour des questions, contacter le développeur.