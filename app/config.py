import os
import cloudinary

def load_api_key_from_files():
    """Tries to load the Google API key from common files."""
    key_files = ['google_cle.txt', 'cle_api.txt']
    for filename in key_files:
        try:
            filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', filename))
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    key = f.read().strip()
                    if key:
                        print(f"INFO: Clé API Google chargée depuis le fichier : {filename}")
                        return key
        except Exception as e:
            print(f"AVERTISSEMENT: Impossible de lire le fichier de clé API {filename}: {e}")
    return None

def load_getimg_api_key():
    """Charge la clé API getimg.ai depuis le fichier."""
    try:
        filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'getimg_key.txt'))
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                key = f.read().strip()
                if key:
                    print(f"INFO: Clé API getimg.ai chargée")
                    return key
    except Exception as e:
        print(f"AVERTISSEMENT: Impossible de lire la clé API getimg.ai: {e}")
    return None

def load_openrouter_api_key():
    """Charge la clé API OpenRouter depuis le fichier."""
    try:
        filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'openrouter_key.txt'))
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                key = f.read().strip()
                if key:
                    print(f"INFO: Clé API OpenRouter chargée")
                    return key
    except Exception as e:
        print(f"AVERTISSEMENT: Impossible de lire la clé API OpenRouter: {e}")
    return None


class Config:
    """Set Flask configuration from .env file."""

    # General Config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-123456789'
    FLASK_APP = os.environ.get('FLASK_APP')
    FLASK_ENV = os.environ.get('FLASK_ENV')
    
    # Session Config
    PERMANENT_SESSION_LIFETIME = 1800 # 30 minutes d'inactivité avant déconnexion

    # Database - Configuration PostgreSQL ou SQLite fallback
    db_url_env = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')
    
    if db_url_env:
        # Supprimer le paramètre 'supa' non standard s'il existe
        db_url = db_url_env.split('?')[0]
        SQLALCHEMY_DATABASE_URI = db_url.replace('postgres://', 'postgresql+psycopg2://')
        print(f"INFO: Base de données PostgreSQL externe configurée")
    elif os.environ.get('VERCEL'):
        # Sur Vercel sans BDD, utiliser SQLite temporaire
        db_path = '/tmp/jenny_memory.db'
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
        print(f"INFO: Base de données SQLite temporaire Vercel configurée")
    else:
        # En local, utiliser SQLite par défaut
        instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'instance')
        os.makedirs(instance_path, exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{instance_path}/jenny_memory.db'
        print(f"INFO: Base de données SQLite locale configurée")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration des uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
    IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload

    # Google Gemini API
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY') or load_api_key_from_files()
    GOOGLE_MODEL = "gemini-2.5-pro" # Configuration pour le Premium

    # getimg.ai API
    GETIMG_API_KEY = os.environ.get('GETIMG_API_KEY') or load_getimg_api_key()
    
    # OpenRouter API
    OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY') or load_openrouter_api_key()
    if OPENROUTER_API_KEY:
        print(f"INFO: Clé OpenRouter chargée: {OPENROUTER_API_KEY[:10]}...")
    else:
        print("AVERTISSEMENT: Aucune clé OpenRouter trouvée.")
    OPENROUTER_MODEL = "deepseek/deepseek-chat"

    # OpenAI API (Pour les utilisateurs Free)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = "gpt-3.5-turbo" # Ou gpt-4o-mini selon votre préférence

    # DeepSeek API (Direct)
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
    DEEPSEEK_MODEL = "deepseek-chat"

    # Configuration Cloudinary
    if 'CLOUDINARY_URL' in os.environ:
        cloudinary_url = os.environ.get('CLOUDINARY_URL', '').replace('<', '').replace('>', '')
        cloudinary.config(
            cloud_name=cloudinary_url.split('@')[-1],
            api_key=cloudinary_url.split('//')[1].split(':')[0],
            api_secret=cloudinary_url.split(':')[2].split('@')[0]
        )
        print("INFO: Cloudinary configuré.")