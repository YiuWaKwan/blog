from pydantic import BaseModel


class UnlockRequest(BaseModel):
    type: str
    id: str
    password: str
