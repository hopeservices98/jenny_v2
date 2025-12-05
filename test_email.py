#!/usr/bin/env python3
"""
Script de test pour vérifier l'envoi d'emails avec SendGrid
"""

import os
import sys

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.abspath('.'))

from app.services.email import send_verification_email

def test_email_simulation():
    """Test en mode simulation (sans clé API)"""
    print("🧪 Test d'envoi d'email en mode simulation...")
    
    test_email = "test@example.com"
    test_code = "123456"
    
    result = send_verification_email(test_email, test_code)
    
    if result:
        print("✅ Test réussi - Email simulé avec succès")
    else:
        print("❌ Test échoué - Erreur lors de la simulation")
    
    return result

def test_email_config():
    """Vérifier la configuration des variables d'environnement"""
    print("\n🔧 Vérification de la configuration...")
    
    sendgrid_key = os.environ.get('SENDGRID_API_KEY')
    
    if sendgrid_key:
        print(f"✅ SENDGRID_API_KEY configurée: {sendgrid_key[:10]}...")
        return True
    else:
        print("⚠️ SENDGRID_API_KEY non configurée - Utilisation du mode simulation")
        return False

def main():
    print("🚀 Test du service d'email Jenny")
    print("=" * 50)
    
    # Vérifier la configuration
    has_api_key = test_email_config()
    
    # Tester l'envoi
    success = test_email_simulation()
    
    print("\n" + "=" * 50)
    print("📊 Résumé:")
    if has_api_key:
        if success:
            print("✅ Service d'email opérationnel avec SendGrid")
        else:
            print("❌ Configuration SendGrid incorrecte")
    else:
        if success:
            print("✅ Service d'email en mode simulation")
            print("💡 Pour activer l'envoi réel: configurez SENDGRID_API_KEY")
        else:
            print("❌ Erreur dans le mode simulation")
    
    print("\n📋 Étapes pour activer l'envoi réel:")
    print("1. Créer un compte sur sendgrid.com")
    print("2. Obtenir une API key gratuite (100 emails/jour)")
    print("3. Vérifier un domaine d'expéditeur")
    print("4. Configurer SENDGRID_API_KEY dans les variables d'environnement")

if __name__ == "__main__":
    main()