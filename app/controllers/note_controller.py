from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.core.response import error, success
from app.dependencies import get_unlocked_note_ids
from app.schemas.queries.note import NoteListQuery
from app.services.note_service import NoteService

router = APIRouter(prefix="/api", tags=["note"])


@router.post("/get_notes")
def get_notes(body: NoteListQuery) -> dict[str, Any]:
    data = NoteService().list_notes(body)
    return success(data.model_dump())


@router.get("/get_note")
def get_note(
    slug: str,
    unlocked_ids: set[str] = Depends(get_unlocked_note_ids),
) -> dict[str, Any]:
    result = NoteService().get_note_by_slug(slug, unlocked_ids=unlocked_ids)
    if result.requires_unlock:
        return error(
            403,
            "需要密码解锁",
            data={"requires_unlock": True, "id": str(result.note_id)},
        )
    if not result.detail:
        raise HTTPException(status_code=404, detail="笔记不存在")
    return success(result.detail.model_dump())
