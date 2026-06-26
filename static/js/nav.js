document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('nav-toggle');
  const links = document.getElementById('nav-links');

  function closeNav() {
    links?.classList.remove('is-open');
    document.body.classList.remove('nav-open');
  }

  function openNav() {
    links?.classList.add('is-open');
    document.body.classList.add('nav-open');
  }

  if (toggle && links) {
    toggle.addEventListener('click', (e) => {
      e.stopPropagation();
      if (links.classList.contains('is-open')) {
        closeNav();
      } else {
        openNav();
      }
    });

    links.querySelectorAll('.nav__link, .firefly-nav__link').forEach((link) => {
      link.addEventListener('click', closeNav);
    });

    document.querySelector('.nav__back')?.addEventListener('click', closeNav);
    document.querySelector('.firefly-nav__brand')?.addEventListener('click', closeNav);

    document.addEventListener('click', (e) => {
      if (!links.classList.contains('is-open')) return;
      if (e.target.closest('.nav__inner, .firefly-nav__inner')) return;
      closeNav();
    });

    window.addEventListener('resize', () => {
      if (window.innerWidth > 768) closeNav();
    });
  }
});
