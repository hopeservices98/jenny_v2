from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(email='rak.angelo98@gmail.com').first()
    if user:
        user.is_admin = False
        db.session.commit()
        print(f"L'utilisateur {user.username} n'est plus administrateur.")
    else:
        print("Utilisateur non trouvé.")