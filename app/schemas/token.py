from pydantic import BaseModel
import uuid

class Token(BaseModel):
    """
    Response model for successful authentication.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """
    Data payload for a JWT, stored in the 'sub' claim.
    """
    user_id: uuid.UUID | None = None
