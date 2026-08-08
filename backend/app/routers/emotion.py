"""
情感分析 API 路由
"""

from fastapi import APIRouter, HTTPException

from app.models.emotion import EmotionResult, EmotionAnalysisRequest
from app.services.emotion_service import emotion_service
from app.utils.logger import logger

router = APIRouter(prefix="/api/emotion", tags=["emotion"])


@router.post("/analyze", response_model=EmotionResult)
async def analyze_emotion(req: EmotionAnalysisRequest):
    """分析文本情感"""
    try:
        result = await emotion_service.analyze(req.text, req.method)
        return result
    except Exception as e:
        logger.error(f"情感分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
