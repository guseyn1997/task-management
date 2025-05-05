from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, constr
from datetime import datetime

# Общие атрибуты
class UserBase(BaseModel):
    email: EmailStr
    password: constr(min_length=8, regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")
    username: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

# Свойства для создания пользователя
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

# Свойства для обновления пользователя
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

# Свойства модели, возвращаемые API
class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Свойства для логина
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Токен доступа
class Token(BaseModel):
    access_token: str
    token_type: str

# Данные токена
class TokenPayload(BaseModel):
    sub: int
    exp: int
