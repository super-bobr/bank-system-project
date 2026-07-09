from pydantic import BaseModel

class UserResponse(BaseModel):
    id: int
    name: str
    username: str

    class Config:
        from_attributes = True