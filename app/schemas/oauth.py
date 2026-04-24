from pydantic import BaseModel, EmailStr

class OAuthUserData(BaseModel):
    provider: str
    account_id: str
    email: EmailStr

class OAuthLoginRequest(BaseModel):
    code: str