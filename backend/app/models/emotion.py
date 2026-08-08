"""
情感分析结果模型
"""

from typing import Optional

from pydantic import BaseModel


class EmotionResult(BaseModel):
    """情感分析结果"""
    emotion: str = "neutral"
    confidence: float = 0.0
    emoji: str = "😐"
    details: Optional[dict] = None


class EmotionAnalysisRequest(BaseModel):
    """情感分析请求"""
    text: str
    method: str = "auto"  # "auto" | "rule" | "ai"


class BatchEmotionRequest(BaseModel):
    """批量情感分析请求"""
    texts: list[str]
    method: str = "auto"
