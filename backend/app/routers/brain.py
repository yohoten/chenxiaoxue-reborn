"""
Brain API — 第二大脑知识库

个人知识管理系统 API，基于 2nd Brain 技能规范。
提供对人物、地点、游戏、技术、事件、媒体、想法和组织的知识管理。

## 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET    | /api/brain/entries         | 列出所有条目 |
| POST   | /api/brain/entries         | 创建新条目 |
| GET    | /api/brain/entries/search  | 搜索条目 |
| GET    | /api/brain/entries/{category}/{slug} | 获取条目详情 |
| PUT    | /api/brain/entries/{category}/{slug} | 更新条目 |
| DELETE | /api/brain/entries/{category}/{slug} | 删除条目 |
| GET    | /api/brain/entries/{category}/{slug}/attachments | 列出附件 |
| POST   | /api/brain/entries/{category}/{slug}/attachments | 添加附件 |
| GET    | /api/brain/templates       | 列出模板 |
| GET    | /api/brain/templates/{category} | 获取模板详情 |
| GET    | /api/brain/stats           | 获取统计信息 |
"""

from __future__ import annotations

from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel, Field
from typing import Optional

from app.services.brain_service import (
    brain_service,
    CATEGORIES,
    CATEGORY_ICONS,
    BrainEntry,
    SearchResult,
)

router = APIRouter(prefix="/api/brain", tags=["brain"])


# ─── 请求模型 ───────────────────────────────────────────────


class CreateEntryRequest(BaseModel):
    """创建条目请求"""
    category: str = Field(..., description="条目类别", examples=["people"])
    title: str = Field(..., min_length=1, max_length=200, description="条目名称")
    data: Optional[dict] = Field(None, description="额外的 frontmatter 字段")
    notes: Optional[str] = Field(None, description="初始笔记")


class UpdateEntryRequest(BaseModel):
    """更新条目请求"""
    data: Optional[dict] = Field(None, description="要更新的 frontmatter 字段")
    notes: Optional[str] = Field(None, description="要追加的笔记")


# ─── 响应模型 ───────────────────────────────────────────────


class EntryResponse(BaseModel):
    """条目响应"""
    id: str
    category: str
    title: str
    frontmatter: dict
    content: str
    file_path: str
    created_at: str
    updated_at: str
    tags: list[str]
    has_attachments: bool = False


class EntryListResponse(BaseModel):
    """条目列表响应"""
    entries: list[EntryResponse]
    total: int
    category: Optional[str] = None


class SearchResponse(BaseModel):
    """搜索响应"""
    entries: list[EntryResponse]
    total: int
    query: str


class TemplateInfo(BaseModel):
    """模板信息"""
    id: str
    name: str
    category: str


class StatsResponse(BaseModel):
    """统计响应"""
    total_entries: int
    categories: dict


class AttachmentResponse(BaseModel):
    """附件响应"""
    filename: str
    description: str
    added: str
    file_size: int
    mime_type: str


# ─── API 端点 ───────────────────────────────────────────────


@router.get(
    "/entries",
    response_model=EntryListResponse,
    summary="列出知识库条目",
    description="获取所有知识条目，可按类别和排序方式过滤。",
)
async def list_entries(
    category: Optional[str] = None,
    sort_by: str = "updated_at",
    limit: int = 50,
):
    """列出知识库条目"""
    if category and category not in CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category: {category}. Valid: {list(CATEGORIES.keys())}",
        )

    entries = await brain_service.list_entries(
        category=category,
        sort_by=sort_by,
        limit=limit,
    )
    return EntryListResponse(
        entries=[_to_response(e) for e in entries],
        total=len(entries),
        category=category,
    )


@router.post(
    "/entries",
    response_model=EntryResponse,
    summary="创建知识条目",
    description="创建新的知识库条目，支持 8 种实体类型。",
    status_code=201,
)
async def create_entry(req: CreateEntryRequest):
    """创建新条目"""
    if req.category not in CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category: {req.category}. Valid: {list(CATEGORIES.keys())}",
        )

    try:
        entry = await brain_service.create_entry(
            category=req.category,
            title=req.title,
            data=req.data,
            notes=req.notes,
        )
        return _to_response(entry)
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/entries/search",
    response_model=SearchResponse,
    summary="搜索知识库",
    description="跨所有类别或指定类别搜索知识条目。",
)
async def search_entries(
    q: str = Query(..., description="搜索关键词"),
    category: Optional[str] = None,
    limit: int = 20,
):
    """搜索知识条目"""
    if category and category not in CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category: {category}",
        )

    result = await brain_service.search(
        query=q,
        category=category,
        limit=limit,
    )
    return SearchResponse(
        entries=[_to_response(e) for e in result.entries],
        total=result.total,
        query=result.query,
    )


@router.get(
    "/entries/{category}/{slug}",
    response_model=EntryResponse,
    summary="获取条目详情",
    description="获取指定知识条目的详细内容。",
)
async def get_entry(category: str, slug: str):
    """获取条目详情"""
    if category not in CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid category: {category}")

    entry = await brain_service.get_entry(category, slug)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    return _to_response(entry)


@router.put(
    "/entries/{category}/{slug}",
    response_model=EntryResponse,
    summary="更新条目",
    description="更新条目的 frontmatter 字段或追加笔记。",
)
async def update_entry(category: str, slug: str, req: UpdateEntryRequest):
    """更新条目"""
    if category not in CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid category: {category}")

    entry = await brain_service.update_entry(
        category=category,
        slug=slug,
        data=req.data,
        notes=req.notes,
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    return _to_response(entry)


@router.delete(
    "/entries/{category}/{slug}",
    summary="删除条目",
    description="删除指定的知识条目及其附件。",
)
async def delete_entry(category: str, slug: str):
    """删除条目"""
    if category not in CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid category: {category}")

    deleted = await brain_service.delete_entry(category, slug)
    if not deleted:
        raise HTTPException(status_code=404, detail="Entry not found")

    return {"message": f"Entry deleted: {category}/{slug}"}


@router.get(
    "/entries/{category}/{slug}/attachments",
    response_model=list[AttachmentResponse],
    summary="列出附件",
    description="获取条目的附件列表。",
)
async def list_attachments(category: str, slug: str):
    """列出附件"""
    if category not in CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid category: {category}")

    attachments = await brain_service.list_attachments(category, slug)
    return [
        AttachmentResponse(**a.__dict__) for a in attachments
    ]


@router.post(
    "/entries/{category}/{slug}/attachments",
    response_model=AttachmentResponse,
    summary="添加附件",
    description="为条目上传附件文件。",
    status_code=201,
)
async def add_attachment(
    category: str,
    slug: str,
    file: UploadFile = File(...),
    description: str = Form(""),
):
    """添加附件"""
    if category not in CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid category: {category}")

    # Save uploaded file temporarily
    temp_path = Path(f"/tmp/brain_{slug}_{file.filename}")
    content = await file.read()
    temp_path.write_bytes(content)

    try:
        info = await brain_service.add_attachment(
            category=category,
            slug=slug,
            source_path=str(temp_path),
            description=description,
        )
        if not info:
            raise HTTPException(status_code=404, detail="Entry not found")
        return AttachmentResponse(**info.__dict__)
    finally:
        if temp_path.exists():
            temp_path.unlink()


@router.get(
    "/templates",
    response_model=list[TemplateInfo],
    summary="列出模板",
    description="获取所有可用的条目创建模板。",
)
async def list_templates():
    """列出模板"""
    return brain_service.list_templates()


@router.get(
    "/templates/{category}",
    summary="获取模板内容",
    description="获取指定类别的模板 Markdown 内容。",
)
async def get_template(category: str):
    """获取模板详情"""
    if category not in CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid category: {category}")

    content = brain_service.get_template(category)
    if not content:
        raise HTTPException(status_code=404, detail="Template not found")

    return {"category": category, "content": content}


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="获取统计信息",
    description="获取知识库的统计信息，包括各类别的条目数量。",
)
async def get_stats():
    """获取统计信息"""
    return await brain_service.get_stats()


# ─── 辅助函数 ───────────────────────────────────────────────


def _to_response(entry: BrainEntry) -> EntryResponse:
    """将 BrainEntry 转为 EntryResponse"""
    return EntryResponse(
        id=entry.id,
        category=entry.category,
        title=entry.title,
        frontmatter=entry.frontmatter,
        content=entry.content,
        file_path=entry.file_path,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
        tags=entry.tags,
        has_attachments=entry.has_attachments,
    )
