-- 收藏软删除与 URL 健康检查
ALTER TABLE bookmarks
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

ALTER TABLE bookmarks
    ADD COLUMN IF NOT EXISTS url_check_fail_days INTEGER NOT NULL DEFAULT 0;

ALTER TABLE bookmarks
    ADD COLUMN IF NOT EXISTS last_url_check_at TIMESTAMPTZ;

CREATE INDEX IF NOT EXISTS idx_bookmarks_not_deleted
    ON bookmarks(deleted_at)
    WHERE deleted_at IS NULL;
