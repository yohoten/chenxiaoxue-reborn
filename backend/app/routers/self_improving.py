"""
Self-Improving API 路由
提供记忆管理、统计查询等功能
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List

from app.self_improving import get_manager
from app.utils.logger import logger

router = APIRouter(prefix="/api/self-improving", tags=["self-improving"])


class MemoryStatsResponse(BaseModel):
    """记忆统计响应"""
    success: bool
    stats: dict


class MemorySearchRequest(BaseModel):
    """记忆搜索请求"""
    query: str
    tier: str = "all"  # all, hot, warm, cold


class MemorySearchResponse(BaseModel):
    """记忆搜索响应"""
    success: bool
    query: str
    count: int
    results: list[dict]


class ForgetTopicRequest(BaseModel):
    """遗忘主题请求"""
    topic: str
    confirm: bool = False


class ForgetTopicResponse(BaseModel):
    """遗忘主题响应"""
    success: bool
    topic: str
    removed: bool
    message: str


@router.get("/stats", response_model=MemoryStatsResponse)
async def get_memory_stats():
    """获取记忆系统统计信息"""
    try:
        manager = get_manager()
        stats = manager.get_stats()
        
        return MemoryStatsResponse(
            success=True,
            stats=stats
        )
    except Exception as e:
        logger.error(f"获取记忆统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=MemorySearchResponse)
async def search_memory(req: MemorySearchRequest):
    """搜索记忆内容"""
    try:
        manager = get_manager()
        results = manager.storage.search_memory(req.query)
        
        # 按层级过滤
        if req.tier != "all":
            results = [r for r in results if r["tier"].lower() == req.tier.lower()]
        
        return MemorySearchResponse(
            success=True,
            query=req.query,
            count=len(results),
            results=results
        )
    except Exception as e:
        logger.error(f"搜索记忆失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forget", response_model=ForgetTopicResponse)
async def forget_topic(req: ForgetTopicRequest):
    """遗忘指定主题的记忆"""
    try:
        if not req.confirm:
            return ForgetTopicResponse(
                success=False,
                topic=req.topic,
                removed=False,
                message="需要确认删除操作。请设置 confirm=true 以继续。"
            )
        
        manager = get_manager()
        removed = manager.forget_topic(req.topic)
        
        return ForgetTopicResponse(
            success=True,
            topic=req.topic,
            removed=removed,
            message=f"已{'删除' if removed else '未找到'}关于 '{req.topic}' 的记忆"
        )
    except Exception as e:
        logger.error(f"遗忘主题失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/heartbeat")
async def run_heartbeat():
    """手动触发心跳维护（晋升/降级记忆）"""
    try:
        manager = get_manager()
        manager.run_heartbeat()
        
        return {
            "success": True,
            "message": "心跳维护已完成"
        }
    except Exception as e:
        logger.error(f"心跳维护失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hot-memory")
async def get_hot_memory():
    """获取 HOT 层记忆内容"""
    try:
        manager = get_manager()
        memory_content = manager.storage.read_hot_memory()
        
        return {
            "success": True,
            "content": memory_content
        }
    except Exception as e:
        logger.error(f"获取 HOT 记忆失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/corrections")
async def get_corrections(limit: int = Query(50, ge=1, le=200)):
    """获取最近的纠正记录"""
    try:
        manager = get_manager()
        corrections = manager.storage.read_corrections(limit=limit)
        
        return {
            "success": True,
            "corrections": corrections
        }
    except Exception as e:
        logger.error(f"获取纠正记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
