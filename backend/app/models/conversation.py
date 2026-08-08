"""
对话模型 - SQLAlchemy + Pydantic
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Conversation(Base):
    """对话记录 ORM 模型"""

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user_input: Mapped[str] = mapped_column(Text, nullable=False)
    assistant_response: Mapped[str] = mapped_column(Text, nullable=False)
    intent: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    emotion: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    model_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )

    # 关系
    user = relationship("User", back_populates="conversations")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_input": self.user_input,
            "assistant_response": self.assistant_response,
            "intent": self.intent,
            "emotion": self.emotion,
            "model_name": self.model_name,
            "tokens_used": self.tokens_used,
            "created_at": self.created_at.isoformat(),
        }


# ── Pydantic Schemas ───────────────────────────────────────


class ConversationCreate(BaseModel):
    """创建对话的请求模型"""
    model_config = {"protected_namespaces": ()}
    user_input: str
    assistant_response: str = ""
    intent: Optional[str] = None
    emotion: Optional[str] = None
    model_name: Optional[str] = None
    tokens_used: Optional[int] = None


class ConversationResponse(BaseModel):
    """对话响应模型"""
    model_config = {"protected_namespaces": ()}
    id: int
    user_id: int
    user_input: str
    assistant_response: str
    intent: Optional[str] = None
    emotion: Optional[str] = None
    model_name: Optional[str] = None
    tokens_used: Optional[int] = None
    created_at: str

    @classmethod
    def from_orm(cls, conv: Conversation) -> "ConversationResponse":
        return cls(
            id=conv.id,
            user_id=conv.user_id,
            user_input=conv.user_input,
            assistant_response=conv.assistant_response,
            intent=conv.intent,
            emotion=conv.emotion,
            model_name=conv.model_name,
            tokens_used=conv.tokens_used,
            created_at=conv.created_at.isoformat(),
        )


class ConversationList(BaseModel):
    """对话列表响应"""
    items: list[ConversationResponse]
    total: int
