"""
梦境记录模型 - SQLAlchemy + Pydantic
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.conversation import Base


class DreamRecord(Base):
    """梦境记录 ORM 模型"""

    __tablename__ = "dream_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    dream_text: Mapped[str] = mapped_column(Text, nullable=False)
    emotion: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    detected_symbols: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    traditional_analysis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_analysis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    analysis_type: Mapped[str] = mapped_column(String(20), default="traditional")
    dream_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


# ── Pydantic Schemas ───────────────────────────────────────

class DreamCreate(BaseModel):
    """创建梦境记录"""
    model_config = {"protected_namespaces": ()}
    dream_text: str = Field(..., min_length=1, max_length=5000)
    dream_date: Optional[str] = None
    use_ai: bool = False


class DreamResponse(BaseModel):
    """梦境响应模型"""
    model_config = {"protected_namespaces": ()}
    id: int
    user_id: int
    dream_text: str
    emotion: Optional[str] = None
    detected_symbols: list[dict] = []
    traditional_analysis: Optional[str] = None
    ai_analysis: Optional[str] = None
    analysis_type: str = "traditional"
    dream_date: str
    created_at: str

    @classmethod
    def from_orm(cls, record) -> "DreamResponse":
        import json
        symbols = []
        if record.detected_symbols:
            try:
                symbols = json.loads(record.detected_symbols)
            except (json.JSONDecodeError, TypeError):
                pass
        return cls(
            id=record.id,
            user_id=record.user_id,
            dream_text=record.dream_text,
            emotion=record.emotion,
            detected_symbols=symbols,
            traditional_analysis=record.traditional_analysis,
            ai_analysis=record.ai_analysis,
            analysis_type=record.analysis_type,
            dream_date=record.dream_date.isoformat(),
            created_at=record.created_at.isoformat(),
        )


class DreamListResponse(BaseModel):
    """梦境列表响应"""
    items: list[DreamResponse]
    total: int


class SymbolEncyclopediaItem(BaseModel):
    """符号百科条目"""
    symbol: str
    category: str
    interpretations: list[str]
    emoji: str
    related_symbols: list[str] = []


class SymbolListResponse(BaseModel):
    """符号列表响应"""
    symbols: list[SymbolEncyclopediaItem]
    categories: list[str]
    total: int
