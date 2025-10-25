from datetime import datetime
from pydantic import BaseModel, EmailStr

# Pydantic model for user creation
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# Pydantic model for user output
class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True  # This allows Pydantic to work with ORM models

# Pydantic model for token response
class Token(BaseModel):
    access_token: str
    token_type: str

class FileUploadResponse(BaseModel):
    id: int
    filename: str
    uploaded_at: datetime
    cleaned_file_path: str  # Add cleaned file path to the response
    message: str
