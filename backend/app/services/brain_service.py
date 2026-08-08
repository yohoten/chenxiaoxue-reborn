"""
Brain Service — 第二大脑知识库

基于文件的个人知识管理系统，用于捕获和检索关于人物、地点、事物和想法的信息。
遵循 2nd Brain 技能的完整规范，支持 8 种实体类型：

- people: 人物
- places: 地点（餐厅、地标、场所）
- games: 游戏
- tech: 技术（设备、产品）
- events: 事件（会议、聚会）
- media: 媒体（书籍、影视、播客）
- ideas: 想法
- orgs: 组织（公司、社区、团体）

数据以 Markdown + YAML frontmatter 格式存储在 data/brain/ 目录下。
"""

from __future__ import annotations

import os
import re
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict

import logging
logger = logging.getLogger(__name__)


# ─── 配置 ───────────────────────────────────────────────────

# 数据存储根目录 (相对于项目根目录)
BRAIN_ROOT = Path(__file__).resolve().parent.parent.parent.parent / "data" / "brain"

# 支持的实体类别及对应目录
CATEGORIES = {
    "people": "人物",
    "places": "地点",
    "games": "游戏",
    "tech": "技术",
    "events": "事件",
    "media": "媒体",
    "ideas": "想法",
    "orgs": "组织",
}

CATEGORY_ICONS = {
    "people": "👤",
    "places": "📍",
    "games": "🎮",
    "tech": "💻",
    "events": "📅",
    "media": "📖",
    "ideas": "💡",
    "orgs": "🏢",
}

# 模板目录
TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent.parent / "skills" / "brain" / "templates"

# 模板文件名到类别键的映射 (文件名单数 -> CATEGORIES 键复数)
TEMPLATE_CATEGORY_MAP = {
    "person": "people",
    "place": "places",
    "game": "games",
    "tech": "tech",
    "event": "events",
    "media": "media",
    "idea": "ideas",
    "org": "orgs",
}


# ─── 数据模型 ───────────────────────────────────────────────


@dataclass
class BrainEntry:
    """知识库条目"""
    id: str = ""                    # 唯一标识 (slug)
    category: str = ""              # 类别
    title: str = ""                 # 标题/名称
    frontmatter: dict = field(default_factory=dict)  # YAML 前置元数据
    content: str = ""               # Markdown 正文
    file_path: str = ""             # 文件路径
    created_at: str = ""            # 创建时间
    updated_at: str = ""            # 更新时间
    tags: List[str] = field(default_factory=list)
    has_attachments: bool = False   # 是否有附件


@dataclass
class SearchResult:
    """搜索结果"""
    entries: List[BrainEntry] = field(default_factory=list)
    total: int = 0
    query: str = ""


@dataclass
class AttachmentInfo:
    """附件信息"""
    filename: str = ""
    description: str = ""
    added: str = ""
    file_size: int = 0
    mime_type: str = ""


# ─── 文件级知识库服务 ─────────────────────────────────────


class BrainService:
    """
    第二大脑知识库服务

    基于文件的实现，每个条目存储为一个 .md 文件。
    文件格式: YAML frontmatter + Markdown 正文
    目录结构: data/brain/{category}/{slug}.md
    带附件的目录结构: data/brain/{category}/{slug}/ + attachments/
    """

    def __init__(self):
        self._ensure_directories()
        logger.info(f"Brain Service initialized, root: {BRAIN_ROOT}")

    def _ensure_directories(self):
        """确保所有分类目录存在"""
        for cat in CATEGORIES:
            (BRAIN_ROOT / cat).mkdir(parents=True, exist_ok=True)

    # ── 路径工具 ──────────────────────────────────────────

    def _get_entry_path(self, category: str, slug: str) -> Path:
        """获取条目文件路径"""
        return BRAIN_ROOT / category / f"{slug}.md"

    def _get_entry_folder(self, category: str, slug: str) -> Path:
        """获取条目文件夹路径（用于带附件的条目）"""
        return BRAIN_ROOT / category / slug

    def _slugify(self, name: str) -> str:
        """将名称转为 slug"""
        slug = name.lower().strip()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        return slug.strip('-') or 'untitled'

    def _parse_frontmatter(self, text: str) -> Tuple[dict, str]:
        """解析 YAML frontmatter 和正文"""
        frontmatter = {}
        body = text

        if text.startswith('---'):
            parts = text.split('---', 2)
            if len(parts) >= 3:
                fm_text = parts[1].strip()
                body = parts[2].strip()
                # 解析简单的 YAML
                current_key = None
                current_list = None
                for line in fm_text.split('\n'):
                    line = line.rstrip()
                    if not line:
                        continue
                    # Check for list item continuation
                    if line.startswith('  - ') and current_key and isinstance(current_list, list):
                        current_list.append(line.strip('- ').strip().strip('"').strip("'"))
                        continue
                    elif line.startswith('  - ') and current_key:
                        current_list = [line.strip('- ').strip().strip('"').strip("'")]
                        frontmatter[current_key] = current_list
                        continue
                    
                    # Key: value
                    if ':' in line:
                        key, _, value = line.partition(':')
                        key = key.strip()
                        value = value.strip()
                        
                        # Handle list values
                        if value.startswith('[]'):
                            frontmatter[key] = []
                            current_key = key
                            current_list = []
                            continue
                        
                        # Remove quotes
                        if (value.startswith('"') and value.endswith('"')) or \
                           (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                        
                        # Try parsing as number
                        try:
                            if '.' in value:
                                frontmatter[key] = float(value)
                            else:
                                frontmatter[key] = int(value)
                        except (ValueError, TypeError):
                            frontmatter[key] = value
                        
                        current_key = key
                        if isinstance(frontmatter.get(key), list):
                            current_list = frontmatter[key]
                        else:
                            current_list = None
                            current_key = None

        return frontmatter, body

    def _build_frontmatter_text(self, data: dict) -> str:
        """将字典转为 YAML frontmatter 文本"""
        lines = ['---']
        for key, value in data.items():
            if value is None or value == '':
                lines.append(f'{key}: ')
            elif isinstance(value, list):
                if not value:
                    lines.append(f'{key}: []')
                else:
                    lines.append(f'{key}:')
                    for item in value:
                        lines.append(f'  - {item}')
            elif isinstance(value, bool):
                lines.append(f'{key}: {"true" if value else "false"}')
            elif isinstance(value, (int, float)):
                lines.append(f'{key}: {value}')
            else:
                lines.append(f'{key}: {value}')
        lines.append('---')
        return '\n'.join(lines)

    # ── 模板 ──────────────────────────────────────────────

    def list_templates(self) -> List[dict]:
        """列出所有可用模板"""
        templates = []
        if TEMPLATES_DIR.exists():
            for f in sorted(TEMPLATES_DIR.glob('*.md')):
                if f.name == 'attachments-index.md':
                    continue
                stem = f.stem  # person, place, game, etc.
                mapped_cat = TEMPLATE_CATEGORY_MAP.get(stem)
                if mapped_cat:
                    templates.append({
                        "id": stem,
                        "name": f"{CATEGORY_ICONS.get(mapped_cat, '')} {CATEGORIES.get(mapped_cat, stem)}",
                        "file": f.name,
                        "category": mapped_cat,
                    })
        return templates

    def get_template(self, category: str) -> Optional[str]:
        """获取指定类别的模板内容"""
        template_path = TEMPLATES_DIR / f"{category}.md"
        if template_path.exists():
            return template_path.read_text(encoding='utf-8')
        return None

    # ── CRUD 操作 ─────────────────────────────────────────

    async def create_entry(
        self,
        category: str,
        title: str,
        data: Optional[dict] = None,
        notes: Optional[str] = None,
    ) -> BrainEntry:
        """
        创建新的知识条目

        Args:
            category: 类别 (people/places/games/tech/events/media/ideas/orgs)
            title: 条目名称
            data: 额外的 frontmatter 数据
            notes: 初始笔记内容

        Returns:
            创建的 BrainEntry
        """
        if category not in CATEGORIES:
            raise ValueError(f"Invalid category: {category}. Valid: {list(CATEGORIES.keys())}")

        slug = self._slugify(title)
        file_path = self._get_entry_path(category, slug)

        if file_path.exists():
            raise FileExistsError(f"Entry already exists: {file_path}")

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        today = datetime.now().strftime('%Y-%m-%d')

        # 构建 frontmatter
        frontmatter = {
            "type": category.rstrip('s'),  # people -> person
            "name": title,
            "tags": [],
            "created": today,
            "last_updated": today,
        }
        if data:
            # Merge, keeping our defaults as fallbacks
            for k, v in data.items():
                if v is not None and v != '' and v != []:
                    frontmatter[k] = v

        # 构建笔记内容
        body_parts = ["", "## Notes", ""]
        if notes:
            body_parts.append(f"- **{today}**: {notes}")
        else:
            body_parts.append("- ")

        # 写文件
        content = self._build_frontmatter_text(frontmatter) + '\n'.join(body_parts)
        file_path.write_text(content, encoding='utf-8')

        entry = BrainEntry(
            id=slug,
            category=category,
            title=title,
            frontmatter=frontmatter,
            content='\n'.join(body_parts),
            file_path=str(file_path),
            created_at=now,
            updated_at=now,
            tags=frontmatter.get('tags', []),
        )

        logger.info(f"Brain entry created: {category}/{slug}")
        return entry

    async def get_entry(self, category: str, slug: str) -> Optional[BrainEntry]:
        """获取指定条目"""
        # Try direct file path first
        file_path = self._get_entry_path(category, slug)
        if not file_path.exists():
            # Try folder structure
            folder_path = self._get_entry_folder(category, slug)
            file_path = folder_path / f"{slug}.md"
            if not file_path.exists():
                return None

        text = file_path.read_text(encoding='utf-8')
        frontmatter, body = self._parse_frontmatter(text)

        # Check for attachments
        has_attachments = False
        attachments_path = file_path.parent / "attachments"
        if attachments_path.exists() and any(attachments_path.iterdir()):
            has_attachments = True

        tags = frontmatter.get('tags', [])
        if isinstance(tags, str):
            tags = [tags]

        return BrainEntry(
            id=slug,
            category=category,
            title=frontmatter.get('name', slug),
            frontmatter=frontmatter,
            content=body,
            file_path=str(file_path),
            created_at=frontmatter.get('created', ''),
            updated_at=frontmatter.get('last_updated', ''),
            tags=tags,
            has_attachments=has_attachments,
        )

    async def update_entry(
        self,
        category: str,
        slug: str,
        data: Optional[dict] = None,
        notes: Optional[str] = None,
    ) -> Optional[BrainEntry]:
        """
        更新条目

        Args:
            category: 类别
            slug: 条目标识
            data: 要更新的 frontmatter 字段
            notes: 要追加的笔记

        Returns:
            更新后的 BrainEntry
        """
        entry = await self.get_entry(category, slug)
        if not entry:
            return None

        file_path = Path(entry.file_path)
        frontmatter = entry.frontmatter.copy()
        today = datetime.now().strftime('%Y-%m-%d')

        # Update frontmatter
        if data:
            for k, v in data.items():
                if v is not None:
                    frontmatter[k] = v

        frontmatter['last_updated'] = today

        # Update body
        body = entry.content
        if notes:
            # Append note to Notes section
            note_line = f"- **{today}**: {notes}"
            if "## Notes" in body:
                # Add after the Notes heading
                body = re.sub(
                    r'(## Notes\n)',
                    rf'\1{note_line}\n',
                    body,
                    count=1,
                )
            else:
                body += f"\n## Notes\n\n{note_line}\n"

        # Write updated content
        content = self._build_frontmatter_text(frontmatter) + '\n' + body.strip()
        file_path.write_text(content, encoding='utf-8')

        logger.info(f"Brain entry updated: {category}/{slug}")
        return await self.get_entry(category, slug)

    async def delete_entry(self, category: str, slug: str) -> bool:
        """删除条目"""
        file_path = self._get_entry_path(category, slug)
        folder_path = self._get_entry_folder(category, slug)

        deleted = False
        if file_path.exists():
            file_path.unlink()
            deleted = True

        # Remove folder if exists
        if folder_path.exists():
            shutil.rmtree(folder_path)
            deleted = True

        if deleted:
            logger.info(f"Brain entry deleted: {category}/{slug}")
        return deleted

    # ── 搜索 ──────────────────────────────────────────────

    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 20,
    ) -> SearchResult:
        """
        搜索知识库

        Args:
            query: 搜索关键词
            category: 可选的类别过滤
            limit: 最大返回数量

        Returns:
            SearchResult
        """
        results = []
        query_lower = query.lower()

        categories_to_search = [category] if category else list(CATEGORIES.keys())

        for cat in categories_to_search:
            if cat not in CATEGORIES:
                continue

            cat_dir = BRAIN_ROOT / cat
            if not cat_dir.exists():
                continue

            for f in cat_dir.rglob('*.md'):
                if f.name == 'index.md' or 'attachments' in f.parts:
                    continue

                try:
                    text = f.read_text(encoding='utf-8')
                    frontmatter, body = self._parse_frontmatter(text)

                    # Search in title and content
                    title = frontmatter.get('name', '').lower()
                    searchable_text = (title + ' ' + body).lower()

                    if query_lower in searchable_text:
                        slug = f.stem
                        tags = frontmatter.get('tags', [])
                        if isinstance(tags, str):
                            tags = [tags]

                        results.append(BrainEntry(
                            id=slug,
                            category=cat,
                            title=frontmatter.get('name', slug),
                            frontmatter=frontmatter,
                            content=body[:200] + ('...' if len(body) > 200 else ''),
                            file_path=str(f),
                            created_at=frontmatter.get('created', ''),
                            updated_at=frontmatter.get('last_updated', ''),
                            tags=tags,
                        ))

                        if len(results) >= limit:
                            break
                except Exception:
                    continue

            if len(results) >= limit:
                break

        return SearchResult(
            entries=results,
            total=len(results),
            query=query,
        )

    async def list_entries(
        self,
        category: Optional[str] = None,
        sort_by: str = "updated_at",
        limit: int = 50,
    ) -> List[BrainEntry]:
        """
        列出条目

        Args:
            category: 可选的类别过滤
            sort_by: 排序字段 (updated_at, created_at, name)
            limit: 最大返回数量

        Returns:
            条目列表
        """
        entries = []
        categories_to_list = [category] if category else list(CATEGORIES.keys())

        for cat in categories_to_list:
            if cat not in CATEGORIES:
                continue

            cat_dir = BRAIN_ROOT / cat
            if not cat_dir.exists():
                continue

            for f in sorted(cat_dir.glob('*.md')):
                try:
                    text = f.read_text(encoding='utf-8')
                    frontmatter, body = self._parse_frontmatter(text)

                    slug = f.stem
                    tags = frontmatter.get('tags', [])
                    if isinstance(tags, str):
                        tags = [tags]

                    entries.append(BrainEntry(
                        id=slug,
                        category=cat,
                        title=frontmatter.get('name', slug),
                        frontmatter=frontmatter,
                        content=body[:100] + ('...' if len(body) > 100 else ''),
                        file_path=str(f),
                        created_at=frontmatter.get('created', ''),
                        updated_at=frontmatter.get('last_updated', ''),
                        tags=tags,
                    ))
                except Exception:
                    continue

        # Sort
        if sort_by == "name":
            entries.sort(key=lambda e: e.title.lower())
        elif sort_by == "created_at":
            entries.sort(key=lambda e: e.created_at, reverse=True)
        else:  # updated_at
            entries.sort(key=lambda e: e.updated_at, reverse=True)

        return entries[:limit]

    # ── 附件管理 ──────────────────────────────────────────

    async def add_attachment(
        self,
        category: str,
        slug: str,
        source_path: str,
        description: str = "",
    ) -> Optional[AttachmentInfo]:
        """
        为条目添加附件

        Args:
            category: 类别
            slug: 条目标识
            source_path: 源文件路径
            description: 附件描述

        Returns:
            AttachmentInfo 或 None
        """
        entry = await self.get_entry(category, slug)
        if not entry:
            return None

        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        # Convert to folder structure if needed
        file_path = Path(entry.file_path)
        if file_path.parent.name != slug:
            # Move to folder structure
            folder_path = self._get_entry_folder(category, slug)
            folder_path.mkdir(parents=True, exist_ok=True)
            new_file_path = folder_path / f"{slug}.md"
            file_path.rename(new_file_path)
            file_path = new_file_path

        # Ensure attachments dir
        attachments_dir = file_path.parent / "attachments"
        attachments_dir.mkdir(parents=True, exist_ok=True)

        # Copy file
        ext = source.suffix
        dest_filename = f"{slug}-attachment-{len(list(attachments_dir.iterdir()))}{ext}"
        dest_path = attachments_dir / dest_filename
        shutil.copy2(source, dest_path)

        # Update attachments index
        today = datetime.now().strftime('%Y-%m-%d')
        index_path = attachments_dir / "index.md"
        if not index_path.exists():
            index_path.write_text(
                "# Attachments\n\n"
                "| File | Description | Added |\n"
                "|------|-------------|-------|\n",
                encoding='utf-8'
            )

        index_content = index_path.read_text(encoding='utf-8')
        index_content += f"| {dest_filename} | {description} | {today} |\n"
        index_path.write_text(index_content, encoding='utf-8')

        info = AttachmentInfo(
            filename=dest_filename,
            description=description,
            added=today,
            file_size=dest_path.stat().st_size,
            mime_type=self._guess_mime(ext),
        )

        logger.info(f"Attachment added to {category}/{slug}: {dest_filename}")
        return info

    async def list_attachments(self, category: str, slug: str) -> List[AttachmentInfo]:
        """列出条目的附件"""
        entries = []
        folder_path = self._get_entry_folder(category, slug)
        attachments_dir = folder_path / "attachments"

        if not attachments_dir.exists():
            return []

        index_path = attachments_dir / "index.md"
        descriptions = {}
        if index_path.exists():
            text = index_path.read_text(encoding='utf-8')
            for line in text.split('\n'):
                if line.startswith('|') and not line.startswith('|---'):
                    parts = line.split('|')
                    if len(parts) >= 4:
                        fname = parts[1].strip()
                        desc = parts[2].strip()
                        added = parts[3].strip()
                        if fname and fname != 'File':
                            descriptions[fname] = (desc, added)

        for f in sorted(attachments_dir.iterdir()):
            if f.name == 'index.md' or not f.is_file():
                continue
            desc, added = descriptions.get(f.name, ('', ''))
            entries.append(AttachmentInfo(
                filename=f.name,
                description=desc,
                added=added,
                file_size=f.stat().st_size,
                mime_type=self._guess_mime(f.suffix),
            ))

        return entries

    def _guess_mime(self, ext: str) -> str:
        """猜测文件 MIME 类型"""
        mime_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.mp4': 'video/mp4',
            '.mp3': 'audio/mpeg',
            '.pdf': 'application/pdf',
            '.md': 'text/markdown',
            '.txt': 'text/plain',
            '.json': 'application/json',
        }
        return mime_map.get(ext.lower(), 'application/octet-stream')

    # ── 统计 ──────────────────────────────────────────────

    async def get_stats(self) -> dict:
        """获取知识库统计信息"""
        stats = {}
        total = 0
        for cat in CATEGORIES:
            cat_dir = BRAIN_ROOT / cat
            count = len(list(cat_dir.glob('*.md'))) if cat_dir.exists() else 0
            stats[cat] = {
                "count": count,
                "name": CATEGORIES[cat],
                "icon": CATEGORY_ICONS.get(cat, ''),
            }
            total += count

        return {
            "total_entries": total,
            "categories": stats,
        }


# ─── 全局单例 ───────────────────────────────────────────────

brain_service = BrainService()
