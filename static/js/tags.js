/**
 * 标签筛选、TagInput 回显、统计渲染
 */

function renderTagPills(container, tags) {
  if (!container) return;
  container.innerHTML = tags.map(t =>
    `<a href="/pages/tags/detail?slug=${t.slug}" class="tag-pill">${t.name}${t.count ? `<span class="tag-pill__count">${t.count}</span>` : ''}</a>`
  ).join('');
}

function renderTagCloud(container, tags) {
  if (!container) return;
  const max = Math.max(...tags.map(t => t.total_count || 0), 1);
  container.innerHTML = tags.map(t => {
    const ratio = (t.total_count || 0) / max;
    let size = 'sm';
    if (ratio > 0.75) size = 'xl';
    else if (ratio > 0.5) size = 'lg';
    else if (ratio > 0.25) size = 'md';
    return `<a href="/pages/tags/detail?slug=${t.slug}" class="tag-cloud__item tag-cloud__item--${size}">${t.name} · ${t.total_count || 0}</a>`;
  }).join('');
}

/** TagInput 组件 — 后台编辑页标签回显 */
class TagInput {
  constructor(wrapperEl, options = {}) {
    this.wrapper = wrapperEl;
    this.chipsEl = wrapperEl.querySelector('.tag-input__chips');
    this.fieldEl = wrapperEl.querySelector('.tag-input__field');
    this.hiddenEl = wrapperEl.querySelector('[name="tag_ids"]');
    this.suggestionsEl = wrapperEl.querySelector('.tag-input__suggestions');
    this.tags = options.initialTags || [];
    this.onSearch = options.onSearch || (() => []);
    this.render();
    this.bindEvents();
  }

  render() {
    this.chipsEl.innerHTML = this.tags.map((t, i) =>
      `<span class="tag-input__chip" data-index="${i}">${t.name}<button type="button" class="tag-input__chip-remove" aria-label="移除">×</button></span>`
    ).join('');
    if (this.hiddenEl) {
      this.hiddenEl.value = JSON.stringify(this.tags.map(t => t.id));
    }
  }

  bindEvents() {
    this.chipsEl.addEventListener('click', (e) => {
      if (e.target.classList.contains('tag-input__chip-remove')) {
        const idx = parseInt(e.target.closest('.tag-input__chip').dataset.index, 10);
        this.tags.splice(idx, 1);
        this.render();
      }
    });

    let debounce;
    this.fieldEl.addEventListener('input', () => {
      clearTimeout(debounce);
      debounce = setTimeout(async () => {
        const q = this.fieldEl.value.trim();
        if (!q) { this.suggestionsEl.innerHTML = ''; return; }
        const items = await this.onSearch(q);
        this.suggestionsEl.innerHTML = items.map(t =>
          `<div class="tag-input__suggestion" data-id="${t.id}" data-name="${t.name}">${t.name}</div>`
        ).join('');
      }, 200);
    });

    this.suggestionsEl.addEventListener('click', (e) => {
      const el = e.target.closest('.tag-input__suggestion');
      if (!el) return;
      const id = el.dataset.id;
      const name = el.dataset.name;
      if (!this.tags.find(t => t.id === id)) {
        this.tags.push({ id, name });
        this.render();
      }
      this.fieldEl.value = '';
      this.suggestionsEl.innerHTML = '';
    });
  }
}

window.TagInput = TagInput;
window.renderTagPills = renderTagPills;
window.renderTagCloud = renderTagCloud;
