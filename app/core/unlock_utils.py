"""解锁 Cookie 工具。"""

UNLOCK_COOKIE_NAME = "unlock_tokens"


def parse_unlock_tokens(cookie_value: str | None) -> list[str]:
    if not cookie_value:
        return []
    return [token.strip() for token in cookie_value.split(",") if token.strip()]


def append_unlock_token(cookie_value: str | None, token: str) -> str:
    tokens = parse_unlock_tokens(cookie_value)
    if token not in tokens:
        tokens.append(token)
    return ",".join(tokens)
