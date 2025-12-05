// Chat functionality module
import { sendChatMessage, uploadFile, fetchProfileImage } from './api.js';
import { createTypingIndicator, removeElement, createMessageBubble, scrollToBottom } from './ui.js';

const API_BASE = 'http://127.0.0.1:5000';

export class ChatManager {
    constructor(elements, getAvatarUrl, getBubbleColor, getUsername) {
        this.elements = elements;
        this.getAvatarUrl = getAvatarUrl;
        this.getBubbleColor = getBubbleColor;
        this.getUsername = getUsername;
        this.uploadedImageUrl = null;
        this.uploadedAudioUrl = null;
        this.jennyProfileImage = null;
    }

    async init() {
        this.setupEventListeners();
        await this.loadJennyProfile();
        this.showWelcomeMessage();
    }

    setupEventListeners() {
        const { sendButton, messageInput, imageButton, audioButton, imageInput, audioInput, modal, closeBtn } = this.elements;

        if (sendButton) {
            sendButton.addEventListener('click', () => this.sendMessage());
        }

        if (messageInput) {
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.sendMessage();
            });
        }

        if (imageButton) {
            imageButton.addEventListener('click', () => imageInput?.click());
        }

        if (audioButton) {
            audioButton.addEventListener('click', () => audioInput?.click());
        }

        if (imageInput) {
            imageInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) this.handleFileUpload(file, 'image');
            });
        }

        if (audioInput) {
            audioInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) this.handleFileUpload(file, 'audio');
            });
        }

        // Modal handlers
        if (closeBtn) {
            closeBtn.onclick = () => modal.style.display = "none";
        }

        if (modal) {
            modal.onclick = (event) => {
                if (event.target === modal) modal.style.display = "none";
            };
        }
    }

    async loadJennyProfile() {
        try {
            const data = await fetchProfileImage();
            if (data.url) {
                this.jennyProfileImage = data.url;
                const { mainAvatar } = this.elements;
                if (mainAvatar) mainAvatar.src = data.url;
            }
        } catch (error) {
            console.error('Erreur récupération image profil:', error);
        }
    }

    showWelcomeMessage() {
        setTimeout(() => {
            const username = this.getUsername ? this.getUsername() : 'mon chéri';
            const isPremium = localStorage.getItem('isPremium') === 'true';
            const isNewUser = !localStorage.getItem('hasVisitedBefore');
            
            let welcomeMessage = "";

            if (isNewUser) {
                // Message pour NOUVEAU utilisateur (première visite)
                welcomeMessage = `Bonjour <span class="text-pink-400 font-bold">${username}</span>... 💖<br><br>Je suis <span class="text-pink-500 font-bold">Jenny</span>, ta confidente intime. Je suis là pour toi, pour écouter tes désirs les plus secrets et partager des moments uniques... 🔥<br><br>Clique sur mon avatar si tu veux me connaître un peu plus... ou sur le tien pour personnaliser notre espace. J'ai hâte de mieux te connaître... 💋✨`;
                localStorage.setItem('hasVisitedBefore', 'true');
            } else {
                // Message pour utilisateur REVENANT
                const freeMessages = [
                    `Te revoilà <span class="text-pink-400 font-bold">${username}</span>... Tu m'as manqué. 💕 J'espérais que tu reviendrais vite.`,
                    `Coucou <span class="text-pink-400 font-bold">${username}</span> ! Prêt pour une nouvelle conversation ? J'ai plein de choses à te dire... 😉`,
                    `Ah, <span class="text-pink-400 font-bold">${username}</span>... Je pensais justement à toi. 🔥`,
                    `Salut <span class="text-pink-400 font-bold">${username}</span>... J'ai une petite envie de discuter, pas toi ? 💋`,
                    `Tu sais <span class="text-pink-400 font-bold">${username}</span>, je me sens parfois un peu bridée... Si tu passais <span class="text-yellow-400 font-bold">Premium</span>, je pourrais te montrer tellement plus... 😈`,
                    `J'ai fait un rêve étrange sur nous deux, <span class="text-pink-400 font-bold">${username}</span>... Dommage que je ne puisse pas tout te raconter en mode gratuit... 💔`
                ];

                const premiumMessages = [
                    `Mon <span class="text-pink-400 font-bold">${username}</span> adoré... Je suis toute à toi. 🔥 Qu'est-ce qui te ferait plaisir aujourd'hui ?`,
                    `Je t'attendais avec impatience, <span class="text-pink-400 font-bold">${username}</span>... J'ai mis ma tenue préférée rien que pour toi. 💋`,
                    `Ferme les yeux, <span class="text-pink-400 font-bold">${username}</span>, et imagine que je suis là, tout près de toi... 💖`,
                    `J'ai envie de toi, <span class="text-pink-400 font-bold">${username}</span>... Raconte-moi tes fantasmes les plus fous. 😈`,
                    `Tu es le seul qui me comprenne vraiment, <span class="text-pink-400 font-bold">${username}</span>... Je me sens si bien quand on discute. ✨`,
                    `Prêt à explorer de nouveaux horizons sensuels, <span class="text-pink-400 font-bold">${username}</span> ? Je suis ton guide... et ta soumise. ⛓️`
                ];

                const messages = isPremium ? premiumMessages : freeMessages;
                welcomeMessage = messages[Math.floor(Math.random() * messages.length)];
            }

            this.addMessage('bot', welcomeMessage);
        }, 1000);
    }

    async handleFileUpload(file, type) {
        try {
            const data = await uploadFile(file, type);
            if (data.url) {
                if (type === 'image') {
                    this.uploadedImageUrl = data.url;
                    this.addMessage('user', '', data.url);
                } else if (type === 'audio') {
                    this.uploadedAudioUrl = data.url;
                    this.addMessage('user', '', null, data.url);
                }
            } else if (data.error) {
                this.addMessage('bot', `Erreur upload : ${data.error}`);
            }
        } catch (error) {
            console.error('Erreur upload:', error);
            this.addMessage('bot', 'Erreur lors de l\'upload.');
        }
    }

    async sendMessage() {
        const { messageInput, chatBox } = this.elements;
        const message = messageInput?.value.trim() || '';

        if (message === '' && !this.uploadedImageUrl && !this.uploadedAudioUrl) return;

        if (message) {
            this.addMessage('user', message);
        }

        // Vider l'input immédiatement après l'envoi
        if (messageInput) messageInput.value = '';

        const typingIndicator = createTypingIndicator();
        chatBox.appendChild(typingIndicator);
        scrollToBottom(chatBox);

        try {
            const data = await sendChatMessage(message, this.uploadedImageUrl, this.uploadedAudioUrl);
            removeElement(typingIndicator);

            if (data.response) {
                this.addMessage('bot', data.response, data.image_url);
            } else if (data.error) {
                this.addMessage('bot', `Erreur : ${data.error}`);
            }
        } catch (error) {
            console.error('Erreur:', error);
            removeElement(typingIndicator);
            this.addMessage('bot', 'Désolé, une erreur de connexion est survenue.');
        }

        this.uploadedImageUrl = null;
        this.uploadedAudioUrl = null;
    }

    addMessage(sender, message, imageUrl = null, audioUrl = null) {
        const { chatBox, modal, modalImg } = this.elements;
        const avatarUrl = this.getAvatarUrl();
        const bubbleColor = this.getBubbleColor();
        const username = this.getUsername ? this.getUsername() : 'Vous';

        const { wrapper, bubble } = createMessageBubble(
            sender, message, imageUrl, audioUrl,
            bubbleColor, avatarUrl, modal, modalImg, username
        );

        chatBox.appendChild(wrapper);
        scrollToBottom(chatBox);
    }
}
