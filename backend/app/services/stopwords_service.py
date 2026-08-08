"""
停用词管理服务
从旧项目迁移，支持多来源停用词文件和单例模式
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Set

from app.config.settings import settings
from app.utils.logger import logger


class StopwordsService:
    """
    停用词管理服务 - 单例模式
    
    负责加载和管理各种停用词文件
    使用状态标志避免重复初始化
    """
    
    _instance: "StopwordsService | None" = None
    _initialized: bool = False
    
    def __new__(cls) -> "StopwordsService":
        """单例模式确保全局唯一实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化停用词管理器"""
        # 如果已经初始化过，直接返回
        if StopwordsService._initialized:
            return
        
        self.stopwords_dir = settings.RESOURCE_PATH / "stopwords"
        self.stopwords: Set[str] = set()
        self.stopwords_sources: dict[str, Set[str]] = {}
        
        # 异步加载停用词
        self._load_all_stopwords()
        
        # 标记为已初始化
        StopwordsService._initialized = True
        logger.info(f"停用词服务初始化完成，共加载 {len(self.stopwords)} 个停用词")
    
    def _load_all_stopwords(self):
        """加载所有停用词文件（内部方法，仅在首次初始化时调用）"""
        logger.info(f"开始加载停用词，目录: {self.stopwords_dir}")
        
        if not self.stopwords_dir.exists():
            logger.warning(f"停用词目录不存在: {self.stopwords_dir}")
            # 创建默认目录
            self.stopwords_dir.mkdir(parents=True, exist_ok=True)
            return
            
        # 获取所有txt文件
        txt_files = [f for f in self.stopwords_dir.iterdir() if f.suffix == '.txt']
        logger.info(f"找到 {len(txt_files)} 个停用词文件: {[f.name for f in txt_files]}")
        
        total_count = 0
        for txt_file in txt_files:
            try:
                count = self._load_stopwords_from_file(txt_file)
                total_count += count
                logger.debug(f"从 {txt_file.name} 加载了 {count} 个停用词")
            except Exception as e:
                logger.error(f"加载停用词文件 {txt_file.name} 失败: {e}", exc_info=True)
        
        if total_count > 0:
            logger.info(f"停用词加载完成: 共 {total_count:,} 个词")
        else:
            logger.warning("未加载到任何停用词")
    
    def _load_stopwords_from_file(self, file_path: Path) -> int:
        """
        从文件加载停用词
        
        Args:
            file_path: 停用词文件路径
            
        Returns:
            加载的停用词数量
        """
        stopwords_set: Set[str] = set()
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                word = line.strip()
                if word:  # 忽略空行
                    stopwords_set.add(word)
        
        source_name = file_path.stem
        self.stopwords_sources[source_name] = stopwords_set
        # 合并到总停用词集合
        self.stopwords.update(stopwords_set)
        
        return len(stopwords_set)
    
    def get_stopwords(self) -> Set[str]:
        """获取所有停用词"""
        return self.stopwords.copy()
    
    def get_stopwords_by_source(self, source_name: str) -> Set[str]:
        """获取特定来源的停用词"""
        return self.stopwords_sources.get(source_name, set()).copy()
    
    def get_stats(self) -> dict:
        """获取停用词统计信息"""
        return {
            'total_count': len(self.stopwords),
            'sources_count': len(self.stopwords_sources),
            'sources': list(self.stopwords_sources.keys())
        }
    
    def add_stopword(self, word: str):
        """添加单个停用词"""
        self.stopwords.add(word)
    
    def remove_stopword(self, word: str):
        """移除单个停用词"""
        self.stopwords.discard(word)
        # 从各个来源中也移除
        for source_set in self.stopwords_sources.values():
            source_set.discard(word)
    
    def is_stopword(self, word: str) -> bool:
        """检查单词是否为停用词"""
        return word in self.stopwords
    
    def filter_text(self, text: str, separator: str = " ") -> str:
        """
        过滤文本中的停用词
        
        Args:
            text: 输入文本
            separator: 分词分隔符（默认空格）
            
        Returns:
            过滤后的文本
        """
        words = text.split(separator)
        filtered = [w for w in words if w and not self.is_stopword(w)]
        return separator.join(filtered)
    
    def reload(self):
        """重新加载停用词（热重载）"""
        self.stopwords.clear()
        self.stopwords_sources.clear()
        self._load_all_stopwords()
        logger.info("停用词已重新加载")
    
    @classmethod
    def reset(cls):
        """重置单例（用于测试）"""
        cls._instance = None
        cls._initialized = False


# 全局停用词服务实例
stopwords_service = StopwordsService()