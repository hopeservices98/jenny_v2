import sqlite3
import os

# Chemin vers la base de données
db_path = os.path.join('instance', 'jenny_memory.db')

def migrate():
    if not os.path.exists(db_path):
        print(f"Erreur: La base de données n'existe pas à {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Vérifier si les colonnes existent déjà
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'email_verified' not in columns:
            print("Ajout de la colonne email_verified...")
            cursor.execute("ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT 0")
            
        if 'validation_code' not in columns:
            print("Ajout de la colonne validation_code...")
            cursor.execute("ALTER TABLE users ADD COLUMN validation_code VARCHAR(6)")
            
        conn.commit()
        print("Migration réussie.")

    except sqlite3.Error as e:
        print(f"Erreur SQLite: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate()