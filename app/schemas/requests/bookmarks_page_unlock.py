from pydantic import BaseModel


class BookmarksPageUnlockRequest(BaseModel):
    password: str
