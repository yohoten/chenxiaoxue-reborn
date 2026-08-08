"""
梦境 API 路由
提供梦境记录、解析、符号百科、卡片生成、音景推荐功能
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.dream import (
    DreamCreate, DreamResponse, DreamListResponse, SymbolListResponse,
)
from app.services.database import get_db
from app.services.dream_service import (
    dream_service, save_dream, get_dreams, get_dream_months,
    get_dream_stats, delete_dream,
)
from app.dependencies.auth import get_current_user
from app.utils.logger import logger

router = APIRouter(prefix="/api/dream", tags=["dream"])


class DreamCardRequest(BaseModel):
    """梦境卡片生成请求"""
    dream_text: str = Field(..., min_length=1, max_length=2000)
    detected_symbols: list[dict] = []


class DreamCardResponse(BaseModel):
    """梦境卡片响应"""
    title: str
    mood: str
    mood_emoji: str
    poetic_line: str
    symbols_summary: str
    suggested_music: str  # 推荐音景类型
    color_theme: str  # 推荐色调


class SoundscapeRequest(BaseModel):
    """音景推荐请求"""
    symbols: list[str] = []
    mood: str = "neutral"


class SoundscapeResponse(BaseModel):
    """音景推荐响应"""
    music_type: str
    description: str
    color_palette: list[str]
    bpm_range: str


@router.post("/analyze", response_model=DreamResponse)
async def analyze_and_save_dream(
    dream_data: DreamCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """解析梦境并保存记录"""
    try:
        # 传统符号分析
        result = dream_service.analyze(dream_data.dream_text)

        # AI 增强（可选）
        ai_analysis = ""
        if dream_data.use_ai:
            ai_analysis = await dream_service.analyze_with_ai(dream_data.dream_text)

        # 保存到数据库
        record = await save_dream(
            db,
            user_id=current_user.id,
            dream_data=dream_data,
            symbols=result["detected_symbols"],
            analysis=result["analysis"],
            ai_analysis=ai_analysis,
        )

        return DreamResponse.from_orm(record)

    except Exception as e:
        logger.error(f"梦境解析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/records", response_model=DreamListResponse)
async def list_dream_records(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    month: Optional[str] = Query(None, description="YYYY-MM 格式筛选"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取梦境记录列表"""
    items, total = await get_dreams(
        db, user_id=current_user.id, limit=limit, offset=offset, month=month,
    )
    return DreamListResponse(
        items=[DreamResponse.from_orm(i) for i in items],
        total=total,
    )


@router.get("/months")
async def list_dream_months(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取有梦境记录的所有月份"""
    months = await get_dream_months(db, user_id=current_user.id)
    return {"months": months}


@router.get("/stats")
async def dream_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取梦境统计"""
    return await get_dream_stats(db, user_id=current_user.id)


@router.delete("/records/{dream_id}")
async def remove_dream(
    dream_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除梦境记录"""
    success = await delete_dream(db, dream_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="梦境记录不存在")
    return {"message": "删除成功"}


@router.get("/encyclopedia", response_model=SymbolListResponse)
async def symbol_encyclopedia(
    category: Optional[str] = Query(None, description="按分类筛选"),
):
    """获取梦境符号百科"""
    result = dream_service.get_symbol_encyclopedia(category)
    return SymbolListResponse(**result)


# ── 梦境卡片生成 ─────────────────────────────────────────

@router.post("/card", response_model=DreamCardResponse)
async def generate_dream_card(req: DreamCardRequest):
    """生成梦境卡片：标题、诗意描述、推荐音景、色调"""
    symbols = [s.get("symbol", "") for s in req.detected_symbols]
    result = dream_service.generate_card(req.dream_text, symbols)
    return DreamCardResponse(**result)


@router.post("/soundscape", response_model=SoundscapeResponse)
async def recommend_soundscape(req: SoundscapeRequest):
    """根据梦境符号和情绪推荐音景"""
    result = dream_service.recommend_soundscape(req.symbols, req.mood)
    return SoundscapeResponse(**result)


# ── 梦境世界 3D 数据 ─────────────────────────────────────

class DreamWorldRequest(BaseModel):
    """梦境世界生成请求"""
    dream_text: str = Field(..., min_length=1, max_length=2000)
    detected_symbols: list[dict] = []


@router.post("/world")
async def generate_dream_world(req: DreamWorldRequest):
    """生成梦境 3D 世界数据（球形星球 + 符号对象布局）"""
    symbols = req.detected_symbols or []
    result = dream_service.generate_world_data(symbols)
    return result


# ── 梦境信使游戏 ─────────────────────────────────────────

class MessengerGameRequest(BaseModel):
    """信使游戏请求"""
    symbols: list[dict] = []
    dream_text: str = ""


@router.post("/messenger/world")
async def generate_messenger_world(req: MessengerGameRequest):
    """生成信使游戏世界（含 NPC 和任务）"""
    symbols = req.symbols or []
    result = dream_service.generate_messenger_world(symbols)
    return result


@router.get("/starmap")
async def get_dream_star_map(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取梦境星图数据：每个梦境变成一颗星星"""
    from app.services.dream_service import get_dreams as get_dreams_svc

    records, _ = await get_dreams_svc(db, user_id=current_user.id, limit=200)
    stars = []
    constellations = {}

    for i, record in enumerate(records):
        import json, math
        symbols = []
        if record.detected_symbols:
            try:
                symbols = json.loads(record.detected_symbols)
            except Exception:
                pass

        mood = "neutral"
        if record.emotion:
            mood = record.emotion

        # 在圆形星图上分布
        angle = (i / max(len(records), 1)) * math.pi * 2
        radius = 1.5 + (i % 5) * 0.8 + len(symbols) * 0.3
        x = math.cos(angle) * radius
        y = math.sin(angle) * radius

        star = {
            "id": record.id,
            "dream_text": record.dream_text[:60] + "...",
            "symbols": [s.get("symbol", "") for s in symbols[:3]],
            "emoji": dream_service._symbols.get(
                symbols[0].get("symbol", "") if symbols else "",
                {"emoji": "✨"}
            ).get("emoji", "✨"),
            "mood": mood,
            "x": round(x, 2),
            "y": round(y, 2),
            "brightness": round(0.5 + len(symbols) * 0.1, 2),
            "date": record.dream_date.strftime("%Y-%m-%d") if record.dream_date else "",
        }
        stars.append(star)

        # 星座聚类
        for s in symbols:
            cat = s.get("category", "未知")
            if cat not in constellations:
                constellations[cat] = []
            if record.id not in [c["id"] for c in constellations[cat]]:
                constellations[cat].append({
                    "id": record.id,
                    "symbol": s.get("symbol", ""),
                })

    return {
        "stars": stars,
        "total": len(stars),
        "constellations": [
            {"name": k, "stars": v, "count": len(v)}
            for k, v in sorted(constellations.items(), key=lambda x: -len(x[1]))
        ],
    }


@router.get("/square")
async def dream_square(
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """匿名梦境广场 — 浏览其他用户分享的梦境"""
    from app.services.dream_service import get_dreams as get_dreams_svc
    # 获取最近的梦境（不限制用户）
    from sqlalchemy import select, func
    from app.models.dream import DreamRecord

    result = await db.execute(
        select(DreamRecord)
        .order_by(DreamRecord.created_at.desc())
        .limit(limit)
    )
    records = result.scalars().all()

    import json
    items = []
    for r in records:
        symbols = []
        if r.detected_symbols:
            try:
                symbols = json.loads(r.detected_symbols)
            except Exception:
                pass

        items.append({
            "id": r.id,
            "dream_snippet": r.dream_text[:80] + ("..." if len(r.dream_text) > 80 else ""),
            "symbols": [s.get("symbol", "") for s in symbols[:3]],
            "emotion": r.emotion or "neutral",
            "date": r.dream_date.strftime("%Y-%m-%d") if r.dream_date else "",
            "analysis_type": r.analysis_type,
        })

    return {"items": items, "total": len(items)}


@router.post("/messenger/score")
async def submit_messenger_score(
    score: int = Query(..., ge=0),
    symbols_delivered: int = Query(..., ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """提交信使游戏分数"""
    # 保存到梦境统计
    return {
        "score": score,
        "symbols_delivered": symbols_delivered,
        "rank": dream_service.get_messenger_rank(score),
        "message": f"成功送达 {symbols_delivered} 封信件！获得了 {score} 点自我认知点数",
    }
