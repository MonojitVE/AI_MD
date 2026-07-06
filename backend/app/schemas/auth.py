from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None

class LoginCredentials(BaseModel):
    employee_id: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class UserRegistrationRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    department: Optional[str] = None
    password: str
