from flask import current_app
from .. import db
from ..models import User
from ..jenny import JENNY_MOODS
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import time
import logging
from bs4 import BeautifulSoup
import re

def clean_html_response(ai_message):
    """
    Supprime toutes les balises HTML de la réponse de l'IA.
    """
    if not ai_message:
        return ""
        
    # Utilise BeautifulSoup pour analyser le HTML
    soup = BeautifulSoup(ai_message, 'html.parser')
    
    # 1. get_text() extrait tout le texte et supprime toutes les balises.
    #    separator=' ' garantit qu'il y a un espace entre les mots précédemment séparés par des balises.
    clean_text = soup.get_text(separator=' ', strip=True)
    
    # 2. Nettoyage supplémentaire des espaces multiples ou des symboles indésirables
    #    (comme les virgules seules si le modèle en ajoute).
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    return clean_text

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
    
    model = genai.GenerativeModel(model_name="gemini-2.5-flash") # Utiliser un modèle plus léger pour l'extraction
    
    try:
        response = model.generate_content(final_prompt)
        if response.parts:
            return response.text
        else:
            logging.warning("Gemini n'a pas pu extraire de points clés.")
            return None
    except Exception as e:
        logging.error(f"Erreur lors de l'extraction de mémoire par Gemini: {e}")
        return None
def call_gemini(message_history, mood='neutre', system_prompt_override=None, user=None):
    """
    Appelle l'API Gemini avec Jenny comme IA.
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
        if not user.is_premium:
            user_context += f"\nPhase de séduction actuelle: {user.interaction_step}/10 (Plus le chiffre est haut, plus tu dois teaser/frustrer)"

    full_system_instruction = f"{base_prompt}{user_context}\n\nAgis le personnage à la perfection. Humeur actuelle : {mood_instruction}"

    # --- OPENROUTER (POUR UTILISATEURS FREE) ---
    # Si l'utilisateur n'est pas premium et n'est pas admin, on utilise OpenRouter (modèle gratuit/moins cher)
    if user and not user.is_premium and not user.is_admin and current_app.config.get('OPENROUTER_API_KEY'):
        try:
            import requests
            
            # Construction de l'historique pour OpenAI-compatible API (OpenRouter)
            messages = [{"role": "system", "content": full_system_instruction}]
            
            # Limiter l'historique pour économiser des tokens
            recent_history = message_history[-10:] if len(message_history) > 10 else message_history
            
            for item in recent_history:
                messages.append({"role": item["role"], "content": item["content"]})
            
            payload = {
                "model": current_app.config['OPENROUTER_MODEL'],
                "messages": messages,
                "temperature": 0.8,
                "max_tokens": 300,
            }
            
            headers = {
                "Authorization": f"Bearer {current_app.config['OPENROUTER_API_KEY']}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://jenny-ai.com", # Requis par OpenRouter
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
                return clean_html_response(result['choices'][0]['message']['content'])
            elif response.status_code == 402 or response.status_code == 429: # Payment Required or Too Many Requests
                print(f"QUOTA OPENROUTER ATTEINT: {response.status_code}")
                # On laisse le modèle gérer la réponse en se basant sur le prompt système
                pass
            else:
                print(f"ERREUR OPENROUTER: {response.status_code} - {response.text}")
                return "Désolée, une erreur technique m'empêche de répondre pour le moment."
                
        except Exception as e:
            print(f"ERREUR OPENROUTER: {e}")
            return "Désolée, une erreur de connexion m'empêche de répondre."

    # --- GOOGLE GEMINI (POUR PREMIUM & ADMIN) ---
    # Si on arrive ici et qu'on est un utilisateur FREE, c'est qu'on ne doit PAS utiliser Gemini
    if user and not (user.is_premium or user.is_admin):
         # On laisse le modèle gérer la réponse en se basant sur le prompt système
         pass

    # 1. Config
    genai.configure(api_key=current_app.config['GOOGLE_API_KEY'])

    # 2. Les Réglages de Sécurité (CRUCIAL POUR JENNY)
    # Note: Pour éviter les blocages Google, on utilise des seuils permissifs mais on garde une sécurité minimale
    # pour ne pas être flaggé comme application malveillante.
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE, # On garde NONE ici pour le RP
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
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
        # Au lieu de planter si Google bloque, on vérifie s'il y a du texte
        if response.parts:
            return clean_html_response(response.text)
        else:
            # Si Google a bloqué quand même (Finish Reason)
            print(f"DEBUG: Réponse bloquée. Finish Reason: {response.candidates[0].finish_reason}")
            return "(Jenny rougit et détourne le regard) Je... je ne peux pas dire ça ici."

    except Exception as e:
        print(f"ERREUR API: {e}")
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
