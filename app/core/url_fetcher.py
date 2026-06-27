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


def fetch_with_curl_cffi(
    url: str,
    *,
    timeout: float,
    proxy: str | None = None,
    impersonate: str = "chrome120",
) -> FetchResult:
    target = normalize_url(url)
    try:
        from curl_cffi import requests as cffi_requests
    except ImportError:
        return FetchResult(
            FetchOutcome.BLOCKED,
            strategy="curl_cffi",
            detail="curl_cffi not installed",
        )

    proxies = None
    if proxy:
        proxies = {"http": proxy, "https": proxy}

    try:
        response = cffi_requests.get(
            target,
            impersonate=impersonate,
            timeout=timeout,
            allow_redirects=True,
            proxies=proxies,
        )
    except Exception as exc:  # noqa: BLE001
        if is_ssl_block_error(exc):
            return FetchResult(
                FetchOutcome.BLOCKED,
                strategy="curl_cffi",
                detail=f"tls blocked: {exc}",
            )
        return FetchResult(FetchOutcome.FAILURE, strategy="curl_cffi", detail=str(exc))

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
        strategy=f"curl_cffi:{impersonate}",
        detail=detail,
    )


def fetch_with_playwright(
    url: str,
    *,
    timeout: float,
    proxy: str | None = None,
) -> FetchResult:
    target = normalize_url(url)
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ImportError:
        return FetchResult(
            FetchOutcome.BLOCKED,
            strategy="playwright",
            detail="playwright not installed",
        )

    launch_kwargs: dict = {"headless": True}
    if proxy:
        launch_kwargs["proxy"] = {"server": proxy}

    timeout_ms = int(timeout * 1000)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(**launch_kwargs)
            try:
                page = browser.new_page(
                    user_agent=CHROME_HEADERS["User-Agent"],
                    locale="zh-CN",
                )
                response = page.goto(
                    target,
                    timeout=timeout_ms,
                    wait_until="domcontentloaded",
                )
                status = response.status if response else None
                title = page.title().strip() or None
                html = page.content()
            finally:
                browser.close()
    except PlaywrightError as exc:
        if is_ssl_block_error(exc):
            return FetchResult(
                FetchOutcome.BLOCKED,
                strategy="playwright",
                detail=f"tls blocked: {exc}",
            )
        return FetchResult(FetchOutcome.FAILURE, strategy="playwright", detail=str(exc))

    if status is None:
        return FetchResult(
            FetchOutcome.FAILURE,
            strategy="playwright",
            detail="no response",
        )

    outcome = classify_http_status(status)
    if outcome is not FetchOutcome.SUCCESS and looks_like_cloudflare_challenge(html, "cloudflare"):
        outcome = FetchOutcome.BLOCKED
        detail = "cloudflare challenge"
    else:
        detail = f"http {status}"

    if outcome is FetchOutcome.SUCCESS and not title:
        title = extract_page_title(html)

    return FetchResult(
        outcome=outcome,
        title=title,
        status_code=status,
        server="playwright",
        strategy="playwright",
        detail=detail,
    )


def fetch_url_best_effort(
    url: str,
    *,
    timeout: float,
    proxy: str | None = None,
    use_curl_cffi: bool = True,
    use_playwright: bool = False,
) -> FetchResult:
    """按优先级尝试多种抓取方式。"""
    result = fetch_with_httpx(url, timeout=timeout, proxy=proxy)
    if result.outcome is FetchOutcome.SUCCESS:
        return result

    if use_curl_cffi and result.outcome is FetchOutcome.BLOCKED:
        last_cffi = result
        for impersonate in ("chrome120", "chrome", "safari17_0"):
            cffi_result = fetch_with_curl_cffi(
                url,
                timeout=timeout,
                proxy=proxy,
                impersonate=impersonate,
            )
            if cffi_result.outcome is FetchOutcome.SUCCESS:
                return cffi_result
            last_cffi = cffi_result
        result = last_cffi

    if use_playwright and result.outcome is FetchOutcome.BLOCKED:
        return fetch_with_playwright(url, timeout=timeout, proxy=proxy)

    return result
