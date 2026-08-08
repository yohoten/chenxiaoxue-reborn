"""
资源文件 API 路由

提供背景图片、角色图片等资源文件的访问接口
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from cachetools import TTLCache

from app.config.settings import settings
from app.utils.logger import logger

router = APIRouter(prefix="/api/resources", tags=["resources"])

# ── 资源列表缓存（5 分钟 TTL）─────────────────────────────────
_resource_cache: TTLCache = TTLCache(maxsize=10, ttl=300)


@router.get("/backgrounds")
async def list_backgrounds():
    """获取所有背景图片列表（5 分钟缓存）"""
    cache_key = "backgrounds"
    if cache_key in _resource_cache:
        return _resource_cache[cache_key]

    bg_dir = settings.RESOURCE_PATH / "Background Image"
    if not bg_dir.exists():
        return {"backgrounds": []}

    backgrounds = []
    for f in sorted(bg_dir.iterdir()):
        if f.suffix.lower() in (".gif", ".png", ".jpg", ".jpeg"):
            backgrounds.append({
                "name": f.stem,
                "path": f"/api/resources/file/backgrounds/{f.name}",
                "type": f.suffix[1:],
                "is_animated": f.suffix.lower() == ".gif",
            })

    result = {"backgrounds": backgrounds}
    _resource_cache[cache_key] = result
    return result


@router.get("/characters")
async def list_characters():
    """获取所有角色图片列表（5 分钟缓存）"""
    cache_key = "characters"
    if cache_key in _resource_cache:
        return _resource_cache[cache_key]

    char_dir = settings.RESOURCE_PATH / "Character Image"
    if not char_dir.exists():
        return {"characters": []}

    characters = []
    for f in sorted(char_dir.iterdir()):
        if f.suffix.lower() in (".gif", ".png", ".jpg", ".jpeg"):
            characters.append({
                "name": f.stem,
                "path": f"/api/resources/file/characters/{f.name}",
                "type": f.suffix[1:],
                "is_animated": f.suffix.lower() == ".gif",
            })

    result = {"characters": characters}
    _resource_cache[cache_key] = result
    return result


@router.get("/star-maps")
async def list_star_maps():
    """获取所有星图列表"""
    star_dir = settings.RESOURCE_PATH / "Star Map"
    if not star_dir.exists():
        return {"star_maps": []}

    star_maps = []
    for f in sorted(star_dir.iterdir()):
        if f.suffix.lower() in (".gif", ".png", ".jpg", ".jpeg"):
            star_maps.append({
                "name": f.stem,
                "path": f"/api/resources/file/star_maps/{f.name}",
                "type": f.suffix[1:],
                "is_animated": f.suffix.lower() == ".gif",
            })

    return {"star_maps": star_maps}


@router.get("/sounds")
async def list_sounds():
    """获取所有音频文件列表"""
    sound_dir = settings.RESOURCE_PATH / "Sound"
    if not sound_dir.exists():
        return {"sounds": []}

    sounds = []
    for f in sorted(sound_dir.iterdir()):
        if f.suffix.lower() in (".mp3", ".wav", ".ogg", ".aac"):
            # 根据文件名推断情感类型
            emotion = f.stem.split('_')[-1] if '_' in f.stem else 'neutral'
            sounds.append({
                "name": f.stem,
                "path": f"/api/resources/file/sounds/{f.name}",
                "type": f.suffix[1:],
                "emotion": emotion,
                "size_kb": round(f.stat().st_size / 1024, 2),
            })

    return {"sounds": sounds}


@router.get("/file/{category}/{filename}")
async def get_resource_file(category: str, filename: str):
    """获取资源文件"""
    # 安全检查: 防止路径遍历
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    category_map = {
        "backgrounds": "Background Image",
        "characters": "Character Image",
        "players": "Player Image",
        "ecg": "ECG Image",
        "star_maps": "Star Map",
        "sounds": "Sound",  # 新增音频支持
    }

    dir_name = category_map.get(category)
    if not dir_name:
        raise HTTPException(status_code=404, detail="Category not found")

    file_path = settings.RESOURCE_PATH / dir_name / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(str(file_path))
