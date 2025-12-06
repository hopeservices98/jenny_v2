// UI utilities for chat
const API_BASE = 'http://127.0.0.1:5000';

export function createTypingIndicator() {
    const messageWrapper = document.createElement('div');
    messageWrapper.classList.add('flex', 'mb-4', 'justify-start');

    const typingBubble = document.createElement('div');
    typingBubble.classList.add('bg-gray-700', 'rounded-2xl', 'p-4', 'max-w-xs', 'lg:max-w-md');

    const typingElement = document.createElement('div');
    typingElement.classList.add('flex', 'space-x-1');
    typingElement.innerHTML = `
        <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
        <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s;"></div>
        <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s;"></div>
    `;
    typingBubble.appendChild(typingElement);
    messageWrapper.appendChild(typingBubble);
    
    return messageWrapper;
}

export function createSexyImageLoader() {
    const loaderContainer = document.createElement('div');
    loaderContainer.classList.add('image-loader-sexy', 'mt-3', 'p-4', 'rounded-xl', 'bg-gradient-to-r', 'from-pink-900/30', 'to-purple-900/30', 'border', 'border-pink-500/30');
    
    loaderContainer.innerHTML = `
        <div class="flex items-center space-x-3">
            <div class="relative">
                <div class="w-12 h-12 rounded-full border-2 border-pink-500/50 border-t-pink-500 animate-spin"></div>
                <div class="absolute inset-0 flex items-center justify-center">
                    <span class="text-lg">💋</span>
                </div>
            </div>
            <div class="flex-1">
                <p class="text-pink-300 text-sm font-medium sexy-loading-text">Je me prépare pour toi...</p>
                <div class="mt-2 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                    <div class="h-full bg-gradient-to-r from-pink-500 to-purple-500 rounded-full animate-pulse" style="width: 30%; animation: loadingProgress 2s ease-in-out infinite;"></div>
                </div>
            </div>
        </div>
        <style>
            @keyframes loadingProgress {
                0% { width: 10%; }
                50% { width: 70%; }
                100% { width: 10%; }
            }
        </style>
    `;
    
    // Messages sexy qui changent
    const sexyMessages = [
        "Je me prépare pour toi... 💋",
        "Patience, ça vaut le coup d'attendre... 🔥",
        "Je me fais belle... ✨",
        "Presque prête... 😘",
        "Un instant, je me déshabille... 💕",
        "Je veux que ce soit parfait pour toi... 💖"
    ];
    
    let messageIndex = 0;
    const textElement = loaderContainer.querySelector('.sexy-loading-text');
    
    const messageInterval = setInterval(() => {
        messageIndex = (messageIndex + 1) % sexyMessages.length;
        if (textElement) {
            textElement.style.opacity = '0';
            setTimeout(() => {
                textElement.textContent = sexyMessages[messageIndex];
                textElement.style.opacity = '1';
            }, 200);
        }
    }, 2500);
    
    loaderContainer.dataset.intervalId = messageInterval;
    
    return loaderContainer;
}

export function removeSexyLoader(loader) {
    if (loader) {
        const intervalId = loader.dataset.intervalId;
        if (intervalId) clearInterval(parseInt(intervalId));
        if (loader.parentNode) loader.parentNode.removeChild(loader);
    }
}

export function removeElement(element) {
    if (element && element.parentNode) {
        element.parentNode.removeChild(element);
    }
}

export function createMessageBubble(sender, message, imageUrl, audioUrl, userBubbleColor, currentUserAvatarUrl, modal, modalImg, username = 'Vous') {
    const messageWrapper = document.createElement('div');
    messageWrapper.classList.add('flex', 'mb-4', sender === 'user' ? 'justify-end' : 'justify-start', 'items-end');

    const messageBubble = document.createElement('div');
    // Utilisation des nouvelles classes CSS pour un style plus sexy
    const bubbleClass = sender === 'user' ? 'chat-bubble-user' : 'chat-bubble-bot';
    
    // On garde la couleur personnalisée si c'est l'utilisateur, sinon style par défaut
    if (sender === 'user' && userBubbleColor && !userBubbleColor.includes('bg-pink-500')) {
         messageBubble.classList.add(userBubbleColor.split(' ')[0]);
    } else {
         messageBubble.classList.add(bubbleClass);
    }
    
    messageBubble.classList.add('rounded-2xl', 'p-3', 'md:p-4', 'max-w-[85%]', 'md:max-w-md', 'lg:max-w-lg', 'relative', 'overflow-hidden', 'text-sm', 'md:text-base');

    // Container for avatar and name
    const avatarContainer = document.createElement('div');
    avatarContainer.classList.add('flex', 'flex-col', 'items-center', 'ml-2');

    // Add user avatar next to bubble
    if (sender === 'user') {
        if (currentUserAvatarUrl) {
            const avatarImg = document.createElement('img');
            avatarImg.src = currentUserAvatarUrl;
            avatarImg.classList.add('w-8', 'h-8', 'rounded-full', 'object-cover', 'border', 'border-gray-600');
            avatarContainer.appendChild(avatarImg);
        }
        
        // Add username below avatar
        const nameElement = document.createElement('span');
        nameElement.classList.add('text-[10px]', 'text-gray-400', 'mt-1');
        nameElement.textContent = username;
        avatarContainer.appendChild(nameElement);

        messageWrapper.appendChild(messageBubble);
        messageWrapper.appendChild(avatarContainer);
    } else {
        messageWrapper.appendChild(messageBubble);
    }

    if (message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('text-white', 'text-sm');
        if (window.markdownit) {
            const md = window.markdownit({
                html: true, // Permettre le HTML dans le Markdown
            });
            messageElement.innerHTML = md.render(message);
        } else {
            // Fallback si markdown-it n'est pas chargé
            messageElement.innerHTML = message;
        }
        messageBubble.appendChild(messageElement);
    }

    if (imageUrl) {
        const imageElement = document.createElement('img');
        // Gérer les URLs externes (Pollinations) et locales
        imageElement.src = imageUrl.startsWith('http') ? imageUrl : `${API_BASE}${imageUrl}`;
        imageElement.classList.add('chat-image', 'rounded-lg', 'mt-2', 'cursor-pointer');
        imageElement.onclick = () => {
            modal.classList.remove('hidden');
            modal.classList.add('flex');
            modalImg.src = imageElement.src;
        };
        messageBubble.appendChild(imageElement);
    }

    if (audioUrl) {
        const audioElement = document.createElement('audio');
        audioElement.src = `${API_BASE}${audioUrl}`;
        audioElement.controls = true;
        audioElement.classList.add('chat-audio', 'w-full', 'mt-2');
        messageBubble.appendChild(audioElement);
    }

    messageWrapper.appendChild(messageBubble);
    return { wrapper: messageWrapper, bubble: messageBubble };
}

export function scrollToBottom(element) {
    element.scrollTop = element.scrollHeight;
}
