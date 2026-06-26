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

function renderNote(note) {
  return `
    <header class="article-header">
      <h1>${escapeHtml(note.title)}</h1>
      <div class="article-meta">
        <time>${formatDate(note.published_at)}</time>
        <span>${note.reading_time_minutes || 0} 分钟阅读</span>
      </div>
      ${renderTags(note.tags)}
    </header>
    <div class="prose">${renderMarkdown(note.content)}</div>
    <nav class="article-nav">
      <a href="/pages/notes/list" class="text-secondary">← 返回列表</a>
    </nav>
  `;
}

async function initNoteDetail() {
  const root = document.getElementById('note-root');
  const slug = getQuerySlug();
  if (!root) return;

  if (!slug) {
    root.innerHTML = '<p class="text-secondary">缺少 slug 参数</p>';
    return;
  }

  const result = await apiGet('/api/get_note', { slug });

  if (result.code === 403 && result.data?.requires_unlock) {
    window.location.href = `/pages/unlock?type=note&id=${result.data.id}`;
    return;
  }

  if (result.code !== 0 || !result.data) {
    root.innerHTML = `<p class="text-secondary">${escapeHtml(result.message || '笔记不存在')}</p>`;
    return;
  }

  document.title = `${result.data.title} — Personal Blog`;
  root.innerHTML = renderNote(result.data);
}

document.addEventListener('DOMContentLoaded', initNoteDetail);
