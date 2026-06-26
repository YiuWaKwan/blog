from app.schemas.requests.admin_bookmark import DeleteBookmarkRequest
from app.schemas.requests.admin_note import DeleteNoteRequest
from app.schemas.requests.admin_post import DeletePostRequest, SavePostRequest
from app.schemas.requests.admin_tag import DeleteTagRequest, SaveTagRequest
from app.schemas.requests.unlock import UnlockRequest

__all__ = [
    "DeleteBookmarkRequest",
    "DeleteNoteRequest",
    "DeletePostRequest",
    "DeleteTagRequest",
    "SavePostRequest",
    "SaveTagRequest",
    "UnlockRequest",
]
