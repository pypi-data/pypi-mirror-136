import datetime as _dt

import pydantic as _pydantic
from pydantic import Field
from uuid import UUID
from typing import List, Optional


class AuthToken(_pydantic.BaseModel):
    id: str
    user_id: str
    token: str

class _UserBase(_pydantic.BaseModel):
    email: str

class UserUpdate(_UserBase):
    first_name: str
    last_name: str
    phone_number: str
    organization: str

class UserPasswordUpdate(_pydantic.BaseModel):
    password: str

class UserTokenVerification(_pydantic.BaseModel):
    email: str
    redirect_url: str
class UserCodeVerification(_pydantic.BaseModel):
    email: str
    code_length: Optional[int] = Field(None, title="This is the length of the verification code, which is 6 by default", example=5)

class UserCreate(_UserBase):
    password: str
    first_name: str
    last_name: str
    verification_method: str = Field(..., title="The user verification method you prefer, this is either: token or code", example="code")
    verification_redirect_url: Optional[str] = Field(None, title="This is the redirect url if you are chosing token verification method", example="https://bigfastapi.com/verify")
    verification_code_length: Optional[int] = Field(None, title="This is the length of the verification code, which is 6 by default", example=5)

    class Config:
        orm_mode = True

class UserOrgLogin(_UserBase):
    password: str
    organization: str
    
class UserLogin(_UserBase):
    password: str


class User(_UserBase):
    id: str
    first_name: str
    last_name: str
    phone_number: str
    is_active: bool
    is_verified: bool
    is_superuser: bool
    organization: str

    class Config:
        orm_mode = True




