"""
MCP Server 实现

提供标准 MCP 协议端点:
- GET  /mcp/info      - 服务器信息
- GET  /mcp/tools     - 工具列表
- POST /mcp/execute   - 执行工具
- POST /mcp/chat      - MCP 兼容的聊天端点
"""

from __future__ import annotations

import json
from typing import Any, AsyncGenerator

from app.mcp.tools import ALL_TOOLS, get_all_tool_definitions
from app.mcp.external_server import external_mcp_manager
from app.services.ai_router import TaskType, Complexity, ai_router
from app.services.emotion_service import emotion_service
from app.services.dream_service import dream_service
from app.services.memory_service import memory_service
from app.services.stopwords_service import stopwords_service
from app.self_improving import get_manager
from app.config.constants import Constants
from app.utils.logger import logger


class MCPServer:
    """
    MCP 协议服务器
    
    职责:
    1. 对外暴露 MCP 标准接口
    2. 管理 Tool 注册和调用
    3. 桥接 AI 模型和 MCP 客户端
    """

    def __init__(self):
        self.name = Constants.MCP_SERVER_NAME
        self.version = Constants.MCP_SERVER_VERSION
        self._initialized_external = False
        self._init_handlers()
    
    async def initialize_external_servers(self):
        """初始化外部 MCP 服务器"""
        if self._initialized_external:
            return
        
        # 加载配置文件
        external_mcp_manager.load_from_file()
        
        # 初始化所有外部服务器
        await external_mcp_manager.initialize_all()
        
        self._initialized_external = True
        logger.info("✅ 外部 MCP 服务器已初始化")

    def _init_handlers(self):
        """初始化所有 Tool 的处理函数"""
        # 防御性检查：确保 ALL_TOOLS 不为空
        if not ALL_TOOLS:
            logger.warning("⚠️ ALL_TOOLS 为空，可能是导入顺序问题")
            return
        
        # 注入 chat_completion handler
        if "chat_completion" in ALL_TOOLS:
            ALL_TOOLS["chat_completion"].handler = self._handle_chat_completion
        else:
            logger.warning("⚠️ chat_completion 工具未注册")
        
        if "analyze_emotion" in ALL_TOOLS:
            ALL_TOOLS["analyze_emotion"].handler = self._handle_analyze_emotion
        
        if "translate_text" in ALL_TOOLS:
            ALL_TOOLS["translate_text"].handler = self._handle_translate
        
        if "get_model_list" in ALL_TOOLS:
            ALL_TOOLS["get_model_list"].handler = self._handle_get_models
        
        # 新增工具 handlers
        if "analyze_dream" in ALL_TOOLS:
            ALL_TOOLS["analyze_dream"].handler = self._handle_analyze_dream
        
        if "memory_store" in ALL_TOOLS:
            ALL_TOOLS["memory_store"].handler = self._handle_memory_store
        
        if "memory_retrieve" in ALL_TOOLS:
            ALL_TOOLS["memory_retrieve"].handler = self._handle_memory_retrieve
        
        if "filter_stopwords" in ALL_TOOLS:
            ALL_TOOLS["filter_stopwords"].handler = self._handle_filter_stopwords
        
        # Self-Improving tools handlers
        if "get_memory_stats" in ALL_TOOLS:
            ALL_TOOLS["get_memory_stats"].handler = self._handle_get_memory_stats
        
        if "search_memory" in ALL_TOOLS:
            ALL_TOOLS["search_memory"].handler = self._handle_search_memory
        
        if "forget_topic" in ALL_TOOLS:
            ALL_TOOLS["forget_topic"].handler = self._handle_forget_topic
        
        # 协作聊天工具 handler
        if "collaborative_chat" in ALL_TOOLS:
            ALL_TOOLS["collaborative_chat"].handler = self._handle_collaborative_chat
        
        logger.info(f"✅ MCP 工具处理器初始化完成，共 {len(ALL_TOOLS)} 个工具")

    # ── MCP 协议端点 ─────────────────────────────────────

    def get_info(self) -> dict:
        """MCP 服务器信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": "Chen筱雪 AI 助手 MCP Server",
            "tools_count": len(ALL_TOOLS),
        }

    def list_tools(self) -> list[dict]:
        """获取所有可用的 Tool"""
        return get_all_tool_definitions()

    async def execute_tool(
        self, tool_name: str, arguments: dict
    ) -> dict:
        """
        执行指定的 Tool
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            MCP 格式的工具执行结果
        """
        if tool_name not in ALL_TOOLS:
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Tool not found: {tool_name}"}],
            }

        tool = ALL_TOOLS[tool_name]

        try:
            result = await tool.handler(**arguments)
            return {
                "isError": False,
                "content": [{"type": "text", "text": result}],
            }
        except Exception as e:
            logger.error(f"MCP Tool {tool_name} 执行失败: {e}")
            return {
                "isError": True,
                "content": [{"type": "text", "text": str(e)}],
            }

    async def execute_tool_stream(
        self, tool_name: str, arguments: dict
    ) -> AsyncGenerator[str, None]:
        """
        流式执行 Tool (SSE)
        
        目前仅 chat_completion 支持流式
        """
        if tool_name == "chat_completion" and arguments.get("stream"):
            messages = arguments["messages"]
            preferred = arguments.get("model")

            # 调用 AI Router 流式接口
            stream = await ai_router.chat_completion(
                messages=messages,
                task_type=TaskType.CHAT,
                complexity=Complexity.SIMPLE,
                preferred_provider=preferred,
                stream=True,
            )

            async for chunk in stream:
                yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"

            yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
        else:
            result = await self.execute_tool(tool_name, arguments)
            yield f"data: {json.dumps({**result, 'done': True})}\n\n"

    # ── Tool 处理函数 ─────────────────────────────────────

    async def _handle_chat_completion(
        self,
        messages: list[dict],
        model: str | None = None,
        stream: bool = False,
        temperature: float = 0.7,
        **kwargs,
    ) -> str:
        """处理聊天补全请求"""
        preferred = None
        complexity = Complexity.MEDIUM

        # 如果指定了模型，确定提供方
        if model:
            for provider, config in ai_router.get_providers().items():
                if model in config.get("models", []):
                    preferred = provider
                    break

        result = await ai_router.chat_completion(
            messages=messages,
            task_type=TaskType.CHAT,
            complexity=complexity,
            preferred_provider=preferred,
            stream=False,
        )

        # 构建 MCP 格式响应
        response_data = {
            "response": result["response"],
            "model": result["model_name"],
            "provider": result["provider"],
            "usage": result["usage"],
            "latency_ms": result["latency_ms"],
        }

        return json.dumps(response_data, ensure_ascii=False)

    async def _handle_analyze_emotion(
        self, text: str, method: str = "auto"
    ) -> str:
        """处理情感分析请求"""
        result = await emotion_service.analyze(text, method)
        return json.dumps(result.model_dump(), ensure_ascii=False)

    async def _handle_translate(
        self, text: str, target_lang: str
    ) -> str:
        """处理翻译请求"""
        messages = [
            {
                "role": "system",
                "content": (
                    f"你是一个翻译助手。请将以下文本翻译成"
                    f"{Constants.SUPPORTED_LANGUAGES.get(target_lang, target_lang)}。"
                    "只需返回翻译结果，不要其他内容。"
                ),
            },
            {"role": "user", "content": text},
        ]

        result = await ai_router.chat_completion(
            messages=messages,
            task_type=TaskType.TRANSLATE,
            complexity=Complexity.SIMPLE,
        )

        return json.dumps(
            {
                "original_text": text,
                "translated_text": result["response"],
                "target_language": target_lang,
                "model": result["model_name"],
            },
            ensure_ascii=False,
        )

    async def _handle_get_models(self, **kwargs) -> str:
        """处理获取模型列表请求"""
        models = ai_router.get_available_models()
        return json.dumps(models, ensure_ascii=False)

    async def _handle_analyze_dream(
        self, dream_text: str, use_ai: bool = True
    ) -> str:
        """处理梦境解析请求"""
        result = dream_service.analyze_dream(dream_text, use_ai)
        return json.dumps(result, ensure_ascii=False)

    async def _handle_memory_store(
        self,
        content: str,
        category: str = "general",
        importance: float = 0.5,
        tags: list[str] = None,
        user_id: str = None
    ) -> str:
        """处理记忆存储请求"""
        # 优先使用调用方传入的 user_id，否则回退到默认值
        actual_user_id = user_id or "default_user"
        logger.info(f"存储记忆: user={actual_user_id}, category={category}")
        
        memory = memory_service.store_memory(
            user_id=actual_user_id,
            content=content,
            category=category,
            importance=importance,
            tags=tags or []
        )
        
        return json.dumps({
            "success": True,
            "memory_id": memory.id,
            "user_id": actual_user_id,
            "message": "记忆已存储"
        }, ensure_ascii=False)

    async def _handle_memory_retrieve(
        self,
        keyword: str,
        category: str = None,
        limit: int = 5,
        user_id: str = None
    ) -> str:
        """处理记忆检索请求"""
        # 优先使用调用方传入的 user_id，否则回退到默认值
        actual_user_id = user_id or "default_user"
        logger.info(f"检索记忆: user={actual_user_id}, keyword={keyword}")
        
        memories = memory_service.search_memories(
            user_id=actual_user_id,
            keyword=keyword,
            limit=limit
        )
        
        return json.dumps({
            "success": True,
            "count": len(memories),
            "user_id": actual_user_id,
            "memories": [m.to_dict() for m in memories]
        }, ensure_ascii=False)

    async def _handle_filter_stopwords(
        self, text: str, separator: str = " "
    ) -> str:
        """处理停用词过滤请求"""
        filtered_text = stopwords_service.filter_text(text, separator)
        
        return json.dumps({
            "original": text,
            "filtered": filtered_text,
            "removed_count": len(text.split(separator)) - len(filtered_text.split(separator)) if separator else 0
        }, ensure_ascii=False)

    async def _handle_get_memory_stats(self, **kwargs) -> str:
        """处理获取记忆统计信息请求"""
        manager = get_manager()
        stats = manager.get_stats()
        
        return json.dumps({
            "success": True,
            "stats": stats
        }, ensure_ascii=False)

    async def _handle_search_memory(
        self, query: str, tier: str = "all"
    ) -> str:
        """处理记忆搜索请求"""
        manager = get_manager()
        results = manager.storage.search_memory(query)
        
        # Filter by tier if specified
        if tier != "all":
            results = [r for r in results if r["tier"].lower() == tier.lower()]
        
        return json.dumps({
            "success": True,
            "query": query,
            "count": len(results),
            "results": results
        }, ensure_ascii=False)

    async def _handle_forget_topic(
        self, topic: str, confirm: bool = False
    ) -> str:
        """处理遗忘主题请求"""
        if not confirm:
            return json.dumps({
                "success": False,
                "message": "需要确认删除操作。请设置 confirm=true 以继续。"
            }, ensure_ascii=False)
        
        manager = get_manager()
        removed = manager.forget_topic(topic)
        
        return json.dumps({
            "success": True,
            "topic": topic,
            "removed": removed,
            "message": f"已{'删除' if removed else '未找到'}关于 '{topic}' 的记忆"
        }, ensure_ascii=False)

    async def _handle_collaborative_chat(
        self,
        messages: list[dict],
        enable_collaboration: bool = True,
        **kwargs,
    ) -> str:
        """处理协作聊天请求"""
        try:
            result = await ai_router.collaborative_chat(
                messages=messages,
                task_type=TaskType.COMPLEX,
                enable_collaboration=enable_collaboration,
            )
            
            return json.dumps(result, ensure_ascii=False, default=str)
        
        except Exception as e:
            logger.error(f"协作聊天失败: {e}")
            return json.dumps({
                "error": str(e),
                "fallback_message": "协作模式执行失败，建议使用标准对话模式",
            }, ensure_ascii=False)


# 全局单例
mcp_server = MCPServer()
