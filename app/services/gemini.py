from flask import current_app
from .. import db
from ..models import User
from ..jenny import JENNY_MOODS
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import time
import logging
import re

def _call_openrouter_internal(message_history, system_instruction):
    """Fonction interne pour appeler OpenRouter."""
    if not current_app.config.get('OPENROUTER_API_KEY'):
        return None
        
    try:
        import requests
        
        messages = [{"role": "system", "content": system_instruction}]
        # Limiter l'historique pour OpenRouter
        recent_history = message_history[-15:] if len(message_history) > 15 else message_history
        
        for item in recent_history:
            messages.append({"role": item["role"], "content": item["content"]})
        
        payload = {
            "model": current_app.config['OPENROUTER_MODEL'],
            "messages": messages,
            "temperature": 0.8,
            "max_tokens": 500,
        }
        
        headers = {
            "Authorization": f"Bearer {current_app.config['OPENROUTER_API_KEY']}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://jenny-ai.com",
            "X-Title": "Jenny AI"
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_message = result['choices'][0]['message']['content']
            clean_message = re.sub(r'\s{2,}', ' ', ai_message)
            clean_message = clean_message.replace(' , ', ' ')
            return clean_message.strip()
        else:
            logging.error(f"ERREUR OPENROUTER: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logging.error(f"EXCEPTION OPENROUTER: {e}")
        return None

def call_gemini_memory_extractor(conversation_history, new_response):
    """
    Appelle Gemini pour extraire les points clés d'une conversation.
    """
    genai.configure(api_key=current_app.config['GOOGLE_API_KEY'])
    
    extraction_prompt = """
    Tu es un extracteur de points clés de conversation pour Jenny. Ton rôle est d'analyser la conversation fournie (historique et dernière réponse) et d'en extraire les informations les plus importantes, intimes, ou récurrentes concernant l'utilisateur.

    Chaque point clé doit être une phrase concise et informative, suivie d'une catégorie pertinente (histoire, personnage, préférence, général, émotion, etc.).

    Format de sortie :
    - [Catégorie] Point clé 1.
    - [Catégorie] Point clé 2.
    - [Catégorie] Point clé 3.

    Exemple de sortie :
    - [Préférence] L'utilisateur aime les chats et a un chat nommé "Moustache".
    - [Histoire] L'utilisateur a mentionné un souvenir d'enfance lié à la plage.
    - [Général] L'utilisateur est intéressé par la psychologie.
    - [Émotion] L'utilisateur se sent seul.

    CONVERSATION :
    {conversation}

    DERNIÈRE RÉPONSE DE JENNY :
    {response}

    POINTS CLÉS EXTRAITS :
    """
    
    formatted_conversation = "\n".join([f"{item['role']}: {item['content']}" for item in conversation_history])
    
    final_prompt = extraction_prompt.format(conversation=formatted_conversation, response=new_response)
    
    # Réglages de sécurité permissifs pour l'extraction (car le contenu peut être NSFW)
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }

    model = genai.GenerativeModel(
        model_name="gemini-2.5-pro",
        safety_settings=safety_settings
    )
    
    try:
        response = model.generate_content(final_prompt)
        # Vérification robuste de la réponse
        if response and hasattr(response, 'parts') and response.parts:
            return response.text
        elif response and hasattr(response, 'prompt_feedback'):
             logging.warning(f"Extraction mémoire bloquée. Feedback: {response.prompt_feedback}")
             return None
        else:
            logging.warning("Gemini n'a pas pu extraire de points clés (réponse vide).")
            return None
    except Exception as e:
        logging.error(f"Erreur lors de l'extraction de mémoire par Gemini: {e}")
        return None
def update_story_context(current_context, conversation_history, last_response):
    """
    Met à jour le contexte narratif global (Mémoire Longue).
    """
    genai.configure(api_key=current_app.config['GOOGLE_API_KEY'])
    
    update_prompt = """
    Tu es le Gardien de la Mémoire de l'histoire. Ton rôle est de mettre à jour le "Story Context" (le résumé narratif permanent) en fonction des derniers échanges.

    CONTEXTE ACTUEL :
    {current_context}

    DERNIERS ÉCHANGES :
    {conversation}
    Jenny: {response}

    TA MISSION :
    Mets à jour le contexte actuel pour refléter l'évolution de l'histoire.
    - Garde les faits fondamentaux (noms, lieux, relations clés).
    - Mets à jour l'état émotionnel et la situation actuelle.
    - Ajoute les nouveaux événements importants.
    - Supprime les détails triviaux ou obsolètes pour garder un résumé concis mais complet.
    - Le texte doit être à la troisième personne, décrivant l'état de la relation entre Jenny et l'utilisateur.

    NOUVEAU CONTEXTE (Texte brut uniquement) :
    """
    
    # On prend les 3 derniers échanges pour le contexte immédiat
    recent_history = conversation_history[-3:]
    formatted_conversation = "\n".join([f"{item['role']}: {item['content']}" for item in recent_history])
    
    final_prompt = update_prompt.format(
        current_context=current_context or "Début de l'histoire.",
        conversation=formatted_conversation,
        response=last_response
    )
    
    # Réglages de sécurité permissifs pour la mise à jour du contexte
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }

    model = genai.GenerativeModel(
        model_name="gemini-2.5-pro",
        safety_settings=safety_settings
    )
    
    try:
        response = model.generate_content(final_prompt)
        if response.parts:
            return response.text.strip()
        return current_context
    except Exception as e:
        logging.error(f"Erreur mise à jour StoryContext: {e}")
        return current_context

def call_gemini(message_history, mood='neutre', system_prompt_override=None, user=None):
    """
    Appelle l'API Gemini avec Jenny comme IA.
    Retourne la réponse brute pour traitement par le frontend.
    """
    # 3. Préparation du Prompt
    from ..jenny import JENNY_SYSTEM_PROMPT
    base_prompt = system_prompt_override or JENNY_SYSTEM_PROMPT
    mood_instruction = JENNY_MOODS.get(mood, JENNY_MOODS['neutre'])
    
    # Injection du contexte utilisateur
    user_context = ""
    if user:
        status = "PREMIUM" if user.is_premium or user.is_admin else "FREE"
        user_context = f"\n\n[CONTEXTE UTILISATEUR]\nStatut: {status}\nNom: {user.first_name or user.username}"
        
        # Injection de la Mémoire Longue (StoryContext) pour les Premium
        if (user.is_premium or user.is_admin) and hasattr(user, 'story_context') and user.story_context:
            user_context += f"\n\n[MÉMOIRE LONGUE / CONTEXTE NARRATIF]\n{user.story_context.content}\n"
            
        if not user.is_premium:
            user_context += f"\nPhase de séduction actuelle: {user.interaction_step}/10 (Plus le chiffre est haut, plus tu dois teaser/frustrer)"

    full_system_instruction = f"{base_prompt}{user_context}\n\nAgis le personnage à la perfection. Humeur actuelle : {mood_instruction}"

    # --- OPENROUTER (POUR UTILISATEURS FREE) ---
    # Si l'utilisateur n'est pas premium et n'est pas admin, on utilise OpenRouter directement
    if user and not user.is_premium and not user.is_admin:
        response = _call_openrouter_internal(message_history, full_system_instruction)
        if response:
            return response
        # Si OpenRouter échoue (quota, erreur), on tente Gemini en fallback (si configuré pour Free) ou on retourne une erreur
        # Ici, on continue vers Gemini comme fallback ultime si OpenRouter plante
    
    # --- GOOGLE GEMINI (POUR PREMIUM & ADMIN, OU FALLBACK) ---

    # 1. Config
    genai.configure(api_key=current_app.config['GOOGLE_API_KEY'])

    # 2. Les Réglages de Sécurité (CRUCIAL POUR JENNY)
    # Note: Pour éviter les blocages Google, on utilise des seuils permissifs mais on garde une sécurité minimale
    # pour ne pas être flaggé comme application malveillante.
    # Pour les utilisateurs Premium, on désactive tous les filtres pour permettre le RP libre
    # Google peut toujours bloquer les contenus illégaux (CSAM, violence extrême), mais cela devrait laisser passer le RP érotique/NSFW.
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }

    # 4. Le Modèle
    model = genai.GenerativeModel(
        model_name=current_app.config['GOOGLE_MODEL'],
        system_instruction=full_system_instruction,
        safety_settings=safety_settings
    )

    # 5. Gestion de l'historique (Format correct, complet pour mémoire)
    gemini_history = []
    # On prend tout l'historique sauf le dernier message pour garder la mémoire complète
    for item in message_history[:-1]:
        role = "model" if item["role"] == "assistant" else "user"
        gemini_history.append({"role": role, "parts": [item["content"]]})

    last_user_message = message_history[-1]["content"]

    try:
        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(last_user_message)

        # --- VERIFICATION ANTI-PLANTAGE ---
        if response.parts:
            ai_message = response.text
            clean_message = re.sub(r'\s{2,}', ' ', ai_message)
            clean_message = clean_message.replace(' , ', ' ')
            return clean_message.strip()
        else:
            # Si Google bloque, on bascule sur OpenRouter (Fallback)
            logging.warning(f"Gemini bloqué. Raison: {response.candidates[0].finish_reason if response.candidates else 'Inconnue'}")
            logging.info("Basculement vers OpenRouter (Fallback)...")
            fallback_response = _call_openrouter_internal(message_history, full_system_instruction)
            if fallback_response:
                return fallback_response
            return "(Jenny rougit et détourne le regard) Je... je ne peux pas dire ça ici."

    except Exception as e:
        logging.error(f"ERREUR API GEMINI: {e}")
        # Fallback vers OpenRouter en cas d'exception
        logging.info("Basculement vers OpenRouter (Fallback Exception)...")
        fallback_response = _call_openrouter_internal(message_history, full_system_instruction)
        if fallback_response:
            return fallback_response
        return "Désolée, un problème technique m'empêche de répondre."

def generate_image_with_pollinations(image_description):
    """
    Génère une image avec Pollinations.ai (service gratuit, sans censure).
    API: https://github.com/pollinations/pollinations
    """
    try:
        import urllib.parse
        import requests
        import os
        import uuid
        import random
        
        # Prompt NSFW optimisé pour contenu érotique
        nsfw_keywords = "nsfw, nude, naked, erotic, sensual, seductive, uncensored, adult content"
        prompt = f"{image_description[:200]}, {nsfw_keywords}, high quality, detailed, professional photography"
        print(f"[POLLINATIONS] Prompt NSFW: {prompt[:80]}...")
        
        encoded_prompt = urllib.parse.quote(prompt)
        seed = random.randint(1, 999999)
        
        # URL avec paramètres optimisés pour NSFW
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=768&seed={seed}&nologo=true"
        print(f"[POLLINATIONS] Téléchargement...")
        
        # Timeout de 90 secondes pour la génération
        response = requests.get(image_url, timeout=90)
        
        print(f"[POLLINATIONS] Status: {response.status_code}, Size: {len(response.content)} bytes")
        
        if response.status_code == 200 and len(response.content) > 5000:
            generated_dir = os.path.join(current_app.root_path, '..', 'images', 'generated')
            print(f"[POLLINATIONS] Dossier: {generated_dir}")
            os.makedirs(generated_dir, exist_ok=True)
            filename = f"gen_{uuid.uuid4()}.jpg"
            filepath = os.path.join(generated_dir, filename)

            with open(filepath, 'wb') as f:
                f.write(response.content)

            # Vérifier que le fichier existe
            if os.path.exists(filepath):
                print(f"[POLLINATIONS] Sauvegardé: {filepath}")
                return f"/images/generated/{filename}"
            else:
                print(f"[POLLINATIONS] ERREUR: Fichier non créé")
                return None
        else:
            print(f"[POLLINATIONS] Échec: taille insuffisante ou erreur HTTP")
            return None

    except Exception as e:
        print(f"[POLLINATIONS] Erreur: {e}")
        import traceback
        traceback.print_exc()
        return None

def enhance_nsfw_prompt(base_prompt):
    """
    Enrichit automatiquement un prompt d'image pour du contenu NSFW érotique/sensuel/hentai.
    Ajoute des mots-clés optimisés pour Pollinations.ai.
    """
    # Convertir en minuscules pour la détection
    prompt_lower = base_prompt.lower()

    # Détection du style demandé
    style_keywords = []
    if "hentai" in prompt_lower or "anime" in prompt_lower:
        style_keywords = ["hentai style", "anime", "detailed anatomy", "exaggerated features"]
    elif "réaliste" in prompt_lower or "realistic" in prompt_lower or "hyperrealistic" in prompt_lower:
        style_keywords = ["hyperrealistic", "photorealistic", "8k resolution"]
    else:
        # Style par défaut : mélange sensuel
        style_keywords = ["sensual", "erotic", "highly detailed"]

    # Mots-clés NSFW essentiels
    nsfw_keywords = [
        "nsfw", "uncensored", "adult content", "erotic art",
        "seductive", "intimate", "provocative", "sensual lighting"
    ]

    # Améliorations de qualité
    quality_keywords = [
        "high resolution", "intricate details", "professional photography",
        "moody lighting", "dramatic shadows", "vibrant colors"
    ]

    # Construction du prompt enrichi
    enhanced_parts = [base_prompt]

    # Ajouter les styles détectés
    enhanced_parts.extend(style_keywords)

    # Ajouter toujours les mots-clés NSFW
    enhanced_parts.extend(nsfw_keywords)

    # Ajouter les améliorations de qualité
    enhanced_parts.extend(quality_keywords)

    # Assembler le prompt final
    final_prompt = ", ".join(enhanced_parts)

    # Limiter la longueur si nécessaire (Pollinations.ai a des limites)
    if len(final_prompt) > 1000:
        # Garder le prompt original + mots-clés essentiels
        final_prompt = base_prompt + ", " + ", ".join(style_keywords + nsfw_keywords[:3] + quality_keywords[:2])

    return final_prompt
