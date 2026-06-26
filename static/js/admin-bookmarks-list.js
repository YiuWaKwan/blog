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

async function loadBookmarksList() {
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

async function importBookmarks(text) {
  const resultEl = document.getElementById('bookmarks-import-result');
  const submitBtn = document.querySelector('#bookmarks-import-form button[type="submit"]');

  if (resultEl) {
    resultEl.hidden = true;
    resultEl.textContent = '';
    resultEl.className = 'admin-import-panel__result';
  }
  if (submitBtn) submitBtn.disabled = true;

  const res = await adminPost('import_bookmarks', { text });

  if (submitBtn) submitBtn.disabled = false;

  if (res.code !== 0) {
    if (resultEl) {
      resultEl.textContent = res.message || '导入失败';
      resultEl.classList.add('is-error');
      resultEl.hidden = false;
    }
    return;
  }

  const { imported = 0, skipped = 0, errors = [] } = res.data || {};
  let message = `成功导入 ${imported} 条`;
  if (skipped) message += `，跳过 ${skipped} 行`;
  if (errors.length) message += `，失败 ${errors.length} 条`;

  if (resultEl) {
    resultEl.textContent = message;
    resultEl.classList.add(errors.length ? 'is-error' : 'is-success');
    resultEl.hidden = false;
  }

  if (errors.length) {
    alert(errors.slice(0, 5).join('\n') + (errors.length > 5 ? `\n…共 ${errors.length} 条失败` : ''));
  }

  if (imported > 0) {
    await loadBookmarksList();
    document.getElementById('bookmarks-import-text').value = '';
  }
}

async function initAdminBookmarksList() {
  const tbody = document.getElementById('bookmarks-list-body');
  if (!tbody) return;

  await loadBookmarksList();

  tbody.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-delete-id]');
    if (btn) deleteBookmark(btn.dataset.deleteId);
  });

  const importForm = document.getElementById('bookmarks-import-form');
  importForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = document.getElementById('bookmarks-import-text')?.value || '';
    await importBookmarks(text);
  });
}

document.addEventListener('DOMContentLoaded', initAdminBookmarksList);
