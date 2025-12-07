document.addEventListener('DOMContentLoaded', () => {
    const userList = document.getElementById('user-list');
    const createUserForm = document.getElementById('create-user-form');
    const createErrorMessage = document.getElementById('create-error-message');
    const editModal = document.getElementById('edit-modal');
    const editUserForm = document.getElementById('edit-user-form');
    const cancelEditButton = document.getElementById('cancel-edit');

    const fetchUsers = async () => {
        const response = await fetch('/api/users');
        const users = await response.json();
        userList.innerHTML = '';
        users.forEach(user => {
            const row = document.createElement('tr');
            row.className = 'hover:bg-gray-700/30 transition-colors border-b border-gray-700/50 last:border-0';
            const statusClass = user.is_active ? 'bg-green-900/30 text-green-400 border-green-500/30' : 'bg-yellow-900/30 text-yellow-400 border-yellow-500/30';
            const statusText = user.is_active ? 'Actif' : 'En attente';
            const premiumClass = user.is_premium ? 'bg-yellow-900/30 text-yellow-400 border-yellow-500/30' : 'bg-gray-700/30 text-gray-400 border-gray-600/30';
            
            row.innerHTML = `
                <td class="p-3 text-gray-400 font-mono text-xs">#${user.id}</td>
                <td class="p-3 font-medium text-white">${user.username}</td>
                <td class="p-3 text-sm text-gray-400">${user.email || '-'}</td>
                <td class="p-3">
                    <span class="px-2 py-1 rounded-full text-xs border ${statusClass}">${statusText}</span>
                </td>
                <td class="p-3">
                    <span class="px-2 py-1 rounded-full text-xs border ${premiumClass}">${user.is_premium ? 'Premium' : 'Free'}</span>
                </td>
                <td class="p-3">
                    ${user.is_admin ? '<span class="text-pink-400 font-bold">Admin</span>' : '<span class="text-gray-500">User</span>'}
                </td>
                <td class="p-3 text-right">
                    <div class="flex justify-end space-x-2">
                        <button class="bg-blue-600/20 hover:bg-blue-600/40 text-blue-400 border border-blue-500/30 hover:border-blue-500/50 p-1.5 rounded-lg transition-all" onclick="openEditModal(${user.id}, '${user.username}', ${user.is_admin}, ${user.is_active})" title="Modifier">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                        </button>
                        <button class="${user.is_premium ? 'bg-gray-600/20 hover:bg-gray-600/40 text-gray-400 border-gray-500/30' : 'bg-yellow-600/20 hover:bg-yellow-600/40 text-yellow-400 border-yellow-500/30'} border p-1.5 rounded-lg transition-all" onclick="togglePremium(${user.id})" title="${user.is_premium ? 'Retirer Premium' : 'Passer Premium'}">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7" /></svg>
                        </button>
                        ${!user.is_active ? `<button class="bg-green-600/20 hover:bg-green-600/40 text-green-400 border border-green-500/30 hover:border-green-500/50 p-1.5 rounded-lg transition-all" onclick="validateUser(${user.id})" title="Valider">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                        </button>` : ''}
                        ${user.username !== 'admin' ? `<button class="bg-red-600/20 hover:bg-red-600/40 text-red-400 border border-red-500/30 hover:border-red-500/50 p-1.5 rounded-lg transition-all" onclick="deleteUser(${user.id})" title="Supprimer">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                        </button>` : ''}
                    </div>
                </td>
            `;
            userList.appendChild(row);
        });
    };

    createUserForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = e.target['create-username'].value;
        const password = e.target['create-password'].value;
        const isAdmin = e.target['create-is-admin'].checked;

        const response = await fetch('/api/users', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, is_admin: isAdmin })
        });

        if (response.ok) {
            fetchUsers();
            createUserForm.reset();
            createErrorMessage.textContent = '';
        } else {
            const data = await response.json();
            createErrorMessage.textContent = data.error || 'Une erreur est survenue.';
        }
    });

    window.openEditModal = (id, username, isAdmin, isActive) => {
        editModal.classList.remove('hidden');
        document.getElementById('edit-user-id').value = id;
        document.getElementById('edit-username').value = username;
        document.getElementById('edit-is-admin').checked = isAdmin;
        
        // Ajouter checkbox is_active si elle n'existe pas
        let activeContainer = document.getElementById('edit-active-container');
        const wrapper = document.getElementById('edit-active-wrapper');
        
        if (!activeContainer && wrapper) {
            activeContainer = document.createElement('div');
            activeContainer.id = 'edit-active-container';
            activeContainer.innerHTML = `
                <label class="inline-flex items-center cursor-pointer">
                    <input type="checkbox" id="edit-is-active" class="sr-only peer">
                    <div class="relative w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-pink-800 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                    <span class="ms-3 text-sm font-medium text-gray-300">Compte Actif</span>
                </label>
            `;
            wrapper.appendChild(activeContainer);
        }
        
        const activeCheckbox = document.getElementById('edit-is-active');
        if (activeCheckbox) {
            activeCheckbox.checked = isActive;
        }
    };

    cancelEditButton.addEventListener('click', () => {
        editModal.classList.add('hidden');
    });

    // Gestion du bouton Sauvegarder (hors formulaire)
    document.getElementById('save-edit-btn').addEventListener('click', async () => {
        const id = document.getElementById('edit-user-id').value;
        const username = document.getElementById('edit-username').value;
        const password = document.getElementById('edit-password').value;
        const isAdmin = document.getElementById('edit-is-admin').checked;
        const activeCheckbox = document.getElementById('edit-is-active');
        const isActive = activeCheckbox ? activeCheckbox.checked : false;

        const payload = { username, is_admin: isAdmin, is_active: isActive };
        if (password) {
            payload.password = password;
        }

        const response = await fetch(`/api/users/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            fetchUsers();
            editModal.classList.add('hidden');
        } else {
            alert("Erreur lors de la mise à jour");
        }
    });

    window.validateUser = async (id) => {
        if (confirm('Voulez-vous valider ce compte utilisateur ?')) {
            const response = await fetch(`/api/users/${id}/validate`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.ok) {
                fetchUsers();
                alert("Utilisateur validé avec succès !");
            } else {
                alert("Erreur lors de la validation.");
            }
        }
    };

    window.togglePremium = async (id) => {
        const response = await fetch(`/api/users/${id}/toggle_premium`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
            fetchUsers();
        } else {
            alert("Erreur lors du changement de statut.");
        }
    };

    window.deleteUser = async (id) => {
        if (confirm('Êtes-vous sûr de vouloir supprimer cet utilisateur ?')) {
            const response = await fetch(`/api/users/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                fetchUsers();
            } else {
                // Handle error
            }
        }
    };

    fetchUsers();
});
    // --- Chat Logic ---
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const chatBox = document.getElementById('chat-box');
    const mainAvatar = document.getElementById('main-avatar');

    // Récupérer l'image de profil de Jenny
    const fetchProfileImage = async () => {
        try {
            const response = await fetch('/profile_image');
            const data = await response.json();
            if (data.url) {
                mainAvatar.src = data.url;
            }
        } catch (error) {
            console.error('Erreur récupération image profil:', error);
        }
    };
    fetchProfileImage();

    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    function sendMessage() {
        const message = messageInput.value.trim();
        if (message === '') return;

        addMessageToChatBox('user', message);
        const typingMessage = addTypingIndicator();

        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message
            }),
        })
            .then(async response => {
                const contentType = response.headers.get("content-type");
                if (contentType && contentType.indexOf("application/json") !== -1) {
                    return response.json();
                } else {
                    const text = await response.text();
                    // Si c'est une page HTML (probablement redirection login), on avertit l'utilisateur
                    if (text.trim().startsWith("<!DOCTYPE html>") || text.trim().startsWith("<html")) {
                        throw new Error("Session expirée. Veuillez rafraîchir la page et vous reconnecter.");
                    }
                    console.error("Réponse non-JSON:", text);
                    throw new Error(`Réponse inattendue du serveur (${response.status}): ${text.substring(0, 50)}...`);
                }
            })
            .then(data => {
                removeTypingIndicator(typingMessage);
                if (data.response) {
                    addMessageToChatBox('bot', data.response, data.image_url);
                } else if (data.error) {
                    addMessageToChatBox('bot', `Erreur : ${data.error}`);
                }
            })
            .catch((error) => {
                console.error('Erreur:', error);
                removeTypingIndicator(typingMessage);
                addMessageToChatBox('bot', `Désolé, une erreur est survenue: ${error.message}`);
            });

        messageInput.value = '';
    }

    function addTypingIndicator() {
        const messageWrapper = document.createElement('div');
        messageWrapper.classList.add('flex', 'mb-4', 'justify-start');

        const typingBubble = document.createElement('div');
        typingBubble.classList.add('bg-gray-700', 'rounded-2xl', 'p-4', 'max-w-xs', 'lg:max-w-md');

        const typingElement = document.createElement('div');
        typingElement.classList.add('flex', 'space-x-1');
        typingElement.innerHTML = '<div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div><div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s;"></div><div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s;"></div>';
        typingBubble.appendChild(typingElement);

        messageWrapper.appendChild(typingBubble);
        chatBox.appendChild(messageWrapper);
        chatBox.scrollTop = chatBox.scrollHeight;
        return messageWrapper;
    }

    function removeTypingIndicator(typingMessage) {
        if (typingMessage && typingMessage.parentNode) {
            typingMessage.parentNode.removeChild(typingMessage);
        }
    }

    function addMessageToChatBox(sender, message, imageUrl = null) {
        const messageWrapper = document.createElement('div');
        messageWrapper.classList.add('flex', 'mb-4', sender === 'user' ? 'justify-end' : 'justify-start');

        const messageBubble = document.createElement('div');
        const bubbleColor = sender === 'user' ? 'bg-pink-500' : 'bg-gray-700';
        messageBubble.classList.add(bubbleColor, 'rounded-2xl', 'p-4', 'max-w-xs', 'lg:max-w-md');

        if (message) {
            const messageElement = document.createElement('div');
            messageElement.classList.add('text-white', 'text-sm');
            messageElement.innerHTML = marked.parse(message);
            messageBubble.appendChild(messageElement);
        }

        if (imageUrl) {
            const imageElement = document.createElement('img');
            imageElement.src = imageUrl;
            imageElement.classList.add('chat-image', 'rounded-lg', 'mt-2');
            messageBubble.appendChild(imageElement);
        }

        messageWrapper.appendChild(messageBubble);
        chatBox.appendChild(messageWrapper);
        chatBox.scrollTop = chatBox.scrollHeight;
    }