// AromaLuxe Client JavaScript

document.addEventListener('DOMContentLoaded', () => {
    // Mobile menu toggle
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.flash-alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 4000);
    });

    // Quick filter accord click
    const accordPills = document.querySelectorAll('.accord-pill');
    accordPills.forEach(pill => {
        pill.addEventListener('click', () => {
            const accordName = pill.getAttribute('data-accord');
            if (accordName) {
                window.location.href = `/catalogo?acorde=${encodeURIComponent(accordName)}`;
            }
        });
    });
});
