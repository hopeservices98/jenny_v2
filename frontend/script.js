// Main application entry point
import { ProfileManager } from './js/profile.js';
import { PremiumManager } from './js/premium.js';
import { ThemeManager } from './js/theme.js';
import { ChatManager } from './js/chat.js';
import { RulesManager } from './js/rules.js';
import { setupModal, openModal, closeModal } from './js/modal.js';

document.addEventListener('DOMContentLoaded', async () => {
    // Collect all DOM elements
    const elements = {
        // Chat elements
        messageInput: document.getElementById('message-input'),
        sendButton: document.getElementById('send-button'),
        imageButton: document.getElementById('image-button'),
        audioButton: document.getElementById('audio-button'),
        imageInput: document.getElementById('image-input'),
        audioInput: document.getElementById('audio-input'),
        chatBox: document.getElementById('chat-box'),
        mainAvatar: document.getElementById('main-avatar'),
        modal: document.getElementById('image-modal'),
        modalImg: document.getElementById('modal-image'),
        closeBtn: document.getElementsByClassName('close')[0],

        // Profile elements
        profileName: document.getElementById('profile-name'),
        profileEmail: document.getElementById('profile-email'),
        userAvatarPlaceholder: document.getElementById('user-avatar-placeholder'),
        profileForm: document.getElementById('profile-form'),
        profileUsernameInput: document.getElementById('profile-username'),
        profileFirstnameInput: document.getElementById('profile-firstname'),
        profileLastnameInput: document.getElementById('profile-lastname'),
        profileAddressInput: document.getElementById('profile-address'),
        profileBirthdateInput: document.getElementById('profile-birthdate'),
        profileMessage: document.getElementById('profile-message'),
        avatarUploadInput: document.getElementById('avatar-upload'),
        avatarContainer: document.getElementById('avatar-container'),
        headerAvatarBtn: document.getElementById('header-avatar-btn'),
        closeProfileModalBtn: document.getElementById('close-profile-modal'),
        profileModal: document.getElementById('profile-modal'),
        headerAvatarPlaceholder: document.getElementById('header-avatar-placeholder'),

        // Premium elements
        premiumBadge: document.getElementById('premium-badge'),
        premiumModal: document.getElementById('premium-modal'),
        closePremiumModalBtn: document.getElementById('close-premium-modal'),
        premiumCodeInput: document.getElementById('premium-code-input'),
        premiumCodeBtn: document.getElementById('premium-code-btn'),
        premiumCodeMessage: document.getElementById('premium-code-message'),

        // Theme elements
        mainBg: document.getElementById('main-bg'),
        themeBgBtns: document.querySelectorAll('.theme-bg-btn'),
        themeUserBtns: document.querySelectorAll('.theme-user-btn'),

        // Jenny Profile elements
        jennyProfileBtn: document.getElementById('jenny-profile-btn'),
        jennyProfileModal: document.getElementById('jenny-profile-modal'),
        closeJennyModalBtn: document.getElementById('close-jenny-modal'),
        // headerJennyAvatar supprimé car on utilise mainAvatar
        jennyModalAvatar: document.getElementById('jenny-modal-avatar'),
    };

    // Initialize managers
    const rulesManager = new RulesManager(elements);
    rulesManager.init();

    const themeManager = new ThemeManager(elements);
    themeManager.init();

    const profileManager = new ProfileManager(elements);
    
    const premiumManager = new PremiumManager(elements, (sender, message) => {
        chatManager.addMessage(sender, message);
    });
    premiumManager.init();

    // Link profile premium status to premium manager
    profileManager.onPremiumChange = (isPremium) => {
        premiumManager.setIsPremium(isPremium);
    };

    await profileManager.init();

    const chatManager = new ChatManager(
        elements,
        () => profileManager.getAvatarUrl(),
        () => themeManager.getUserBubbleColor(),
        () => profileManager.getUsername()
    );
    await chatManager.init();

    // Setup profile modal
    setupModal(
        elements.profileModal,
        elements.closeProfileModalBtn,
        () => closeModal(elements.profileModal)
    );

    if (elements.headerAvatarBtn) {
        elements.headerAvatarBtn.addEventListener('click', () => openModal(elements.profileModal));
    }

    // Setup Jenny Profile Modal
    setupModal(
        elements.jennyProfileModal,
        elements.closeJennyModalBtn,
        () => closeModal(elements.jennyProfileModal)
    );

    if (elements.jennyProfileBtn) {
        elements.jennyProfileBtn.addEventListener('click', () => openModal(elements.jennyProfileModal));
    }

    // Sync Jenny's avatar in modal
    // On attend un peu que le profil soit chargé par ChatManager
    setTimeout(() => {
        const jennyAvatarUrl = chatManager.jennyProfileImage;
        if (jennyAvatarUrl) {
            if (elements.jennyModalAvatar) elements.jennyModalAvatar.src = jennyAvatarUrl;
        }
    }, 1000);
});
