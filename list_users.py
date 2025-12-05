from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    users = User.query.all()
    print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Is Admin':<10} {'Is Premium':<10}")
    print("-" * 90)
    for user in users:
        print(f"{user.id:<5} {user.username:<20} {user.email:<30} {str(user.is_admin):<10} {str(user.is_premium):<10}")