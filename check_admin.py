from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f"Admin found: {admin.username}, Email: {admin.email}")
        if admin.check_password('Mine3472@'):
            print("Password correct")
        else:
            print("Password incorrect")
    else:
        print("Admin user not found")