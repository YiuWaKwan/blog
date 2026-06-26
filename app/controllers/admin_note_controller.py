from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.core.response import error, success
from app.schemas.queries.admin import AdminNoteListQuery
from app.schemas.requests.admin_note import DeleteNoteRequest, SaveNoteRequest
from app.services.note_service import NoteService

router = APIRouter(prefix="/api/admin", tags=["admin-note"])


@router.post("/get_notes")
def admin_get_notes(body: AdminNoteListQuery) -> dict[str, Any]:
    data = NoteService().list_notes_for_admin(body)
    return success(data.model_dump())


@router.get("/get_note")
def admin_get_note(id: UUID) -> dict[str, Any]:
    data = NoteService().get_note_for_admin(id)
    if not data:
        raise HTTPException(status_code=404, detail="笔记不存在")
    return success(data.model_dump())


@router.post("/save_note")
def save_note(body: SaveNoteRequest) -> dict[str, Any]:
    try:
        note_id = NoteService().save_note(body)
    except ValueError as exc:
        return error(400, str(exc))
    return success({"id": str(note_id)})


@router.post("/delete_note")
def delete_note(body: DeleteNoteRequest) -> dict[str, Any]:
    try:
        NoteService().delete_note(body.id)
    except ValueError as exc:
        return error(404, str(exc))
    return success()
