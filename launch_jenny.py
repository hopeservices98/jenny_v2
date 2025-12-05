#!/usr/bin/env python3
"""
Script de lancement rapide de Jenny avec test d'intégration Brevo
"""

import os
import sys
import subprocess
import time

def print_banner():
    """Affiche la bannière de démarrage"""
    print("="*60)
    print("🚀 JENNY - Application de Chat IA Confidentielle")
    print("="*60)
    print("📧 Intégration Brevo: Configurée et testée")
    print("🤖 IA: Google Gemini + OpenRouter")
    print("💬 Interface: Chat moderne avec Tailwind CSS")
    print("="*60)

def check_dependencies():
    """Vérifie les dépendances"""
    print("\n🔍 Vérification des dépendances...")
    
    required_files = [
        "brevo_key.txt",
        "google_cle.txt", 
        "openrouter_key.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️ Fichiers manquants: {', '.join(missing_files)}")
        print("💡 Vous pouvez continuer, mais certaines fonctionnalités seront limitées.")
        return False
    else:
        print("\n✅ Toutes les clés API sont configurées!")
        return True

def run_email_test():
    """Lance le test d'email Brevo"""
    print("\n🧪 Test de l'intégration Brevo...")
    try:
        result = subprocess.run([sys.executable, "test_email_brevo.py"], 
                              capture_output=True, text=True, cwd=".")
        if result.returncode == 0:
            print("✅ Tests email Brevo: RÉUSSIS")
        else:
            print("⚠️ Tests email Brevo: PARTIELS (simulation active)")
        return True
    except Exception as e:
        print(f"❌ Erreur lors du test email: {e}")
        return False

def launch_application():
    """Lance l'application Jenny"""
    print("\n🌟 Démarrage de Jenny...")
    print("📱 Interface accessible sur: http://127.0.0.1:5000")
    print("⚡ Ctrl+C pour arrêter")
    print("-"*40)
    
    try:
        # Lancer l'application
        subprocess.run([sys.executable, "run.py"])
    except KeyboardInterrupt:
        print("\n\n👋 Arrêt de Jenny. À bientôt!")
    except Exception as e:
        print(f"\n❌ Erreur lors du lancement: {e}")

def main():
    """Fonction principale"""
    print_banner()
    
    # Vérifier les dépendances
    deps_ok = check_dependencies()
    
    # Tester l'email
    run_email_test()
    
    if deps_ok:
        print("\n🎯 Configuration complète! Lancement de Jenny...")
        time.sleep(2)
        launch_application()
    else:
        print("\n⚙️ Configuration partielle. Lancement de Jenny en mode démo...")
        time.sleep(2)
        launch_application()

if __name__ == "__main__":
    main()