"""页面路由 — 渲染 HTML 模板。"""

from pathlib import Path

from fastapi import APIRouter, Cookie, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import Response

from app.core.bookmarks_page_auth import (
    BOOKMARKS_PAGE_COOKIE_NAME,
    verify_auth_cookie,
)

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))

router = APIRouter(prefix="/pages", tags=["pages"])


@router.get("/")
def home(request: Request) -> Response:
    return templates.TemplateResponse(request, "index.html")


@router.get("/blog/list")
def blog_list(request: Request) -> Response:
    return templates.TemplateResponse(request, "blog/list.html")


@router.get("/blog/detail")
def blog_detail(request: Request) -> Response:
    return templates.TemplateResponse(request, "blog/detail.html")


@router.get("/notes/list")
def notes_list(request: Request) -> Response:
    return templates.TemplateResponse(request, "notes/list.html")


@router.get("/notes/detail")
def notes_detail(request: Request) -> Response:
    return templates.TemplateResponse(request, "notes/detail.html")


@router.get("/bookmarks")
def bookmarks(
    request: Request,
    bookmarks_page_auth: str | None = Cookie(
        default=None,
        alias=BOOKMARKS_PAGE_COOKIE_NAME,
    ),
) -> Response:
    if not verify_auth_cookie(bookmarks_page_auth):
        return templates.TemplateResponse(request, "bookmarks-unlock.html")
    return templates.TemplateResponse(request, "bookmarks.html")


@router.get("/tags/")
def tags_index(request: Request) -> Response:
    return templates.TemplateResponse(request, "tags/index.html")


@router.get("/tags/detail")
def tags_detail(request: Request) -> Response:
    return templates.TemplateResponse(request, "tags/detail.html")


@router.get("/search")
def search_page(request: Request) -> Response:
    return templates.TemplateResponse(request, "search.html")


@router.get("/unlock")
def unlock_page(request: Request) -> Response:
    return templates.TemplateResponse(request, "unlock.html")


@router.get("/admin/login")
def admin_login(request: Request) -> Response:
    return templates.TemplateResponse(request, "admin/login.html")


@router.get("/admin/dashboard")
def admin_dashboard(request: Request) -> Response:
    return templates.TemplateResponse(request, "admin/dashboard.html")


@router.get("/admin/blog-list")
def admin_blog_list(request: Request) -> Response:
    return templates.TemplateResponse(request, "admin/blog-list.html")


@router.get("/admin/blog-edit")
def admin_blog_edit(request: Request) -> Response:
    return templates.TemplateResponse(request, "admin/blog-edit.html")


@router.get("/admin/notes-list")
def admin_notes_list(request: Request) -> Response:
    return templates.TemplateResponse(request, "admin/notes-list.html")


@router.get("/admin/notes-edit")
def admin_notes_edit(request: Request) -> Response:
    return templates.TemplateResponse(request, "admin/notes-edit.html")


@router.get("/admin/bookmarks-list")
def admin_bookmarks_list(request: Request) -> Response:
    return templates.TemplateResponse(request, "admin/bookmarks-list.html")


@router.get("/admin/bookmarks-edit")
def admin_bookmarks_edit(request: Request) -> Response:
    return templates.TemplateResponse(request, "admin/bookmarks-edit.html")


@router.get("/admin/tags-list")
def admin_tags_list(request: Request) -> Response:
    return templates.TemplateResponse(request, "admin/tags-list.html")
