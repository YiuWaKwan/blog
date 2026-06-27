-- 为已有数据库添加收藏访问计数
ALTER TABLE bookmarks
    ADD COLUMN IF NOT EXISTS visit_count INTEGER NOT NULL DEFAULT 0;

CREATE INDEX IF NOT EXISTS idx_bookmarks_visit_count ON bookmarks(visit_count DESC);
