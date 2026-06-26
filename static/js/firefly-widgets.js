/**
 * Firefly 侧栏小组件 — 非首页页面加载统计与精选
 */

function ffHashString(str) {
  let h = 0;
  for (let i = 0; i < str.length; i++) {
    h = ((h << 5) - h) + str.charCodeAt(i);
    h |= 0;
  }
  return Math.abs(h);
}

const FF_COVER_GRADIENTS = [
  'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
  'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
  'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)',
];

function ffGetCoverStyle(post) {
  if (post.cover_image_url) {
    return { backgroundImage: `url(${post.cover_image_url})` };
  }
  const idx = ffHashString(post.slug || post.title) % FF_COVER_GRADIENTS.length;
  return { background: FF_COVER_GRADIENTS[idx] };
}

function ffStyleStr(styleObj) {
  return Object.entries(styleObj)
    .map(([k, v]) => `${k.replace(/([A-Z])/g, '-$1').toLowerCase()}:${v}`)
    .join(';');
}

function ffFormatDate(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
}

function ffEscapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str ?? '';
  return div.innerHTML;
}

function renderFireflySiteStats(stats) {
  const el = document.getElementById('site-stats');
  if (!el || !stats) return;

  el.innerHTML = `
    <li><span>📄 文章</span><strong>${stats.posts ?? 0}</strong></li>
    <li><span>📝 笔记</span><strong>${stats.notes ?? 0}</strong></li>
    <li><span>🏷 标签</span><strong>${stats.tags ?? 0}</strong></li>
    <li><span>📁 分类</span><strong>${Math.max(1, Math.ceil((stats.tags ?? 0) / 3))}</strong></li>
  `;
}

function renderFireflySidebarPost(post) {
  const styleStr = ffStyleStr(ffGetCoverStyle(post));
  return `
    <a href="/pages/blog/detail?slug=${encodeURIComponent(post.slug)}" class="sidebar-post">
      <div class="sidebar-post__cover" style="${styleStr}"></div>
      <div class="sidebar-post__info">
        <strong>${ffEscapeHtml(post.title)}</strong>
        <span>${ffFormatDate(post.published_at)}</span>
      </div>
    </a>
  `;
}

async function initFireflySidebarWidgets() {
  if (document.getElementById('main-feed')) return;

  const statsEl = document.getElementById('site-stats');
  const featuredEl = document.getElementById('sidebar-featured');
  if (!statsEl && !featuredEl) return;

  const requests = [];
  if (statsEl) requests.push(apiGet('/api/get_site_stats'));
  if (featuredEl) requests.push(apiPost('/api/get_posts', { page: 1, limit: 5 }));

  const results = await Promise.all(requests);
  let idx = 0;

  if (statsEl) {
    const statsRes = results[idx++];
    if (statsRes.code === 0) {
      renderFireflySiteStats(statsRes.data);
    }
  }

  if (featuredEl) {
    const postsRes = results[idx++];
    if (postsRes.code === 0) {
      const posts = postsRes.data?.list || [];
      featuredEl.innerHTML = posts.length
        ? posts.map(renderFireflySidebarPost).join('')
        : '<p class="text-secondary">暂无精选</p>';
    } else {
      featuredEl.innerHTML = '<p class="text-secondary">加载失败</p>';
    }
  }
}

document.addEventListener('DOMContentLoaded', initFireflySidebarWidgets);
