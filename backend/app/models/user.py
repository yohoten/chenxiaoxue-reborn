"""
用户模型 - SQLAlchemy + Pydantic
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr
from sqlalchemy import Boolean, Column, DateTime, Integer, String

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.conversation import Base  # 共享同一个 Base/registry，确保 relationship 字符串引用可解析


class User(Base):
    """用户 ORM 模型"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 关系
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "nickname": self.nickname,
            "avatar_url": self.avatar_url,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }


# ── Pydantic Schemas ───────────────────────────────────────


class UserCreate(BaseModel):
    """用户注册模型"""
    username: str
    email: Optional[EmailStr] = None
    password: str
    nickname: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "username": "xiaoxue_user",
                "email": "user@example.com",
                "password": "secure_password123",
                "nickname": "小雪花"
            }
        }


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str
    password: str


class UserResponse(BaseModel):
    """用户响应模型（不包含密码）"""
    id: int
    username: str
    email: Optional[str] = None
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: str
    last_login: Optional[str] = None

    @classmethod
    def from_orm(cls, user: User) -> "UserResponse":
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            nickname=user.nickname,
            avatar_url=user.avatar_url,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            last_login=user.last_login.isoformat() if user.last_login else None,
        )


class UserUpdate(BaseModel):
    """用户更新模型"""
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    password: Optional[str] = None


class Token(BaseModel):
    """JWT Token 响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Token 中的数据"""
    username: Optional[str] = None
    user_id: Optional[int] = None
