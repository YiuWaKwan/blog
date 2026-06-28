function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str ?? '';
  return div.innerHTML;
}

const COLLAPSED_GROUPS_KEY = 'bookmarks_collapsed_groups';

function getCollapsedGroups() {
  try {
    const raw = localStorage.getItem(COLLAPSED_GROUPS_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function setGroupCollapsed(slug, collapsed) {
  const state = getCollapsedGroups();
  if (collapsed) {
    state[slug] = true;
  } else {
    delete state[slug];
  }
  localStorage.setItem(COLLAPSED_GROUPS_KEY, JSON.stringify(state));
}

function renderBookmark(b) {
  const deleteBtn = `
    <button type="button" class="bookmark-card__delete" data-delete-id="${escapeHtml(b.id)}" aria-label="删除收藏">
      删除
    </button>
  `;

  if (b.requires_unlock) {
    const unlockUrl = `/pages/unlock?type=bookmark&id=${encodeURIComponent(b.id)}&redirect=${encodeURIComponent('/pages/bookmarks')}`;
    return `
      <article class="bookmark-card bookmark-card--locked" data-id="${escapeHtml(b.id)}">
        <a href="${unlockUrl}" class="bookmark-card__title">
          <span class="bookmark-card__lock" aria-hidden="true">🔒</span>
          ${escapeHtml(b.title)}
        </a>
        ${deleteBtn}
      </article>
    `;
  }

  return `
    <article class="bookmark-card" data-id="${escapeHtml(b.id)}">
      <a href="${escapeHtml(b.url)}" target="_blank" rel="noopener" class="bookmark-card__title" data-visit-link title="${escapeHtml(b.url)}">
        ${escapeHtml(b.title || b.url)}
      </a>
      <div class="bookmark-card__actions">
        <button type="button" class="bookmark-card__copy" data-url="${escapeHtml(b.url)}" aria-label="复制链接">
          复制
        </button>
        ${deleteBtn}
      </div>
    </article>
  `;
}

function groupBookmarks(items, categories) {
  const groups = new Map();

  for (const category of categories) {
    groups.set(category.slug, {
      name: category.name,
      slug: category.slug,
      sortOrder: category.sort_order ?? 0,
      items: [],
    });
  }

  for (const item of items) {
    const slug = item.category_slug || 'default';
    const name = item.category_name || '默认';
    if (!groups.has(slug)) {
      groups.set(slug, {
        name,
        slug,
        sortOrder: 999,
        items: [],
      });
    }
    groups.get(slug).items.push(item);
  }

  return [...groups.values()]
    .filter((group) => group.items.length > 0)
    .sort((a, b) => a.sortOrder - b.sortOrder || a.name.localeCompare(b.name, 'zh-CN'));
}

function renderBookmarkGroups(items, categories, listEl) {
  if (!items.length) {
    listEl.innerHTML = '<p class="text-secondary">暂无收藏</p>';
    return;
  }

  const groups = groupBookmarks(items, categories);
  if (!groups.length) {
    listEl.innerHTML = '<p class="text-secondary">暂无收藏</p>';
    return;
  }

  const collapsedState = getCollapsedGroups();

  listEl.innerHTML = groups.map((group) => {
    const isCollapsed = !!collapsedState[group.slug];
    return `
      <section
        class="bookmark-group${isCollapsed ? ' is-collapsed' : ''}"
        data-category="${escapeHtml(group.slug)}"
      >
        <button
          type="button"
          class="bookmark-group__header"
          aria-expanded="${isCollapsed ? 'false' : 'true'}"
        >
          <svg class="bookmark-group__chevron" viewBox="0 0 16 16" aria-hidden="true">
            <path d="M6 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span class="bookmark-group__name">${escapeHtml(group.name)}</span>
          <span class="bookmark-group__count">${group.items.length}</span>
        </button>
        <div class="bookmark-group__body">
          <div class="bookmark-grid">
            ${group.items.map(renderBookmark).join('')}
          </div>
        </div>
      </section>
    `;
  }).join('');
}

async function copyUrl(url, btn) {
  try {
    await navigator.clipboard.writeText(url);
  } catch {
    const ta = document.createElement('textarea');
    ta.value = url;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
  }

  const original = btn.textContent;
  btn.textContent = '已复制';
  btn.classList.add('is-copied');
  setTimeout(() => {
    btn.textContent = original;
    btn.classList.remove('is-copied');
  }, 1500);
}

let searchTimer = null;
let cachedCategories = [];

async function loadCategories() {
  const result = await apiGet('/api/get_bookmark_categories');
  if (result.code === 403) {
    window.location.reload();
    return [];
  }
  if (result.code !== 0) return [];
  cachedCategories = result.data?.list || [];
  return cachedCategories;
}

function initCategoryPicker(pickerEl, categories, selectedId = '') {
  if (!pickerEl || !categories.length) return null;

  const btn = pickerEl.querySelector('.bookmarks-add__picker-btn');
  const label = pickerEl.querySelector('.bookmarks-add__picker-label');
  const menu = pickerEl.querySelector('.bookmarks-add__picker-menu');
  const input = pickerEl.querySelector('input[type="hidden"]');
  if (!btn || !label || !menu || !input) return null;

  const defaultCategory = categories.find((c) => c.slug === 'default') || categories[0];
  let currentId = selectedId || (defaultCategory ? String(defaultCategory.id) : '');

  function renderMenu() {
    menu.innerHTML = categories.map((category) => {
      const id = String(category.id);
      const isSelected = id === currentId;
      return `
        <li role="presentation">
          <button
            type="button"
            class="bookmarks-add__picker-option${isSelected ? ' is-selected' : ''}"
            role="option"
            data-id="${escapeHtml(id)}"
            aria-selected="${isSelected}"
          >
            ${escapeHtml(category.name)}
          </button>
        </li>
      `;
    }).join('');
  }

  function closeMenu() {
    menu.hidden = true;
    btn.setAttribute('aria-expanded', 'false');
    pickerEl.classList.remove('is-open');
  }

  function openMenu() {
    menu.hidden = false;
    btn.setAttribute('aria-expanded', 'true');
    pickerEl.classList.add('is-open');
  }

  function setSelected(id) {
    currentId = id;
    input.value = id;
    const category = categories.find((c) => String(c.id) === id);
    label.textContent = category ? category.name : '选择分组';
    renderMenu();
    closeMenu();
  }

  setSelected(currentId);

  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    if (menu.hidden) {
      openMenu();
    } else {
      closeMenu();
    }
  });

  menu.addEventListener('click', (e) => {
    const option = e.target.closest('.bookmarks-add__picker-option');
    if (!option) return;
    setSelected(option.dataset.id);
  });

  const onDocumentClick = (e) => {
    if (!pickerEl.contains(e.target)) closeMenu();
  };

  document.addEventListener('click', onDocumentClick);

  return {
    reset() {
      setSelected(defaultCategory ? String(defaultCategory.id) : '');
    },
    destroy() {
      document.removeEventListener('click', onDocumentClick);
    },
  };
}

async function loadBookmarks(listEl, query = '') {
  const params = query ? { q: query } : {};
  const result = await apiGet('/api/get_bookmarks', params);
  if (result.code === 403) {
    window.location.reload();
    return null;
  }
  if (result.code !== 0) {
    listEl.innerHTML = `<p class="text-secondary">${escapeHtml(result.message || '加载失败')}</p>`;
    return null;
  }
  return result.data?.list || [];
}

async function refreshBookmarkList(listEl, query = '') {
  listEl.innerHTML = '<p class="text-secondary">加载中…</p>';
  const items = await loadBookmarks(listEl, query);
  if (items) renderBookmarkGroups(items, cachedCategories, listEl);
}

async function deleteBookmark(id, listEl, query = '') {
  if (!confirm('确定删除这条收藏？')) return;

  const result = await apiPost('/api/delete_bookmark', { id });
  if (result.code === 403) {
    window.location.reload();
    return;
  }
  if (result.code !== 0) {
    alert(result.message || '删除失败');
    return;
  }

  await refreshBookmarkList(listEl, query);
}

async function initBookmarks() {
  const list = document.getElementById('bookmark-list');
  if (!list) return;

  const searchInput = document.getElementById('bookmarks-search-input');
  const addModal = document.getElementById('bookmarks-add-modal');
  const addOpenBtn = document.getElementById('bookmarks-add-open');
  const addForm = document.getElementById('bookmarks-add-form');
  const addTitleInput = document.getElementById('bookmarks-add-title');
  const addUrlInput = document.getElementById('bookmarks-add-url');
  const categoryPicker = document.getElementById('bookmarks-add-category-picker');
  const addError = document.getElementById('bookmarks-add-error');

  const categories = await loadCategories();
  const picker = initCategoryPicker(categoryPicker, categories);

  function openAddModal() {
    if (!addModal) return;
    if (addError) {
      addError.hidden = true;
      addError.textContent = '';
    }
    if (addTitleInput) addTitleInput.value = '';
    if (addUrlInput) addUrlInput.value = '';
    picker?.reset();
    addModal.hidden = false;
    addModal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('bookmarks-modal-open');
    requestAnimationFrame(() => addUrlInput?.focus());
  }

  function closeAddModal() {
    if (!addModal) return;
    addModal.hidden = true;
    addModal.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('bookmarks-modal-open');
  }

  addOpenBtn?.addEventListener('click', openAddModal);

  addModal?.querySelectorAll('[data-close-modal]').forEach((el) => {
    el.addEventListener('click', closeAddModal);
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && addModal && !addModal.hidden) {
      closeAddModal();
    }
  });

  list.addEventListener('click', (e) => {
    const header = e.target.closest('.bookmark-group__header');
    if (header) {
      const group = header.closest('.bookmark-group');
      const slug = group?.dataset.category;
      if (!slug) return;

      const collapsed = group.classList.toggle('is-collapsed');
      header.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
      setGroupCollapsed(slug, collapsed);
      return;
    }

    const btn = e.target.closest('.bookmark-card__copy');
    if (btn) {
      e.preventDefault();
      e.stopPropagation();
      const url = btn.dataset.url;
      if (url) copyUrl(url, btn);
      return;
    }

    const deleteBtn = e.target.closest('.bookmark-card__delete');
    if (deleteBtn) {
      e.preventDefault();
      e.stopPropagation();
      const bookmarkId = deleteBtn.dataset.deleteId;
      if (!bookmarkId) return;
      const query = searchInput?.value.trim() || '';
      deleteBookmark(bookmarkId, list, query);
      return;
    }

    const visitLink = e.target.closest('a[data-visit-link]');
    if (!visitLink) return;

    const card = visitLink.closest('.bookmark-card');
    const bookmarkId = card?.dataset.id;
    if (!bookmarkId) return;

    fetch('/api/visit_bookmark', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: bookmarkId }),
      keepalive: true,
    }).catch(() => {});
  });

  if (searchInput) {
    searchInput.addEventListener('input', () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(async () => {
        const query = searchInput.value.trim();
        await refreshBookmarkList(list, query);
      }, 300);
    });
  }

  if (addForm && addUrlInput) {
    addForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (addError) {
        addError.hidden = true;
        addError.textContent = '';
      }

      const url = addUrlInput.value.trim();
      if (!url) return;

      const title = addTitleInput?.value.trim() || '';
      const categoryInput = document.getElementById('bookmarks-add-category');
      const categoryId = categoryInput?.value || '';
      const payload = { url };
      if (title) payload.title = title;
      if (categoryId) payload.category_id = categoryId;

      const submitBtn = addForm.querySelector('button[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;

      const result = await apiPost('/api/add_bookmark', payload);
      if (submitBtn) submitBtn.disabled = false;

      if (result.code === 403) {
        window.location.reload();
        return;
      }
      if (result.code !== 0) {
        if (addError) {
          addError.textContent = result.message || '保存失败';
          addError.hidden = false;
        }
        return;
      }

      closeAddModal();
      const query = searchInput?.value.trim() || '';
      await refreshBookmarkList(list, query);
    });
  }

  await refreshBookmarkList(list);
}

document.addEventListener('DOMContentLoaded', initBookmarks);
