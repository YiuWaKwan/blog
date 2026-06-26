/**
 * 标签详情页
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

const TYPE_LABELS = { blog: '博客', note: '笔记' };

function renderItem(item) {
  const label = TYPE_LABELS[item.content_type] || item.content_type;

  const href = item.content_type === 'blog'
    ? `/pages/blog/detail?slug=${encodeURIComponent(item.slug)}`
    : `/pages/notes/detail?slug=${encodeURIComponent(item.slug)}`;

  return `
    <article class="card">
      <div class="card__body">
        <div class="card__meta">${label}${item.published_at ? ' · ' + formatDate(item.published_at) : ''}</div>
        <h3 class="card__title"><a href="${href}">${escapeHtml(item.title)}</a></h3>
      </div>
    </article>
  `;
}

function setActiveTab(type) {
  document.querySelectorAll('.tabs .tab').forEach((tab) => {
    tab.classList.toggle('is-active', tab.dataset.type === type);
  });
}

async function loadTagDetail(slug, type) {
  const header = document.getElementById('tag-header');
  const grid = document.getElementById('tag-items');
  if (!grid) return;

  grid.innerHTML = '<p class="text-secondary">加载中…</p>';

  const result = await apiGet('/api/get_tag', { slug, content_type: type });

  if (result.code !== 0 || !result.data) {
    grid.innerHTML = `<p class="text-secondary">${escapeHtml(result.message || '标签不存在')}</p>`;
    return;
  }

  const { tag, items } = result.data;
  const visibleItems = items.filter((item) => item.content_type !== 'bookmark');

  if (header) {
    const total = (tag.blog_count || 0) + (tag.note_count || 0);
    header.innerHTML = `
      <h1>${escapeHtml(tag.name)}</h1>
      <p class="text-secondary">
        博客 ${tag.blog_count || 0} · 笔记 ${tag.note_count || 0} · 合计 ${total}
      </p>
    `;
    document.title = `${tag.name} — Personal Blog`;
  }

  grid.innerHTML = visibleItems.length
    ? visibleItems.map(renderItem).join('')
    : '<p class="text-secondary">该分类下暂无内容</p>';
}

function initTagsDetail() {
  const params = new URLSearchParams(window.location.search);
  const slug = params.get('slug');
  const type = params.get('type') || 'all';
  const safeType = type === 'bookmark' ? 'all' : type;

  if (!slug) {
    document.getElementById('tag-items').innerHTML = '<p class="text-secondary">缺少 slug 参数</p>';
    return;
  }

  setActiveTab(safeType);

  document.querySelectorAll('.tabs .tab').forEach((tab) => {
    tab.addEventListener('click', (e) => {
      e.preventDefault();
      const newType = tab.dataset.type;
      const url = new URL(window.location.href);
      url.searchParams.set('type', newType);
      history.replaceState(null, '', url);
      setActiveTab(newType);
      loadTagDetail(slug, newType);
    });
  });

  loadTagDetail(slug, safeType);
}

document.addEventListener('DOMContentLoaded', initTagsDetail);
