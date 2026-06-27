"""URL 解析工具。"""

from urllib.parse import urlparse


def extract_domain_from_url(url: str) -> str:
    """从 URL 提取主域名（hostname，去掉 www 与端口）。"""
    cleaned = url.strip()
    if not cleaned:
        return cleaned

    parse_target = cleaned if "://" in cleaned else f"https://{cleaned}"
    parsed = urlparse(parse_target)
    host = parsed.netloc or parsed.path.split("/")[0]

    if ":" in host:
        host = host.rsplit(":", 1)[0]

    host = host.lower()
    if host.startswith("www."):
        host = host[4:]

    return host or cleaned
