from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.controllers import (
    admin_bookmark_controller,
    admin_note_controller,
    admin_post_controller,
    admin_tag_controller,
    bookmark_controller,
    landing_controller,
    note_controller,
    page_controller,
    post_controller,
    search_controller,
    tag_controller,
    unlock_controller,
    bookmarks_page_auth_controller,
)
from app.core.config import settings
from app.core.database_service import db_service
from app.core.scheduler import shutdown_scheduler, start_scheduler

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """应用启动时初始化 DatabaseService 连接池（长连接）。"""
    _ = db_service.engine
    start_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": exc.detail, "data": None},
    )


@app.exception_handler(OperationalError)
async def db_connection_error(_request: Request, _exc: OperationalError) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"code": 503, "message": "数据库未连接，请启动 PostgreSQL", "data": None},
    )


@app.exception_handler(SQLAlchemyError)
async def db_error(_request: Request, _exc: SQLAlchemyError) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "数据库错误", "data": None},
    )

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.include_router(landing_controller.router)
app.include_router(page_controller.router)
app.include_router(post_controller.router)
app.include_router(note_controller.router)
app.include_router(search_controller.router)
app.include_router(bookmark_controller.router)
app.include_router(tag_controller.router)
app.include_router(unlock_controller.router)
app.include_router(bookmarks_page_auth_controller.router)
app.include_router(admin_post_controller.router)
app.include_router(admin_note_controller.router)
app.include_router(admin_bookmark_controller.router)
app.include_router(admin_tag_controller.router)
