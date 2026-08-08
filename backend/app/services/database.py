"""
数据库服务 - 基于 SQLAlchemy 异步引擎（支持用户隔离）
"""

from pathlib import Path
from typing import Optional

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config.settings import settings
from app.models.conversation import Base, Conversation, ConversationCreate
from app.models.dream import DreamRecord
from app.models.user import User

# ── 全局引擎 & Session 工厂 ────────────────────────────────
_engine = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


async def init_db():
    """初始化数据库（创建表结构）"""
    global _engine, _session_factory

    # 确保 data 目录存在
    db_path = settings.DATA_DIR / "chenxiaoxue.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    db_url = f"sqlite+aiosqlite:///{db_path}"
    _engine = create_async_engine(db_url, echo=False)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """关闭数据库连接"""
    global _engine
    if _engine:
        await _engine.dispose()


async def get_session() -> AsyncSession:
    """获取异步数据库会话（直接使用已初始化的工厂）"""
    if _session_factory is None:
        raise RuntimeError("数据库未初始化，请先调用 init_db()")
    return _session_factory()


async def get_db():
    """FastAPI 依赖: 获取数据库会话（自动关闭）"""
    session = await get_session()
    try:
        yield session
    finally:
        await session.close()


# ── 用户 CRUD 操作 ─────────────────────────────────────────


async def get_user_by_username(username: str) -> Optional[User]:
    """根据用户名获取用户"""
    async with await get_session() as session:
        result = await session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()


async def get_user_by_id(user_id: int) -> Optional[User]:
    """根据 ID 获取用户"""
    async with await get_session() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()


async def create_user(user: User) -> User:
    """创建新用户"""
    async with await get_session() as session:
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


# ── 对话 CRUD 操作（支持用户隔离）──────────────────────────


async def save_conversation(conv: ConversationCreate, user_id: int) -> Conversation:
    """保存对话记录（关联用户）"""
    async with await get_session() as session:
        db_conv = Conversation(
            user_id=user_id,
            user_input=conv.user_input,
            assistant_response=conv.assistant_response,
            intent=conv.intent,
            emotion=conv.emotion,
            model_name=conv.model_name,
            tokens_used=conv.tokens_used,
        )
        session.add(db_conv)
        await session.commit()
        await session.refresh(db_conv)
        return db_conv


async def get_conversations(
    user_id: int,
    limit: int = 50,
    offset: int = 0
) -> tuple[list[Conversation], int]:
    """获取指定用户的对话历史列表"""
    async with await get_session() as session:
        # 查询总数（按用户过滤）
        count_query = select(func.count()).select_from(
            Conversation
        ).where(Conversation.user_id == user_id)
        total = (await session.execute(count_query)).scalar() or 0

        # 查询分页数据
        query = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(query)
        items = list(result.scalars().all())

        return items, total


async def delete_conversation(conv_id: int, user_id: int) -> bool:
    """删除对话记录（验证用户权限）"""
    async with await get_session() as session:
        # 先验证对话属于该用户
        result = await session.execute(
            select(Conversation).where(
                Conversation.id == conv_id,
                Conversation.user_id == user_id
            )
        )
        conv = result.scalar_one_or_none()
        
        if not conv:
            return False
        
        await session.delete(conv)
        await session.commit()
        return True


async def clear_conversations(user_id: int) -> int:
    """清空指定用户的所有对话记录"""
    async with await get_session() as session:
        stmt = delete(Conversation).where(Conversation.user_id == user_id)
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount
