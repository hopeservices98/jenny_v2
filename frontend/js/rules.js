export class RulesManager {
    constructor(elements) {
        this.elements = elements;
        this.currentSlide = 0;
        this.slides = [
            {
                title: "Bienvenue avec Jenny",
                content: "Jenny est votre confidente IA personnelle. Elle est là pour vous écouter, vous soutenir et discuter de tout, sans jugement.",
                icon: "👋"
            },
            {
                title: "Respect et Bienveillance",
                content: "Soyez respectueux dans vos échanges. Jenny est programmée pour être bienveillante, et elle attend la même chose de vous.",
                icon: "🤝"
            },
            {
                title: "Confidentialité",
                content: "Vos conversations sont privées. Cependant, évitez de partager des informations sensibles comme vos mots de passe ou coordonnées bancaires dans le chat.",
                icon: "🔒"
            },
            {
                title: "Limites",
                content: "Jenny est une IA. Elle ne remplace pas un professionnel de santé. En cas d'urgence ou de détresse grave, veuillez contacter les services appropriés.",
                icon: "⚠️"
            },
            {
                title: "Prêt à discuter ?",
                content: "En continuant, vous acceptez ces règles de bonne conduite. Profitez de votre moment avec Jenny !",
                icon: "✨"
            }
        ];
    }

    init() {
        // Vérifier si l'utilisateur a déjà vu les règles
        // On utilise une clé unique par utilisateur si possible, sinon globale
        // Pour l'instant, on utilise une clé globale simple pour tester
        const hasAcceptedRules = localStorage.getItem('rulesAccepted');
        
        if (!hasAcceptedRules) {
            // Petit délai pour s'assurer que le DOM est prêt et que l'animation est fluide
            setTimeout(() => {
                this.showRulesModal();
            }, 500);
        }
    }

    showRulesModal() {
        const modal = document.createElement('div');
        modal.id = 'rules-modal';
        modal.className = 'fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/90 backdrop-blur-sm';
        
        modal.innerHTML = `
            <div class="bg-gray-800 rounded-2xl shadow-2xl w-full max-w-md overflow-hidden border border-pink-500/30 relative">
                <div class="p-8 text-center">
                    <div id="rules-icon" class="text-6xl mb-6 animate-bounce">👋</div>
                    <h2 id="rules-title" class="text-2xl font-bold text-pink-500 mb-4">Bienvenue</h2>
                    <p id="rules-content" class="text-gray-300 mb-8 min-h-[80px]">Chargement...</p>
                    
                    <div class="flex justify-between items-center">
                        <div class="flex space-x-2" id="rules-dots">
                            <!-- Dots will be injected here -->
                        </div>
                        <button id="rules-next-btn" class="bg-pink-600 hover:bg-pink-700 text-white rounded-full px-6 py-2 font-bold transition-colors shadow-lg shadow-pink-600/20">
                            Suivant
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        this.elements.rulesModal = modal;
        this.elements.rulesTitle = modal.querySelector('#rules-title');
        this.elements.rulesContent = modal.querySelector('#rules-content');
        this.elements.rulesIcon = modal.querySelector('#rules-icon');
        this.elements.rulesNextBtn = modal.querySelector('#rules-next-btn');
        this.elements.rulesDots = modal.querySelector('#rules-dots');

        this.renderSlide(0);

        this.elements.rulesNextBtn.addEventListener('click', () => this.nextSlide());
    }

    renderSlide(index) {
        const slide = this.slides[index];
        this.elements.rulesTitle.textContent = slide.title;
        this.elements.rulesContent.textContent = slide.content;
        this.elements.rulesIcon.textContent = slide.icon;

        // Update dots
        this.elements.rulesDots.innerHTML = this.slides.map((_, i) => `
            <div class="w-2 h-2 rounded-full transition-colors ${i === index ? 'bg-pink-500' : 'bg-gray-600'}"></div>
        `).join('');

        // Update button text on last slide
        if (index === this.slides.length - 1) {
            this.elements.rulesNextBtn.textContent = "J'accepte et je commence";
        } else {
            this.elements.rulesNextBtn.textContent = "Suivant";
        }
    }

    nextSlide() {
        if (this.currentSlide < this.slides.length - 1) {
            this.currentSlide++;
            this.renderSlide(this.currentSlide);
        } else {
            this.closeModal();
        }
    }

    closeModal() {
        localStorage.setItem('rulesAccepted', 'true');
        const modal = document.getElementById('rules-modal');
        if (modal) {
            modal.classList.add('opacity-0', 'transition-opacity', 'duration-300');
            setTimeout(() => modal.remove(), 300);
        }
    }
}