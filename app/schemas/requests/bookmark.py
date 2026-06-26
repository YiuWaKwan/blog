from pydantic import BaseModel


class AddBookmarkRequest(BaseModel):
    url: str
