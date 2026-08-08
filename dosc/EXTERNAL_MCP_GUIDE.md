# 外部 MCP 服务器配置指南

## 概述

陈筱雪 Reborn 支持通过 JSON 配置文件连接外部 MCP (Model Context Protocol) 服务器，扩展 AI 助手的能力。

## 快速开始

### 1. 创建配置文件

在 `backend/config/` 目录下创建 `mcp_servers.json` 文件：

```json
{
  "mcpServers": {
    "bing_cn": {
      "type": "sse",
      "url": "https://mcp-bing-cn.ksai.scnet.cn:58043/sse",
      "enabled": true,
      "description": "必应中文搜索服务"
    }
  }
}
```

### 2. 重启后端服务

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

启动时你会看到：
```
INFO: ✅ 已从 config/mcp_servers.json 加载 MCP 服务器配置
INFO: 📝 已加载外部 MCP 服务器配置: bing_cn
INFO: ✅ 外部 MCP 服务器已连接: bing_cn (https://mcp-bing-cn.ksai.scnet.cn:58043/sse)
INFO: 🚀 外部 MCP 服务器管理器已初始化 (1 个服务器)
```

### 3. 验证连接

访问 API 端点查看外部服务器状态：

```bash
curl http://localhost:8000/mcp/external
```

返回示例：
```json
{
  "servers": {
    "bing_cn": {
      "type": "sse",
      "url": "https://mcp-bing-cn.ksai.scnet.cn:58043/sse",
      "enabled": true,
      "tools_count": 5,
      "connected": true
    }
  },
  "total": 1
}
```

## 配置格式详解

### 基本结构

```json
{
  "mcpServers": {
    "<服务器名称>": {
      "type": "<协议类型>",
      "url": "<SSE 服务器 URL>",
      "enabled": true|false,
      "description": "<可选描述>"
    }
  }
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | string | ✅ | 协议类型：`"sse"` 或 `"stdio"` |
| `url` | string | SSE 必填 | SSE 服务器的完整 URL |
| `command` | string | stdio 必填 | 启动命令（stdio 模式） |
| `args` | array | 否 | 命令参数（stdio 模式） |
| `env` | object | 否 | 环境变量 |
| `enabled` | boolean | 否 | 是否启用，默认 `true` |
| `description` | string | 否 | 服务器描述 |

### 支持的协议类型

#### 1. SSE (Server-Sent Events) - 推荐

适用于远程 HTTP 服务器：

```json
{
  "bing_cn": {
    "type": "sse",
    "url": "https://mcp-bing-cn.ksai.scnet.cn:58043/sse",
    "enabled": true
  }
}
```

#### 2. stdio (标准输入输出) - 待实现

适用于本地进程：

```json
{
  "local_tool": {
    "type": "stdio",
    "command": "python",
    "args": ["-m", "my_mcp_server"],
    "env": {
      "API_KEY": "your-api-key"
    },
    "enabled": true
  }
}
```

## 常见配置示例

### 1. 必应中文搜索

```json
{
  "mcpServers": {
    "bing_cn": {
      "type": "sse",
      "url": "https://mcp-bing-cn.ksai.scnet.cn:58043/sse",
      "enabled": true,
      "description": "必应中文搜索服务"
    }
  }
}
```

### 2. 多个服务器

```json
{
  "mcpServers": {
    "bing_cn": {
      "type": "sse",
      "url": "https://mcp-bing-cn.ksai.scnet.cn:58043/sse",
      "enabled": true,
      "description": "必应中文搜索"
    },
    "web_search": {
      "type": "sse",
      "url": "https://search.example.com/sse",
      "enabled": false,
      "description": "通用网页搜索（禁用）"
    },
    "memory_store": {
      "type": "sse",
      "url": "https://memory.example.com/sse",
      "enabled": true,
      "description": "外部记忆存储"
    }
  }
}
```

### 3. 临时禁用服务器

```json
{
  "mcpServers": {
    "test_server": {
      "type": "sse",
      "url": "https://test.example.com/sse",
      "enabled": false,
      "description": "测试服务器（已禁用）"
    }
  }
}
```

## API 使用

### 1. 获取外部服务器列表

```bash
GET /mcp/external
```

响应：
```json
{
  "servers": {
    "bing_cn": {
      "type": "sse",
      "url": "https://...",
      "enabled": true,
      "tools_count": 5,
      "connected": true
    }
  },
  "total": 1
}
```

### 2. 执行外部服务器的工具

```bash
POST /mcp/external/execute
Content-Type: application/json

{
  "server": "bing_cn",
  "tool": "search",
  "arguments": {
    "query": "人工智能最新进展",
    "count": 5
  }
}
```

响应：
```json
{
  "isError": false,
  "content": [
    {
      "type": "text",
      "text": "{...搜索结果...}"
    }
  ]
}
```

## 前端集成

### 在 App.tsx 中添加外部 MCP 面板

```tsx
import { ExternalMCPPanel } from './components/MCP/ExternalMCPPanel';
import './components/MCP/ExternalMCPPanel.css';

// 在设置页面或独立标签页中使用
{activeTab === 'external-mcp' && <ExternalMCPPanel />}
```

## 故障排查

### 问题 1: 服务器连接失败

**症状**: `connected: false`

**可能原因**:
- URL 错误
- 网络不通
- 服务器未启动
- SSL 证书问题

**解决**:
```bash
# 测试 URL 是否可访问
curl https://mcp-bing-cn.ksai.scnet.cn:58043/sse

# 检查后端日志
# 查看是否有连接错误信息
```

### 问题 2: 工具数量为 0

**症状**: `tools_count: 0`

**可能原因**:
- 服务器未正确暴露工具列表
- API 路径不匹配

**解决**:
- 检查外部服务器的 `/tools` 端点
- 查看 `external_server.py` 中的 `_discover_tools()` 方法

### 问题 3: 工具执行失败

**症状**: 调用工具时返回错误

**可能原因**:
- 参数格式不正确
- 工具不存在
- 服务器内部错误

**解决**:
```bash
# 查看详细错误信息
curl -X POST http://localhost:8000/mcp/external/execute \
  -H "Content-Type: application/json" \
  -d '{"server":"bing_cn","tool":"search","arguments":{}}'
```

## 安全注意事项

### 1. 不要提交敏感信息

`.gitignore` 中应包含：
```
backend/config/mcp_servers.json
```

使用 `.env` 文件存储 API Key：
```env
BING_API_KEY=your-secret-key
```

在配置中引用：
```json
{
  "env": {
    "API_KEY": "${BING_API_KEY}"
  }
}
```

### 2. 限制外部服务器权限

- 只连接可信的 MCP 服务器
- 启用必要的服务器（其他设为 `enabled: false`）
- 定期审查和更新配置

### 3. HTTPS 强制

生产环境中应使用 HTTPS 协议的 URL：
```json
{
  "url": "https://..."  // ✅ 推荐
  // "url": "http://..."  // ❌ 不安全
}
```

## 高级用法

### 1. 动态加载配置

可以通过 API 动态更新配置（需自行实现）：

```python
# 伪代码
@router.post("/mcp/external/reload")
async def reload_external_servers():
    external_mcp_manager.load_from_file()
    await external_mcp_manager.initialize_all()
    return {"status": "reloaded"}
```

### 2. 自定义工具发现逻辑

修改 `external_server.py` 中的 `_discover_tools()` 方法以适配不同的 MCP 服务器实现。

### 3. 工具缓存

对于频繁调用的工具，可以添加结果缓存以提高性能。

## 相关资源

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [陈筱雪 MCP 工具列表](http://localhost:8000/mcp/tools)

## 常见问题 (FAQ)

### Q: 支持哪些 MCP 服务器？

A: 理论上支持任何遵循 MCP 协议的服务器，包括：
- 官方 MCP 服务器
- 社区开发的第三方服务器
- 自定义实现的 MCP 服务器

### Q: 可以同时连接多少个外部服务器？

A: 没有硬性限制，但建议：
- 开发环境：3-5 个
- 生产环境：根据性能和需求调整

### Q: stdio 协议什么时候支持？

A: 目前仅完全支持 SSE 协议。stdio 支持正在开发中。

### Q: 如何调试外部服务器？

A: 
1. 查看后端日志中的连接信息
2. 使用 `curl` 直接测试外部服务器
3. 访问 `/mcp/external` 查看连接状态
4. 检查浏览器的 Network 标签

---

**最后更新**: 2026-05-05  
**版本**: 1.0