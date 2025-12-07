# Configuration Vercel pour le Mode Gratuit (OpenAI)

Pour que les utilisateurs gratuits fonctionnent sur Vercel, vous devez ajouter votre clé API OpenAI.

## Étapes Rapides :

1.  Allez sur votre dashboard Vercel : https://vercel.com/dashboard
2.  Sélectionnez votre projet **jenny-v2**.
3.  Allez dans l'onglet **Settings** > **Environment Variables**.
4.  Ajoutez une nouvelle variable :
    *   **Key** : `OPENAI_API_KEY`
    *   **Value** : `sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx` (Votre clé OpenAI commençant par sk-)
5.  (Optionnel) Si vous voulez changer le modèle (par défaut gpt-3.5-turbo) :
    *   **Key** : `OPENAI_MODEL`
    *   **Value** : `gpt-4o-mini` (ou autre)
6.  **IMPORTANT** : Une fois les variables ajoutées, vous devez **Redéployer** votre application pour qu'elles soient prises en compte (allez dans Deployments > Redeploy).

## Vérification

Le code est déjà configuré pour détecter cette clé :
- Si `OPENAI_API_KEY` est présente -> Utilise OpenAI (Mode Free).
- Si `OPENAI_API_KEY` est absente -> Tente OpenRouter (Fallback).