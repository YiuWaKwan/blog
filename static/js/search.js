/**
 * 搜索页 — 根据 URL 参数 q 调用搜索 API 并渲染结果
 */

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str ?? '';
  return div.innerHTML;
}

function formatDate(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
}

const TYPE_LABELS = {
  blog: '博客',
  note: '笔记',
  tag: '标签',
};

function itemUrl(item) {
  const slug = encodeURIComponent(item.slug);
  if (item.content_type === 'blog') return `/pages/blog/detail?slug=${slug}`;
  if (item.content_type === 'note') return `/pages/notes/detail?slug=${slug}`;
  return `/pages/tags/detail?slug=${slug}`;
}

function renderSearchItem(item) {
  const label = TYPE_LABELS[item.content_type] || item.content_type;
  const meta = item.published_at
    ? formatDate(item.published_at)
    : escapeHtml(item.excerpt || '');

  return `
    <article class="search-item card">
      <div class="card__body">
        <div class="search-item__meta">
          <span class="search-item__type">${label}</span>
          ${meta ? `<span class="search-item__date">${meta}</span>` : ''}
        </div>
        <h3 class="card__title">
          <a href="${itemUrl(item)}">${escapeHtml(item.title)}</a>
        </h3>
        ${item.excerpt && item.content_type !== 'tag'
          ? `<p class="card__excerpt">${escapeHtml(item.excerpt)}</p>`
          : ''}
      </div>
    </article>
  `;
}

async function initSearch() {
  const resultsEl = document.getElementById('search-results');
  const summaryEl = document.getElementById('search-summary');
  if (!resultsEl) return;

  const q = new URLSearchParams(window.location.search).get('q')?.trim() || '';

  if (!q) {
    if (summaryEl) summaryEl.textContent = '在导航栏输入关键词开始搜索';
    resultsEl.innerHTML = '';
    return;
  }

  if (summaryEl) summaryEl.textContent = `关键词：「${q}」`;

  const result = await apiGet('/api/search', { q, limit: 30 });

  if (result.code !== 0) {
    resultsEl.innerHTML = `<p class="text-secondary">${escapeHtml(result.message || '搜索失败')}</p>`;
    return;
  }

  const items = result.data?.list || [];
  resultsEl.innerHTML = items.length
    ? `<div class="search-results">${items.map(renderSearchItem).join('')}</div>`
    : '<p class="text-secondary">未找到相关内容</p>';
}

document.addEventListener('DOMContentLoaded', initSearch);
