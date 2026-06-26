/**
 * 后台博客编辑 — 按 URL id 加载并回显（含私密状态）
 */

function getPostIdFromUrl() {
  return new URLSearchParams(window.location.search).get('id');
}

function setPasswordGroupVisible(visible) {
  const group = document.getElementById('password-group');
  if (group) group.style.display = visible ? 'block' : 'none';
}

async function fillBlogForm(post) {
  const form = document.getElementById('blog-form');
  if (!form || !post) return null;

  form.querySelector('[name="id"]').value = post.id;
  form.querySelector('[name="title"]').value = post.title || '';
  form.querySelector('[name="slug"]').value = post.slug || '';
  form.querySelector('[name="excerpt"]').value = post.excerpt || '';
  form.querySelector('[name="content"]').value = post.content || '';
  form.querySelector('[name="cover_image_url"]').value = post.cover_image_url || '';

  const publishedEl = form.querySelector('[name="is_published"]');
  const privateEl = form.querySelector('[name="is_private"]');
  if (publishedEl) publishedEl.checked = !!post.is_published;
  if (privateEl) privateEl.checked = !!post.is_private;

  setPasswordGroupVisible(!!post.is_private);

  const titleEl = document.querySelector('.admin-header__title');
  if (titleEl) titleEl.textContent = '编辑博客';

  const tagWrapper = document.querySelector('.tag-input-wrapper');
  if (tagWrapper) {
    tagWrapper.dataset.postId = post.id;
    return initTagInput(tagWrapper, post.id, post.tags || []);
  }
  return null;
}

async function initAdminBlogEdit() {
  const form = document.getElementById('blog-form');
  if (!form) return;

  const postId = getPostIdFromUrl();

  if (postId) {
    const res = await adminGet('get_post', { id: postId });
    if (res.code === 0 && res.data) {
      await fillBlogForm(res.data);
    } else {
      alert(res.message || '文章加载失败');
    }
  } else {
    const tagWrapper = document.querySelector('.tag-input-wrapper');
    if (tagWrapper) {
      await initTagInput(tagWrapper, null, []);
    }
    const titleEl = document.querySelector('.admin-header__title');
    if (titleEl) titleEl.textContent = '新建博客';
  }

  const privateEl = form.querySelector('[name="is_private"]');
  privateEl?.addEventListener('change', (e) => {
    setPasswordGroupVisible(e.target.checked);
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    let tagIds = [];
    try {
      tagIds = JSON.parse(form.querySelector('[name="tag_ids"]')?.value || '[]');
    } catch (_) { /* ignore */ }

    const body = {
      id: fd.get('id') || undefined,
      title: fd.get('title'),
      slug: fd.get('slug'),
      excerpt: fd.get('excerpt') || null,
      content: fd.get('content') || '',
      cover_image_url: fd.get('cover_image_url') || null,
      is_published: form.querySelector('[name="is_published"]')?.checked || false,
      is_private: form.querySelector('[name="is_private"]')?.checked || false,
      tag_ids: tagIds,
    };

    const password = fd.get('access_password');
    if (password) body.access_password = password;

    const res = await adminPost('save_post', body);
    if (res.code === 0) {
      window.location.href = '/pages/admin/blog-list';
      return;
    }
    alert(res.message || '保存失败');
  });
}

async function initTagInput(wrapperEl, postId, initialTags) {
  return new TagInput(wrapperEl, {
    initialTags: initialTags || [],
    onSearch: async (q) => {
      const res = await adminGet('get_tags', { q });
      return res.code === 0 ? (res.data?.list || []) : [];
    },
  });
}

document.addEventListener('DOMContentLoaded', initAdminBlogEdit);
