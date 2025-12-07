from . import db
import json
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime # Importation nécessaire pour le timestamp de Memory

class User(db.Model, UserMixin):
    """Model for user accounts."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    address = db.Column(db.String(200))
    birth_date = db.Column(db.Date)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    history = db.Column(db.Text, nullable=False, default='[]')
    consent_intime = db.Column(db.Boolean, nullable=False, default=False)
    proposal_pending = db.Column(db.Boolean, nullable=False, default=False)
    mood = db.Column(db.String(50), nullable=False, default='neutre')
    avatar_url = db.Column(db.String(255))
    is_premium = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=False) # Validation admin requise
    email_verified = db.Column(db.Boolean, default=False) # Validation email requise
    validation_code = db.Column(db.String(6)) # Code de validation email
    interaction_step = db.Column(db.Integer, default=0) # 0: Découverte, 1: Confiance, 2: Dépendance/Teasing
    reset_token = db.Column(db.String(32), nullable=True) # Token de réinitialisation
    reset_token_expires = db.Column(db.DateTime, nullable=True) # Expiration du token

    def get_id(self):
        return str(self.id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_history(self):
        return json.loads(self.history or '[]')

    def set_history(self, history_list):
        self.history = json.dumps(history_list)

    def __repr__(self):
        return f'<User {self.username}>'

class Memory(db.Model):
    """Model for storing key memories/discussion points for users."""
    __tablename__ = 'memories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    key_point = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), default="general") # e.g., "story", "preference", "event"
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relation avec l'utilisateur
    user = db.relationship('User', backref=db.backref('memories', lazy=True))

    def __repr__(self):
        return f'<Memory {self.id} for User {self.user_id}: {self.key_point[:50]}>'

class StoryContext(db.Model):
    """Model for storing the long-term narrative context (Mémoire Longue)."""
    __tablename__ = 'story_contexts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    content = db.Column(db.Text, nullable=False, default="") # Le résumé narratif permanent
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    # Relation avec l'utilisateur (One-to-One)
    user = db.relationship('User', backref=db.backref('story_context', uselist=False, lazy=True))

    def __repr__(self):
        return f'<StoryContext User {self.user_id}>'