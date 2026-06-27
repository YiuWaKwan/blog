function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str ?? '';
  return div.innerHTML;
}

function renderBookmark(b) {
  if (b.requires_unlock) {
    const unlockUrl = `/pages/unlock?type=bookmark&id=${encodeURIComponent(b.id)}&redirect=${encodeURIComponent('/pages/bookmarks')}`;
    return `
      <article class="bookmark-card bookmark-card--locked">
        <a href="${unlockUrl}" class="bookmark-card__title">
          <span class="bookmark-card__lock" aria-hidden="true">🔒</span>
          ${escapeHtml(b.title)}
        </a>
      </article>
    `;
  }

  return `
    <article class="bookmark-card" data-id="${escapeHtml(b.id)}">
      <a href="${escapeHtml(b.url)}" target="_blank" rel="noopener" class="bookmark-card__title" data-visit-link title="${escapeHtml(b.url)}">
        ${escapeHtml(b.title || b.url)}
      </a>
      <button type="button" class="bookmark-card__copy" data-url="${escapeHtml(b.url)}" aria-label="复制链接">
        复制
      </button>
    </article>
  `;
}

function renderBookmarkList(items, listEl) {
  listEl.innerHTML = items.length
    ? items.map(renderBookmark).join('')
    : '<p class="text-secondary">暂无收藏</p>';
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

async function initBookmarks() {
  const list = document.getElementById('bookmark-list');
  if (!list) return;

  const searchInput = document.getElementById('bookmarks-search-input');
  const addForm = document.getElementById('bookmarks-add-form');
  const addTitleInput = document.getElementById('bookmarks-add-title');
  const addUrlInput = document.getElementById('bookmarks-add-url');
  const addError = document.getElementById('bookmarks-add-error');

  list.addEventListener('click', (e) => {
    const btn = e.target.closest('.bookmark-card__copy');
    if (btn) {
      e.preventDefault();
      e.stopPropagation();
      const url = btn.dataset.url;
      if (url) copyUrl(url, btn);
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
        list.innerHTML = '<p class="text-secondary">加载中…</p>';
        const items = await loadBookmarks(list, query);
        if (items) renderBookmarkList(items, list);
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
      const payload = { url };
      if (title) payload.title = title;

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

      addUrlInput.value = '';
      if (addTitleInput) addTitleInput.value = '';
      const query = searchInput?.value.trim() || '';
      list.innerHTML = '<p class="text-secondary">加载中…</p>';
      const items = await loadBookmarks(list, query);
      if (items) renderBookmarkList(items, list);
    });
  }

  const items = await loadBookmarks(list);
  if (items) renderBookmarkList(items, list);
}

document.addEventListener('DOMContentLoaded', initBookmarks);
