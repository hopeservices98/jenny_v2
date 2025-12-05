// Profile management module
import { fetchUserProfile, updateUserProfile, uploadFile } from './api.js';

export class ProfileManager {
    constructor(elements) {
        this.elements = elements;
        this.currentUserAvatarUrl = null;
        this.isPremium = false;
        this.onPremiumChange = null;
    }

    async init() {
        this.setupEventListeners();
        await this.loadProfile();
    }

    setupEventListeners() {
        const { avatarContainer, avatarUploadInput, profileForm } = this.elements;

        if (avatarContainer) {
            avatarContainer.addEventListener('click', () => avatarUploadInput.click());
        }

        if (avatarUploadInput) {
            avatarUploadInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) this.uploadAvatar(file);
            });
        }

        if (profileForm) {
            profileForm.addEventListener('submit', (e) => this.handleProfileSubmit(e));
        }
    }

    async loadProfile() {
        try {
            const user = await fetchUserProfile();
            this.updateUI(user);
        } catch (error) {
            console.error('Erreur récupération profil:', error);
        }
    }

    updateUI(user) {
        const {
            profileName, profileEmail, userAvatarPlaceholder,
            profileUsernameInput, profileFirstnameInput, profileLastnameInput,
            profileAddressInput, profileBirthdateInput, headerAvatarPlaceholder
        } = this.elements;

        // Stocker le statut premium dans le localStorage pour l'utiliser ailleurs (ex: message de bienvenue)
        localStorage.setItem('isPremium', user.is_premium);
        this.isPremium = user.is_premium;
        if (this.onPremiumChange) this.onPremiumChange(this.isPremium);

        if (profileName) {
            profileName.textContent = `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username;
        }
        if (profileEmail) profileEmail.textContent = user.email;

        // Fill form
        if (profileUsernameInput) profileUsernameInput.value = user.username;
        if (profileFirstnameInput) profileFirstnameInput.value = user.first_name || '';
        if (profileLastnameInput) profileLastnameInput.value = user.last_name || '';
        if (profileAddressInput) profileAddressInput.value = user.address || '';
        if (profileBirthdateInput) profileBirthdateInput.value = user.birth_date || '';

        // Avatar
        this.updateAvatar(user, userAvatarPlaceholder, headerAvatarPlaceholder);
    }

    updateAvatar(user, userAvatarPlaceholder, headerAvatarPlaceholder) {
        if (user.avatar_url) {
            this.currentUserAvatarUrl = user.avatar_url;
            const imgHtml = `<img src="${user.avatar_url}" class="w-full h-full object-cover">`;
            
            if (userAvatarPlaceholder) {
                userAvatarPlaceholder.innerHTML = imgHtml;
                userAvatarPlaceholder.classList.remove('bg-gradient-to-r', 'from-pink-500', 'to-purple-500');
            }
            if (headerAvatarPlaceholder) {
                headerAvatarPlaceholder.innerHTML = imgHtml;
                headerAvatarPlaceholder.classList.remove('bg-gradient-to-r', 'from-pink-500', 'to-purple-500');
            }
        } else {
            const initials = (user.first_name && user.last_name)
                ? `${user.first_name[0]}${user.last_name[0]}`.toUpperCase()
                : user.username.substring(0, 2).toUpperCase();

            if (userAvatarPlaceholder) {
                userAvatarPlaceholder.textContent = initials;
                userAvatarPlaceholder.classList.add('bg-gradient-to-r', 'from-pink-500', 'to-purple-500');
            }
            if (headerAvatarPlaceholder) {
                headerAvatarPlaceholder.textContent = initials;
                headerAvatarPlaceholder.classList.add('bg-gradient-to-r', 'from-pink-500', 'to-purple-500');
            }
        }
    }

    async uploadAvatar(file) {
        try {
            const data = await uploadFile(file, 'avatar');
            if (data.url) {
                this.currentUserAvatarUrl = data.url;
                const { userAvatarPlaceholder } = this.elements;
                if (userAvatarPlaceholder) {
                    userAvatarPlaceholder.innerHTML = `<img src="${data.url}" class="w-full h-full object-cover">`;
                    userAvatarPlaceholder.classList.remove('bg-gradient-to-r', 'from-pink-500', 'to-purple-500');
                }
            }
        } catch (error) {
            console.error('Erreur upload avatar:', error);
        }
    }

    async handleProfileSubmit(e) {
        e.preventDefault();
        const { profileFirstnameInput, profileLastnameInput, profileAddressInput, profileBirthdateInput, profileMessage } = this.elements;

        if (profileMessage) {
            profileMessage.textContent = 'Enregistrement...';
            profileMessage.className = 'text-xs text-center mt-1 text-gray-400';
        }

        const updatedData = {
            first_name: profileFirstnameInput?.value,
            last_name: profileLastnameInput?.value,
            address: profileAddressInput?.value,
            birth_date: profileBirthdateInput?.value
        };

        try {
            const { response, data } = await updateUserProfile(updatedData);

            if (response.ok) {
                this.updateUI(data);
                if (profileMessage) {
                    profileMessage.textContent = 'Modifications enregistrées !';
                    profileMessage.className = 'text-xs text-center mt-1 text-green-400';
                    setTimeout(() => profileMessage.textContent = '', 3000);
                }
            } else {
                if (profileMessage) {
                    profileMessage.textContent = data.error || 'Erreur lors de la mise à jour.';
                    profileMessage.className = 'text-xs text-center mt-1 text-red-400';
                }
            }
        } catch (error) {
            console.error('Erreur mise à jour profil:', error);
            if (profileMessage) {
                profileMessage.textContent = 'Erreur de connexion.';
                profileMessage.className = 'text-xs text-center mt-1 text-red-400';
            }
        }
    }

    getAvatarUrl() {
        return this.currentUserAvatarUrl;
    }

    getUsername() {
        const { profileUsernameInput } = this.elements;
        return profileUsernameInput ? profileUsernameInput.value : 'Vous';
    }
}
