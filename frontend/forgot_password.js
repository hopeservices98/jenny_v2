document.getElementById('forgot-password-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = e.target.email.value;
    const messageDiv = document.getElementById('message');

    const response = await fetch('/forgot-password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email })
    });

    const data = await response.json();
    messageDiv.textContent = data.message;
    if (response.ok) {
        messageDiv.classList.add('text-green-500');
        messageDiv.classList.remove('text-red-500');
    } else {
        messageDiv.classList.add('text-red-500');
        messageDiv.classList.remove('text-green-500');
    }
});