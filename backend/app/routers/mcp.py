"""
MCP 协议端点

提供兼容 MCP (Model Context Protocol) 的 HTTP API，支持：
- 工具发现和列表查询
- 同步和流式工具执行
- 外部 MCP 服务器集成
- SSE 实时响应推送

## MCP 协议简介

MCP (Model Context Protocol) 是一个开放协议，允许 AI 模型发现和调用外部工具。
本实现遵循官方规范，提供标准化的工具调用接口。

## 核心功能

1. **工具发现** (`GET /mcp/tools`) - 获取所有可用工具列表
2. **工具执行** (`POST /mcp/execute`) - 同步执行工具
3. **流式执行** (`POST /mcp/stream`) - SSE 流式执行，适合长时间任务
4. **外部集成** (`GET /mcp/external`) - 管理外部 MCP 服务器
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.mcp.server import mcp_server
from app.mcp.external_server import external_mcp_manager
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.utils.logger import logger

router = APIRouter(
    prefix="/mcp",
    tags=["mcp"],
    responses={
        404: {"description": "工具未找到"},
        500: {"description": "工具执行失败"},
    },
)


class ExecuteRequest(BaseModel):
    """工具执行请求模型"""
    name: str = Field(
        ...,
        description="工具名称",
        examples=["chat_completion", "analyze_emotion", "collaborative_chat"]
    )
    arguments: dict = Field(
        default={},
        description="工具参数（根据工具定义）",
        examples=[{
            "messages": [
                {"role": "user", "content": "你好"}
            ]
        }]
    )


class ExternalExecuteRequest(BaseModel):
    """外部服务器工具执行请求模型"""
    server: str = Field(
        ...,
        description="外部服务器名称",
        examples=["weather-server", "github-tools"]
    )
    tool: str = Field(
        ...,
        description="工具名称",
        examples=["get_weather", "search_repos"]
    )
    arguments: dict = Field(
        default={},
        description="工具参数"
    )


@router.get(
    "/info",
    summary="获取MCP服务器信息",
    description="返回MCP服务器的基本信息，包括名称、版本、描述和可用工具数量",
    response_description="包含服务器元数据的JSON对象",
)
async def get_mcp_info():
    """获取 MCP 服务器信息"""
    return mcp_server.get_info()


@router.get(
    "/tools",
    summary="获取工具列表",
    description="""
获取所有可用的 MCP 工具列表及其详细定义。

每个工具包含：
- `name`: 工具唯一标识
- `description`: 工具功能描述
- `inputSchema`: JSON Schema 格式的输入参数定义

**可用工具**:
- `chat_completion`: AI 对话补全
- `analyze_emotion`: 情感分析
- `translate_text`: 文本翻译
- `get_model_list`: 获取模型列表
- `analyze_dream`: 梦境解析
- `memory_store`: 存储记忆
- `memory_retrieve`: 检索记忆
- `filter_stopwords`: 过滤停用词
- `get_memory_stats`: 获取记忆统计
- `search_memory`: 搜索记忆
- `forget_topic`: 遗忘主题
- `collaborative_chat`: 多模型协作聊天
""",
    response_description="包含工具列表的JSON对象",
)
async def list_mcp_tools():
    """获取所有可用的 MCP 工具"""
    return {
        "tools": mcp_server.list_tools(),
    }


@router.post(
    "/execute",
    summary="执行MCP工具",
    description="""
同步执行指定的 MCP 工具。

**使用示例**:

```bash
curl -X POST http://localhost:8000/mcp/execute \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "chat_completion",
    "arguments": {
      "messages": [{"role": "user", "content": "你好"}]
    }
  }'
```

**注意**: 
- 对于长时间运行的任务，建议使用 `/mcp/stream` 端点
- 工具执行超时时间为30秒（可配置）
""",
    response_description="工具执行结果，格式为MCP标准响应",
)
async def execute_mcp_tool(
    req: ExecuteRequest,
    current_user: User = Depends(get_current_user)
):
    """执行 MCP 工具"""
    logger.info(f"MCP 执行工具: {req.name} (用户: {current_user.id})")
    # 为记忆相关操作注入当前用户ID
    if req.name in ("memory_store", "memory_retrieve"):
        req.arguments["user_id"] = str(current_user.id)
    result = await mcp_server.execute_tool(req.name, req.arguments)
    return result


@router.post(
    "/stream",
    summary="流式执行MCP工具（SSE）",
    description="""
使用 Server-Sent Events (SSE) 流式执行 MCP 工具。

适用于：
- 长时间运行的任务
- 需要实时反馈的场景
- 大型数据处理

**SSE 事件格式**:
```
data: {"content": "部分结果", "done": false}

data: {"content": "", "done": true}
```

**使用示例**:

```javascript
const eventSource = new EventSource('/mcp/stream', {
  headers: {
    'Content-Type': 'application/json'
  }
});

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.done) {
    eventSource.close();
  } else {
    console.log(data.content);
  }
};
```
""",
    response_description="SSE 流式响应",
)
async def stream_mcp_tool(
    req: ExecuteRequest,
    current_user: User = Depends(get_current_user)
):
    """流式执行 MCP 工具 (SSE)"""
    logger.info(f"MCP 流式执行工具: {req.name} (用户: {current_user.id})")
    
    # 为记忆相关操作注入当前用户ID
    if req.name in ("memory_store", "memory_retrieve"):
        req.arguments["user_id"] = str(current_user.id)
    
    return StreamingResponse(
        mcp_server.execute_tool_stream(req.name, req.arguments),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )