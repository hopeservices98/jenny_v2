import sqlite3
from app import create_app, db

def migrate():
    app = create_app()
    with app.app_context():
        # Connexion directe à la base de données SQLite
        conn = sqlite3.connect('instance/jenny_memory.db')
        cursor = conn.cursor()
        
        try:
            # Ajouter la colonne is_premium
            print("Ajout de la colonne is_premium...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_premium BOOLEAN DEFAULT 0")
        except sqlite3.OperationalError as e:
            print(f"Erreur (probablement déjà existante) : {e}")

        try:
            # Ajouter la colonne interaction_step
            print("Ajout de la colonne interaction_step...")
            cursor.execute("ALTER TABLE users ADD COLUMN interaction_step INTEGER DEFAULT 0")
        except sqlite3.OperationalError as e:
            print(f"Erreur (probablement déjà existante) : {e}")

        conn.commit()
        conn.close()
        print("Migration terminée.")

if __name__ == '__main__':
    migrate()