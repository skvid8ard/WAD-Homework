from pydantic import BaseModel, ConfigDict, Field, field_validator, EmailStr
import uuid
import re

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., min_length=3, max_length=255)
    password: str = Field(...)

    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        """
        Проверка пароля на соответствие Best Practices:
        - Минимум 1 заглавная буква
        - Минимум 1 строчная буква
        - Минимум 1 цифра
        - Минимум 1 спецсимвол
        """
        if len(v) < 8:
            raise ValueError('Пароль должен быть не менее 8 символов')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        if not re.search(r'[a-z]', v):
            raise ValueError('Пароль должен содержать хотя бы одну строчную букву')
        if not re.search(r'[0-9]', v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Пароль должен содержать хотя бы один спецсимвол')
        return v

# Схема для ответа при регистрации и входе (без пароля)
class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)

class VerifyEmailRequest(BaseModel):
    email_or_username: str
    verification_code: str = Field(..., min_length=6, max_length=6)

class ResendCodeRequest(BaseModel):
    email_or_username: str