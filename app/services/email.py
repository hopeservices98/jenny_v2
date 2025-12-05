"""
Service d'envoi d'emails avec Brevo (ex-Sendinblue)
"""
import requests
import os
import logging
from datetime import datetime

def load_brevo_api_key():
    """Charge la clé API Brevo de manière sécurisée"""
    # Essayer d'abord les variables d'environnement
    api_key = os.environ.get('BREVO_API_KEY')
    
    if api_key:
        return api_key
    
    # Fallback vers le fichier de configuration
    try:
        possible_paths = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'brevo_key.txt')),
            os.path.abspath('brevo_key.txt'),
            'brevo_key.txt'
        ]
        
        for brevo_config_path in possible_paths:
            if os.path.exists(brevo_config_path):
                with open(brevo_config_path, 'r') as f:
                    file_key = f.read().strip()
                    if file_key:
                        print(f"INFO: Clé API Brevo chargée depuis {brevo_config_path}")
                        return file_key
                    else:
                        logging.error("Clé API Brevo vide dans le fichier de configuration")
                        break
        else:
            logging.error("Aucun fichier de clé API Brevo trouvé")
    except Exception as e:
        logging.error(f"Erreur lors de la lecture de la clé API Brevo: {e}")
    
    return None

def send_verification_email(email, code):
    """
    Envoie un email de vérification avec un code à 6 chiffres via Brevo
    """
    try:
        # Charger la clé API
        api_key = load_brevo_api_key()
        
        if not api_key:
            # Simulation si aucune clé n'est disponible
            logging.warning("BREVO_API_KEY non configurée - simulation d'envoi")
            print(f"--- EMAIL SIMULATION ---")
            print(f"To: {email}")
            print(f"Code: {code}")
            print(f"Subject: Code de vérification - Jenny")
            print(f"--- END SIMULATION ---")
            return True
        
        # Configuration de l'email
        email_data = {
            "sender": {
                "name": "Jenny",
                "email": "9d6e49001@smtp-brevo.com"
            },
            "to": [
                {
                    "email": email,
                    "name": "Utilisateur"
                }
            ],
            "subject": "Code de vérification - Jenny",
            "htmlContent": f'''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Code de vérification Jenny</title>
            </head>
            <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; margin: 0; padding: 20px;">
                <div style="max-width: 500px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%); padding: 30px; text-align: center;">
                        <h1 style="color: white; margin: 0; font-size: 28px;">Jenny</h1>
                        <p style="color: #fce7f3; margin: 5px 0 0 0; font-style: italic;">Ta confidente intime</p>
                    </div>
                    
                    <div style="padding: 30px;">
                        <h2 style="color: #374151; margin-top: 0;">Vérification de votre email</h2>
                        
                        <p style="color: #6b7280; line-height: 1.6;">
                            Bonjour !<br>
                            Pour compléter votre inscription sur Jenny, utilisez ce code de vérification :
                        </p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <div style="display: inline-block; background: #f3f4f6; padding: 20px; border-radius: 10px; border: 2px dashed #d1d5db;">
                                <span style="font-size: 36px; font-weight: bold; color: #ec4899; letter-spacing: 8px; font-family: monospace;">{code}</span>
                            </div>
                        </div>
                        
                        <p style="color: #6b7280; font-size: 14px; margin-bottom: 0;">
                            <strong>⚠️ Important :</strong> Ce code expire dans <strong>10 minutes</strong>.
                        </p>
                        
                        <div style="background: #fef3c7; border: 1px solid #f59e0b; border-radius: 5px; padding: 15px; margin-top: 20px;">
                            <p style="color: #92400e; margin: 0; font-size: 14px;">
                                💡 <strong>Conseil :</strong> Si vous n'avez pas demandé ce code, ignorez cet email.
                            </p>
                        </div>
                    </div>
                    
                    <div style="background: #f9fafb; padding: 20px; text-align: center; border-top: 1px solid #e5e7eb;">
                        <p style="color: #9ca3af; font-size: 12px; margin: 0;">
                            © 2025 Jenny - Votre confidente IA
                        </p>
                    </div>
                </div>
            </body>
            </html>
            '''
        }
        
        # Envoi via l'API Brevo
        headers = {
            'api-key': api_key,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            'https://api.brevo.com/v3/smtp/email',
            headers=headers,
            json=email_data
        )
        
        if response.status_code == 201:
            logging.info(f"Email envoyé avec succès à {email}")
            print(f"SUCCESS: Email envoyé à {email} - Code: {code}")
            return True
        else:
            logging.error(f"Erreur envoi email - Status: {response.status_code} - {response.text}")
            print(f"ERROR: Erreur envoi email: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logging.error(f"Erreur lors de l'envoi de l'email: {e}")
        print(f"❌ Erreur envoi email: {e}")
        return False

def send_password_reset_email(email, reset_link):
    """
    Envoie un email pour la réinitialisation de mot de passe via Brevo
    """
    try:
        # Charger la clé API
        api_key = load_brevo_api_key()
        
        if not api_key:
            # Simulation si aucune clé n'est disponible
            logging.warning("BREVO_API_KEY non configurée - simulation d'envoi")
            print(f"--- EMAIL SIMULATION ---")
            print(f"To: {email}")
            print(f"Subject: Réinitialisation de mot de passe - Jenny")
            print(f"Link: {reset_link}")
            print(f"--- END SIMULATION ---")
            return True
        
        email_data = {
            "sender": {
                "name": "Jenny",
                "email": "9d6e49001@smtp-brevo.com"
            },
            "to": [
                {
                    "email": email,
                    "name": "Utilisateur"
                }
            ],
            "subject": "Réinitialisation de mot de passe - Jenny",
            "htmlContent": f'''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Réinitialisation de mot de passe</title>
            </head>
            <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; margin: 0; padding: 20px;">
                <div style="max-width: 500px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%); padding: 30px; text-align: center;">
                        <h1 style="color: white; margin: 0; font-size: 28px;">Jenny</h1>
                        <p style="color: #fce7f3; margin: 5px 0 0 0; font-style: italic;">Ta confidente intime</p>
                    </div>
                    
                    <div style="padding: 30px;">
                        <h2 style="color: #374151; margin-top: 0;">Réinitialisation de mot de passe</h2>
                        
                        <p style="color: #6b7280; line-height: 1.6;">
                            Vous avez demandé à réinitialiser votre mot de passe pour Jenny.
                        </p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{reset_link}" 
                               style="display: inline-block; background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; box-shadow: 0 4px 6px rgba(236, 72, 153, 0.3);">
                                Réinitialiser mon mot de passe
                            </a>
                        </div>
                        
                        <p style="color: #6b7280; font-size: 14px;">
                            Ce lien expire dans <strong>1 heure</strong>.
                        </p>
                        
                        <div style="background: #fef3c7; border: 1px solid #f59e0b; border-radius: 5px; padding: 15px; margin-top: 20px;">
                            <p style="color: #92400e; margin: 0; font-size: 14px;">
                                ⚠️ <strong>Sécurité :</strong> Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.
                            </p>
                        </div>
                    </div>
                    
                    <div style="background: #f9fafb; padding: 20px; text-align: center; border-top: 1px solid #e5e7eb;">
                        <p style="color: #9ca3af; font-size: 12px; margin: 0;">
                            © 2025 Jenny - Votre confidente IA
                        </p>
                    </div>
                </div>
            </body>
            </html>
            '''
        }
        
        headers = {
            'api-key': api_key,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            'https://api.brevo.com/v3/smtp/email',
            headers=headers,
            json=email_data
        )
        
        if response.status_code == 201:
            logging.info(f"Email de réinitialisation envoyé à {email}")
            print(f"SUCCESS: Email de réinitialisation envoyé à {email}")
            return True
        else:
            logging.error(f"Erreur envoi email réinitialisation - Status: {response.status_code} - {response.text}")
            print(f"ERROR: Erreur envoi email réinitialisation: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logging.error(f"Erreur lors de l'envoi de l'email de réinitialisation: {e}")
        print(f"❌ Erreur envoi email réinitialisation: {e}")
        return False