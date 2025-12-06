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

        # Uploader vers Cloudinary
        import cloudinary.uploader
        try:
            upload_result = cloudinary.uploader.upload(file)
            url = upload_result.get('secure_url')
            if not url:
                return jsonify({'error': 'Erreur lors de l\'upload vers Cloudinary'}), 500
        except Exception as e:
            logging.error(f"Erreur d'upload Cloudinary: {e}")
            return jsonify({'error': 'Erreur serveur lors de l\'upload'}), 500

        if file_type == 'avatar':
            current_user.avatar_url = url
            db.session.commit()

        return jsonify({'url': url})
