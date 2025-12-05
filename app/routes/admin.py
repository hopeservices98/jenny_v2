from flask import current_app, jsonify, request
from flask_login import login_required, current_user
from functools import wraps
from .. import db
from ..models import User

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return jsonify({'error': 'Accès non autorisé'}), 403
        return f(*args, **kwargs)
    return decorated_function

def register_admin_routes(app):
    """Enregistre les routes d'administration."""
    
    @app.route('/admin')
    @login_required
    @admin_required
    def admin():
        return current_app.send_static_file('admin.html')

    @app.route('/api/users', methods=['GET'])
    @login_required
    @admin_required
    def get_users():
        users = User.query.all()
        return jsonify([{
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'is_admin': u.is_admin,
            'is_active': u.is_active,
            'is_premium': u.is_premium
        } for u in users])

    @app.route('/api/users/<int:user_id>/validate', methods=['PUT'])
    @login_required
    @admin_required
    def validate_user(user_id):
        user = User.query.get_or_404(user_id)
        user.is_active = True
        db.session.commit()
        # Ici, on pourrait envoyer un email de confirmation
        return jsonify({'message': 'Utilisateur validé avec succès'})

    @app.route('/api/users/<int:user_id>/toggle_premium', methods=['PUT'])
    @login_required
    @admin_required
    def toggle_premium(user_id):
        user = User.query.get_or_404(user_id)
        user.is_premium = not user.is_premium
        db.session.commit()
        status = "Premium" if user.is_premium else "Free"
        return jsonify({'message': f'Utilisateur passé en {status}', 'is_premium': user.is_premium})

    @app.route('/api/users', methods=['POST'])
    @login_required
    @admin_required
    def create_user():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        is_admin = data.get('is_admin', False)
        if not username or not password:
            return jsonify({'error': 'Nom d\'utilisateur et mot de passe requis'}), 400
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Ce nom d\'utilisateur existe déjà'}), 400
        new_user = User(username=username, is_admin=is_admin)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'id': new_user.id, 'username': new_user.username, 'is_admin': new_user.is_admin}), 201

    @app.route('/api/users/<int:user_id>', methods=['PUT'])
    @login_required
    @admin_required
    def update_user(user_id):
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        is_admin = data.get('is_admin')
        is_active = data.get('is_active')
        
        if username:
            if User.query.filter(User.id != user_id, User.username == username).first():
                return jsonify({'error': 'Ce nom d\'utilisateur existe déjà'}), 400
            user.username = username
        if password:
            user.set_password(password)
        if is_admin is not None:
            user.is_admin = is_admin
        if is_active is not None:
            user.is_active = is_active
            
        db.session.commit()
        return jsonify({
            'id': user.id,
            'username': user.username,
            'is_admin': user.is_admin,
            'is_active': user.is_active
        })

    @app.route('/api/users/<int:user_id>', methods=['DELETE'])
    @login_required
    @admin_required
    def delete_user(user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return '', 204

    @app.route('/api/clean_old_generations', methods=['POST'])
    @login_required
    @admin_required
    def clean_old_generations():
        """Nettoie les générations anciennes (plus de 1 heure)."""
        import time
        current_time = time.time()
        to_remove = []

        # Cette partie pourrait être dans un cache séparé
        # Pour l'instant, on retourne juste un message
        return jsonify({'cleaned': 0})
