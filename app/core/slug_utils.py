import re
import unicodedata
from uuid import uuid4


def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    if slug:
        return slug
    return f"item-{uuid4().hex[:8]}"
