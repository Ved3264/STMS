from typing import Optional
from pydantic import BaseModel, EmailStr

class UserRequest(BaseModel):
    name: str  
    email: EmailStr  
    password: str  
    is_active: Optional[bool] = True 
    is_admin: Optional[bool] = False 


class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str