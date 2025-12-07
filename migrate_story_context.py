from app import create_app, db
from app.models import StoryContext

app = create_app()

with app.app_context():
    try:
        db.create_all()
        print("Table StoryContext créée (si elle n'existait pas).")
    except Exception as e:
        print(f"Erreur lors de la migration : {e}")