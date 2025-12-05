// Premium management module
import { upgradeToPremium } from './api.js';

export class PremiumManager {
    constructor(elements, onMessage) {
        this.elements = elements;
        this.isPremium = false;
        this.onMessage = onMessage;
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        const {
            closePremiumModalBtn, premiumModal, premiumCodeBtn, premiumCodeInput
        } = this.elements;

        if (closePremiumModalBtn) {
            closePremiumModalBtn.addEventListener('click', () => this.closeModal());
        }

        if (premiumModal) {
            premiumModal.addEventListener('click', (e) => {
                if (e.target === premiumModal) this.closeModal();
            });
        }

        if (premiumCodeBtn) {
            premiumCodeBtn.addEventListener('click', () => this.processPremiumCode());
        }

        if (premiumCodeInput) {
            premiumCodeInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.processPremiumCode();
            });
        }
    }

    setIsPremium(value) {
        this.isPremium = value;
        this.updateBadge();
    }

    updateBadge() {
        const { premiumBadge } = this.elements;
        if (!premiumBadge) return;

        premiumBadge.classList.remove('hidden');
        if (this.isPremium) {
            premiumBadge.textContent = 'PREMIUM';
            premiumBadge.className = 'cursor-default px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider shadow-lg bg-gradient-to-r from-yellow-400 to-yellow-600 text-white border border-yellow-300';
            premiumBadge.onclick = null;
        } else {
            premiumBadge.textContent = 'FREE';
            premiumBadge.className = 'cursor-pointer px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider transition-all duration-300 transform hover:scale-105 shadow-lg bg-gray-700 text-gray-300 border border-gray-600 hover:bg-gray-600';
            premiumBadge.onclick = () => this.openModal();
        }
    }

    openModal() {
        const { premiumModal } = this.elements;
        if (premiumModal) premiumModal.classList.remove('hidden');
    }

    closeModal() {
        const { premiumModal } = this.elements;
        if (premiumModal) premiumModal.classList.add('hidden');
    }

    async processPremiumCode() {
        const { premiumCodeInput, premiumCodeBtn, premiumCodeMessage } = this.elements;
        
        if (!premiumCodeInput || !premiumCodeBtn) return;
        
        const code = premiumCodeInput.value.trim();
        
        if (!code) {
            this.showMessage(premiumCodeMessage, 'Veuillez entrer un code premium.', 'error');
            return;
        }
        
        const originalText = premiumCodeBtn.textContent;
        premiumCodeBtn.textContent = 'Vérification...';
        premiumCodeBtn.disabled = true;
        this.hideMessage(premiumCodeMessage);
        
        try {
            const response = await fetch('/api/upgrade_premium', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ code: code })
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                this.isPremium = true;
                this.updateBadge();
                this.closeModal();
                
                if (this.onMessage) {
                    this.onMessage('bot', data.message + " 🔥");
                }
                
                if (premiumCodeInput) {
                    premiumCodeInput.value = '';
                }
            } else {
                this.showMessage(premiumCodeMessage, data.message || 'Code invalide.', 'error');
                premiumCodeBtn.textContent = originalText;
                premiumCodeBtn.disabled = false;
            }
        } catch (error) {
            console.error('Erreur:', error);
            this.showMessage(premiumCodeMessage, 'Erreur de connexion. Réessayez.', 'error');
            premiumCodeBtn.textContent = originalText;
            premiumCodeBtn.disabled = false;
        }
    }
    
    showMessage(element, message, type) {
        if (!element) return;
        
        element.textContent = message;
        element.classList.remove('hidden');
        
        if (type === 'error') {
            element.className = 'mt-4 p-3 rounded-lg text-sm bg-red-900/50 text-red-300 border border-red-700';
        } else if (type === 'success') {
            element.className = 'mt-4 p-3 rounded-lg text-sm bg-green-900/50 text-green-300 border border-green-700';
        } else {
            element.className = 'mt-4 p-3 rounded-lg text-sm bg-blue-900/50 text-blue-300 border border-blue-700';
        }
    }
    
    hideMessage(element) {
        if (element) {
            element.classList.add('hidden');
        }
    }
}
