document.getElementById('reset-password-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const newPassword = document.getElementById('new_password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    const errorMessage = document.getElementById('error-message');
    
    if (newPassword !== confirmPassword) {
        errorMessage.textContent = 'Les mots de passe ne correspondent pas.';
        errorMessage.className = 'sexy-alert error';
        return;
    }
    
    // Extraire le token de l'URL (le dernier segment)
    const token = window.location.pathname.split('/').pop();
    
    try {
        const response = await fetch('/api/reset-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token, new_password: newPassword })
        });

        const data = await response.json();

        if (response.ok) {
            errorMessage.textContent = 'Mot de passe modifié avec succès ! Redirection...';
            errorMessage.className = 'sexy-alert success';
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
        } else {
            errorMessage.textContent = data.error || 'Une erreur est survenue.';
            errorMessage.className = 'sexy-alert error';
        }
    } catch (error) {
        errorMessage.textContent = 'Erreur de connexion.';
        errorMessage.className = 'sexy-alert error';
    }
});