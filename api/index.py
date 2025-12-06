# api/index.py
from app.services.email import send_verification_email
from app import create_app, db
from app.models import User
from flask import request, jsonify
import random

# Créer l'application Flask
app = create_app()

# Route API pour l'envoi de code
@app.route('/api/send-code', methods=['POST'])
def api_send_code():
    """API pour envoyer le code de vérification par email"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({"error": "Email manquant"}), 400

        # Générer un code à 6 chiffres
        code = str(random.randint(100000, 999999))
        print(f"DEBUG: Code généré pour {email}: {code}")

        # Envoyer l'email via Brevo
        success = send_verification_email(email, code)
        
        if success:
            return jsonify({"message": "Code envoyé", "status": "success"}), 200
        else:
            return jsonify({"error": "Échec envoi email"}), 500
            
    except Exception as e:
        print(f"DEBUG: Erreur API send-code: {e}")
        return jsonify({"error": "Erreur serveur"}), 500

# Route API pour l'inscription
@app.route('/api/register', methods=['POST'])
def api_register():
    """API pour l'inscription avec vérification code"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        verification_code = data.get('verification_code')
        
        if not all([username, email, password, verification_code]):
            return jsonify({"error": "Tous les champs sont requis"}), 400

        # Vérifier si l'email existe déjà
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email déjà utilisé"}), 400
            
        # Vérifier si le username existe déjà
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username déjà utilisé"}), 400
        
        # Créer l'utilisateur
        new_user = User(
            username=username,
            email=email,
            is_active=True,
            email_verified=True
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({"message": "Inscription réussie !", "status": "success"}), 200
        
    except Exception as e:
        print(f"DEBUG: Erreur API register: {e}")
        return jsonify({"error": "Erreur serveur"}), 500
# api/index.py
from app.services.email import send_verification_email
from app import create_app, db
from app.models import User
from flask import request, jsonify, url_for
from flask_login import login_user
import random

# Créer l'application Flask
app = create_app()

# Route API pour l'envoi de code
@app.route('/api/send-code', methods=['POST'])
def api_send_code():
    """API pour envoyer le code de vérification par email"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({"error": "Email manquant"}), 400

        # Générer un code à 6 chiffres
        code = str(random.randint(100000, 999999))
        print(f"DEBUG: Code généré pour {email}: {code}")

        # Envoyer l'email via Brevo
        success = send_verification_email(email, code)
        
        if success:
            return jsonify({"message": "Code envoyé", "status": "success"}), 200
        else:
            return jsonify({"error": "Échec envoi email"}), 500
            
    except Exception as e:
        print(f"DEBUG: Erreur API send-code: {e}")
        return jsonify({"error": "Erreur serveur"}), 500

# Route API pour l'inscription
@app.route('/api/register', methods=['POST'])
def api_register():
    """API pour l'inscription avec vérification code"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        verification_code = data.get('verification_code')
        
        if not all([username, email, password, verification_code]):
            return jsonify({"error": "Tous les champs sont requis"}), 400

        # Vérifier si l'email existe déjà
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email déjà utilisé"}), 400
            
        # Vérifier si le username existe déjà
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username déjà utilisé"}), 400
        
        # Créer l'utilisateur
        new_user = User(
            username=username,
            email=email,
            is_active=True,
            email_verified=True
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({"message": "Inscription réussie !", "status": "success"}), 200
        
    except Exception as e:
        print(f"DEBUG: Erreur API register: {e}")
        return jsonify({"error": "Erreur serveur"}), 500

# Route API pour la connexion
@app.route('/api/login', methods=['POST'])
def api_login():
    """API pour la connexion des utilisateurs."""
    with app.app_context():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email et mot de passe requis'}), 400

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            redirect_url = url_for('admin') if user.is_admin else url_for('chat_page')
            return jsonify({'redirect': redirect_url})
        
        return jsonify({'error': 'Email ou mot de passe invalide'}), 401