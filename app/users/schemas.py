from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: int
    email: EmailStr

    model_config = {
        "from_attributes":True
    }

class Token(BaseModel):
    access_token: str
    token_type: str
