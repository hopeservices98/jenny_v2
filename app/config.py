import os

def load_api_key_from_files():
    """Tries to load the Google API key from common files."""
    # List of potential files, in order of priority
    key_files = ['google_cle.txt', 'cle_api.txt']
    for filename in key_files:
        try:
            # Construct the full path relative to the app's root
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

    # Database - Configuration Vercel compatible
    if os.environ.get('VERCEL'):
        # Sur Vercel, utiliser le répertoire /tmp accessible en écriture
        db_path = '/tmp/jenny_memory.db'
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    else:
        # En local, utiliser instance/
        instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'instance')
        os.makedirs(instance_path, exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{instance_path}/jenny_memory.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration des uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
    IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload


    # Google Gemini API (backup)
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY') or load_api_key_from_files()
    GOOGLE_MODEL = "gemini-1.5-pro-latest"

    # getimg.ai API
    GETIMG_API_KEY = os.environ.get('GETIMG_API_KEY') or load_getimg_api_key()
    
    # OpenRouter API (remplace Gemini)
    OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY') or load_openrouter_api_key()
    OPENROUTER_MODEL = "meta-llama/llama-3.3-70b-instruct"  # Modèle sans censure

    # Local LLM (LM Studio)
    USE_LOCAL_LLM = False
    LOCAL_LLM_API_BASE = "http://192.168.0.106:1234/v1"
    LOCAL_LLM_MODEL = "uncensored-phi-3-mini-4k-geminified"

    # Image Directory
    IMAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images'))