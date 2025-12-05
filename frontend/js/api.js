// API utilities
const API_BASE = 'http://127.0.0.1:5000';

export async function fetchJSON(url, options = {}) {
    const response = await fetch(`${API_BASE}${url}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        }
    });
    return response;
}

export async function uploadFile(file, type) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);

    const response = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
    });
    return response.json();
}

export async function sendChatMessage(message, imageUrl, audioUrl) {
    const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            message,
            image_url: imageUrl,
            audio_url: audioUrl
        }),
    });
    return response.json();
}

export async function fetchUserProfile() {
    const response = await fetch('/api/me');
    if (response.ok) {
        return response.json();
    }
    throw new Error('Failed to fetch profile');
}

export async function updateUserProfile(data) {
    const response = await fetch('/api/me', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return { response, data: await response.json() };
}

export async function upgradeToPremium() {
    const response = await fetch('/api/upgrade_premium', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    });
    return response.json();
}

export async function fetchProfileImage() {
    const response = await fetch('/profile_image');
    return response.json();
}

export async function checkImageGenerationStatus(generationId) {
    const response = await fetch(`/api/image_generation_status/${generationId}`);
    if (response.ok) {
        return response.json();
    }
    throw new Error('Failed to check status');
}
