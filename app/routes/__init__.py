from functools import wraps
from flask import current_app, jsonify
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return jsonify({'error': 'Accès non autorisé'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Fichier de routage principal vide - les routes sont maintenant dans des modules séparés
