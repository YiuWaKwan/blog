"""内容相关通用逻辑。"""

from uuid import UUID

from app.core.security import hash_password
from app.core.slug_utils import slugify


def estimate_reading_time(content: str) -> int:
    if not content.strip():
        return 0
    return max(1, len(content) // 500)


def apply_private_password(
    *,
    is_private: bool,
    access_password: str | None,
    current_hash: str | None,
) -> str | None:
    if not is_private:
        return None
    if access_password:
        return hash_password(access_password)
    if current_hash:
        return current_hash
    raise ValueError("私密内容必须设置访问密码")


def ensure_unique_slug(
    base_slug: str,
    exists_fn,
    exclude_id: UUID | None = None,
) -> str:
    slug = slugify(base_slug) if base_slug else slugify("item")
    if not exists_fn(slug, exclude_id):
        return slug

    suffix = 2
    while exists_fn(f"{slug}-{suffix}", exclude_id):
        suffix += 1
    return f"{slug}-{suffix}"
