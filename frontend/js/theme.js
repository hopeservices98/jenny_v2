// Theme customization module
export class ThemeManager {
    constructor(elements) {
        this.elements = elements;
        this.userBubbleColor = 'bg-pink-500';
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        const { themeBgBtns, themeUserBtns, mainBg } = this.elements;

        if (themeBgBtns) {
            themeBgBtns.forEach(btn => {
                btn.addEventListener('click', () => {
                    const colorClass = btn.dataset.color;
                    if (mainBg) {
                        mainBg.classList.remove('bg-gray-900', 'bg-slate-900', 'bg-zinc-900', 'bg-neutral-900');
                        mainBg.classList.add(colorClass);
                    }
                    themeBgBtns.forEach(b => b.classList.remove('border-2', 'border-white'));
                    btn.classList.add('border-2', 'border-white');
                });
            });
        }

        if (themeUserBtns) {
            themeUserBtns.forEach(btn => {
                btn.addEventListener('click', () => {
                    this.userBubbleColor = btn.dataset.color;
                    themeUserBtns.forEach(b => b.classList.remove('border-2', 'border-white'));
                    btn.classList.add('border-2', 'border-white');
                });
            });
        }
    }

    getUserBubbleColor() {
        return this.userBubbleColor;
    }
}
