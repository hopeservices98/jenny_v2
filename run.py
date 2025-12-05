from app import create_app, db
from app.models import User

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', email='admin@example.com', is_admin=True, is_active=True)
            admin_user.set_password('Admin123!') # Mot de passe par défaut plus standard (à changer)
            db.session.add(admin_user)
            db.session.commit()
    app.run(debug=True, port=5000)