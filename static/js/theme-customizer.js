/**
 * 主题定制面板 UI
 */
(function () {
  const { DEFAULTS, load, update, reset } = window.ThemeConfig;

  function $(id) {
    return document.getElementById(id);
  }

  function bindRange(id, key, displayId, formatter) {
    const input = $(id);
    if (!input) return;

    input.addEventListener('input', () => {
      const value = Number(input.value);
      if (displayId) {
        const el = $(displayId);
        if (el) el.textContent = formatter ? formatter(value) : String(value);
      }
      update({ [key]: value });
    });
  }

  function bindModeButtons(containerId, key) {
    const container = $(containerId);
    if (!container) return;

    container.querySelectorAll('[data-value]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const value = btn.getAttribute('data-value');
        container.querySelectorAll('[data-value]').forEach((b) => {
          b.classList.toggle('is-active', b === btn);
        });
        update({ [key]: value });
      });
    });
  }

  function syncUI(settings) {
    const hueInput = $('theme-hue');
    if (hueInput) hueInput.value = settings.hue;
    const hueVal = $('theme-hue-value');
    if (hueVal) hueVal.textContent = String(settings.hue);

    const wpOpacity = $('theme-wallpaper-opacity');
    if (wpOpacity) wpOpacity.value = settings.wallpaperOpacity;
    const wpOpacityVal = $('theme-wallpaper-opacity-value');
    if (wpOpacityVal) wpOpacityVal.textContent = `${settings.wallpaperOpacity}%`;

    const blur = $('theme-bg-blur');
    if (blur) blur.value = settings.bgBlur;
    const blurVal = $('theme-bg-blur-value');
    if (blurVal) blurVal.textContent = `${settings.bgBlur.toFixed(1)}px`;

    const cardOp = $('theme-card-opacity');
    if (cardOp) cardOp.value = settings.cardOpacity;
    const cardOpVal = $('theme-card-opacity-value');
    if (cardOpVal) cardOpVal.textContent = `${settings.cardOpacity}%`;

    document.querySelectorAll('#theme-wallpaper-modes [data-value]').forEach((btn) => {
      btn.classList.toggle('is-active', btn.getAttribute('data-value') === settings.wallpaperMode);
    });

    document.querySelectorAll('#theme-layout-modes [data-value]').forEach((btn) => {
      btn.classList.toggle('is-active', btn.getAttribute('data-value') === settings.articleLayout);
    });
  }

  function initPanel() {
    const panel = $('theme-panel');
    const openBtn = $('theme-panel-open');
    const closeBtn = $('theme-panel-close');
    const resetBtn = $('theme-panel-reset');

    if (!panel || !openBtn) return;

    const settings = load();
    syncUI(settings);

    bindRange('theme-hue', 'hue', 'theme-hue-value');
    bindRange('theme-wallpaper-opacity', 'wallpaperOpacity', 'theme-wallpaper-opacity-value', (v) => `${v}%`);
    bindRange('theme-bg-blur', 'bgBlur', 'theme-bg-blur-value', (v) => `${Number(v).toFixed(1)}px`);
    bindRange('theme-card-opacity', 'cardOpacity', 'theme-card-opacity-value', (v) => `${v}%`);

    bindModeButtons('theme-wallpaper-modes', 'wallpaperMode');
    bindModeButtons('theme-layout-modes', 'articleLayout');

    openBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      panel.hidden = false;
      openBtn.setAttribute('aria-expanded', 'true');
    });

    closeBtn?.addEventListener('click', () => {
      panel.hidden = true;
      openBtn.setAttribute('aria-expanded', 'false');
    });

    resetBtn?.addEventListener('click', () => {
      const next = reset();
      syncUI(next);
    });

    document.addEventListener('click', (e) => {
      if (panel.hidden) return;
      if (panel.contains(e.target) || openBtn.contains(e.target)) return;
      panel.hidden = true;
      openBtn.setAttribute('aria-expanded', 'false');
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !panel.hidden) {
        panel.hidden = true;
        openBtn.setAttribute('aria-expanded', 'false');
      }
    });

    window.addEventListener('themeconfigchange', (e) => {
      syncUI(e.detail);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPanel);
  } else {
    initPanel();
  }
})();
