/**
 * 博客列表页 — 动态加载文章列表
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

function renderTags(tags) {
  if (!tags?.length) return '';
  return `<div class="tag-pills">${tags.map((t) =>
    `<a href="/pages/tags/detail?slug=${encodeURIComponent(t.slug)}" class="tag-pill">${escapeHtml(t.name)}</a>`
  ).join('')}</div>`;
}

function renderPostCard(post) {
  return `
    <article class="card">
      <div class="card__body">
        <div class="card__meta">${formatDate(post.published_at)} · ${post.reading_time_minutes || 0} 分钟</div>
        <h3 class="card__title">
          <a href="/pages/blog/detail?slug=${encodeURIComponent(post.slug)}">${escapeHtml(post.title)}</a>
        </h3>
        <p class="card__excerpt">${escapeHtml(post.excerpt || '')}</p>
        ${renderTags(post.tags)}
      </div>
    </article>
  `;
}

async function initBlogList() {
  const listEl = document.getElementById('post-list');
  if (!listEl) return;

  const tag = new URLSearchParams(window.location.search).get('tag') || null;
  const result = await apiPost('/api/get_posts', { page: 1, limit: 20, tag });

  if (result.code !== 0) {
    listEl.innerHTML = `<p class="text-secondary">${escapeHtml(result.message || '加载失败')}</p>`;
    return;
  }

  const posts = result.data?.list || [];
  listEl.innerHTML = posts.length
    ? posts.map(renderPostCard).join('')
    : '<p class="text-secondary">暂无文章</p>';
}

document.addEventListener('DOMContentLoaded', initBlogList);
