// The Fragance´s Interactive JavaScript

// Theme (Light / Dark Mode) Toggle Logic
function updateThemeUI(theme) {
    const sunIcon = document.getElementById('themeSunIcon');
    const moonIcon = document.getElementById('themeMoonIcon');
    const toggleContainer = document.getElementById('themeToggleBtn');
    
    if (theme === 'light') {
        document.documentElement.classList.remove('dark');
        if (sunIcon) sunIcon.className = 'w-5 h-5 rounded-full bg-amber-400 text-black flex items-center justify-center text-[10px] shadow-sm';
        if (moonIcon) moonIcon.className = 'w-5 h-5 rounded-full text-slate-400 flex items-center justify-center text-[10px]';
        if (toggleContainer) toggleContainer.setAttribute('title', 'Cambiar a Modo Oscuro');
    } else {
        document.documentElement.classList.add('dark');
        if (sunIcon) sunIcon.className = 'w-5 h-5 rounded-full text-slate-500 flex items-center justify-center text-[10px]';
        if (moonIcon) moonIcon.className = 'w-5 h-5 rounded-full bg-indigo-500 text-white flex items-center justify-center text-[10px] shadow-sm';
        if (toggleContainer) toggleContainer.setAttribute('title', 'Cambiar a Modo Claro');
    }
}

function toggleTheme() {
    const isDark = document.documentElement.classList.contains('dark');
    const newTheme = isDark ? 'light' : 'dark';
    localStorage.setItem('thefragances_theme', newTheme);
    updateThemeUI(newTheme);
}

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Theme
    const savedTheme = localStorage.getItem('thefragances_theme') || 'dark';
    updateThemeUI(savedTheme);

    const themeBtn = document.getElementById('themeToggleBtn');
    if (themeBtn) {
        themeBtn.addEventListener('click', toggleTheme);
    }

    // Mobile menu toggle
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.flash-alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 4000);
    });
});
