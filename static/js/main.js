// ===== TOAST NOTIFICATIONS =====
function showToast(message, type = 'success') {
    // Remove existing toasts
    document.querySelectorAll('.toast-js').forEach(t => t.remove());
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} toast-js`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => toast.remove(), 3500);
}

// Auto-remove server-rendered toasts
document.querySelectorAll('.toast:not(.toast-js)').forEach(t => {
    setTimeout(() => t.style.animation = 'fadeOut 0.3s ease forwards', 3000);
    setTimeout(() => t.remove(), 3400);
});

// ===== SMOOTH SCROLL TO ANCHOR =====
document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
        const target = document.querySelector(a.getAttribute('href'));
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});
