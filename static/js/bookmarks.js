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
    <article class="bookmark-card">
      <a href="${escapeHtml(b.url)}" target="_blank" rel="noopener" class="bookmark-card__title">
        ${escapeHtml(b.title)}
      </a>
      <button type="button" class="bookmark-card__copy" data-url="${escapeHtml(b.url)}" aria-label="复制链接">
        复制
      </button>
    </article>
  `;
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

async function initBookmarks() {
  const list = document.getElementById('bookmark-list');
  if (!list) return;

  list.addEventListener('click', (e) => {
    const btn = e.target.closest('.bookmark-card__copy');
    if (!btn) return;
    e.preventDefault();
    e.stopPropagation();
    const url = btn.dataset.url;
    if (url) copyUrl(url, btn);
  });

  const result = await apiGet('/api/get_bookmarks');
  if (result.code === 403) {
    window.location.reload();
    return;
  }
  if (result.code !== 0) {
    list.innerHTML = `<p class="text-secondary">${escapeHtml(result.message || '加载失败')}</p>`;
    return;
  }

  const items = result.data?.list || [];
  list.innerHTML = items.length
    ? items.map(renderBookmark).join('')
    : '<p class="text-secondary">暂无收藏</p>';
}

document.addEventListener('DOMContentLoaded', initBookmarks);
