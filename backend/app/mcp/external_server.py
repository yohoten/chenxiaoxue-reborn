"""
外部 MCP 服务器管理器

支持通过 JSON 配置文件连接外部 MCP 服务器（SSE/stdio 协议）
"""

from __future__ import annotations

import json
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

import httpx
from app.utils.logger import logger


@dataclass
class ExternalMCPServer:
    """外部 MCP 服务器配置"""
    name: str
    server_type: str  # "sse" or "stdio"
    url: Optional[str] = None
    command: Optional[str] = None
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    tools: List[Dict[str, Any]] = field(default_factory=list)
    client: Optional[httpx.AsyncClient] = None
    
    async def initialize(self):
        """初始化连接"""
        if self.server_type == "sse" and self.url:
            self.client = httpx.AsyncClient(base_url=self.url, timeout=30.0)
            await self._discover_tools()
            logger.info(f"✅ 外部 MCP 服务器已连接: {self.name} ({self.url})")
        elif self.server_type == "stdio" and self.command:
            # TODO: 实现 stdio 协议支持
            logger.warning(f"⚠️  stdio 协议暂未完全支持: {self.name}")
    
    async def _discover_tools(self):
        """从 SSE 服务器发现可用工具"""
        if not self.client:
            return
        
        try:
            # 尝试获取工具列表（根据具体 MCP SSE 实现调整）
            response = await self.client.get("/tools")
            if response.status_code == 200:
                self.tools = response.json().get("tools", [])
                logger.info(f"📦 {self.name} 发现 {len(self.tools)} 个工具")
        except Exception as e:
            logger.warning(f"⚠️  无法从 {self.name} 获取工具列表: {e}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """调用外部服务器的工具"""
        if not self.client:
            raise RuntimeError(f"服务器 {self.name} 未初始化")
        
        try:
            response = await self.client.post(
                f"/tools/{tool_name}/call",
                json={"arguments": arguments},
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ 调用 {self.name}.{tool_name} 失败: {e}")
            raise
    
    async def close(self):
        """关闭连接"""
        if self.client:
            await self.client.aclose()
            logger.info(f"🔌 已断开外部 MCP 服务器: {self.name}")


class ExternalMCPServerManager:
    """
    外部 MCP 服务器管理器
    
    职责:
    1. 从 JSON 文件加载配置
    2. 管理多个外部服务器的生命周期
    3. 提供统一的工具调用接口
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.servers: Dict[str, ExternalMCPServer] = {}
        self.config_path = Path(config_path) if config_path else Path("config/mcp_servers.json")
        self._initialized = False
    
    def load_config(self, config_dict: Dict[str, Any]):
        """从字典加载配置"""
        mcp_servers = config_dict.get("mcpServers", {})
        
        for name, config in mcp_servers.items():
            server = ExternalMCPServer(
                name=name,
                server_type=config.get("type", "sse"),
                url=config.get("url"),
                command=config.get("command"),
                args=config.get("args", []),
                env=config.get("env", {}),
                enabled=config.get("enabled", True),
            )
            self.servers[name] = server
            logger.info(f"📝 已加载外部 MCP 服务器配置: {name}")
    
    def load_from_file(self, file_path: Optional[str] = None):
        """从 JSON 文件加载配置"""
        path = Path(file_path) if file_path else self.config_path
        
        if not path.exists():
            logger.warning(f"⚠️  MCP 服务器配置文件不存在: {path}")
            return
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                config = json.load(f)
            self.load_config(config)
            logger.info(f"✅ 已从 {path} 加载 MCP 服务器配置")
        except Exception as e:
            logger.error(f"❌ 加载 MCP 服务器配置失败: {e}")
    
    async def initialize_all(self):
        """初始化所有启用的服务器"""
        if self._initialized:
            return
        
        for name, server in self.servers.items():
            if server.enabled:
                try:
                    await server.initialize()
                except Exception as e:
                    logger.error(f"❌ 初始化外部服务器 {name} 失败: {e}")
        
        self._initialized = True
        logger.info(f"🚀 外部 MCP 服务器管理器已初始化 ({len(self.servers)} 个服务器)")
    
    async def shutdown_all(self):
        """关闭所有服务器连接"""
        for name, server in self.servers.items():
            try:
                await server.close()
            except Exception as e:
                logger.error(f"❌ 关闭外部服务器 {name} 失败: {e}")
        
        logger.info("👋 所有外部 MCP 服务器已断开连接")
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """获取所有外部服务器提供的工具"""
        all_tools = []
        for name, server in self.servers.items():
            if server.enabled and server.tools:
                for tool in server.tools:
                    # 添加工具来源标识
                    tool_with_source = tool.copy()
                    tool_with_source["_source"] = name
                    all_tools.append(tool_with_source)
        return all_tools
    
    async def execute_external_tool(
        self, 
        server_name: str, 
        tool_name: str, 
        arguments: Dict[str, Any]
    ) -> Any:
        """执行外部服务器的工具"""
        if server_name not in self.servers:
            raise ValueError(f"未知的外部服务器: {server_name}")
        
        server = self.servers[server_name]
        if not server.enabled:
            raise ValueError(f"外部服务器已禁用: {server_name}")
        
        return await server.call_tool(tool_name, arguments)
    
    def get_server_info(self) -> Dict[str, Any]:
        """获取所有服务器信息"""
        return {
            name: {
                "type": server.server_type,
                "url": server.url,
                "enabled": server.enabled,
                "tools_count": len(server.tools),
                "connected": server.client is not None,
            }
            for name, server in self.servers.items()
        }


# 全局单例
external_mcp_manager = ExternalMCPServerManager()