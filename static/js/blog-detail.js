/**
 * 博客详情页 — 按 URL slug 加载文章，私密文章跳转解锁页
 */

function getQuerySlug() {
  return new URLSearchParams(window.location.search).get('slug');
}

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

function renderMarkdown(content) {
  if (typeof marked !== 'undefined') {
    return marked.parse(content || '');
  }
  return `<p>${escapeHtml(content).replace(/\n/g, '<br>')}</p>`;
}

function renderArticle(post) {
  return `
    <header class="article-header">
      <h1>${escapeHtml(post.title)}</h1>
      <div class="article-meta">
        <time>${formatDate(post.published_at)}</time>
        <span>${post.reading_time_minutes || 0} 分钟阅读</span>
      </div>
      ${renderTags(post.tags)}
    </header>
    <div class="prose">${renderMarkdown(post.content)}</div>
    <nav class="article-nav">
      <a href="/pages/blog/list" class="text-secondary">← 返回列表</a>
    </nav>
  `;
}

async function initBlogDetail() {
  const root = document.getElementById('article-root');
  const slug = getQuerySlug();

  if (!root) return;

  if (!slug) {
    root.innerHTML = '<p class="text-secondary">缺少文章 slug 参数</p>';
    return;
  }

  const result = await apiGet('/api/get_post', { slug });

  if (result.code === 403 && result.data?.requires_unlock) {
    window.location.href = `/pages/unlock?type=blog_post&id=${result.data.id}`;
    return;
  }

  if (result.code !== 0 || !result.data) {
    root.innerHTML = `<p class="text-secondary">${escapeHtml(result.message || '文章不存在')}</p>`;
    return;
  }

  const post = result.data;
  document.title = `${post.title} — Personal Blog`;
  root.innerHTML = renderArticle(post);
}

document.addEventListener('DOMContentLoaded', initBlogDetail);
