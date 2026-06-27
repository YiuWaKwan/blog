"""HTML 解析工具。"""

import re
from html import unescape


_TITLE_RE = re.compile(
    r"<title[^>]*>(.*?)</title>",
    re.IGNORECASE | re.DOTALL,
)


def extract_page_title(html: str, *, max_length: int = 255) -> str | None:
    match = _TITLE_RE.search(html[:100_000])
    if not match:
        return None

    title = unescape(match.group(1))
    title = re.sub(r"\s+", " ", title).strip()
    if not title:
        return None

    return title[:max_length]
