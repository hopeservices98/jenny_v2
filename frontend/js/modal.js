// Modal management utilities
export function setupModal(modalElement, closeBtn, onClose) {
    if (closeBtn) {
        closeBtn.addEventListener('click', onClose);
    }

    if (modalElement) {
        modalElement.addEventListener('click', (e) => {
            if (e.target === modalElement) onClose();
        });
    }
}

export function openModal(modalElement) {
    if (modalElement) modalElement.classList.remove('hidden');
}

export function closeModal(modalElement) {
    if (modalElement) modalElement.classList.add('hidden');
}
