from flask import current_app, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from .. import db
from ..models import User

def register_user_routes(app):
    """Enregistre les routes utilisateur."""
    
    # Routes principales de base
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('chat_page'))
        return current_app.send_static_file('home.html')

    @app.route('/chat_page')
    @login_required
    def chat_page():
        return current_app.send_static_file('index.html')

    # API Routes pour l'utilisateur
    @app.route('/api/me', methods=['GET'])
    @login_required
    def get_current_user():
        user = current_user
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'address': user.address,
            'birth_date': user.birth_date.isoformat() if user.birth_date else None,
            'avatar_url': user.avatar_url,
            'is_admin': user.is_admin,
            'is_premium': user.is_premium
        })

    @app.route('/api/upgrade_premium', methods=['POST'])
    @login_required
    def upgrade_premium():
        user = current_user
        data = request.get_json()
        premium_code = data.get('code', '').strip()
        
        # Vérification du code premium
        if premium_code != 'Mine3472@':
            return jsonify({'success': False, 'message': 'Code premium invalide.'}), 400
        
        user.is_premium = True
        db.session.commit()
        return jsonify({'success': True, 'message': 'Félicitations ! Vous êtes maintenant Premium.'})

    @app.route('/api/me', methods=['PUT'])
    @login_required
    def update_current_user():
        user = current_user
        data = request.get_json()
        
        # Champs modifiables par l'utilisateur
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'address' in data:
            user.address = data['address']
        if 'birth_date' in data:
            try:
                user.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Format de date invalide'}), 400
        if 'username' in data:
            new_username = data['username']
            if new_username != user.username:
                if User.query.filter(User.id != user.id, User.username == new_username).first():
                    return jsonify({'error': 'Ce nom d\'utilisateur existe déjà'}), 400
                user.username = new_username

        db.session.commit()
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'address': user.address,
            'birth_date': user.birth_date.isoformat() if user.birth_date else None,
            'avatar_url': user.avatar_url,
            'is_admin': user.is_admin,
            'is_premium': user.is_premium
        })
