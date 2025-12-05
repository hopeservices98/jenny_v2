# Import de l'application Flask
from app import create_app, db
from app.models import User

# Instance Flask globale - convention Vercel
app = create_app()

# Initialisation de la base de données
with app.app_context():
    try:
        db.create_all()
        # Créer l'utilisateur admin s'il n'existe pas
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', email='admin@example.com', is_admin=True, is_active=True)
            admin_user.set_password('Admin123!')
            db.session.add(admin_user)
            db.session.commit()
    except Exception as e:
        print(f"Erreur d'initialisation: {e}")

# Handler Vercel simplifié
def handler(request):
    # Gestion basique pour éviter les erreurs WSGI complexes
    return "Jenny AI Chat - Application en ligne!".encode('utf-8')