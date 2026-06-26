/**
 * Home page (/pages/) — Firefly layout
 */

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
  'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
  'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
];

const DEMO_TAGS = [
  { name: 'Python', slug: 'python', total_count: 12 },
  { name: 'FastAPI', slug: 'fastapi', total_count: 8 },
  { name: 'PostgreSQL', slug: 'postgresql', total_count: 5 },
  { name: '学习笔记', slug: 'learning', total_count: 15 },
];

const DEMO_POSTS = [
  {
    title: 'Hello World',
    slug: 'hello-world',
    excerpt: '我的第一篇博客文章，欢迎阅读。',
    published_at: '2026-01-15T00:00:00Z',
    reading_time_minutes: 3,
    is_private: false,
    cover_image_url: null,
    tags: [{ name: 'Python', slug: 'python' }, { name: 'FastAPI', slug: 'fastapi' }],
  },
  {
    title: 'FastAPI 入门指南',
    slug: 'fastapi-guide',
    excerpt: '从零开始学习 FastAPI 框架的核心概念。',
    published_at: '2026-01-10T00:00:00Z',
    reading_time_minutes: 5,
    is_private: false,
    cover_image_url: null,
    tags: [{ name: 'FastAPI', slug: 'fastapi' }],
  },
];

function getCoverStyle(post) {
  if (post.cover_image_url) {
    return { backgroundImage: `url(${post.cover_image_url})` };
  }
  const idx = hashString(post.slug || post.title) % COVER_GRADIENTS.length;
  return { background: COVER_GRADIENTS[idx] };
}

function formatDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' });
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function renderHashTags(tags) {
  if (!tags?.length) return '';
  return tags.map((t) =>
    `<a href="/pages/tags/detail?slug=${encodeURIComponent(t.slug)}" class="feed-card__tag">#${escapeHtml(t.name)}</a>`
  ).join('');
}

function renderMainPost(post, index) {
  const coverStyle = getCoverStyle(post);
  const styleStr = Object.entries(coverStyle)
    .map(([k, v]) => `${k.replace(/([A-Z])/g, '-$1').toLowerCase()}:${v}`)
    .join(';');
  const pinned = index === 0 ? '<span class="feed-card__badge">置顶</span>' : '';
  const category = post.tags?.[0]?.name || '未分类';

  return `
    <article class="feed-card">
      <div class="feed-card__body">
        <div class="feed-card__meta">
          ${pinned}
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

function renderSidebarPost(post) {
  const coverStyle = getCoverStyle(post);
  const styleStr = Object.entries(coverStyle)
    .map(([k, v]) => `${k.replace(/([A-Z])/g, '-$1').toLowerCase()}:${v}`)
    .join(';');

  return `
    <a href="/pages/blog/detail?slug=${encodeURIComponent(post.slug)}" class="sidebar-post">
      <div class="sidebar-post__cover" style="${styleStr}"></div>
      <div class="sidebar-post__info">
        <strong>${escapeHtml(post.title)}</strong>
        <span>${formatDate(post.published_at)}</span>
      </div>
    </a>
  `;
}

function renderCategoryPill(tag) {
  return `
    <a href="/pages/tags/detail?slug=${encodeURIComponent(tag.slug)}" class="firefly-categories__pill">
      ${escapeHtml(tag.name)}<strong>${tag.total_count || 0}</strong>
    </a>
  `;
}

function renderSiteStats(stats) {
  const el = document.getElementById('site-stats');
  if (!el || !stats) return;

  el.innerHTML = `
    <li><span>📄 文章</span><strong>${stats.posts ?? 0}</strong></li>
    <li><span>📝 笔记</span><strong>${stats.notes ?? 0}</strong></li>
    <li><span>🏷 标签</span><strong>${stats.tags ?? 0}</strong></li>
    <li><span>📁 分类</span><strong>${Math.max(1, Math.ceil((stats.tags ?? 0) / 3))}</strong></li>
  `;
}

function showDbBanner() {
  const layout = document.querySelector('.firefly-layout');
  if (!layout || document.getElementById('db-banner')) return;

  const banner = document.createElement('div');
  banner.id = 'db-banner';
  banner.className = 'home-page__banner';
  banner.innerHTML = `
    数据库未连接，当前显示示例内容。请运行
    <code>docker compose up -d</code> 启动 PostgreSQL 后刷新。
  `;
  layout.before(banner);
}

function renderHomeContent(tags, posts, stats, isDemo = false) {
  const mainFeed = document.getElementById('main-feed');
  const sidebarFeatured = document.getElementById('sidebar-featured');
  const categoryList = document.getElementById('category-list');

  if (categoryList) {
    categoryList.innerHTML = tags.length
      ? tags.slice(0, 6).map(renderCategoryPill).join('')
      : '<span class="text-secondary">暂无分类</span>';
  }

  if (mainFeed) {
    mainFeed.innerHTML = posts.length
      ? posts.map(renderMainPost).join('')
      : '<p class="text-secondary firefly-feed__loading">暂无博客文章</p>';
  }

  if (sidebarFeatured) {
    const featured = posts.slice(0, 5);
    sidebarFeatured.innerHTML = featured.length
      ? featured.map(renderSidebarPost).join('')
      : '<p class="text-secondary">暂无精选</p>';
  }

  renderSiteStats(stats);
  if (isDemo) showDbBanner();
}

async function initHomePage() {
  const mainFeed = document.getElementById('main-feed');
  if (!mainFeed) return;

  const [tagsRes, postsRes, statsRes] = await Promise.all([
    apiGet('/api/get_popular_tags', { limit: 12 }),
    apiPost('/api/get_posts', { page: 1, limit: 8 }),
    apiGet('/api/get_site_stats'),
  ]);

  const apiOk = tagsRes.code === 0 && postsRes.code === 0;

  if (apiOk) {
    renderHomeContent(
      tagsRes.data?.list || [],
      postsRes.data?.list || [],
      statsRes.code === 0 ? statsRes.data : null,
      false,
    );
    return;
  }

  renderHomeContent(DEMO_TAGS, DEMO_POSTS, { posts: 2, notes: 0, tags: 4 }, true);
}

document.addEventListener('DOMContentLoaded', initHomePage);
