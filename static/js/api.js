/**
 * API 封装 — 约定：参数 ≤2 且较短用 GET，否则用 POST + JSON body
 */

const API_BASE = '';

async function parseResponse(res) {
  const contentType = res.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return res.json();
  }
  return {
    code: res.status,
    message: res.status === 503 ? '数据库未连接' : `请求失败 (${res.status})`,
    data: null,
  };
}

async function apiGet(path, params = {}) {
  const url = new URL(API_BASE + path, window.location.origin);
  Object.entries(params).forEach(([k, v]) => {
    if (v !== null && v !== undefined && v !== '') {
      url.searchParams.set(k, v);
    }
  });
  try {
    const res = await fetch(url);
    return parseResponse(res);
  } catch {
    return { code: -1, message: '网络错误', data: null };
  }
}

async function apiPost(path, body = {}) {
  try {
    const res = await fetch(API_BASE + path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    return parseResponse(res);
  } catch {
    return { code: -1, message: '网络错误', data: null };
  }
}

/** 示例：加载博客列表 */
async function loadPosts(tag, page = 1) {
  const result = await apiPost('/api/get_posts', { tag, page, limit: 10 });
  if (result.code !== 0) {
    console.error(result.message);
    return null;
  }
  return result.data;
}

/** 示例：加载博客详情 */
async function loadPost(slug) {
  const result = await apiGet('/api/get_post', { slug });
  if (result.code === 403 && result.data?.requires_unlock) {
    window.location.href = `/pages/unlock?type=blog_post&id=${result.data.id}`;
    return null;
  }
  if (result.code !== 0) {
    console.error(result.message);
    return null;
  }
  return result.data;
}
