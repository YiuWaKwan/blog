from typing import Any

from fastapi import APIRouter, Depends

from app.core.response import error, success
from app.schemas.queries.search import SearchQuery
from app.services.search_service import SearchService

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search")
def search(query: SearchQuery = Depends()) -> dict[str, Any]:
    q = query.q.strip()
    if not q:
        return error(400, "请输入搜索关键词")

    items = SearchService().search(q, query.limit)
    return success({"list": [item.model_dump() for item in items], "q": q})
