from pydantic import BaseModel
from typing import Optional,List


class IdentityPayLoad(BaseModel):
    data: str
    identity_provider: str
    fcm_token: str = None


class AuthResponseToken(BaseModel):
    access_token: str
    refresh_token: Optional[str]
    token_type: str


class BaseUser(BaseModel):
    id: Optional[str] = None
    email: str = ""
    identity_provider: str = ""


class BaseUserWithDetail(BaseModel):
    phone: str = None
    nickname: str = None
    age:          int = None
    gender:       int = None
    corona:       bool = False
    car:          bool = False
    region:       dict = None
    mbti:         str = None
    introduction: str = None
    me:           List[str] = None
    leisure:      List[str] = None


class UserDetailIn(BaseUserWithDetail):
    pass


class UserOut(BaseUserWithDetail):
    id: Optional[str] = None
    email: str = None
    identity_provider: str = ""
    images:       List[str] = []
    is_block:     bool = None

    class Config:
        orm_mode = True


class UserImageOut:
    image_url: str


class PostUserResponse(BaseModel):

    token: AuthResponseToken
    user: UserOut

    class Config:
        orm_mode = True


class UserImageOut(BaseModel):
    image_url: str = None


class UserImageListOut(BaseModel):
    image_urls: List[str] = []