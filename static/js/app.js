/**
 * MannMitra - Professional Client Utilities
 */

// Immediate theme bootstrap (Only 3 modes: night, peacock, peace)
(function() {
  let savedTheme = localStorage.getItem('mannmitra-theme');
  if (!savedTheme || savedTheme === 'light' || savedTheme === 'day') {
    savedTheme = 'peacock';
    localStorage.setItem('mannmitra-theme', 'peacock');
  }
  document.documentElement.dataset.theme = savedTheme;
  document.addEventListener('DOMContentLoaded', () => {
    updateThemeButtons(savedTheme);
    highlightActiveNav();
  });
})();

function highlightActiveNav() {
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-links a.nav-link, .mobile-drawer-links a').forEach(link => {
    const href = link.getAttribute('href');
    if (!href) return;
    try {
      const linkPath = new URL(href, window.location.origin).pathname;
      const isMatch = (linkPath === currentPath) || (linkPath !== '/' && currentPath.startsWith(linkPath));
      if (isMatch) {
        link.classList.add('active');
        link.setAttribute('aria-current', 'page');
      } else {
        link.classList.remove('active');
        link.removeAttribute('aria-current');
      }
    } catch(e) {}
  });
}

function setTheme(theme) {
  if (theme === 'light') theme = 'peacock';
  document.documentElement.dataset.theme = theme;
  localStorage.setItem('mannmitra-theme', theme);
  updateThemeButtons(theme);
  toast(`Switched to ${theme.charAt(0).toUpperCase() + theme.slice(1)} Mode ✦`);
}

function updateThemeButtons(theme) {
  document.querySelectorAll('.theme-pill-btn').forEach(btn => {
    const isActive = btn.dataset.theme === theme;
    btn.classList.toggle('active', isActive);
    btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');
  });
}

function toggleMobileNav() {
  const drawer = document.getElementById('mobileDrawer');
  if (!drawer) return;
  const isHidden = drawer.hidden;
  drawer.hidden = !isHidden;
  document.body.classList.toggle('modal-open', !isHidden);
}

function toast(msg) {
  let t = document.getElementById('globalToast');
  if (!t) {
    t = document.querySelector('.mm-toast');
  }
  if (!t) {
    t = document.createElement('div');
    t.className = 'mm-toast';
    t.id = 'globalToast';
    document.body.appendChild(t);
  }
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(window.mmToastTimer);
  window.mmToastTimer = setTimeout(() => {
    t.classList.remove('show');
  }, 2300);
}

// Global text-to-speech utility
function speakText(text, lang = 'hi-IN') {
  if (!('speechSynthesis' in window)) {
    toast('Text-to-speech is not supported on this device.');
    return;
  }
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = lang;
  u.rate = 0.92;
  window.speechSynthesis.speak(u);
  toast('Reciting audio 🔊');
}
