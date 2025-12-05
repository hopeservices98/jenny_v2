// Gestion de l'envoi du code de vérification
const sendCodeBtn = document.getElementById('send-code-btn');
const emailInput = document.getElementById('email');
const verificationCodeContainer = document.getElementById('verification-code-container');
const errorMessage = document.getElementById('error-message');

sendCodeBtn.addEventListener('click', async () => {
    const email = emailInput.value;
    if (!email) {
        errorMessage.className = 'sexy-alert error';
        errorMessage.textContent = 'Veuillez entrer une adresse email.';
        return;
    }

    // Désactiver le bouton pour éviter le spam
    sendCodeBtn.disabled = true;
    sendCodeBtn.textContent = 'Envoi...';
    sendCodeBtn.classList.add('opacity-50', 'cursor-not-allowed');

    try {
        const response = await fetch('/auth/send-code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email })
        });

        const data = await response.json();
        console.log('Réponse send-code:', data);

        if (response.ok) {
            errorMessage.className = 'sexy-alert success';
            errorMessage.textContent = 'Code envoyé ! Vérifiez votre email.';
            verificationCodeContainer.classList.remove('hidden');
            
            // Réactiver le bouton après 60s
            let countdown = 60;
            const interval = setInterval(() => {
                sendCodeBtn.textContent = `Renvoyer (${countdown}s)`;
                countdown--;
                if (countdown < 0) {
                    clearInterval(interval);
                    sendCodeBtn.disabled = false;
                    sendCodeBtn.textContent = 'Renvoyer code';
                    sendCodeBtn.classList.remove('opacity-50', 'cursor-not-allowed');
                }
            }, 1000);
        } else {
            console.error('Erreur send-code:', data);
            errorMessage.className = 'sexy-alert error';
            errorMessage.textContent = data.error || 'Erreur lors de l\'envoi du code.';
            sendCodeBtn.disabled = false;
            sendCodeBtn.textContent = 'Envoyer code';
            sendCodeBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    } catch (error) {
        console.error('Erreur:', error);
        errorMessage.className = 'sexy-alert error';
        errorMessage.textContent = 'Erreur de connexion.';
        sendCodeBtn.disabled = false;
        sendCodeBtn.textContent = 'Envoyer code';
        sendCodeBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    }
});

document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = e.target.username.value;
    const email = e.target.email.value;
    const first_name = e.target.first_name.value;
    const last_name = e.target.last_name.value;
    const address = e.target.address.value;
    const birth_date = e.target.birth_date.value;
    const password = e.target.password.value;
    const confirm_password = e.target.confirm_password.value;
    const verification_code = document.getElementById('verification_code').value;

    // Vérification des mots de passe (déjà gérée en temps réel, mais double sécurité)
    if (password !== confirm_password) {
        errorMessage.className = 'sexy-alert error';
        errorMessage.textContent = 'Les mots de passe ne correspondent pas.';
        return;
    }

    if (!verification_code) {
        errorMessage.className = 'sexy-alert error';
        errorMessage.textContent = 'Veuillez entrer le code de vérification reçu par email.';
        return;
    }

    const response = await fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username,
            email,
            first_name,
            last_name,
            address,
            birth_date,
            password,
            confirm_password,
            verification_code
        })
    });

    const data = await response.json();

    if (response.ok) {
        // Afficher le message de succès et rediriger vers login après un délai
        errorMessage.className = 'sexy-alert success';
        errorMessage.textContent = data.message || 'Inscription réussie ! Redirection...';
        setTimeout(() => {
            window.location.href = '/login';
        }, 3000);
    } else {
        errorMessage.className = 'sexy-alert error';
        // Gérer le cas spécifique du Rate Limiting (429)
        if (response.status === 429) {
            errorMessage.textContent = "Trop de tentatives d'inscription. Veuillez réessayer plus tard.";
        } else {
            errorMessage.textContent = data.error || 'Une erreur est survenue.';
        }
    }
});
function setupPasswordToggle(toggleId, inputId) {
    const toggleButton = document.getElementById(toggleId);
    const inputField = document.getElementById(inputId);

    toggleButton.addEventListener('click', function () {
        const type = inputField.getAttribute('type') === 'password' ? 'text' : 'password';
        inputField.setAttribute('type', type);
        
        if (type === 'text') {
            this.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
</svg>`;
        } else {
            this.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
</svg>`;
        }
    });
}

setupPasswordToggle('toggle-password', 'password');
setupPasswordToggle('toggle-confirm-password', 'confirm_password');


// Vérification en temps réel des mots de passe
const passwordInput = document.getElementById('password');
const confirmPasswordInput = document.getElementById('confirm_password');
const submitButton = document.querySelector('button[type="submit"]');
// errorMessage déjà déclaré plus haut

function checkPasswords() {
    const pass = passwordInput.value;
    const confirm = confirmPasswordInput.value;

    if (confirm && pass !== confirm) {
        confirmPasswordInput.classList.add('border-red-500', 'ring-2', 'ring-red-500');
        confirmPasswordInput.classList.remove('focus:ring-pink-500');
        submitButton.disabled = true;
        submitButton.classList.add('opacity-50', 'cursor-not-allowed');
        errorMessage.className = 'sexy-alert error';
        errorMessage.textContent = 'Les mots de passe ne correspondent pas.';
    } else {
        confirmPasswordInput.classList.remove('border-red-500', 'ring-2', 'ring-red-500');
        confirmPasswordInput.classList.add('focus:ring-pink-500');
        submitButton.disabled = false;
        submitButton.classList.remove('opacity-50', 'cursor-not-allowed');
        errorMessage.textContent = '';
    }
}

passwordInput.addEventListener('input', checkPasswords);
confirmPasswordInput.addEventListener('input', checkPasswords);