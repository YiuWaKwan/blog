-- 为未分组的收藏创建默认分组
INSERT INTO bookmark_categories (name, slug, sort_order)
VALUES ('默认', 'default', 0)
ON CONFLICT (slug) DO NOTHING;

UPDATE bookmarks
SET category_id = (
    SELECT id FROM bookmark_categories WHERE slug = 'default' LIMIT 1
)
WHERE category_id IS NULL
  AND deleted_at IS NULL;
