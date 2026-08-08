"""
应用常量定义
"""

from pathlib import Path

from .settings import settings


class Constants:
    """集中管理所有魔法数字和常量"""

    # ── 窗口 ────────────────────────────────────────────────
    WINDOW_DEFAULT_WIDTH = 1200
    WINDOW_DEFAULT_HEIGHT = 700
    WINDOW_MIN_WIDTH = 800
    WINDOW_MIN_HEIGHT = 600

    # ── 背景轮播 ────────────────────────────────────────────
    BACKGROUND_SWITCH_INTERVAL = 30000  # 毫秒

    # ── 聊天 ────────────────────────────────────────────────
    MESSAGE_MAX_LENGTH = 5000
    CONTEXT_HISTORY_LIMIT = 50
    TYPEWRITER_DELAY = 50  # 打字机效果延迟（毫秒）

    # ── 情感分析 ────────────────────────────────────────────
    EMOTION_LABELS = [
        "ecstatic", "happy", "content", "neutral",
        "confused", "sad", "angry", "embarrassed", "surprised",
    ]
    MAX_TEXT_LENGTH_FOR_ANALYSIS = 500

    # ── API ─────────────────────────────────────────────────
    API_TIMEOUT = 60  # 秒
    API_MAX_RETRIES = 3
    STREAM_CHUNK_SIZE = 50  # SSE 流式传输块大小

    # ── MCP ─────────────────────────────────────────────────
    MCP_SERVER_NAME = "chenxiaoxue-mcp"
    MCP_SERVER_VERSION = "1.0.0"
    MCP_MAX_TOOLS_PER_REQUEST = 10

    # ── 国际化 ──────────────────────────────────────────────
    DEFAULT_LANGUAGE = "zh_CN"
    SUPPORTED_LANGUAGES = {
        "zh_CN": "简体中文",
        "en_US": "English",
        "ja_JP": "日本語",
    }

    # ── 导出 ────────────────────────────────────────────────
    EXPORT_FORMATS = ["json", "txt", "csv", "html"]
