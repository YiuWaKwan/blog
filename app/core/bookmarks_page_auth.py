"""收藏页整页访问鉴权（签名 Cookie）。"""

import base64
import hashlib
import hmac
import time

from app.core.config import settings

BOOKMARKS_PAGE_COOKIE_NAME = "bookmarks_page_auth"
BOOKMARKS_PAGE_MAX_AGE = 86400 * 7


def _signing_key() -> bytes | None:
    password = settings.bookmarks_page_password
    if not password:
        return None
    return password.encode()


def create_auth_cookie() -> str | None:
    key = _signing_key()
    if not key:
        return None
    exp = int(time.time()) + BOOKMARKS_PAGE_MAX_AGE
    payload = f"bookmarks:{exp}"
    sig = hmac.new(key, payload.encode(), hashlib.sha256).hexdigest()
    raw = f"{payload}:{sig}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def verify_auth_cookie(cookie_value: str | None) -> bool:
    key = _signing_key()
    if not key or not cookie_value:
        return False
    try:
        raw = base64.urlsafe_b64decode(cookie_value.encode()).decode()
        payload, sig = raw.rsplit(":", 1)
        expected = hmac.new(key, payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return False
        _, exp_str = payload.split(":", 1)
        return int(exp_str) > time.time()
    except (ValueError, TypeError):
        return False


def verify_page_password(password: str) -> bool:
    expected = settings.bookmarks_page_password
    if not expected:
        return False
    return hmac.compare_digest(password, expected)
