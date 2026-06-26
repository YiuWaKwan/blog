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

function renderNoteItem(note) {
  const tags = (note.tags || []).map((t) =>
    `<span class="tag-pill">${escapeHtml(t.name)}</span>`
  ).join('');

  return `
    <a href="/pages/notes/detail?slug=${encodeURIComponent(note.slug)}" class="note-list__item">
      <div>
        <strong>${escapeHtml(note.title)}</strong>
        ${tags ? `<div class="tag-pills" style="margin-top:8px">${tags}</div>` : ''}
      </div>
      <span class="text-secondary">${formatDate(note.published_at)}</span>
    </a>
  `;
}

async function initNotesList() {
  const list = document.getElementById('note-list');
  if (!list) return;

  const tag = new URLSearchParams(window.location.search).get('tag') || null;
  const result = await apiPost('/api/get_notes', { page: 1, limit: 30, tag });

  if (result.code !== 0) {
    list.innerHTML = `<p class="text-secondary">${escapeHtml(result.message || '加载失败')}</p>`;
    return;
  }

  const notes = result.data?.list || [];
  list.innerHTML = notes.length
    ? notes.map(renderNoteItem).join('')
    : '<p class="text-secondary">暂无笔记</p>';
}

document.addEventListener('DOMContentLoaded', initNotesList);
