(function initPageBg() {
  let bgInstance = null;

  function shouldInitCanvas() {
    const mode = document.documentElement.getAttribute('data-wallpaper-mode') || 'banner';
    return mode === 'banner' || mode === 'transparent';
  }

  function start() {
    const canvas = document.getElementById('ambient-canvas')
      || document.getElementById('cover-canvas');
    if (!canvas || typeof initDynamicBg !== 'function') return;

    if (bgInstance?.destroy) {
      bgInstance.destroy();
      bgInstance = null;
    }

    if (shouldInitCanvas()) {
      bgInstance = initDynamicBg('#' + canvas.id, { particleCount: 45 });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }

  window.addEventListener('themeconfigchange', start);
})();
