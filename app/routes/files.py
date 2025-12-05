from flask import current_app, request, jsonify, send_from_directory
from flask_login import login_required, current_user
import os
import uuid
import time
import random
import logging
from .. import db

def register_files_routes(app):
    """Enregistre les routes de gestion des fichiers."""
    
    @app.route('/images/<path:filename>')
    def serve_image(filename):
        return send_from_directory(current_app.config['IMAGE_DIR'], filename)

    @app.route('/images/generated/<path:filename>')
    def serve_generated_image(filename):
        generated_dir = os.path.join(current_app.root_path, '..', 'images', 'generated')
        return send_from_directory(generated_dir, filename)

    @app.route('/profile_image')
    @login_required
    def get_profile_image():
        try:
            available_images = [f for f in os.listdir(current_app.config['IMAGE_DIR']) if os.path.isfile(os.path.join(current_app.config['IMAGE_DIR'], f))]
            if available_images:
                chosen_image = random.choice(available_images)
                return jsonify({'url': f"/images/{chosen_image}"})
            else:
                return jsonify({'url': None})
        except FileNotFoundError:
            return jsonify({'url': None})

    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        upload_dir = os.path.join(current_app.root_path, '..', 'uploads')
        return send_from_directory(upload_dir, filename)

    @app.route('/vid/<path:filename>')
    def serve_video(filename):
        video_dir = os.path.join(current_app.root_path, '..', 'vid')
        return send_from_directory(video_dir, filename)

    @app.route('/upload', methods=['POST'])
    @login_required
    def upload_file():
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nom de fichier vide'}), 400
        file_type = request.form.get('type')
        if file_type not in ['image', 'audio', 'avatar']:
            return jsonify({'error': 'Type de fichier invalide'}), 400

        # Vérification de l'extension
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.mp3', '.wav', '.ogg'}
        ext = os.path.splitext(file.filename)[1].lower()
        
        if ext not in allowed_extensions:
            return jsonify({'error': 'Type de fichier non autorisé'}), 400
        
        # Vérification du contenu réel (MIME type) pour plus de sécurité
        if file_type in ['image', 'avatar'] and not file.content_type.startswith('image/'):
             return jsonify({'error': 'Le fichier n\'est pas une image valide'}), 400
        if file_type == 'audio' and not file.content_type.startswith('audio/'):
             return jsonify({'error': 'Le fichier n\'est pas un audio valide'}), 400

        # Créer le dossier uploads s'il n'existe pas
        upload_dir = os.path.join(current_app.root_path, '..', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        # Générer un nom unique
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)

        url = f"/uploads/{unique_filename}"

        if file_type == 'avatar':
            current_user.avatar_url = url
            db.session.commit()

        return jsonify({'url': url})
