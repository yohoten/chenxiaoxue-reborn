"""
MCP (Model Context Protocol) 实现模块

Chen筱雪 MCP Server 提供:
- 标准 MCP 协议端点 (HTTP/SSE)
- AI 模型调用工具
- 数据分析工具
- 插件执行工具
"""

from .server import MCPServer

__all__ = ["MCPServer"]
