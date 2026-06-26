"""Landing page — 高级入口页 (/)。"""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import Response

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))

router = APIRouter(tags=["landing"])


@router.get("/")
def landing(request: Request) -> Response:
    return templates.TemplateResponse(request, "landing.html")
