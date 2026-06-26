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

function hashString(str) {
  let h = 0;
  for (let i = 0; i < str.length; i++) {
    h = ((h << 5) - h) + str.charCodeAt(i);
    h |= 0;
  }
  return Math.abs(h);
}

const COVER_GRADIENTS = [
  'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
  'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
  'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)',
];

function getCoverStyle(post) {
  if (post.cover_image_url) {
    return { backgroundImage: `url(${post.cover_image_url})` };
  }
  const idx = hashString(post.slug || post.title) % COVER_GRADIENTS.length;
  return { background: COVER_GRADIENTS[idx] };
}

function renderHashTags(tags) {
  if (!tags?.length) return '';
  return tags.map((t) =>
    `<a href="/pages/tags/detail?slug=${encodeURIComponent(t.slug)}" class="feed-card__tag">#${escapeHtml(t.name)}</a>`
  ).join('');
}

function renderPostCard(post) {
  const coverStyle = getCoverStyle(post);
  const styleStr = Object.entries(coverStyle)
    .map(([k, v]) => `${k.replace(/([A-Z])/g, '-$1').toLowerCase()}:${v}`)
    .join(';');
  const category = post.tags?.[0]?.name || '未分类';

  return `
    <article class="feed-card">
      <div class="feed-card__body">
        <div class="feed-card__meta">
          <span>📅 ${formatDate(post.published_at)}</span>
          <span>📁 ${escapeHtml(category)}</span>
          <span>⏱ ${post.reading_time_minutes || 0} 分钟</span>
        </div>
        <h3 class="feed-card__title">
          <a href="/pages/blog/detail?slug=${encodeURIComponent(post.slug)}">${escapeHtml(post.title)}</a>
        </h3>
        <p class="feed-card__excerpt">${escapeHtml(post.excerpt || '')}</p>
        <div class="feed-card__tags">${renderHashTags(post.tags)}</div>
      </div>
      <a href="/pages/blog/detail?slug=${encodeURIComponent(post.slug)}" class="feed-card__cover-link">
        <div class="feed-card__cover" style="${styleStr}">
          ${!post.cover_image_url ? `<span class="feed-card__cover-text">${escapeHtml(post.title.charAt(0))}</span>` : ''}
        </div>
      </a>
    </article>
  `;
}

async function initBlogList() {
  const listEl = document.getElementById('post-list');
  if (!listEl) return;

  const tag = new URLSearchParams(window.location.search).get('tag') || null;
  const result = await apiPost('/api/get_posts', { page: 1, limit: 20, tag });

  if (result.code !== 0) {
    listEl.innerHTML = `<p class="text-secondary firefly-feed__loading">${escapeHtml(result.message || '加载失败')}</p>`;
    return;
  }

  const posts = result.data?.list || [];
  listEl.innerHTML = posts.length
    ? posts.map(renderPostCard).join('')
    : '<p class="text-secondary firefly-feed__loading">暂无文章</p>';
}

document.addEventListener('DOMContentLoaded', initBlogList);
