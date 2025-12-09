from flask import current_app
from .. import db
from ..models import User
from ..jenny import JENNY_MOODS
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import time
import logging
import re

def _call_openai_generic(messages, temperature=0.7, max_tokens=500):
    """Appelle l'API OpenAI (pour les utilisateurs Free)."""
    api_key = current_app.config.get('OPENAI_API_KEY')
    if not api_key:
        logging.error("Clé API OpenAI manquante.")
        return None
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model=current_app.config.get('OPENAI_MODEL', 'gpt-3.5-turbo'),
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"ERREUR OPENAI: {e}")
        return None

def _call_google_gemini(message_history, system_instruction):
    """Appelle l'API Google Gemini (pour les utilisateurs Premium)."""
    api_key = current_app.config.get('GOOGLE_API_KEY')
    if not api_key:
        logging.error("Clé API Google Gemini manquante.")
        return None
        
    try:
        genai.configure(api_key=api_key)
        
        # Configuration du modèle
        generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }
        
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            },
        ]
        
        model_name = current_app.config.get('GOOGLE_MODEL', 'gemini-1.5-pro')
        model = genai.GenerativeModel(model_name=model_name,
                                      generation_config=generation_config,
                                      safety_settings=safety_settings,
                                      system_instruction=system_instruction)
                                      
        # Conversion de l'historique pour Gemini
        gemini_history = []
        # On exclut le dernier message car send_message le prend en argument
        history_to_convert = message_history[:-1]
        last_user_message = message_history[-1]['content']
        
        for msg in history_to_convert:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})
            
        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(last_user_message)
        
        if response.text:
            logging.info(f"Réponse Gemini reçue (début): {response.text[:100]}...")
            return response.text
        else:
            logging.warning("Réponse Gemini vide ou nulle.")
            if response.candidates:
                for candidate in response.candidates:
                    if candidate.finish_reason:
                        logging.warning(f"Gemini finish reason: {candidate.finish_reason}")
                    if candidate.safety_ratings:
                        logging.warning(f"Gemini safety ratings: {candidate.safety_ratings}")
            logging.error("Gemini a renvoyé une réponse vide ou nulle, ou a été bloqué.")
            return None
        
    except genai.types.BlockedPromptException as e:
        logging.error(f"ERREUR GEMINI (Prompt bloqué): {e}")
        return None
    except genai.types.StopCandidateException as e:
        logging.error(f"ERREUR GEMINI (Candidat arrêté): {e}")
        return None
    except Exception as e:
        logging.error(f"ERREUR GEMINI (Générique): {e}", exc_info=True)
        return None

def _call_openrouter_generic(messages, temperature=0.8, max_tokens=500, model_override=None):
    """Fonction générique pour appeler l'API OpenRouter."""
    api_key = current_app.config.get('OPENROUTER_API_KEY')
    if not api_key:
        logging.error("Clé API OpenRouter manquante.")
        return None
        
    try:
        import requests
        
        payload = {
            "model": model_override or current_app.config.get('OPENROUTER_MODEL', 'google/gemini-2.5-flash'),
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
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
            if 'choices' in result and len(result['choices']) > 0:
                ai_message = result['choices'][0]['message']['content']
                return ai_message.strip()
            else:
                logging.error(f"Réponse OpenRouter vide ou malformée: {result}")
                return None
        else:
            logging.error(f"ERREUR OPENROUTER: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logging.error(f"EXCEPTION OPENROUTER: {e}")
        return None

def call_gemini_memory_extractor(conversation_history, new_response):
    """
    Appelle OpenRouter pour extraire les points clés d'une conversation.
    """
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
    
    messages = [{"role": "user", "content": final_prompt}]
    
    return _call_openrouter_generic(messages, temperature=0.3, max_tokens=500, model_override="openrouter/auto")

def update_story_context(current_context, conversation_history, last_response):
    """
    Met à jour le contexte narratif global (Mémoire Longue) via OpenRouter.
    """
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
    
    messages = [{"role": "user", "content": final_prompt}]
    
    response = _call_openrouter_generic(messages, temperature=0.3, max_tokens=1000, model_override="openrouter/auto")
    return response if response else current_context

def call_gemini(message_history, mood='neutre', system_prompt_override=None, user=None):
    """
    Appelle l'API DeepSeek avec Jenny comme IA.
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
        user_context = f"\\n\\n[CONTEXTE UTILISATEUR]\\nStatut: {status}\\nNom: {user.first_name or user.username}"
        
        # Injection de la Mémoire Longue (StoryContext) pour les Premium
        if (user.is_premium or user.is_admin) and hasattr(user, 'story_context') and user.story_context:
            user_context += f"\\n\\n[MÉMOIRE LONGUE / CONTEXTE NARRATIF]\\n{user.story_context.content}\\n"
            
        if not user.is_premium:
            user_context += f"\\nPhase de séduction actuelle: {user.interaction_step}/10 (Plus le chiffre est haut, plus tu dois teaser/frustrer)"

    full_system_instruction = f"{base_prompt}{user_context}\\n\\nAgis le personnage à la perfection. Humeur actuelle : {mood_instruction}"

    # --- STRATÉGIE HYBRIDE (PREMIUM vs FREE) ---
    
    response = None
    
    # 1. PREMIUM / ADMIN -> Google Gemini Pro
    if user and (user.is_premium or user.is_admin):
        logging.info(f"Utilisateur Premium {user.id}: Appel Gemini Pro")
        response = _call_google_gemini(message_history, full_system_instruction)
        
    # 2. FREE -> OpenAI (ou OpenRouter si pas de clé OpenAI)
    else:
        logging.info(f"Utilisateur Free {user.id if user else 'Anonyme'}: Appel IA Free")
        
        # Si clé OpenAI présente -> OpenAI
        if current_app.config.get('OPENAI_API_KEY'):
            logging.info("Utilisation OpenAI Direct")
            messages = [{"role": "system", "content": full_system_instruction}]
            recent_history = message_history[-20:] if len(message_history) > 20 else message_history
            for item in recent_history:
                messages.append({"role": item["role"], "content": item["content"]})
            response = _call_openai_generic(messages)
            
        # Sinon -> OpenRouter (Fallback Free)
        else:
            logging.info("Pas de clé OpenAI -> Utilisation OpenRouter")
            # On réutilise la fonction interne existante pour OpenRouter
            # Note: _call_openrouter_internal utilise en fait _call_deepseek_generic mais avec la config OpenRouter si adaptée
            # Mais attendez, _call_openrouter_internal appelle _call_deepseek_generic qui utilise DEEPSEEK_API_KEY
            # Il faut s'assurer qu'on utilise bien OPENROUTER_API_KEY
            
            # On va créer un appel spécifique OpenRouter ici pour être sûr
            api_key = current_app.config.get('OPENROUTER_API_KEY')
            if api_key:
                try:
                    import requests
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://jenny-ai.com",
                        "X-Title": "Jenny AI"
                    }
                    payload = {
                        "model": current_app.config.get('OPENROUTER_MODEL', 'deepseek/deepseek-chat'),
                        "messages": [{"role": "system", "content": full_system_instruction}] + message_history[-20:],
                        "temperature": 0.8,
                        "max_tokens": 500
                    }
                    r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=60)
                    if r.status_code == 200:
                        response = r.json()['choices'][0]['message']['content']
                    else:
                        logging.error(f"Erreur OpenRouter: {r.text}")
                except Exception as e:
                    logging.error(f"Exception OpenRouter: {e}")
            else:
                logging.error("Aucune clé API disponible pour le mode Free (ni OpenAI, ni OpenRouter)")

    if response:
        # Nettoyage agressif des balises HTML cassées
        clean_message = re.sub(r'<[^>]+>', '', response) # Supprime toutes les balises <...>
        clean_message = re.sub(r'\s{2,}', ' ', clean_message)
        clean_message = clean_message.replace(' , ', ' ')
        return clean_message.strip()
    
    # 3. FALLBACK -> OpenRouter (si le modèle principal a échoué)
    logging.warning("Échec du modèle principal, tentative de fallback OpenRouter...")
    messages_fallback = [{"role": "system", "content": full_system_instruction}]
    for item in message_history[-10:]: # Utiliser un historique plus court pour le fallback
        messages_fallback.append({"role": item["role"], "content": item["content"]})
    
    fallback_response = _call_openrouter_generic(messages_fallback)
    if fallback_response:
        return fallback_response.strip()

    return "Désolée, je suis momentanément indisponible (Erreur IA)."

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
