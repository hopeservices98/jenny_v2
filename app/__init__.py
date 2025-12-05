from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

db = SQLAlchemy()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address)

def create_app():
    """Construct the core application."""
    # Serve static files from the 'frontend' directory at the root URL
    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
    app = Flask(__name__, instance_relative_config=False, static_folder=frontend_path, static_url_path='')
    app.config.from_object('app.config.Config')

    # Sécurité : En-têtes HTTP (CSP, HSTS, etc.)
    # content_security_policy=None permet de charger les scripts inline et externes (Tailwind, Marked)
    # force_https=False car on est en local (mettre à True en prod)
    Talisman(app, content_security_policy=None, force_https=False)

    # Sécurité : Rate Limiting (Protection contre brute-force et abus)
    limiter.init_app(app)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    # Configuration de la session permanente
    from datetime import timedelta
    app.permanent_session_lifetime = timedelta(seconds=app.config['PERMANENT_SESSION_LIFETIME'])

    with app.app_context():
        # Register all route modules
        from .routes.auth import register_auth_routes
        from .routes.admin import register_admin_routes
        from .routes.chat import register_chat_routes
        from .routes.files import register_files_routes
        from .routes.user import register_user_routes
        
        # Register routes with the app
        register_auth_routes(app)
        register_admin_routes(app)
        register_chat_routes(app)
        register_files_routes(app)
        register_user_routes(app)
        from .models import User

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        # Create database tables for our models
        db.create_all()
        
        # Initialisation base de données avec utilisateur admin
        from app.models import User
        try:
            if not User.query.filter_by(username='admin').first():
                admin_user = User(
                    username='admin',
                    email='admin@example.com',
                    is_admin=True,
                    is_active=True
                )
                admin_user.set_password('Admin123!')
                db.session.add(admin_user)
                db.session.commit()
        except Exception as e:
            print("DB init error:", e)

        return app