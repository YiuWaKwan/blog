/**
 * 后台通用逻辑 stub
 * 约定：参数 ≤2 且较短用 adminGet，否则用 adminPost
 */

async function adminGet(path, params = {}) {
  return apiGet('/api/admin/' + path, params);
}

async function adminPost(path, body = {}) {
  return apiPost('/api/admin/' + path, body);
}

async function initTagInput(wrapperEl, postId) {
  let initialTags = [];
  if (postId) {
    const res = await adminGet('get_post', { id: postId });
    if (res.code === 0 && res.data?.tags) {
      initialTags = res.data.tags;
    }
  }
  return new TagInput(wrapperEl, {
    initialTags,
    onSearch: async (q) => {
      const res = await adminGet('get_tags', { q });
      return res.code === 0 ? (res.data?.list || []) : [];
    },
  });
}

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('blog-form') || document.getElementById('bookmark-form')) return;

  const tagInputWrapper = document.querySelector('.tag-input-wrapper');
  if (tagInputWrapper) {
    const postId = tagInputWrapper.dataset.postId || null;
    const hiddenEl = tagInputWrapper.querySelector('[name="tag_ids"]');
    let initialTags = [];
    if (hiddenEl && hiddenEl.value) {
      try { initialTags = JSON.parse(hiddenEl.value); } catch (_) {}
    }
    if (postId && initialTags.length === 0) {
      initTagInput(tagInputWrapper, postId);
    } else {
      new TagInput(tagInputWrapper, {
        initialTags,
        onSearch: async (q) => {
          const res = await adminGet('get_tags', { q });
          return res.code === 0 ? (res.data?.list || []) : [];
        },
      });
    }
  }

  initAdminMobileNav();
});

function initAdminMobileNav() {
  const sidebar = document.getElementById('admin-sidebar');
  const overlay = document.getElementById('admin-sidebar-overlay');
  if (!sidebar || !overlay) return;

  let toggle = document.getElementById('admin-menu-toggle');
  const header = document.querySelector('.admin-header');

  if (!toggle && header) {
    toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.id = 'admin-menu-toggle';
    toggle.className = 'admin-menu-toggle';
    toggle.setAttribute('aria-label', '打开菜单');
    toggle.textContent = '☰';
    header.prepend(toggle);
  }

  if (!toggle) return;

  function closeSidebar() {
    sidebar.classList.remove('is-open');
    overlay.classList.remove('is-visible');
    document.body.classList.remove('admin-nav-open');
  }

  function openSidebar() {
    sidebar.classList.add('is-open');
    overlay.classList.add('is-visible');
    document.body.classList.add('admin-nav-open');
  }

  toggle.addEventListener('click', () => {
    if (sidebar.classList.contains('is-open')) {
      closeSidebar();
    } else {
      openSidebar();
    }
  });

  overlay.addEventListener('click', closeSidebar);

  sidebar.querySelectorAll('.admin-sidebar__link').forEach((link) => {
    link.addEventListener('click', closeSidebar);
  });

  window.addEventListener('resize', () => {
    if (window.innerWidth > 768) closeSidebar();
  });
}
