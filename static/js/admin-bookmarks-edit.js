/**
 * 后台收藏编辑 — 含私密密码
 */

function getBookmarkIdFromUrl() {
  return new URLSearchParams(window.location.search).get('id');
}

function setPasswordGroupVisible(visible) {
  const group = document.getElementById('password-group');
  if (group) group.style.display = visible ? 'block' : 'none';
}

async function loadCategories(selectEl, selectedId) {
  if (!selectEl) return;
  const res = await adminGet('get_bookmark_categories');
  const categories = res.code === 0 ? (res.data?.list || []) : [];
  const selected = selectedId ? String(selectedId) : '';
  selectEl.innerHTML = '<option value="">无分组</option>' + categories.map((c) =>
    `<option value="${c.id}"${String(c.id) === selected ? ' selected' : ''}>${c.name}</option>`
  ).join('');
}

async function initTagInput(wrapperEl, initialTags) {
  return new TagInput(wrapperEl, {
    initialTags: initialTags || [],
    onSearch: async (q) => {
      const res = await adminGet('get_tags', { q });
      return res.code === 0 ? (res.data?.list || []) : [];
    },
  });
}

async function fillBookmarkForm(bookmark) {
  const form = document.getElementById('bookmark-form');
  if (!form || !bookmark) return;

  form.querySelector('[name="id"]').value = bookmark.id;
  form.querySelector('[name="url"]').value = bookmark.url || '';
  form.querySelector('[name="title"]').value = bookmark.title || '';
  form.querySelector('[name="description"]').value = bookmark.description || '';
  form.querySelector('[name="favicon_url"]').value = bookmark.favicon_url || '';

  const privateEl = form.querySelector('[name="is_private"]');
  if (privateEl) privateEl.checked = !!bookmark.is_private;
  setPasswordGroupVisible(!!bookmark.is_private);

  await loadCategories(form.querySelector('[name="category_id"]'), bookmark.category_id ? String(bookmark.category_id) : '');

  const titleEl = document.querySelector('.admin-header__title');
  if (titleEl) titleEl.textContent = '编辑收藏';

  const tagWrapper = document.querySelector('.tag-input-wrapper');
  if (tagWrapper) {
    await initTagInput(tagWrapper, bookmark.tags || []);
  }
}

async function initAdminBookmarkEdit() {
  const form = document.getElementById('bookmark-form');
  if (!form) return;

  const bookmarkId = getBookmarkIdFromUrl();

  if (bookmarkId) {
    const res = await adminGet('get_bookmark', { id: bookmarkId });
    if (res.code === 0 && res.data) {
      await fillBookmarkForm(res.data);
    } else {
      alert(res.message || '收藏加载失败');
    }
  } else {
    await loadCategories(form.querySelector('[name="category_id"]'), '');
    const tagWrapper = document.querySelector('.tag-input-wrapper');
    if (tagWrapper) await initTagInput(tagWrapper, []);
    const titleEl = document.querySelector('.admin-header__title');
    if (titleEl) titleEl.textContent = '新建收藏';
  }

  form.querySelector('[name="is_private"]')?.addEventListener('change', (e) => {
    setPasswordGroupVisible(e.target.checked);
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    let tagIds = [];
    try {
      tagIds = JSON.parse(form.querySelector('[name="tag_ids"]')?.value || '[]');
    } catch (_) { /* ignore */ }

    const categoryId = fd.get('category_id');
    const title = (fd.get('title') || '').trim();
    const body = {
      id: fd.get('id') || undefined,
      url: fd.get('url'),
      title: title || null,
      description: fd.get('description') || null,
      favicon_url: fd.get('favicon_url') || null,
      is_private: form.querySelector('[name="is_private"]')?.checked || false,
      category_id: categoryId || null,
      tag_ids: tagIds,
    };

    const password = fd.get('access_password');
    if (password) body.access_password = password;

    const res = await adminPost('save_bookmark', body);
    if (res.code === 0) {
      window.location.href = '/pages/admin/bookmarks-list';
      return;
    }
    alert(res.message || '保存失败');
  });
}

document.addEventListener('DOMContentLoaded', initAdminBookmarkEdit);
