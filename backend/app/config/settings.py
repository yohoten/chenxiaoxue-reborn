"""
全局配置管理
使用 Pydantic Settings 统一管理环境变量和配置
"""

from __future__ import annotations

import os
import secrets
from pathlib import Path
from typing import ClassVar, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    应用配置 - 从 .env 文件或环境变量加载
    
    优先级: 环境变量 > .env 文件 > 默认值
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ── 运行环境 ────────────────────────────────────────────
    ENV: str = "development"  # development | production
    DEBUG: bool = True

    # ── 服务器 ──────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # ── DeepSeek ────────────────────────────────────────────
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"

    # ── OpenAI ──────────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com"

    # ── 通义千问 ────────────────────────────────────────────
    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # ── 豆包/火山引擎 ──────────────────────────────────────
    DOUBAO_API_KEY: str = ""
    DOUBAO_BASE_URL: str = "https://ark.cn-beijing.volces.com/api/v3"

    # ── Kimi/月之暗面 ──────────────────────────────────────
    KIMI_API_KEY: str = ""
    KIMI_BASE_URL: str = "https://api.moonshot.cn"

    # ── Claude ──────────────────────────────────────────────
    CLAUDE_API_KEY: str = ""

    # ── 安全 ────────────────────────────────────────────────
    SECRET_KEY: str = ""  # 通过 .env 注入，生产环境必须使用强随机密钥

    @property
    def is_production(self) -> bool:
        """是否生产环境"""
        return self.ENV == "production"

    # ── 数据库 ──────────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/chenxiaoxue.db"

    # ── CORS ──────────────────────────────────────────────────
    CORS_ORIGINS: str = ""  # 额外的允许来源，逗号分隔

    # ── 路径 ────────────────────────────────────────────────
    RESOURCE_DIR: str = ""

    @property
    def BASE_DIR(self) -> Path:
        return Path(__file__).parent.parent.parent

    @property
    def DATA_DIR(self) -> Path:
        path = self.BASE_DIR / "data"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def DB_PATH(self) -> str:
        """返回 SQLite 数据库路径"""
        return f"sqlite+aiosqlite:///{self.DATA_DIR / 'chenxiaoxue.db'}"

    @property
    def RESOURCE_PATH(self) -> Path:
        """资源文件路径 - 优先使用新项目 resource 目录"""
        if self.RESOURCE_DIR:
            return Path(self.RESOURCE_DIR)
        
        # 默认指向当前项目根目录下的 resource 文件夹
        new_resource = self.BASE_DIR / "resource"
        if new_resource.exists():
            return new_resource
        
        # 回退到父目录的 resource（兼容性）
        parent_resource = self.BASE_DIR.parent / "resource"
        if parent_resource.exists():
            return parent_resource
        
        # 最后回退到旧项目路径
        old_resource = self.BASE_DIR.parent / "Chen Xiaoxue" / "resource"
        if old_resource.exists():
            return old_resource
        
        # 如果都不存在，返回当前目录下的 resource
        return self.BASE_DIR / "resource"

    # ── 占位符检测 ─────────────────────────────────────────
    PLACEHOLDER_PATTERNS: ClassVar[list[str]] = [
        "sk-your-",
        "your-",
        "sk-ant-",
    ]

    def _is_placeholder_key(self, api_key: str) -> bool:
        """检测是否是占位符 API Key，避免使用无效配置"""
        if not api_key:
            return True
        for pattern in self.PLACEHOLDER_PATTERNS:
            if api_key.startswith(pattern):
                return True
        # 过于短小的 key 也视为无效
        if len(api_key) < 8:
            return True
        return False

    def get_all_api_keys(self) -> dict[str, dict]:
        """
        获取所有真实已配置的 API Key（跳过占位符）
        
        Returns:
            {provider_name: {api_key, base_url, model_type, ...}}
        """
        providers = {}

        # DeepSeek (OpenAI 兼容格式)
        if not self._is_placeholder_key(self.DEEPSEEK_API_KEY):
            providers["deepseek"] = {
                "api_key": self.DEEPSEEK_API_KEY,
                "base_url": self.DEEPSEEK_BASE_URL,
                "endpoint": f"{self.DEEPSEEK_BASE_URL}/chat/completions",
                "models": ["deepseek-chat", "deepseek-reasoner"],
                "type": "openai_compatible",
            }

        # OpenAI
        if not self._is_placeholder_key(self.OPENAI_API_KEY):
            providers["openai"] = {
                "api_key": self.OPENAI_API_KEY,
                "base_url": self.OPENAI_BASE_URL,
                "endpoint": f"{self.OPENAI_BASE_URL}/v1/chat/completions",
                "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
                "type": "openai_compatible",
            }

        # 通义千问
        if not self._is_placeholder_key(self.QWEN_API_KEY):
            providers["qwen"] = {
                "api_key": self.QWEN_API_KEY,
                "base_url": self.QWEN_BASE_URL,
                "endpoint": f"{self.QWEN_BASE_URL}/chat/completions",
                "models": ["qwen-max", "qwen-plus", "qwen-turbo"],
                "type": "openai_compatible",
            }

        # 豆包/火山引擎 - API Key 格式 arK-xxxxx
        if not self._is_placeholder_key(self.DOUBAO_API_KEY):
            providers["doubao"] = {
                "api_key": self.DOUBAO_API_KEY,
                "base_url": self.DOUBAO_BASE_URL,
                "endpoint": f"{self.DOUBAO_BASE_URL}/chat/completions",
                # 注意：火山引擎 Ark 实际应使用 Endpoint ID 作为 model 参数
                "models": ["doubao-pro-32k", "doubao-pro-128k"],
                "type": "openai_compatible",
            }

        # Kimi/月之暗面
        if not self._is_placeholder_key(self.KIMI_API_KEY):
            providers["kimi"] = {
                "api_key": self.KIMI_API_KEY,
                "base_url": self.KIMI_BASE_URL,
                "endpoint": f"{self.KIMI_BASE_URL}/v1/chat/completions",
                "models": ["moonshot-v1-8k", "moonshot-v1-32k"],
                "type": "openai_compatible",
            }

        return providers


# 全局单例
settings = Settings()


# ── 启动时安全校验 ─────────────────────────────────────────
def _validate_settings():
    """启动时校验关键配置，不安全则拒绝启动"""
    errors: list[str] = []

    if not settings.SECRET_KEY or len(settings.SECRET_KEY) < 32:
        errors.append(
            "SECRET_KEY 未设置或长度不足（需 >= 32 字符）。"
            "请在 .env 文件中设置强随机密钥，例如: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
        )

    if settings.is_production:
        if settings.DEBUG:
            errors.append("生产环境 (ENV=production) 不应开启 DEBUG=True")
        if settings.SECRET_KEY == "your-secret-key-change-in-production":
            errors.append("生产环境禁止使用示例 SECRET_KEY，请生成强随机密钥")

    if errors:
        msg = "\n".join(f"  ❌ {e}" for e in errors)
        raise RuntimeError(f"配置校验失败，拒绝启动:\n{msg}")


_validate_settings()
