(function initPageBg() {
  let bgInstance = null;

  function start() {
    const canvas = document.getElementById('ambient-canvas')
      || document.getElementById('cover-canvas');
    if (!canvas || typeof initDynamicBg !== 'function') return;

    if (bgInstance?.destroy) {
      bgInstance.destroy();
      bgInstance = null;
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }

  window.addEventListener('themeconfigchange', start);
})();
