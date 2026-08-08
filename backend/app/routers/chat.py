"""
聊天 API 路由（支持用户隔离）

提供智能对话功能，包括：
- 消息发送和接收
- 历史对话管理
- SSE 流式响应
- 情感分析集成
- 多模型智能路由
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.models.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationList,
)
from app.models.user import User
from app.services.ai_router import TaskType, Complexity, ai_router
from app.services.database import (
    save_conversation,
    get_conversations,
    delete_conversation,
    clear_conversations,
)
from app.services.emotion_service import emotion_service
from app.self_improving import get_manager
from app.dependencies.auth import get_current_user
from app.utils.logger import logger

router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
    responses={
        401: {"description": "未授权 - 请提供有效的认证Token"},
        500: {"description": "服务器内部错误"},
    },
)


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(
        ...,
        description="用户消息内容",
        min_length=1,
        max_length=10000,
        examples=["你好，陈筱雪！"]
    )
    history: list[dict] = Field(
        default=[],
        description="对话历史记录（OpenAI格式）",
        examples=[[
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好呀！"}
        ]]
    )
    model: Optional[str] = Field(
        default=None,
        description="指定AI模型名称（可选，默认自动路由）",
        examples=["deepseek-chat", "gpt-4o"]
    )
    stream: bool = Field(
        default=False,
        description="是否启用SSE流式响应"
    )
    temperature: float = Field(
        default=0.7,
        description="温度参数（0-2），控制回复的随机性",
        ge=0,
        le=2
    )
    use_collaboration: bool = Field(
        default=False,
        description="是否启用多模型协作模式（适合复杂问题）"
    )


class ChatResponse(BaseModel):
    """聊天响应模型"""
    model_config = {"protected_namespaces": ()}
    
    response: str = Field(..., description="AI助手的回复内容")
    model_name: str = Field(..., description="使用的模型名称")
    provider: str = Field(..., description="模型提供方")
    emotion: str = Field(..., description="情感分析结果")
    usage: dict = Field(..., description="Token使用统计")
    latency_ms: float = Field(..., description="响应延迟（毫秒）")
    collaboration_used: Optional[bool] = Field(
        default=False,
        description="是否使用了多模型协作"
    )


@router.post("/send", response_model=ChatResponse)
async def send_message(
    req: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """发送消息并获取 AI 回复"""
    try:
        # 1. 自我改进：检测学习信号
        si_manager = get_manager()
        learning_signal = si_manager.detect_learning_signal(req.message)
        
        if learning_signal:
            logger.info(f"检测到学习信号: {learning_signal['type']} - {learning_signal['matched_text']}")
            
            if learning_signal['type'] == 'correction':
                # 记录纠正
                si_manager.log_correction(
                    correction_text=req.message,
                    context="chat conversation",
                    correction_type="communication"
                )
            elif learning_signal['type'] == 'preference':
                # 记录偏好
                si_manager.log_preference(
                    preference_text=req.message,
                    scope="global"
                )
        
        # 2. 加载相关记忆到上下文
        memory_context = si_manager.get_memory_for_context()
        
        if memory_context.strip():
            logger.debug(f"加载记忆上下文 ({len(memory_context)} 字符)")
        
        # 3. 情感分析（带降级处理，不阻塞主流程）
        try:
            emotion_result = await emotion_service.analyze(req.message)
        except Exception:
            from app.models.emotion import EmotionResult
            emotion_result = EmotionResult(emotion="neutral", confidence=0.5, emoji="😐")
        
        # 4. 构建消息列表（注入记忆上下文）
        messages = []
        
        # 如果有记忆，添加系统提示
        if memory_context.strip():
            messages.append({
                "role": "system",
                "content": f"以下是关于用户的记忆和偏好，请在回复时参考：\n\n{memory_context}"
            })
        
        if req.history:
            messages.extend(req.history)
        messages.append({"role": "user", "content": req.message})
        
        # 5. 调用 AI 路由（支持提供方名或模型名）
        preferred = req.model
        if preferred:
            # 解析模型名 → 提供方名（避免将模型名误传给 preferred_provider）
            resolved = ai_router.resolve_provider(preferred)
            if resolved != preferred:
                logger.debug(f"模型名 '{preferred}' 解析为提供方 '{resolved}'")
        result = await ai_router.chat_completion(
            messages=messages,
            task_type=TaskType.CHAT,
            complexity=Complexity.MEDIUM if len(req.message) > 100 else Complexity.SIMPLE,
            preferred_provider=resolved if preferred else None,
            stream=False,
        )
        
        # 6. 保存到数据库（关联当前用户）
        conv = ConversationCreate(
            user_input=req.message,
            assistant_response=result["response"],
            emotion=emotion_result.emotion,
            model_name=result["model_name"],
            tokens_used=result["usage"].get("total_tokens", 0),
        )
        await save_conversation(conv, user_id=current_user.id)
        
        return ChatResponse(
            response=result["response"],
            model_name=result["model_name"],
            provider=result["provider"],
            emotion=emotion_result.emotion,
            usage=result["usage"],
            latency_ms=result["latency_ms"],
        )
        
    except Exception as e:
        logger.error(f"聊天请求失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=ConversationList)
async def get_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的聊天历史"""
    items, total = await get_conversations(
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    return ConversationList(
        items=[ConversationResponse.from_orm(item) for item in items],
        total=total,
    )


@router.delete("/history/{conv_id}")
async def delete_message(
    conv_id: int,
    current_user: User = Depends(get_current_user)
):
    """删除指定对话（验证用户权限）"""
    success = await delete_conversation(conv_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="对话记录不存在或无权删除")
    return {"message": "删除成功"}


@router.delete("/history")
async def clear_all_history(current_user: User = Depends(get_current_user)):
    """清空当前用户的所有对话历史"""
    count = await clear_conversations(user_id=current_user.id)
    return {"message": f"已清空 {count} 条对话记录"}
