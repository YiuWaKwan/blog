/**
 * 后台收藏列表
 */

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str ?? '';
  return div.innerHTML;
}

function renderTags(tags) {
  if (!tags?.length) return '—';
  return tags.map((t) => `<span class="tag-pill">${escapeHtml(t.name)}</span>`).join(' ');
}

function renderRow(item) {
  const status = item.is_private
    ? '<span class="badge badge--private">私密</span>'
    : '公开';
  const url = item.url || '—';

  return `
    <tr data-id="${item.id}">
      <td>${escapeHtml(item.title)}</td>
      <td class="admin-table__url">${escapeHtml(url)}</td>
      <td>${escapeHtml(item.category_name || '—')}</td>
      <td>${status}</td>
      <td>${renderTags(item.tags)}</td>
      <td class="admin-table__actions">
        <a href="/pages/admin/bookmarks-edit?id=${encodeURIComponent(item.id)}">编辑</a>
        <button type="button" class="danger" data-delete-id="${item.id}">删除</button>
      </td>
    </tr>
  `;
}

async function deleteBookmark(id) {
  if (!confirm('确定删除这条收藏？')) return;
  const res = await adminPost('delete_bookmark', { id });
  if (res.code === 0) {
    document.querySelector(`tr[data-id="${id}"]`)?.remove();
    return;
  }
  alert(res.message || '删除失败');
}

async function initAdminBookmarksList() {
  const tbody = document.getElementById('bookmarks-list-body');
  if (!tbody) return;

  const res = await adminGet('get_bookmarks');
  if (res.code !== 0) {
    tbody.innerHTML = `<tr><td colspan="6">${escapeHtml(res.message || '加载失败')}</td></tr>`;
    return;
  }

  const items = res.data?.list || [];
  tbody.innerHTML = items.length
    ? items.map(renderRow).join('')
    : '<tr><td colspan="6">暂无收藏</td></tr>';

  tbody.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-delete-id]');
    if (btn) deleteBookmark(btn.dataset.deleteId);
  });
}

document.addEventListener('DOMContentLoaded', initAdminBookmarksList);
