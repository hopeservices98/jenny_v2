from flask import current_app, request, jsonify, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
import random
import string
from .. import db, limiter
from ..models import User

# Stockage temporaire des codes de vérification (email -> code)
# Dans une production réelle, utilisez Redis ou une table de base de données avec expiration
pending_verifications = {}

def generate_validation_code():
    return ''.join(random.choices(string.digits, k=6))

def register_auth_routes(app):
    """Enregistre les routes d'authentification."""
    
    @app.route('/auth/send-code', methods=['POST'])
    @limiter.limit("5 per minute")
    def send_verification_code():
        print(f"DEBUG: Reçu demande send-code")
        try:
            data = request.get_json()
            print(f"DEBUG: Data reçue: {data}")
        except Exception as e:
            print(f"DEBUG: Erreur parsing JSON: {e}")
            return jsonify({'error': 'Invalid JSON'}), 400

        email = data.get('email')
        print(f"DEBUG: Email extrait: {email}")
        
        if not email:
            print("DEBUG: Email manquant")
            return jsonify({'error': 'Email requis'}), 400
            
        if User.query.filter_by(email=email).first():
            print(f"DEBUG: Email {email} déjà utilisé")
            return jsonify({'error': 'Cet email est déjà utilisé'}), 400
            
        code = generate_validation_code()
        pending_verifications[email] = code
        
        # Envoi réel de l'email
        from ..services.email import send_verification_email
        email_sent = send_verification_email(email, code)
        
        if email_sent:
            return jsonify({'message': 'Code envoyé avec succès'})
        else:
            return jsonify({'error': 'Erreur lors de l\'envoi du code. Veuillez réessayer.'}), 500
    @app.route('/api/check-email', methods=['POST'])
    def check_email_availability():
        data = request.get_json()
        email = data.get('email')
        if not email:
            return jsonify({'available': False, 'error': 'Email requis'}), 400
            
        if User.query.filter_by(email=email).first():
            return jsonify({'available': False, 'error': 'Cet email est déjà utilisé. Connectez-vous.'})
        
        return jsonify({'available': True})
    @app.route('/auth/verify-code', methods=['POST'])
    def verify_code_check():
        data = request.get_json()
        email = data.get('email')
        code = data.get('code')
        
        if not email or not code:
            return jsonify({'valid': False, 'message': 'Données incomplètes'}), 400
            
        if email in pending_verifications and pending_verifications[email] == code:
            return jsonify({'valid': True, 'message': 'Code valide !'})
        else:
            return jsonify({'valid': False, 'message': 'Code invalide'}), 200

    @app.route('/login', methods=['GET', 'POST'])
    @limiter.limit("5 per minute") # Limite à 5 tentatives par minute pour éviter le brute-force
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('chat_page'))
        if request.method == 'POST':
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            print(f"Tentative de connexion pour: {email}")
            
            # Vérification spéciale pour l'admin (connexion par username 'admin' sans email)
            if email == 'admin':
                user = User.query.filter_by(username='admin').first()
            else:
                user = User.query.filter_by(email=email).first()

            if user:
                print(f"Utilisateur trouvé: {user.username}")
                if user.check_password(password):
                    print("Mot de passe correct")
                    
                    # Plus de blocage pour email non vérifié ou inactif ici,
                    # car l'inscription garantit désormais la validation.
                    # On garde juste la vérification admin si nécessaire, mais pour l'instant on simplifie.

                    login_user(user)
                    if user.is_admin:
                        return jsonify({'redirect': url_for('admin')})
                    return jsonify({'redirect': url_for('chat_page')})
                else:
                    print("Mot de passe incorrect")
            else:
                print("Utilisateur non trouvé")
            return jsonify({'error': 'Email ou mot de passe invalide'}), 401
        return current_app.send_static_file('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    @limiter.limit("10 per hour") # Limite augmentée pour ne pas frustrer les utilisateurs légitimes
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('chat_page'))
        if request.method == 'POST':
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            confirm_password = data.get('confirm_password')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            address = data.get('address')
            birth_date_str = data.get('birth_date')
            verification_code = data.get('verification_code')

            if not all([username, email, password, confirm_password, first_name, last_name, address, birth_date_str, verification_code]):
                return jsonify({'error': 'Tous les champs sont obligatoires, y compris le code de vérification'}), 400

            if password != confirm_password:
                return jsonify({'error': 'Les mots de passe ne correspondent pas'}), 400

            # Vérification du code
            if email not in pending_verifications or pending_verifications[email] != verification_code:
                return jsonify({'error': 'Code de vérification invalide ou expiré'}), 400

            if User.query.filter_by(username=username).first():
                return jsonify({'error': 'Ce nom d\'utilisateur existe déjà'}), 400
            
            if User.query.filter_by(email=email).first():
                return jsonify({'error': 'Cet email est déjà utilisé'}), 400

            try:
                birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Format de date invalide'}), 400

            new_user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                address=address,
                birth_date=birth_date,
                is_active=True, # Actif directement car email validé
                email_verified=True, # Email validé
                validation_code=None
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            # Nettoyage du code utilisé
            if email in pending_verifications:
                del pending_verifications[email]
            
            return jsonify({
                'message': 'Inscription réussie ! Vous pouvez maintenant vous connecter.',
                'redirect_to_login': True
            })
        return current_app.send_static_file('register.html')

    @app.route('/forgot-password', methods=['GET', 'POST'])
    def forgot_password():
        if request.method == 'POST':
            data = request.get_json()
            email = data.get('email')
            user = User.query.filter_by(email=email).first()
            
            if user:
                # Générer un token de réinitialisation
                import secrets
                import string
                reset_token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
                
                # Stocker le token avec expiration (1 heure)
                from datetime import datetime, timedelta
                user.reset_token = reset_token
                user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
                db.session.commit()
                
                # Créer le lien de réinitialisation
                from flask import url_for
                reset_link = url_for('reset_password_form', token=reset_token, _external=True)
                
                # Envoyer l'email
                from ..services.email import send_password_reset_email
                email_sent = send_password_reset_email(email, reset_link)
                
                if email_sent:
                    return jsonify({'message': 'Un lien de réinitialisation a été envoyé à votre email.'})
                else:
                    return jsonify({'error': 'Erreur lors de l\'envoi de l\'email. Veuillez réessayer.'}), 500
            
            # Toujours retourner le même message pour la sécurité
            return jsonify({'message': 'Si cet email existe, un lien de réinitialisation a été envoyé.'})
        return current_app.send_static_file('forgot_password.html')

    @app.route('/reset-password', methods=['POST'])
    def reset_password():
        data = request.get_json()
        email = data.get('email')
        new_password = data.get('new_password')
        
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(new_password)
            db.session.commit()
            return jsonify({'message': 'Mot de passe mis à jour avec succès'})
        return jsonify({'error': 'Utilisateur non trouvé'}), 404

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))
