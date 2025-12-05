#!/usr/bin/env python3
"""
Script de test pour l'intégration Brevo dans Jenny
Teste l'envoi d'emails de vérification et de réinitialisation
"""

import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.services.email import send_verification_email, send_password_reset_email

def test_verification_email():
    """Test d'envoi d'email de vérification"""
    print("Test d'envoi d'email de verification...")
    
    # Email de test (utilisez votre propre email)
    test_email = "test@example.com"
    test_code = "123456"
    
    try:
        result = send_verification_email(test_email, test_code)
        if result:
            print("SUCCESS: Email de verification envoyé avec succes!")
            print(f"Destinataire: {test_email}")
            print(f"Code: {test_code}")
        else:
            print("ERROR: Echec de l'envoi d'email de verification")
        return result
    except Exception as e:
        print(f"ERROR: Erreur lors du test: {e}")
        return False

def test_password_reset_email():
    """Test d'envoi d'email de réinitialisation"""
    print("\nTest d'envoi d'email de reinitialisation...")
    
    # Email et lien de test
    test_email = "test@example.com"
    test_reset_link = "http://localhost:5000/reset-password?token=abc123"
    
    try:
        result = send_password_reset_email(test_email, test_reset_link)
        if result:
            print("SUCCESS: Email de reinitialisation envoyé avec succes!")
            print(f"Destinataire: {test_email}")
            print(f"Lien: {test_reset_link}")
        else:
            print("ERROR: Echec de l'envoi d'email de reinitialisation")
        return result
    except Exception as e:
        print(f"ERROR: Erreur lors du test: {e}")
        return False

def check_brevo_key():
    """Vérifie si la clé API Brevo est configurée"""
    print("Verification de la cle API Brevo...")
    
    # Vérifier les variables d'environnement
    env_key = os.environ.get('BREVO_API_KEY')
    if env_key:
        print("SUCCESS: Cle API trouvee dans les variables d'environnement")
        return True
    
    # Vérifier le fichier de configuration
    brevo_key_path = os.path.join(os.path.dirname(__file__), 'brevo_key.txt')
    if os.path.exists(brevo_key_path):
        try:
            with open(brevo_key_path, 'r') as f:
                file_key = f.read().strip()
                if file_key:
                    print("SUCCESS: Cle API trouvee dans brevo_key.txt")
                    return True
                else:
                    print("WARNING: Fichier brevo_key.txt trouve mais vide")
        except Exception as e:
            print(f"ERROR: Erreur lecture brevo_key.txt: {e}")
    else:
        print("ERROR: Aucune cle API trouvee")
    
    return False

def main():
    """Fonction principale de test"""
    print("Demarrage des tests d'integration Brevo pour Jenny\n")
    
    # Vérifier la configuration
    if not check_brevo_key():
        print("\nERROR: Configuration incomplète. Verifiez la cle API Brevo.")
        print("Vous pouvez:")
        print("   - Definir la variable d'environnement BREVO_API_KEY")
        print("   - Creer le fichier brevo_key.txt avec votre cle")
        return
    
    print("\n" + "="*50)
    
    # Tester l'email de vérification
    verification_success = test_verification_email()
    
    print("\n" + "-"*30)
    
    # Tester l'email de réinitialisation
    reset_success = test_password_reset_email()
    
    # Résumé des tests
    print("\n" + "="*50)
    print("RESUME DES TESTS:")
    print(f"Email de verification: {'SUCCESS' if verification_success else 'ECHEC'}")
    print(f"Email de reinitialisation: {'SUCCESS' if reset_success else 'ECHEC'}")
    
    if verification_success and reset_success:
        print("\nFELICITATIONS: Tous les tests sont passes avec succes!")
        print("L'integration Brevo est prete pour la production.")
    else:
        print("\nWARNING: Certains tests ont echoue. Verifiez la configuration.")

if __name__ == "__main__":
    main()