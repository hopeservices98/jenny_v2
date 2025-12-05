import os
import google.generativeai as genai

def load_api_key():
    """Charge la clé API depuis un fichier ou une variable d'environnement."""
    # Priorité 1: Variable d'environnement
    key = os.environ.get('GOOGLE_API_KEY')
    if key:
        print("INFO: Clé API chargée depuis la variable d'environnement.")
        return key

    # Priorité 2: Fichiers locaux
    key_files = ['google_cle.txt', 'cle_api.txt']
    for filename in key_files:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                key = f.read().strip()
                if key:
                    print(f"INFO: Clé API chargée depuis le fichier : {filename}")
                    return key
    return None

def run_test():
    """Exécute une série de tests pour valider la clé et la génération de contenu."""
    api_key = load_api_key()
    if not api_key:
        print("\n--- ERREUR ---")
        print("Clé API Google introuvable.")
        print("Veuillez la placer dans un fichier 'google_cle.txt' ou la définir comme variable d'environnement 'GOOGLE_API_KEY'.")
        return

    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"\n--- ERREUR DE CONFIGURATION ---")
        print(f"La configuration de l'API a échoué : {e}")
        return

    # --- Test 1: Lister les modèles ---
    print("\n--- TEST 1: LISTAGE DES MODÈLES ---")
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if not models:
            print("ERREUR: Aucun modèle de génération de contenu trouvé pour cette clé.")
            return
            
        print(f"Succès ! {len(models)} modèles de génération de contenu trouvés.")
        model_to_test = "models/gemini-2.5-flash"
        if model_to_test not in models:
             print(f"AVERTISSEMENT: Le modèle '{model_to_test}' n'est pas dans la liste, mais nous allons quand même essayer.")

    except Exception as e:
        print(f"ERREUR lors du listage des modèles : {e}")
        return

    # --- Test 2: Générer du contenu ---
    print("\n--- TEST 2: GÉNÉRATION DE CONTENU SIMPLE ---")
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = "Bonjour, qui es-tu ?"
        print(f"Envoi du prompt : '{prompt}'")
        
        response = model.generate_content(prompt)
        
        print("\n--- RÉSULTAT ---")
        print("Succès ! L'API a répondu.")
        print(f"Réponse de l'IA : {response.text}")

    except Exception as e:
        print("\n--- ERREUR DE GÉNÉRATION ---")
        print("Le test de génération de contenu a échoué. Voici l'erreur exacte :")
        print(e)

if __name__ == '__main__':
    run_test()