"""
MCP Tool 定义
每个 tool 是对外部能力的标准化封装
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


class ToolSchema:
    """Tool 的 JSON Schema 定义"""
    type: str = "object"
    properties: dict = field(default_factory=dict)
    required: list[str] = field(default_factory=list)


@dataclass
class MCPTool:
    """
    MCP 工具定义
    
    每个 Tool 对应一个可调用的 AI 能力
    """
    name: str                          # 工具名称 (唯一标识)
    description: str                   # 工具描述
    input_schema: dict                 # JSON Schema 输入格式
    handler: Callable                  # 处理函数
    
    # 可选元数据
    categories: list[str] = field(default_factory=list)
    timeout: int = 30                  # 超时秒数
    requires_auth: bool = False


# ── Tool: chat_completion ──────────────────────────────────

CHAT_COMPLETION_TOOL = MCPTool(
    name="chat_completion",
    description="与 AI 模型进行对话，支持多种模型和流式输出",
    input_schema={
        "type": "object",
        "properties": {
            "messages": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "role": {"type": "string", "enum": ["system", "user", "assistant"]},
                        "content": {"type": "string"},
                    },
                },
                "description": "OpenAI 格式的消息列表",
            },
            "model": {
                "type": "string",
                "description": "指定模型名称 (可选，默认自动路由)",
            },
            "stream": {
                "type": "boolean",
                "description": "是否流式输出",
                "default": False,
            },
            "temperature": {
                "type": "number",
                "description": "温度参数 (0-2)",
                "default": 0.7,
            },
        },
        "required": ["messages"],
    },
    handler=None,  # 运行时注入
    categories=["ai", "chat"],
)


# ── Tool: analyze_emotion ──────────────────────────────────

ANALYZE_EMOTION_TOOL = MCPTool(
    name="analyze_emotion",
    description="分析文本的情感状态，返回情感标签和置信度",
    input_schema={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "待分析的文本",
            },
            "method": {
                "type": "string",
                "enum": ["auto", "rule", "ai"],
                "description": "分析方法",
                "default": "auto",
            },
        },
        "required": ["text"],
    },
    handler=None,
    categories=["ai", "emotion"],
)


# ── Tool: translate_text ───────────────────────────────────

TRANSLATE_TOOL = MCPTool(
    name="translate_text",
    description="翻译文本到目标语言",
    input_schema={
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "待翻译文本"},
            "target_lang": {
                "type": "string",
                "enum": ["zh_CN", "en_US", "ja_JP"],
                "description": "目标语言",
            },
        },
        "required": ["text", "target_lang"],
    },
    handler=None,
    categories=["ai", "translate"],
)


# ── Tool: get_model_list ───────────────────────────────────

GET_MODELS_TOOL = MCPTool(
    name="get_model_list",
    description="获取所有可用的 AI 模型列表及其信息",
    input_schema={
        "type": "object",
        "properties": {},
    },
    handler=None,
    categories=["system"],
)


# ── Tool: analyze_dream ────────────────────────────────────

ANALYZE_DREAM_TOOL = MCPTool(
    name="analyze_dream",
    description="解析梦境内容，基于传统解梦学和心理学提供多维度解读",
    input_schema={
        "type": "object",
        "properties": {
            "dream_text": {
                "type": "string",
                "description": "梦境描述文本，越详细越好",
            },
            "use_ai": {
                "type": "boolean",
                "description": "是否使用 AI 增强分析（默认 true）",
                "default": True,
            },
        },
        "required": ["dream_text"],
    },
    handler=None,
    categories=["ai", "dream", "psychology"],
)


# ── Tool: memory_store ─────────────────────────────────────

MEMORY_STORE_TOOL = MCPTool(
    name="memory_store",
    description="存储重要信息到长期记忆，便于后续检索",
    input_schema={
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "要记忆的内容",
            },
            "category": {
                "type": "string",
                "enum": ["fact", "preference", "event", "conversation"],
                "description": "记忆分类",
                "default": "general",
            },
            "importance": {
                "type": "number",
                "description": "重要性评分 (0-1)",
                "default": 0.5,
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "标签列表，便于搜索",
                "default": [],
            },
        },
        "required": ["content"],
    },
    handler=None,
    categories=["memory", "storage"],
)


# ── Tool: memory_retrieve ──────────────────────────────────

MEMORY_RETRIEVE_TOOL = MCPTool(
    name="memory_retrieve",
    description="从长期记忆中检索相关信息",
    input_schema={
        "type": "object",
        "properties": {
            "keyword": {
                "type": "string",
                "description": "搜索关键词",
            },
            "category": {
                "type": "string",
                "description": "分类过滤（可选）",
            },
            "limit": {
                "type": "integer",
                "description": "返回数量限制",
                "default": 5,
            },
        },
        "required": ["keyword"],
    },
    handler=None,
    categories=["memory", "search"],
)


# ── Tool: filter_stopwords ─────────────────────────────────

FILTER_STOPWORDS_TOOL = MCPTool(
    name="filter_stopwords",
    description="过滤文本中的停用词，用于文本预处理",
    input_schema={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "待处理的文本",
            },
            "separator": {
                "type": "string",
                "description": "分词分隔符",
                "default": " ",
            },
        },
        "required": ["text"],
    },
    handler=None,
    categories=["text", "preprocessing"],
)


# ── Tool: get_memory_stats ─────────────────────────────────

GET_MEMORY_STATS_TOOL = MCPTool(
    name="get_memory_stats",
    description="获取自我改进记忆系统的统计信息，包括各层级记忆数量和最近活动",
    input_schema={
        "type": "object",
        "properties": {},
    },
    handler=None,
    categories=["memory", "self-improving"],
)


# ── Tool: search_memory ────────────────────────────────────

SEARCH_MEMORY_TOOL = MCPTool(
    name="search_memory",
    description="在所有记忆层级中搜索特定主题或关键词",
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "搜索查询词",
            },
            "tier": {
                "type": "string",
                "enum": ["all", "hot", "warm", "cold"],
                "description": "搜索范围（默认全部）",
                "default": "all",
            },
        },
        "required": ["query"],
    },
    handler=None,
    categories=["memory", "search", "self-improving"],
)


# ── Tool: forget_topic ─────────────────────────────────────

FORGET_TOPIC_TOOL = MCPTool(
    name="forget_topic",
    description="从所有记忆层级中删除指定主题的记忆（需要确认）",
    input_schema={
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "要遗忘的主题或关键词",
            },
            "confirm": {
                "type": "boolean",
                "description": "确认删除（必须为 true）",
                "default": False,
            },
        },
        "required": ["topic", "confirm"],
    },
    handler=None,
    categories=["memory", "self-improving"],
)


# ── Tool: collaborative_chat ───────────────────────────────

COLLABORATIVE_CHAT_TOOL = MCPTool(
    name="collaborative_chat",
    description="多模型协作模式 - 将复杂问题分解为多个子任务，由不同专业模型分工处理，最后聚合结果。适用于需要多维度分析的复杂问题。",
    input_schema={
        "type": "object",
        "properties": {
            "messages": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "role": {"type": "string", "enum": ["system", "user", "assistant"]},
                        "content": {"type": "string"},
                    },
                },
                "description": "OpenAI 格式的消息列表",
            },
            "enable_collaboration": {
                "type": "boolean",
                "description": "是否启用协作模式（默认 true）",
                "default": True,
            },
        },
        "required": ["messages"],
    },
    handler=None,
    categories=["ai", "collaboration", "advanced"],
)


# ── 所有工具注册表 ─────────────────────────────────────────

ALL_TOOLS: dict[str, MCPTool] = {
    tool.name: tool
    for tool in [
        CHAT_COMPLETION_TOOL,
        ANALYZE_EMOTION_TOOL,
        TRANSLATE_TOOL,
        GET_MODELS_TOOL,
        ANALYZE_DREAM_TOOL,
        MEMORY_STORE_TOOL,
        MEMORY_RETRIEVE_TOOL,
        FILTER_STOPWORDS_TOOL,
        GET_MEMORY_STATS_TOOL,
        SEARCH_MEMORY_TOOL,
        FORGET_TOPIC_TOOL,
        COLLABORATIVE_CHAT_TOOL,
    ]
}


def get_all_tool_definitions() -> list[dict]:
    """获取所有工具的标准化定义 (用于 MCP 协议响应)"""
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "inputSchema": tool.input_schema,
        }
        for tool in ALL_TOOLS.values()
    ]