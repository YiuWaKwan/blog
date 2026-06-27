#!/usr/bin/env python3
"""
收藏 URL 403 / Cloudflare 绕过测试脚本。

基础用法:
  python scripts/test_bookmark_url_bypass.py https://example.com
  python scripts/test_bookmark_url_bypass.py --all <url>

通过本地代理（常见有效，需本机 VPN/代理已开启）:
  python scripts/test_bookmark_url_bypass.py --proxy http://127.0.0.1:7890 --all <url>

真实浏览器（可过部分 Cloudflare JS 挑战，较重）:
  pip install playwright
  playwright install chromium
  python scripts/test_bookmark_url_bypass.py --playwright --proxy http://127.0.0.1:7890 <url>
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# 允许从项目根目录直接运行
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.url_fetcher import (  # noqa: E402
    CHROME_HEADERS,
    FetchOutcome,
    fetch_with_curl_cffi,
    fetch_with_httpx,
    fetch_with_playwright,
    normalize_url,
)


def print_header(url: str, proxy: str | None) -> None:
    print(f"\n{'=' * 72}")
    print(f"URL: {url}")
    if proxy:
        print(f"代理: {proxy}")
    print(f"{'=' * 72}")


def print_row(name: str, result, elapsed_ms: int) -> None:
    mark = "✓" if result.outcome is FetchOutcome.SUCCESS else "✗"
    status = result.status_code if result.status_code is not None else result.outcome.value
    title = ""
    if result.title:
        short = result.title if len(result.title) <= 60 else result.title[:60] + "..."
        title = f' title="{short}"'
    print(
        f"  {mark} [{name}] status={status} {elapsed_ms}ms "
        f"({result.detail}){title}"
    )


def run_probe(name: str, probe_fn) -> tuple:
    started = time.perf_counter()
    result = probe_fn()
    elapsed = int((time.perf_counter() - started) * 1000)
    print_row(name, result, elapsed)
    return result, elapsed


def diagnose(results) -> None:
    winners = [r for r, _ in results if r.outcome is FetchOutcome.SUCCESS]
    print()
    if winners:
        best, ms = next((r, t) for r, t in results if r.outcome is FetchOutcome.SUCCESS)
        print(f"推荐策略: {best.strategy} (HTTP {best.status_code}, {ms}ms)")
        if best.title:
            print(f"页面标题: {best.title}")
        return

    cloudflare_hits = sum(
        1 for r, _ in results
        if "cloudflare" in (r.detail or "").lower()
        or (r.server and "cloudflare" in r.server.lower())
        or r.status_code == 403
    )
    print("所有策略均未拿到 2xx。")
    if cloudflare_hits >= max(1, len(results) // 2):
        print()
        print("诊断: 这是 Cloudflare 在 IP 层拦截，换 User-Agent / curl_cffi 通常无效。")
        print("下一步建议:")
        print("  1. 本机开代理后测试:")
        print("     python scripts/test_bookmark_url_bypass.py --proxy http://127.0.0.1:7890 --all <url>")
        print("  2. 若代理下仍失败，试 Playwright:")
        print("     pip install playwright && playwright install chromium")
        print("     python scripts/test_bookmark_url_bypass.py --playwright --proxy http://127.0.0.1:7890 <url>")
        print("  3. 生产环境在 .env 配置:")
        print("     BOOKMARK_URL_CHECK_PROXY=http://127.0.0.1:7890")
        print("     BOOKMARK_URL_CHECK_USE_CURL_CFFI=true")
        print("  4. 若代理下仍全 403: 该站在服务器侧无法自动检查，但当前逻辑不会误删（记为 blocked）。")


def run_for_url(
    url: str,
    *,
    timeout: float,
    proxy: str | None,
    all_probes: bool,
    use_playwright: bool,
) -> None:
    target = normalize_url(url)
    if not target:
        print("跳过空 URL")
        return

    print_header(target, proxy)
    results = []

    results.append(run_probe(
        "httpx: Chrome",
        lambda: fetch_with_httpx(target, timeout=timeout, proxy=proxy),
    ))

    if all_probes or proxy:
        for browser in ("chrome120", "chrome", "safari17_0"):
            results.append(run_probe(
                f"curl_cffi: {browser}",
                lambda b=browser: fetch_with_curl_cffi(
                    target, timeout=timeout, proxy=proxy, impersonate=b,
                ),
            ))

    if use_playwright:
        results.append(run_probe(
            "playwright: chromium",
            lambda: fetch_with_playwright(target, timeout=timeout, proxy=proxy),
        ))

    if all_probes and not use_playwright:
        results.append(run_probe(
            "playwright: chromium (未安装则跳过)",
            lambda: fetch_with_playwright(target, timeout=timeout, proxy=proxy),
        ))

    diagnose(results)


def load_urls_from_file(path: str) -> list[str]:
    urls: list[str] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            raw = line.strip()
            if raw and not raw.startswith("#"):
                urls.append(raw)
    return urls


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="测试收藏 URL 403 / Cloudflare 绕过")
    parser.add_argument("urls", nargs="*", help="要测试的 URL")
    parser.add_argument("-f", "--file", help="从文件读取 URL，每行一个")
    parser.add_argument("-t", "--timeout", type=float, default=20.0, help="超时秒数")
    parser.add_argument(
        "--proxy",
        help="HTTP/SOCKS5 代理，如 http://127.0.0.1:7890 或 socks5://127.0.0.1:7890",
    )
    parser.add_argument("--all", action="store_true", help="运行 curl_cffi 多种指纹")
    parser.add_argument(
        "--playwright",
        action="store_true",
        help="额外用 Playwright 真实浏览器测试",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    urls = list(args.urls)
    if args.file:
        urls.extend(load_urls_from_file(args.file))
    if not urls:
        print(__doc__)
        return 1

    print("收藏 URL 403 / Cloudflare 绕过测试")
    print(f"超时: {args.timeout}s | 代理: {args.proxy or '无'}")
    print(f"UA 示例: {CHROME_HEADERS['User-Agent'][:50]}...")

    for url in urls:
        run_for_url(
            url,
            timeout=args.timeout,
            proxy=args.proxy,
            all_probes=args.all,
            use_playwright=args.playwright,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
