/**
 * 后台收藏列表
 */

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str ?? '';
  return div.innerHTML;
}

let cachedCategories = [];
let selectedCategoryId = '';

function renderTags(tags) {
  if (!tags?.length) return '—';
  return tags.map((t) => `<span class="tag-pill">${escapeHtml(t.name)}</span>`).join(' ');
}

function renderCategoryBadge(item) {
  if (!item.category_name) {
    return '<span class="admin-category-badge admin-category-badge--empty">未分组</span>';
  }
  return `<span class="admin-category-badge">${escapeHtml(item.category_name)}</span>`;
}

function renderRow(item) {
  const status = item.is_private
    ? '<span class="badge badge--private">私密</span>'
    : '公开';
  const url = item.url || '—';

  return `
    <tr data-id="${item.id}">
      <td class="admin-table__title">${escapeHtml(item.title)}</td>
      <td class="admin-table__url" title="${escapeHtml(url)}">${escapeHtml(url)}</td>
      <td class="admin-table__col-group">${renderCategoryBadge(item)}</td>
      <td>${status}</td>
      <td>${renderTags(item.tags)}</td>
      <td class="admin-table__actions">
        <a href="/pages/admin/bookmarks-edit?id=${encodeURIComponent(item.id)}">编辑</a>
        <button type="button" class="danger" data-delete-id="${item.id}">删除</button>
      </td>
    </tr>
  `;
}

function renderGroupTable(items) {
  if (!items.length) {
    return '<p class="admin-bookmark-group__empty">该分组暂无收藏</p>';
  }

  return `
    <div class="table-wrapper">
      <table class="admin-table">
        <thead>
          <tr><th>标题</th><th>URL</th><th class="admin-table__col-group">分组</th><th>状态</th><th>标签</th><th>操作</th></tr>
        </thead>
        <tbody>
          ${items.map(renderRow).join('')}
        </tbody>
      </table>
    </div>
  `;
}

function groupBookmarksByCategory(items, categories) {
  const groups = new Map();

  for (const category of categories) {
    groups.set(category.id, {
      id: category.id,
      name: category.name,
      slug: category.slug,
      sortOrder: category.sort_order ?? 0,
      bookmarkCount: category.bookmark_count ?? 0,
      items: [],
    });
  }

  for (const item of items) {
    const categoryId = item.category_id ? String(item.category_id) : '';
    if (categoryId && groups.has(categoryId)) {
      groups.get(categoryId).items.push(item);
      continue;
    }

    const fallbackKey = '__uncategorized__';
    if (!groups.has(fallbackKey)) {
      groups.set(fallbackKey, {
        id: fallbackKey,
        name: '未分组',
        slug: '—',
        sortOrder: 9999,
        bookmarkCount: 0,
        items: [],
      });
    }
    groups.get(fallbackKey).items.push(item);
  }

  return [...groups.values()]
    .filter((group) => group.items.length > 0)
    .sort((a, b) => a.sortOrder - b.sortOrder || a.name.localeCompare(b.name, 'zh-CN'));
}

function renderGroupedBookmarks(items, categories, containerEl) {
  if (!items.length) {
    containerEl.innerHTML = '<p class="admin-bookmark-groups__empty">暂无收藏</p>';
    return;
  }

  const groups = groupBookmarksByCategory(items, categories);
  if (!groups.length) {
    containerEl.innerHTML = '<p class="admin-bookmark-groups__empty">暂无收藏</p>';
    return;
  }

  containerEl.innerHTML = groups.map((group) => `
    <section class="admin-bookmark-group" data-category-id="${escapeHtml(String(group.id))}">
      <div class="admin-bookmark-group__header">
        <div class="admin-bookmark-group__title-wrap">
          <h2 class="admin-bookmark-group__title">${escapeHtml(group.name)}</h2>
          <span class="admin-bookmark-group__slug">${escapeHtml(group.slug)}</span>
        </div>
        <span class="admin-bookmark-group__count">${group.items.length} 条</span>
      </div>
      ${renderGroupTable(group.items)}
    </section>
  `).join('');
}

function renderCategoryFilter(categories) {
  const filterEl = document.getElementById('bookmark-category-filter');
  const pillsEl = document.getElementById('bookmark-category-filter-pills');
  if (!filterEl || !pillsEl) return;

  const totalCount = categories.reduce(
    (sum, category) => sum + (category.bookmark_count || 0),
    0,
  );

  const pills = [
    `<button type="button" class="admin-category-filter__pill${selectedCategoryId === '' ? ' is-active' : ''}" data-category-id="">全部 (${totalCount})</button>`,
    ...categories.map((category) => {
      const id = String(category.id);
      const active = selectedCategoryId === id ? ' is-active' : '';
      const count = category.bookmark_count || 0;
      return `<button type="button" class="admin-category-filter__pill${active}" data-category-id="${escapeHtml(id)}">${escapeHtml(category.name)} (${count})</button>`;
    }),
  ];

  pillsEl.innerHTML = pills.join('');
  filterEl.hidden = !categories.length;
}

async function loadBookmarksList(categoryId = selectedCategoryId) {
  const containerEl = document.getElementById('bookmarks-grouped-list');
  if (!containerEl) return;

  const params = categoryId ? { category_id: categoryId } : {};
  const res = await adminGet('get_bookmarks', params);
  if (res.code !== 0) {
    containerEl.innerHTML = `<p class="admin-bookmark-groups__empty">${escapeHtml(res.message || '加载失败')}</p>`;
    return;
  }

  const items = res.data?.list || [];
  renderGroupedBookmarks(items, cachedCategories, containerEl);
}

async function loadBookmarkCategories() {
  const listEl = document.getElementById('bookmark-categories-list');
  const res = await adminGet('get_bookmark_categories');
  if (res.code !== 0) {
    cachedCategories = [];
    if (listEl) {
      listEl.innerHTML = `<li class="admin-category-list__empty">${escapeHtml(res.message || '加载失败')}</li>`;
    }
    renderCategoryFilter([]);
    return;
  }

  cachedCategories = res.data?.list || [];

  if (listEl) {
    listEl.innerHTML = cachedCategories.length
      ? cachedCategories.map((item) => `
          <li class="admin-category-list__item">
            <div class="admin-category-list__main">
              <span class="admin-category-list__name">${escapeHtml(item.name)}</span>
              <span class="admin-category-list__slug">${escapeHtml(item.slug)}</span>
            </div>
            <span class="admin-category-list__count">${item.bookmark_count || 0} 条 URL</span>
          </li>
        `).join('')
      : '<li class="admin-category-list__empty">暂无分组</li>';
  }

  renderCategoryFilter(cachedCategories);
}

async function saveBookmarkCategory(name, slug) {
  const resultEl = document.getElementById('bookmark-category-result');
  const submitBtn = document.querySelector('#bookmark-category-form button[type="submit"]');

  if (resultEl) {
    resultEl.hidden = true;
    resultEl.textContent = '';
    resultEl.className = 'admin-import-panel__result';
  }
  if (submitBtn) submitBtn.disabled = true;

  const body = { name };
  if (slug) body.slug = slug;

  const res = await adminPost('save_bookmark_category', body);

  if (submitBtn) submitBtn.disabled = false;

  if (res.code !== 0) {
    if (resultEl) {
      resultEl.textContent = res.message || '新增失败';
      resultEl.classList.add('is-error');
      resultEl.hidden = false;
    }
    return;
  }

  if (resultEl) {
    resultEl.textContent = '分组已新增';
    resultEl.classList.add('is-success');
    resultEl.hidden = false;
  }

  document.getElementById('bookmark-category-name').value = '';
  document.getElementById('bookmark-category-slug').value = '';
  await loadBookmarkCategories();
  await loadBookmarksList();
}

async function deleteBookmark(id) {
  if (!confirm('确定删除这条收藏？')) return;
  const res = await adminPost('delete_bookmark', { id });
  if (res.code === 0) {
    await loadBookmarkCategories();
    await loadBookmarksList();
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
    await loadBookmarkCategories();
    await loadBookmarksList();
    document.getElementById('bookmarks-import-text').value = '';
  }
}

async function initAdminBookmarksList() {
  const containerEl = document.getElementById('bookmarks-grouped-list');
  if (!containerEl) return;

  await loadBookmarkCategories();
  await loadBookmarksList();

  containerEl.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-delete-id]');
    if (btn) deleteBookmark(btn.dataset.deleteId);
  });

  document.getElementById('bookmark-category-filter-pills')?.addEventListener('click', async (e) => {
    const pill = e.target.closest('.admin-category-filter__pill');
    if (!pill) return;
    selectedCategoryId = pill.dataset.categoryId || '';
    renderCategoryFilter(cachedCategories);
    await loadBookmarksList();
  });

  const importForm = document.getElementById('bookmarks-import-form');
  importForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = document.getElementById('bookmarks-import-text')?.value || '';
    await importBookmarks(text);
  });

  const categoryForm = document.getElementById('bookmark-category-form');
  categoryForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('bookmark-category-name')?.value.trim() || '';
    const slug = document.getElementById('bookmark-category-slug')?.value.trim() || '';
    if (!name) return;
    await saveBookmarkCategory(name, slug);
  });
}

document.addEventListener('DOMContentLoaded', initAdminBookmarksList);
