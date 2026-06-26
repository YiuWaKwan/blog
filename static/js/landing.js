const WEEKDAYS = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];

function pad(n) {
  return String(n).padStart(2, '0');
}

function updateClock() {
  const now = new Date();
  const timeEl = document.getElementById('clock-time');
  const dateEl = document.getElementById('clock-date');
  const weekEl = document.getElementById('clock-week');

  if (timeEl) {
    timeEl.textContent = `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
  }
  if (dateEl) {
    dateEl.textContent = `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`;
  }
  if (weekEl) {
    weekEl.textContent = WEEKDAYS[now.getDay()];
  }
}

document.addEventListener('DOMContentLoaded', () => {
  updateClock();
  setInterval(updateClock, 1000);

  Promise.all([
    apiPost('/api/get_posts', { page: 1, limit: 1 }),
    apiPost('/api/get_notes', { page: 1, limit: 1 }),
    apiGet('/api/get_tags'),
  ]).then(([postsRes, notesRes, tagsRes]) => {
    if (postsRes.code === 0 && postsRes.data?.total != null) {
      document.querySelector('[data-stat="posts"]').textContent = postsRes.data.total;
    }
    if (notesRes.code === 0 && notesRes.data?.total != null) {
      document.querySelector('[data-stat="notes"]').textContent = notesRes.data.total;
    }
    if (tagsRes.code === 0 && tagsRes.data?.list) {
      document.querySelector('[data-stat="tags"]').textContent = tagsRes.data.list.length;
    }
  }).catch(() => {});
});
