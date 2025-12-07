import os
from app import create_app, db
from sqlalchemy import text

def migrate_remote():
    """
    Tente de créer les tables manquantes sur la base de données configurée.
    Fonctionne pour SQLite et PostgreSQL via SQLAlchemy.
    """
    app = create_app()
    
    print(f"Migration sur la base de données : {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    with app.app_context():
        try:
            # Crée toutes les tables définies dans les modèles qui n'existent pas encore
            db.create_all()
            print("✅ db.create_all() exécuté avec succès.")
            print("Les nouvelles tables (comme StoryContext) ont été créées si elles n'existaient pas.")
            
        except Exception as e:
            print(f"❌ Erreur lors de la migration : {e}")

if __name__ == '__main__':
    migrate_remote()