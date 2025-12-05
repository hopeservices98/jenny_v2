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

        # Vérifier si la colonne existe déjà
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'is_active' not in columns:
            print("Ajout de la colonne is_active...")
            # On met is_active à 1 (True) par défaut pour les utilisateurs existants pour ne pas bloquer tout le monde
            cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1")
            conn.commit()
            print("Migration réussie : colonne is_active ajoutée.")
        else:
            print("La colonne is_active existe déjà.")

    except sqlite3.Error as e:
        print(f"Erreur SQLite: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate()