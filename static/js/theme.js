(function () {
  const STORAGE_KEY = 'blog-theme';

  function getPreferred() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved === 'light' || saved === 'dark') return saved;
    } catch (_) { /* private mode */ }
    return 'dark';
  }

  function applyTheme(theme) {
    const root = document.documentElement;
    root.setAttribute('data-theme', theme);
    root.style.colorScheme = theme;
    if (document.body) {
      document.body.classList.remove('theme-light', 'theme-dark');
      document.body.classList.add('theme-' + theme);
    }
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch (_) { /* ignore */ }
    window.dispatchEvent(new CustomEvent('themechange', { detail: { theme } }));
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    applyTheme(current === 'dark' ? 'light' : 'dark');
  }

  applyTheme(getPreferred());

  window.toggleTheme = toggleTheme;
  window.getTheme = function () {
    return document.documentElement.getAttribute('data-theme') || 'dark';
  };

  document.addEventListener('DOMContentLoaded', () => {
    document.body.classList.add('theme-' + getTheme());
  });
})();
