"""URL 抓取工具（健康检查 / 测试脚本共用）。"""

from __future__ import annotations

import ssl
from dataclasses import dataclass
from enum import Enum

import httpx

from app.core.html_utils import extract_page_title

CHROME_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}

_BLOCKED_STATUS_CODES = frozenset({401, 403, 405, 429})
_FAILURE_STATUS_CODES = frozenset({404, 410, 500, 502, 503, 504})

_CF_CHALLENGE_MARKERS = (
    "just a moment",
    "cf-browser-verification",
    "challenge-platform",
    "cloudflare",
)


class FetchOutcome(Enum):
    SUCCESS = "success"
    BLOCKED = "blocked"
    FAILURE = "failure"


@dataclass
class FetchResult:
    outcome: FetchOutcome
    title: str | None = None
    status_code: int | None = None
    server: str | None = None
    strategy: str = "httpx"
    detail: str = ""


def normalize_url(url: str) -> str:
    cleaned = url.strip()
    if not cleaned:
        return cleaned
    if "://" not in cleaned:
        return f"https://{cleaned}"
    return cleaned


def is_ssl_block_error(exc: BaseException) -> bool:
    if isinstance(exc, ssl.SSLError):
        return True
    cause = getattr(exc, "__cause__", None)
    if isinstance(cause, ssl.SSLError):
        return True
    message = str(exc).lower()
    return "ssl" in message and (
        "unexpected_eof" in message or "eof occurred" in message
    )


def looks_like_cloudflare_challenge(html: str, server: str | None) -> bool:
    if server and "cloudflare" in server.lower():
        return True
    snippet = html[:8000].lower()
    return any(marker in snippet for marker in _CF_CHALLENGE_MARKERS)


def classify_http_status(status: int) -> FetchOutcome:
    if status in _BLOCKED_STATUS_CODES:
        return FetchOutcome.BLOCKED
    if status in _FAILURE_STATUS_CODES or status >= 500:
        return FetchOutcome.FAILURE
    if status >= 400:
        return FetchOutcome.BLOCKED
    return FetchOutcome.SUCCESS


def fetch_with_httpx(
    url: str,
    *,
    timeout: float,
    proxy: str | None = None,
) -> FetchResult:
    target = normalize_url(url)
    if not target:
        return FetchResult(FetchOutcome.FAILURE, detail="empty url")

    timeout_cfg = httpx.Timeout(timeout, connect=min(10.0, timeout))
    try:
        with httpx.Client(
            timeout=timeout_cfg,
            follow_redirects=True,
            headers=CHROME_HEADERS,
            proxy=proxy or None,
        ) as client:
            response = client.get(target)
    except httpx.TimeoutException as exc:
        return FetchResult(FetchOutcome.FAILURE, strategy="httpx", detail=str(exc))
    except httpx.ConnectError as exc:
        if is_ssl_block_error(exc):
            return FetchResult(
                FetchOutcome.BLOCKED,
                strategy="httpx",
                detail=f"tls blocked: {exc}",
            )
        return FetchResult(FetchOutcome.FAILURE, strategy="httpx", detail=str(exc))
    except httpx.HTTPError as exc:
        if is_ssl_block_error(exc):
            return FetchResult(
                FetchOutcome.BLOCKED,
                strategy="httpx",
                detail=f"tls blocked: {exc}",
            )
        return FetchResult(FetchOutcome.FAILURE, strategy="httpx", detail=str(exc))

    server = response.headers.get("server")
    outcome = classify_http_status(response.status_code)
    title = None
    detail = ""
    if outcome is FetchOutcome.SUCCESS:
        title = extract_page_title(response.text)
    elif looks_like_cloudflare_challenge(response.text, server):
        outcome = FetchOutcome.BLOCKED
        detail = "cloudflare challenge"
    else:
        detail = f"http {response.status_code}"

    return FetchResult(
        outcome=outcome,
        title=title,
        status_code=response.status_code,
        server=server,
        strategy="httpx",
        detail=detail,
    )


def fetch_url_best_effort(
    url: str,
    *,
    timeout: float,
    proxy: str | None = None,
) -> FetchResult:
    return fetch_with_httpx(url, timeout=timeout, proxy=proxy)
