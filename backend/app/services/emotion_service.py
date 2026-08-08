"""
情感分析服务

支持三种模式:
1. rule - 关键词规则引擎 (快速、离线)
2. ai - 调用 AI 模型分析 (准确)
3. auto - 自动选择 (短文本用 AI, 长文本用规则)
"""

from __future__ import annotations

from typing import Optional

from app.config.constants import Constants
from app.models.emotion import EmotionResult
from app.services.ai_router import TaskType, Complexity, ai_router
from app.utils.logger import logger

# 情感 → Emoji 映射
EMOTION_EMOJIS = {
    "ecstatic": "😊✨🎉",
    "happy": "😊",
    "content": "🙂",
    "neutral": "😐",
    "confused": "😕",
    "sad": "😢",
    "angry": "😠",
    "embarrassed": "😳",
    "surprised": "😲",
}

# 关键词规则
POSITIVE_WORDS = [
    "开心", "高兴", "快乐", "喜欢", "棒", "好", "幸福",
    "兴奋", "美好", "爱", "感谢", "不错", "漂亮",
]
NEGATIVE_WORDS = [
    "难过", "伤心", "生气", "讨厌", "糟糕", "失望",
    "焦虑", "痛苦", "恨", "难受", "崩溃", "烦",
]
CONFUSED_WORDS = ["疑惑", "不懂", "为什么", "奇怪", "迷茫", "困惑"]
SURPRISED_WORDS = ["哇", "天哪", "真的吗", "不会吧", "震惊", "没想到"]


class EmotionService:
    """情感分析服务"""

    async def analyze(
        self, text: str, method: str = "auto"
    ) -> EmotionResult:
        """
        分析文本情感

        Args:
            text: 输入文本
            method: 分析方法 (auto/rule/ai)

        Returns:
            EmotionResult: 分析结果
        """
        if not text or not text.strip():
            return EmotionResult(emotion="neutral", confidence=0.5, emoji="😐")

        text = text[: Constants.MAX_TEXT_LENGTH_FOR_ANALYSIS]

        if method == "rule" or (method == "auto" and len(text) < 20):
            return self._analyze_with_rules(text)
        else:
            return await self._analyze_with_ai(text)

    def _analyze_with_rules(self, text: str) -> EmotionResult:
        """规则引擎情感分析"""
        text_lower = text.lower()

        scores = {
            "happy": sum(1 for w in POSITIVE_WORDS if w in text_lower),
            "sad": sum(1 for w in NEGATIVE_WORDS if w in text_lower),
            "confused": sum(1 for w in CONFUSED_WORDS if w in text_lower),
            "surprised": sum(1 for w in SURPRISED_WORDS if w in text_lower),
        }

        # 找出最高分的情感
        max_emotion = max(scores, key=scores.get)
        max_score = scores[max_emotion]

        if max_score == 0:
            return EmotionResult(
                emotion="neutral",
                confidence=0.5,
                emoji=EMOTION_EMOJIS["neutral"],
            )

        confidence = min(0.5 + max_score * 0.15, 0.95)
        return EmotionResult(
            emotion=max_emotion,
            confidence=confidence,
            emoji=EMOTION_EMOJIS.get(max_emotion, "😐"),
        )

    async def _analyze_with_ai(self, text: str) -> EmotionResult:
        """AI 驱动的情感分析"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "你是一个情感分析专家。请分析以下文本的情感，"
                        f"从以下标签中选择一个: {', '.join(Constants.EMOTION_LABELS)}。"
                        "只需返回情感标签，不要其他内容。"
                    ),
                },
                {"role": "user", "content": text},
            ]

            result = await ai_router.chat_completion(
                messages=messages,
                task_type=TaskType.EMOTION,
                complexity=Complexity.SIMPLE,
            )

            emotion = result["response"].strip().lower()

            # 验证情感标签
            if emotion in Constants.EMOTION_LABELS:
                return EmotionResult(
                    emotion=emotion,
                    confidence=0.85,
                    emoji=EMOTION_EMOJIS.get(emotion, "😐"),
                    details={"ai_model": result["model_name"]},
                )

            return EmotionResult(
                emotion="neutral",
                confidence=0.5,
                emoji=EMOTION_EMOJIS["neutral"],
            )

        except Exception as e:
            logger.warning(f"AI 情感分析失败，降级到规则引擎: {e}")
            return self._analyze_with_rules(text)


# 全局单例
emotion_service = EmotionService()
