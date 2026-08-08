"""
记忆管理服务
提供长期记忆存储、检索和搜索能力
Phase 1: 基于 SQLite 的基础实现
Phase 2: 集成向量数据库（ChromaDB/FAISS）
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config.settings import settings
from app.utils.logger import logger

Base = declarative_base()


class MemoryEntry(Base):
    """记忆条目模型"""
    __tablename__ = "memories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=False, index=True)  # 用户ID
    content = Column(Text, nullable=False)  # 记忆内容
    category = Column(String(50), default="general")  # 分类：fact, preference, event, etc.
    importance = Column(Float, default=0.5)  # 重要性评分 0-1
    tags = Column(Text, default="[]")  # JSON 格式的标签列表
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    access_count = Column(Integer, default=0)  # 访问次数
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content": self.content,
            "category": self.category,
            "importance": self.importance,
            "tags": json.loads(self.tags) if self.tags else [],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "access_count": self.access_count
        }


class MemoryService:
    """
    记忆管理服务
    
    Phase 1: 基于 SQLite 的关键词搜索
    Phase 2: 集成向量数据库进行语义搜索
    """
    
    def __init__(self):
        # 使用 DATA_DIR 而不是 DATABASE_PATH
        self.db_path = settings.DATA_DIR / "memories.db"
        self.db_url = f"sqlite:///{self.db_path}"
        self.engine = create_engine(self.db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        logger.info("记忆服务初始化完成")
    
    def _get_db(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()
    
    def store_memory(
        self,
        user_id: str,
        content: str,
        category: str = "general",
        importance: float = 0.5,
        tags: list[str] = None
    ) -> MemoryEntry:
        """
        存储记忆
        
        Args:
            user_id: 用户ID
            content: 记忆内容
            category: 分类 (fact/preference/event/conversation)
            importance: 重要性 0-1
            tags: 标签列表
            
        Returns:
            创建的记忆条目
        """
        db = self._get_db()
        try:
            memory = MemoryEntry(
                user_id=user_id,
                content=content,
                category=category,
                importance=importance,
                tags=json.dumps(tags or [])
            )
            db.add(memory)
            db.commit()
            db.refresh(memory)
            logger.info(f"存储记忆成功: ID={memory.id}, 用户={user_id}")
            return memory
        except Exception as e:
            db.rollback()
            logger.error(f"存储记忆失败: {e}")
            raise
        finally:
            db.close()
    
    def retrieve_memories(
        self,
        user_id: str,
        category: Optional[str] = None,
        limit: int = 10,
        min_importance: float = 0.0
    ) -> list[MemoryEntry]:
        """
        检索用户的记忆
        
        Args:
            user_id: 用户ID
            category: 分类过滤（可选）
            limit: 返回数量限制
            min_importance: 最低重要性阈值
            
        Returns:
            记忆列表
        """
        db = self._get_db()
        try:
            query = db.query(MemoryEntry).filter(
                MemoryEntry.user_id == user_id,
                MemoryEntry.importance >= min_importance
            )
            
            if category:
                query = query.filter(MemoryEntry.category == category)
            
            memories = query.order_by(
                MemoryEntry.importance.desc(),
                MemoryEntry.created_at.desc()
            ).limit(limit).all()
            
            # 更新访问计数
            for memory in memories:
                memory.access_count += 1
            db.commit()
            
            logger.info(f"检索到 {len(memories)} 条记忆，用户={user_id}")
            return memories
        except Exception as e:
            logger.error(f"检索记忆失败: {e}")
            return []
        finally:
            db.close()
    
    def search_memories(
        self,
        user_id: str,
        keyword: str,
        limit: int = 10
    ) -> list[MemoryEntry]:
        """
        搜索记忆（关键词搜索）
        
        Args:
            user_id: 用户ID
            keyword: 搜索关键词
            limit: 返回数量限制
            
        Returns:
            匹配的记忆列表
        """
        db = self._get_db()
        try:
            memories = db.query(MemoryEntry).filter(
                MemoryEntry.user_id == user_id,
                MemoryEntry.content.contains(keyword)
            ).order_by(
                MemoryEntry.importance.desc(),
                MemoryEntry.created_at.desc()
            ).limit(limit).all()
            
            logger.info(f"搜索记忆: 关键词='{keyword}', 找到 {len(memories)} 条")
            return memories
        except Exception as e:
            logger.error(f"搜索记忆失败: {e}")
            return []
        finally:
            db.close()
    
    def update_memory(
        self,
        memory_id: int,
        content: Optional[str] = None,
        importance: Optional[float] = None,
        tags: Optional[list[str]] = None
    ) -> Optional[MemoryEntry]:
        """更新记忆"""
        db = self._get_db()
        try:
            memory = db.query(MemoryEntry).filter(MemoryEntry.id == memory_id).first()
            if not memory:
                return None
            
            if content is not None:
                memory.content = content
            if importance is not None:
                memory.importance = importance
            if tags is not None:
                memory.tags = json.dumps(tags)
            
            db.commit()
            db.refresh(memory)
            logger.info(f"更新记忆成功: ID={memory_id}")
            return memory
        except Exception as e:
            db.rollback()
            logger.error(f"更新记忆失败: {e}")
            return None
        finally:
            db.close()
    
    def delete_memory(self, memory_id: int) -> bool:
        """删除记忆"""
        db = self._get_db()
        try:
            memory = db.query(MemoryEntry).filter(MemoryEntry.id == memory_id).first()
            if not memory:
                return False
            
            db.delete(memory)
            db.commit()
            logger.info(f"删除记忆成功: ID={memory_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"删除记忆失败: {e}")
            return False
        finally:
            db.close()
    
    def get_stats(self, user_id: str) -> dict:
        """获取用户记忆统计"""
        db = self._get_db()
        try:
            total = db.query(MemoryEntry).filter(MemoryEntry.user_id == user_id).count()
            categories = db.query(MemoryEntry.category).filter(
                MemoryEntry.user_id == user_id
            ).distinct().all()
            
            return {
                "total_memories": total,
                "categories": [c[0] for c in categories],
                "user_id": user_id
            }
        except Exception as e:
            logger.error(f"获取记忆统计失败: {e}")
            return {"total_memories": 0, "categories": [], "user_id": user_id}
        finally:
            db.close()


# 全局记忆服务实例
memory_service = MemoryService()