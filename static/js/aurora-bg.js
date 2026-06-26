/**
 * 动态背景 — 流动网格波浪（随主题变色）
 * Usage: initDynamicBg('#ambient-canvas')
 */

function getThemeHue() {
  const raw = getComputedStyle(document.documentElement).getPropertyValue('--theme-hue').trim();
  const hue = parseInt(raw, 10);
  return Number.isFinite(hue) ? hue : 152;
}

function getBgTheme() {
  return document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
}

function getPalettes(theme) {
  const h = getThemeHue();
  if (theme === 'dark') {
    return {
      base: ['#0a0a12', '#12121f', '#1a1030'],
      waves: [
        { color: `hsla(${h}, 72%, 58%, 0.32)`, amp: 38, freq: 0.004, speed: 0.018, y: 0.28 },
        { color: `hsla(${(h + 90) % 360}, 68%, 55%, 0.26)`, amp: 52, freq: 0.003, speed: 0.012, y: 0.52 },
        { color: `hsla(${(h + 180) % 360}, 65%, 52%, 0.2)`, amp: 44, freq: 0.005, speed: 0.022, y: 0.72 },
        { color: `hsla(${(h + 45) % 360}, 70%, 58%, 0.14)`, amp: 30, freq: 0.006, speed: 0.015, y: 0.42 },
      ],
      dots: 'rgba(255, 255, 255, 0.06)',
    };
  }
  return {
    base: ['#e8f4fd', '#f0e6ff', '#fff0f5'],
    waves: [
      { color: `hsla(${h}, 70%, 52%, 0.22)`, amp: 42, freq: 0.004, speed: 0.016, y: 0.30 },
      { color: `hsla(${(h + 90) % 360}, 68%, 55%, 0.18)`, amp: 55, freq: 0.003, speed: 0.011, y: 0.55 },
      { color: `hsla(${(h + 180) % 360}, 65%, 50%, 0.2)`, amp: 48, freq: 0.005, speed: 0.020, y: 0.75 },
      { color: `hsla(${(h + 45) % 360}, 72%, 55%, 0.14)`, amp: 35, freq: 0.006, speed: 0.014, y: 0.45 },
    ],
    dots: 'rgba(0, 0, 0, 0.04)',
  };
}

function initDynamicBg(canvasSelector, options = {}) {
  const canvas = document.querySelector(canvasSelector);
  if (!canvas) return null;

  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const ctx = canvas.getContext('2d');
  let width = 0;
  let height = 0;
  let time = 0;
  let animationId = null;

  const particles = Array.from({ length: options.particleCount ?? 40 }, () => ({
    x: Math.random(),
    y: Math.random(),
    r: 1 + Math.random() * 2,
    vx: (Math.random() - 0.5) * 0.0004,
    vy: (Math.random() - 0.5) * 0.0004,
    phase: Math.random() * Math.PI * 2,
  }));

  function resize() {
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width * devicePixelRatio;
    canvas.height = height * devicePixelRatio;
    ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
  }

  function drawBase() {
    const pal = getPalettes(getBgTheme());
    const g = ctx.createLinearGradient(0, 0, width, height);
    g.addColorStop(0, pal.base[0]);
    g.addColorStop(0.5, pal.base[1]);
    g.addColorStop(1, pal.base[2]);
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, width, height);
  }

  function drawWave(wave, t) {
    ctx.beginPath();
    ctx.moveTo(0, height);
    for (let x = 0; x <= width; x += 3) {
      const y = wave.y * height
        + Math.sin(x * wave.freq + t * wave.speed) * wave.amp
        + Math.sin(x * wave.freq * 1.7 + t * wave.speed * 0.6) * wave.amp * 0.4;
      ctx.lineTo(x, y);
    }
    ctx.lineTo(width, height);
    ctx.closePath();
    ctx.fillStyle = wave.color;
    ctx.fill();
  }

  function drawParticles(t) {
    const pal = getPalettes(getBgTheme());
    particles.forEach((p) => {
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0 || p.x > 1) p.vx *= -1;
      if (p.y < 0 || p.y > 1) p.vy *= -1;

      const px = p.x * width;
      const py = p.y * height;
      const alpha = 0.3 + Math.sin(t * 0.02 + p.phase) * 0.2;
      ctx.beginPath();
      ctx.arc(px, py, p.r, 0, Math.PI * 2);
      ctx.fillStyle = pal.dots.replace(/[\d.]+\)$/, `${alpha})`);
      ctx.fill();
    });
  }

  function drawFrame() {
    drawBase();
    const pal = getPalettes(getBgTheme());
    pal.waves.forEach((wave) => drawWave(wave, time));
    drawParticles(time);
  }

  function loop() {
    time += 1;
    drawFrame();
    animationId = requestAnimationFrame(loop);
  }

  resize();
  drawFrame();

  if (!prefersReduced) loop();

  const onResize = () => { resize(); drawFrame(); };
  const onTheme = () => drawFrame();

  window.addEventListener('resize', onResize);
  window.addEventListener('themechange', onTheme);
  window.addEventListener('themeconfigchange', onTheme);

  return {
    destroy() {
      if (animationId) cancelAnimationFrame(animationId);
      window.removeEventListener('resize', onResize);
      window.removeEventListener('themechange', onTheme);
      window.removeEventListener('themeconfigchange', onTheme);
    },
  };
}

/* 兼容旧调用 */
function initLightCoverBg(selector, opts) {
  return initDynamicBg(selector, opts);
}

function initAmbientBg(selector) {
  return initDynamicBg(selector, { particleCount: 35 });
}

function initAuroraBg(selector, opts) {
  return initDynamicBg(selector, opts);
}
