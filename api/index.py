# api/index.py
from app import create_app

# Vercel a absolument besoin d'une variable nommée 'app'
app = create_app()