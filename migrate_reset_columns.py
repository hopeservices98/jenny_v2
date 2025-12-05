import sqlite3

def migrate_reset_columns():
    """Ajoute les colonnes reset_token et reset_token_expires à la table users"""
    
    # Connexion directe à la base de données SQLite
    conn = sqlite3.connect('instance/jenny_memory.db')
    cursor = conn.cursor()
    
    try:
        # Ajouter la colonne reset_token
        print("Ajout de la colonne reset_token...")
        cursor.execute("ALTER TABLE users ADD COLUMN reset_token TEXT")
    except sqlite3.OperationalError as e:
        print(f"Erreur reset_token (probablement déjà existante) : {e}")

    try:
        # Ajouter la colonne reset_token_expires
        print("Ajout de la colonne reset_token_expires...")
        cursor.execute("ALTER TABLE users ADD COLUMN reset_token_expires DATETIME")
    except sqlite3.OperationalError as e:
        print(f"Erreur reset_token_expires (probablement déjà existante) : {e}")

    conn.commit()
    conn.close()
    print("Migration des colonnes reset terminée.")

if __name__ == '__main__':
    migrate_reset_columns()