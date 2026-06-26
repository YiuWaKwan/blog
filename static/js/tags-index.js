/**
 * 标签归档页
 */

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str ?? '';
  return div.innerHTML;
}

function renderTagTable(tags) {
  const tbody = document.getElementById('tags-table-body');
  if (!tbody) return;

  if (!tags.length) {
    tbody.innerHTML = '<tr><td colspan="4" class="text-secondary" style="text-align:center">暂无标签</td></tr>';
    return;
  }

  tbody.innerHTML = tags
    .sort((a, b) => (b.total_count || 0) - (a.total_count || 0))
    .map((t) => {
      const total = (t.blog_count || 0) + (t.note_count || 0);
      return `
      <tr>
        <td><a href="/pages/tags/detail?slug=${encodeURIComponent(t.slug)}">${escapeHtml(t.name)}</a></td>
        <td class="num">${t.blog_count || 0}</td>
        <td class="num">${t.note_count || 0}</td>
        <td class="num total">${total}</td>
      </tr>
    `;
    }).join('');
}

async function initTagsIndex() {
  const cloud = document.getElementById('tag-cloud');
  const result = await apiGet('/api/get_tags');

  if (result.code !== 0) {
    if (cloud) cloud.innerHTML = `<p class="text-secondary">${escapeHtml(result.message || '加载失败')}</p>`;
    renderTagTable([]);
    return;
  }

  const tags = result.data?.list || [];
  if (typeof renderTagCloud === 'function' && cloud) {
    renderTagCloud(cloud, tags);
  }
  renderTagTable(tags);
}

document.addEventListener('DOMContentLoaded', initTagsIndex);
