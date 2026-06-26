/**
 * 主题定制 — 配置读写与应用（第一期：色相、壁纸、透明度、布局）
 */
(function () {
  const STORAGE_KEY = 'blog-theme-custom';

  const DEFAULTS = {
    hue: 152,
    wallpaperMode: 'banner',
    wallpaperOpacity: 80,
    bgBlur: 10,
    cardOpacity: 50,
    articleLayout: 'list',
  };

  function load() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return { ...DEFAULTS };
      return { ...DEFAULTS, ...JSON.parse(raw) };
    } catch (_) {
      return { ...DEFAULTS };
    }
  }

  function save(settings) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
    } catch (_) { /* ignore */ }
  }

  function apply(settings) {
    const s = { ...DEFAULTS, ...settings };
    const root = document.documentElement;

    root.style.setProperty('--theme-hue', String(s.hue));
    root.style.setProperty('--wallpaper-opacity', String(s.wallpaperOpacity));
    root.style.setProperty('--bg-blur', `${s.bgBlur}px`);
    root.style.setProperty('--card-opacity', String(s.cardOpacity / 100));
    root.setAttribute('data-wallpaper-mode', s.wallpaperMode);
    root.setAttribute('data-article-layout', s.articleLayout);

    window.dispatchEvent(new CustomEvent('themeconfigchange', { detail: s }));
    return s;
  }

  function reset() {
    save(DEFAULTS);
    return apply(DEFAULTS);
  }

  function update(partial) {
    const next = { ...load(), ...partial };
    save(next);
    return apply(next);
  }

  window.ThemeConfig = {
    STORAGE_KEY,
    DEFAULTS,
    load,
    save,
    apply,
    reset,
    update,
  };

  apply(load());
})();
