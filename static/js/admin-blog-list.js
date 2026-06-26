/**
 * 后台博客列表 — 动态加载
 */

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str ?? '';
  return div.innerHTML;
}

function formatDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' });
}

function renderStatus(post) {
  if (post.is_private) {
    return '<span class="badge badge--private">私密</span>';
  }
  return post.is_published ? '已发布' : '草稿';
}

function renderTags(tags) {
  if (!tags?.length) return '—';
  return tags.map((t) => `<span class="tag-pill">${escapeHtml(t.name)}</span>`).join(' ');
}

function renderRow(post) {
  return `
    <tr data-id="${post.id}">
      <td>${escapeHtml(post.title)}</td>
      <td>${renderTags(post.tags)}</td>
      <td>${renderStatus(post)}</td>
      <td>${formatDate(post.published_at || post.updated_at)}</td>
      <td class="admin-table__actions">
        <a href="/pages/admin/blog-edit?id=${encodeURIComponent(post.id)}">编辑</a>
        <button type="button" class="danger" data-delete-id="${post.id}">删除</button>
      </td>
    </tr>
  `;
}

async function deletePost(id) {
  if (!confirm('确定删除这篇文章？')) return;
  const res = await adminPost('delete_post', { id });
  if (res.code === 0) {
    document.querySelector(`tr[data-id="${id}"]`)?.remove();
    return;
  }
  alert(res.message || '删除失败');
}

async function initAdminBlogList() {
  const tbody = document.getElementById('blog-list-body');
  if (!tbody) return;

  const res = await adminPost('get_posts', { page: 1, limit: 50 });
  if (res.code !== 0) {
    tbody.innerHTML = `<tr><td colspan="5">${escapeHtml(res.message || '加载失败')}</td></tr>`;
    return;
  }

  const posts = res.data?.list || [];
  tbody.innerHTML = posts.length
    ? posts.map(renderRow).join('')
    : '<tr><td colspan="5">暂无文章</td></tr>';

  tbody.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-delete-id]');
    if (btn) deletePost(btn.dataset.deleteId);
  });
}

document.addEventListener('DOMContentLoaded', initAdminBlogList);
