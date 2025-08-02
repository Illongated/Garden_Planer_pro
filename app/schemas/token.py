from pydantic import BaseModel
import uuid

class Token(BaseModel):
    """
    Response model for successful authentication.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    """
    Data payload (the 'sub' claim) for a JWT.
    """
    sub: uuid.UUID
