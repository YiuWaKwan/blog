-- Personal blog schema
-- Run: psql -U postgres -d blog -f sql/schema.sql

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Admin users
CREATE TABLE IF NOT EXISTS admin_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(64) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Blog posts
CREATE TABLE IF NOT EXISTS blog_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    excerpt TEXT,
    content TEXT NOT NULL DEFAULT '',
    cover_image_url VARCHAR(512),
    is_published BOOLEAN NOT NULL DEFAULT FALSE,
    is_private BOOLEAN NOT NULL DEFAULT FALSE,
    access_password_hash VARCHAR(255),
    reading_time_minutes SMALLINT DEFAULT 0,
    view_count INTEGER NOT NULL DEFAULT 0,
    author_id UUID REFERENCES admin_users(id) ON DELETE SET NULL,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_blog_private_password CHECK (
        is_private = FALSE OR access_password_hash IS NOT NULL
    )
);

CREATE INDEX IF NOT EXISTS idx_blog_posts_slug ON blog_posts(slug);
CREATE INDEX IF NOT EXISTS idx_blog_posts_published ON blog_posts(published_at DESC)
    WHERE is_published = TRUE;

-- Note categories
CREATE TABLE IF NOT EXISTS note_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(64) NOT NULL,
    slug VARCHAR(64) NOT NULL UNIQUE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Notes
CREATE TABLE IF NOT EXISTS notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    excerpt TEXT,
    content TEXT NOT NULL DEFAULT '',
    cover_image_url VARCHAR(512),
    is_published BOOLEAN NOT NULL DEFAULT FALSE,
    is_private BOOLEAN NOT NULL DEFAULT FALSE,
    access_password_hash VARCHAR(255),
    reading_time_minutes SMALLINT DEFAULT 0,
    view_count INTEGER NOT NULL DEFAULT 0,
    category_id UUID REFERENCES note_categories(id) ON DELETE SET NULL,
    parent_id UUID REFERENCES notes(id) ON DELETE SET NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    author_id UUID REFERENCES admin_users(id) ON DELETE SET NULL,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_note_private_password CHECK (
        is_private = FALSE OR access_password_hash IS NOT NULL
    )
);

CREATE INDEX IF NOT EXISTS idx_notes_slug ON notes(slug);
CREATE INDEX IF NOT EXISTS idx_notes_category ON notes(category_id, sort_order);

-- Bookmark categories
CREATE TABLE IF NOT EXISTS bookmark_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(64) NOT NULL,
    slug VARCHAR(64) NOT NULL UNIQUE,
    sort_order INTEGER NOT NULL DEFAULT 0
);

-- Bookmarks
CREATE TABLE IF NOT EXISTS bookmarks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    url VARCHAR(2048) NOT NULL,
    description TEXT,
    favicon_url VARCHAR(512),
    category_id UUID REFERENCES bookmark_categories(id) ON DELETE SET NULL,
    is_private BOOLEAN NOT NULL DEFAULT FALSE,
    access_password_hash VARCHAR(255),
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_bookmark_private_password CHECK (
        is_private = FALSE OR access_password_hash IS NOT NULL
    )
);

CREATE INDEX IF NOT EXISTS idx_bookmarks_category ON bookmarks(category_id, sort_order);

-- Tags
CREATE TABLE IF NOT EXISTS tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(64) NOT NULL,
    slug VARCHAR(64) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tags_slug ON tags(slug);
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);

-- Tag associations
CREATE TABLE IF NOT EXISTS blog_post_tags (
    post_id UUID NOT NULL REFERENCES blog_posts(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (post_id, tag_id)
);

CREATE INDEX IF NOT EXISTS idx_blog_post_tags_tag ON blog_post_tags(tag_id);

CREATE TABLE IF NOT EXISTS note_tags (
    note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (note_id, tag_id)
);

CREATE INDEX IF NOT EXISTS idx_note_tags_tag ON note_tags(tag_id);

CREATE TABLE IF NOT EXISTS bookmark_tags (
    bookmark_id UUID NOT NULL REFERENCES bookmarks(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (bookmark_id, tag_id)
);

CREATE INDEX IF NOT EXISTS idx_bookmark_tags_tag ON bookmark_tags(tag_id);

-- Content unlock sessions
CREATE TABLE IF NOT EXISTS content_unlocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resource_type VARCHAR(20) NOT NULL CHECK (resource_type IN ('blog_post', 'note', 'bookmark')),
    resource_id UUID NOT NULL,
    session_token VARCHAR(128) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_content_unlocks_token ON content_unlocks(session_token);
CREATE INDEX IF NOT EXISTS idx_content_unlocks_resource ON content_unlocks(resource_type, resource_id, session_token);

-- Site settings
CREATE TABLE IF NOT EXISTS site_settings (
    key VARCHAR(64) PRIMARY KEY,
    value TEXT NOT NULL DEFAULT ''
);

-- Tag statistics view
CREATE OR REPLACE VIEW v_tag_stats AS
SELECT
    t.id,
    t.name,
    t.slug,
    t.created_at,
    COUNT(DISTINCT bpt.post_id) AS blog_count,
    COUNT(DISTINCT nt.note_id) AS note_count,
    COUNT(DISTINCT bmt.bookmark_id) AS bookmark_count,
    COUNT(DISTINCT bpt.post_id)
        + COUNT(DISTINCT nt.note_id)
        + COUNT(DISTINCT bmt.bookmark_id) AS total_count
FROM tags t
LEFT JOIN blog_post_tags bpt ON bpt.tag_id = t.id
LEFT JOIN note_tags nt ON nt.tag_id = t.id
LEFT JOIN bookmark_tags bmt ON bmt.tag_id = t.id
GROUP BY t.id, t.name, t.slug, t.created_at;

-- Seed sample data for development
INSERT INTO admin_users (username, password_hash)
VALUES ('admin', '$2b$12$placeholder_hash_replace_me')
ON CONFLICT (username) DO NOTHING;

INSERT INTO tags (name, slug) VALUES
    ('Python', 'python'),
    ('FastAPI', 'fastapi'),
    ('PostgreSQL', 'postgresql'),
    ('学习笔记', 'learning')
ON CONFLICT (slug) DO NOTHING;

INSERT INTO blog_posts (title, slug, excerpt, content, is_published, is_private, reading_time_minutes, published_at)
SELECT
    'Hello World',
    'hello-world',
    '我的第一篇博客文章，欢迎阅读。',
    '# Hello World

这是一篇示例文章，用于测试博客系统。

## 特性

- Markdown 支持
- 标签分类
- 私密文章密码保护',
    TRUE,
    FALSE,
    3,
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM blog_posts WHERE slug = 'hello-world');

INSERT INTO blog_post_tags (post_id, tag_id)
SELECT p.id, t.id
FROM blog_posts p, tags t
WHERE p.slug = 'hello-world' AND t.slug IN ('python', 'fastapi')
ON CONFLICT DO NOTHING;

INSERT INTO blog_posts (title, slug, excerpt, content, is_published, is_private, access_password_hash, reading_time_minutes, published_at)
SELECT
    '私密文章示例',
    'private-post',
    '这是一篇需要密码才能阅读的私密文章。',
    '# 私密内容

输入正确密码后才能看到此内容。',
    TRUE,
    TRUE,
    '$2b$12$placeholder',
    2,
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM blog_posts WHERE slug = 'private-post');

INSERT INTO bookmark_categories (name, slug, sort_order) VALUES
    ('开发工具', 'dev-tools', 1),
    ('设计资源', 'design', 2)
ON CONFLICT (slug) DO NOTHING;
SELECT
    'FastAPI 官方文档',
    'https://fastapi.tiangolo.com',
    'FastAPI 框架官方文档',
    FALSE,
    c.id,
    1
FROM bookmark_categories c
WHERE c.slug = 'dev-tools'
  AND NOT EXISTS (SELECT 1 FROM bookmarks WHERE url = 'https://fastapi.tiangolo.com');

INSERT INTO bookmarks (title, url, description, is_private, access_password_hash, category_id, sort_order)
SELECT
    '内部工具箱',
    'https://example.com/internal-tools',
    '需要密码访问的内部链接收藏',
    TRUE,
    '$2b$12$MhioEyH0e.KZ5ZSonD28tekDiCQNJeFJEpTlFP1L1q2QXqUmf/jgy',
    c.id,
    2
FROM bookmark_categories c
WHERE c.slug = 'dev-tools'
  AND NOT EXISTS (SELECT 1 FROM bookmarks WHERE url = 'https://example.com/internal-tools');

INSERT INTO bookmark_tags (bookmark_id, tag_id)
SELECT b.id, t.id
FROM bookmarks b, tags t
WHERE b.url = 'https://fastapi.tiangolo.com' AND t.slug = 'fastapi'
ON CONFLICT DO NOTHING;
