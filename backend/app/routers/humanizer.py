"""
Humanizer: AI 写作模式检测与人性化 API

提供 AI 文本检测和人性化改写接口，基于 Wikipedia "Signs of AI writing" 指南。

## 功能

1. **AI 模式检测** (`POST /api/humanizer/analyze`) - 检测文本中的 AI 写作模式
2. **自动人性化** (`POST /api/humanizer/humanize`) - 自动改写 AI 化文本
3. **模式概览** (`GET /api/humanizer/patterns`) - 获取所有可检测模式列表
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.humanizer_service import (
    humanizer_service,
    PATTERN_NAMES,
    HumanizerResult,
)
from app.utils.logger import logger

router = APIRouter(prefix="/api/humanizer", tags=["humanizer"])


# ─── 请求/响应模型 ──────────────────────────────────────────


class HumanizerRequest(BaseModel):
    """人性化分析请求"""
    text: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="待分析/改写的文本内容",
        examples=["The new software update serves as a testament to the company's commitment to innovation."],
    )


class HumanizerResponse(BaseModel):
    """人性化分析响应"""
    original_text: str = Field(..., description="原始文本")
    humanized_text: str = Field(..., description="人性化改写后的文本")
    total_issues: int = Field(..., description="检测到的问题数量")
    score: float = Field(..., description="AI 化程度 (0.0~1.0)")
    summary: str = Field(..., description="分析摘要")
    matches: list = Field(default_factory=list, description="检测到的模式匹配详情")


class PatternInfo(BaseModel):
    """模式信息"""
    pattern_id: str = Field(..., description="模式编号")
    pattern_name: str = Field(..., description="模式名称")
    description: str = Field(..., description="模式说明")
    severity: str = Field(..., description="默认严重程度")


# ─── API 端点 ───────────────────────────────────────────────


@router.post(
    "/analyze",
    response_model=HumanizerResponse,
    summary="分析文本中的 AI 写作模式",
    description="检测文本中的 24 种 AI 写作模式，返回详细匹配结果和改进建议。",
)
async def analyze_text(req: HumanizerRequest):
    """
    分析文本中的 AI 写作模式
    
    返回详细的模式检测结果，包括：
    - 每种模式的出现位置和次数
    - AI 化程度评分 (0.0~1.0)
    - 改进建议和替换文本
    - 自动人性化改写版本
    
    ### 使用示例
    
    ```json
    {
      "text": "The software serves as a testament to innovation..."
    }
    ```
    """
    try:
        result = await humanizer_service.analyze(req.text)
        return _to_response(result)
    except Exception as e:
        logger.error(f"Humanizer 分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.post(
    "/humanize",
    response_model=HumanizerResponse,
    summary="自动人性化改写文本",
    description="检测并自动修复 AI 写作模式，返回人性化版本。",
)
async def humanize_text(req: HumanizerRequest):
    """
    自动人性化改写文本
    
    对输入文本执行以下操作：
    1. 检测所有 24 种 AI 写作模式
    2. 自动应用规则性修复
    3. 返回人性化版本和分析结果
    
    ### 使用示例
    
    ```json
    {
      "text": "Nestled within the breathtaking region... stands as a vibrant town..."
    }
    ```
    """
    try:
        result = await humanizer_service.analyze(req.text)
        return _to_response(result)
    except Exception as e:
        logger.error(f"Humanizer 改写失败: {e}")
        raise HTTPException(status_code=500, detail=f"改写失败: {str(e)}")


@router.get(
    "/patterns",
    response_model=list[PatternInfo],
    summary="获取所有可检测的 AI 写作模式列表",
    description="返回 Humanizer 能检测的所有 24 种 AI 写作模式及其说明。",
)
async def list_patterns():
    """
    获取所有可检测的 AI 写作模式
    
    返回完整的 24 种模式清单，包含编号、名称和说明，
    帮助用户了解 AI 文本的常见特征。
    """
    patterns = [
        PatternInfo(
            pattern_id="P1",
            pattern_name="过度强调重要性",
            description="LLM 写作会夸大任意事物的意义，添加其如何代表或贡献于更广泛主题的陈述。如 'marking a pivotal moment'",
            severity="high",
        ),
        PatternInfo(
            pattern_id="P2",
            pattern_name="空洞的知名度声明",
            description="LLM 反复强调知名度，通常列举来源但不提供上下文。如 'Her views have been cited in The New York Times, BBC...'",
            severity="high",
        ),
        PatternInfo(
            pattern_id="P3",
            pattern_name="-ing 表层分析",
            description="AI 在句子末尾添加 '-ing' 分词短语来伪造深度。如 '..., symbolizing the community's deep connection to the land'",
            severity="medium",
        ),
        PatternInfo(
            pattern_id="P4",
            pattern_name="促销式语言",
            description="LLM 难以保持中立语气，尤其在文化话题上。如 'Nestled within the breathtaking region...'",
            severity="high",
        ),
        PatternInfo(
            pattern_id="P5",
            pattern_name="模糊归因",
            description="AI 将观点归因于模糊权威而不提供具体来源。如 'Experts believe...', 'Industry reports...'",
            severity="high",
        ),
        PatternInfo(
            pattern_id="P6",
            pattern_name="公式化挑战段落",
            description="许多 LLM 生成的文章包含公式化的 '挑战' 部分。如 'Despite these challenges... continues to thrive'",
            severity="medium",
        ),
        PatternInfo(
            pattern_id="P7",
            pattern_name="AI 高频词汇",
            description="2023 年后文本中高频出现的词汇。如 'Additionally', 'pivotal', 'showcase', 'testament'",
            severity="low",
        ),
        PatternInfo(
            pattern_id="P8",
            pattern_name="系动词回避",
            description="LLM 用复杂结构替代简单系动词。如用 'serves as' 替代 'is'，用 'boasts' 替代 'has'",
            severity="medium",
        ),
        PatternInfo(
            pattern_id="P9",
            pattern_name="否定平行结构",
            description="过度使用 'Not only...but...' 或 'It's not just about..., it's...' 结构",
            severity="medium",
        ),
        PatternInfo(
            pattern_id="P10",
            pattern_name="三要素规则",
            description="LLM 将观点强制排列成三要素以显得全面。如 'keynote sessions, panel discussions, and networking opportunities'",
            severity="low",
        ),
        PatternInfo(
            pattern_id="P11",
            pattern_name="过度同义词替换",
            description="AI 为避免重复而过度替换同义词。如在同一段中用 protagonist/main character/central figure/hero 指代同一人",
            severity="low",
        ),
        PatternInfo(
            pattern_id="P12",
            pattern_name="虚假范围表述",
            description="LLM 使用 'from X to Y' 结构但 X 和 Y 不在有意义的尺度上",
            severity="low",
        ),
        PatternInfo(
            pattern_id="P13",
            pattern_name="长破折号过度使用",
            description="LLM 比人类更频繁使用长破折号模仿有力写作",
            severity="low",
        ),
        PatternInfo(
            pattern_id="P14",
            pattern_name="粗体滥用",
            description="AI 机械地使用粗体强调短语",
            severity="low",
        ),
        PatternInfo(
            pattern_id="P15",
            pattern_name="行内标题列表",
            description="AI 输出中项目以粗体标题加冒号开头的列表格式",
            severity="medium",
        ),
        PatternInfo(
            pattern_id="P16",
            pattern_name="标题大写 (Title Case)",
            description="AI 将所有主要单词大写作为标题",
            severity="low",
        ),
        PatternInfo(
            pattern_id="P17",
            pattern_name="表情符号滥用",
            description="AI 用表情符号装饰标题或列表项",
            severity="low",
        ),
        PatternInfo(
            pattern_id="P18",
            pattern_name="花引号",
            description="ChatGPT 使用花引号替代直引号",
            severity="low",
        ),
        PatternInfo(
            pattern_id="P19",
            pattern_name="聊天机器人痕迹",
            description="聊天机器人用语的痕迹被保留在文本中。如 'I hope this helps!', 'Let me know if...'",
            severity="high",
        ),
        PatternInfo(
            pattern_id="P20",
            pattern_name="知识截止声明",
            description="AI 关于信息不完整的免责声明被保留。如 'While specific details are limited...'",
            severity="medium",
        ),
        PatternInfo(
            pattern_id="P21",
            pattern_name="谄媚语气",
            description="过度积极、取悦他人的语言。如 'Great question!', 'You're absolutely right!'",
            severity="medium",
        ),
        PatternInfo(
            pattern_id="P22",
            pattern_name="填充短语",
            description="冗长表达替代简洁说法。如用 'Due to the fact that' 替代 'Because'",
            severity="low",
        ),
        PatternInfo(
            pattern_id="P23",
            pattern_name="过度模糊化",
            description="过度限定陈述。如 'It could potentially possibly be argued...'",
            severity="low",
        ),
        PatternInfo(
            pattern_id="P24",
            pattern_name="通用正面结论",
            description="模糊的乐观结尾。如 'The future looks bright... Exciting times lie ahead...'",
            severity="medium",
        ),
    ]
    return patterns


# ─── 辅助函数 ───────────────────────────────────────────────


def _to_response(result: HumanizerResult) -> HumanizerResponse:
    """将 HumanizerResult 转换为 HumanizerResponse"""
    matches_data = []
    for m in result.matches:
        matches_data.append({
            "pattern_id": m.pattern_id,
            "pattern_name": m.pattern_name,
            "severity": m.severity,
            "snippet": m.snippet[:100],
            "position": m.position,
            "length": m.length,
            "suggestion": m.suggestion,
        })

    return HumanizerResponse(
        original_text=result.original_text,
        humanized_text=result.humanized_text,
        total_issues=result.total_issues,
        score=round(result.score, 2),
        summary=result.summary,
        matches=matches_data,
    )
