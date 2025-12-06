from flask import current_app, request, jsonify, Blueprint
from flask_login import login_required, current_user
import time
import random
import logging
from datetime import datetime
from .. import db, limiter
from ..models import User, Memory
from ..jenny import KAMASUTRA_POSITIONS
from ..services.gemini import call_gemini, generate_image_with_pollinations, call_gemini_memory_extractor

chat_bp = Blueprint('chat_bp', __name__)

def save_memory(user_id, conversation_history, response_from_gemini):
    if user_id and (current_user.is_premium or current_user.is_admin):
        try:
            extracted_points = call_gemini_memory_extractor(conversation_history, response_from_gemini)
            if extracted_points:
                for point_line in extracted_points.split('\n'):
                    if point_line.strip():
                        if point_line.startswith('- [') and ']' in point_line:
                            category_end_index = point_line.find(']')
                            category = point_line[3:category_end_index].strip().lower()
                            key_point_text = point_line[category_end_index + 1:].strip()
                        else:
                            category = "general"
                            key_point_text = point_line.strip()
                        
                        if key_point_text:
                            memory = Memory(user_id=user_id, key_point=key_point_text, category=category)
                            db.session.add(memory)
                db.session.commit()
                logging.info(f"Mémoires sauvegardées pour l'utilisateur {user_id}.")
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde de la mémoire pour l'utilisateur {user_id}: {e}")

def get_relevant_memories(user_id, current_message):
    if user_id and (current_user.is_premium or current_user.is_admin):
        prioritized_categories = ["histoire", "personnage"]
        
        prioritized_memories = Memory.query.filter_by(user_id=user_id)\
                                            .filter(Memory.category.in_(prioritized_categories))\
                                            .order_by(Memory.timestamp.desc())\
                                            .limit(3).all()
        
        general_memories = Memory.query.filter_by(user_id=user_id)\
                                        .filter(Memory.category.notin_(prioritized_categories))\
                                        .order_by(Memory.timestamp.desc())\
                                        .limit(max(0, 5 - len(prioritized_memories))).all()

        memories = prioritized_memories + general_memories
        
        if memories:
            memories_text = "\n".join([f"- [{m.category.capitalize()}] {m.key_point}" for m in memories])
            return f"\n\n[SOUVENIRS DE JENNY AVEC L'UTILISATEUR (par ordre de pertinence/priorité)]:\n{memories_text}\n"
    return ""

@chat_bp.route('/chat', methods=['POST'])
@login_required
@limiter.limit("20 per minute")
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
            
            memories_context = get_relevant_memories(user.id, message)
            prompt_context += memories_context
            
            if user.is_premium or user.is_admin:
                if any(w in message_lower for w in ["position", "kamasutra", "idée"]):
                    position = random.choice(KAMASUTRA_POSITIONS)
                    prompt_context += f"\n(Contexte: Propose d'analyser la position : {position['name']}. Description : {position['description']})"
            else:
                if user.interaction_step is None:
                    user.interaction_step = 0
                user.interaction_step += 1
                if user.interaction_step > 10: user.interaction_step = 10
                
                if any(w in message_lower for w in ["image", "photo", "montre", "nude", "voir", "position", "kamasutra"]):
                    prompt_context += "\n(Contexte: L'utilisateur demande du contenu Premium. REFUSE en jouant la frustration et incite-le à passer Premium pour te 'libérer'.)"

            history[-1]["content"] += prompt_context
            gemini_start = time.time()
            response_text = call_gemini(history, mood=user.mood, user=user)
            logging.info(f"Temps appel Gemini: {time.time() - gemini_start:.2f}s")

    if "[GENERATE_IMAGE:" in response_text:
        try:
            start_tag = response_text.find("[GENERATE_IMAGE:")
            end_tag = response_text.find("]", start_tag)
            if end_tag != -1:
                image_prompt = response_text[start_tag+16:end_tag].strip()
                response_text = response_text.replace(response_text[start_tag:end_tag+1], "").strip()

                image_url = generate_image_with_pollinations(image_prompt)
                if image_url:
                    response_text += f"\nVoici l'image que tu as demandée : {image_url}"
                else:
                    response_text += "\n(Désolée, je n'ai pas réussi à générer l'image...)"

        except Exception as e:
            print(f"Erreur génération image: {e}")
            response_text += "\n(Désolée, problème technique avec l'image...)"

    history.append({"role": "assistant", "content": response_text})
    
    save_memory(user.id, history, response_text)

    end_words = ["finissons", "terminons", "fin de l'histoire", "arrêtons", "stop", "fini", "c'est fini", "finissons là"]
    if any(word in message_lower for word in end_words):
        history = []
        logging.info("Fin de l'histoire détectée, historique vidé pour nouvelle session.")

    user.set_history(history)
    db.session.commit()

    return jsonify({'response': response_text, 'image_url': image_url})

@chat_bp.route('/api/image_generation_status/<generation_id>', methods=['GET'])
@login_required
def get_image_generation_status(generation_id):
    """Vérifie le statut d'une génération d'image."""
    return jsonify({
        'status': 'unknown',
        'image_url': None,
        'timestamp': time.time()
    })

def register_chat_routes(app):
    """Enregistre les routes de chat."""
    app.register_blueprint(chat_bp)
