# API 文档快速使用指南

## 🚀 5分钟快速上手

### 1. 启动后端服务

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 2. 访问API文档

打开浏览器访问以下任一地址：

#### Swagger UI（推荐 - 交互式）
```
http://localhost:8000/docs
```
**特点**: 
- ✅ 可直接测试API
- ✅ 实时查看响应
- ✅ 完全中文化

#### ReDoc（美观 - 适合阅读）
```
http://localhost:8000/redoc
```
**特点**:
- ✅ 三栏布局更清晰
- ✅ 适合打印和分享
- ✅ 代码示例更详细

---

## 📖 主要功能模块

### 🔐 认证模块 (`/api/auth`)

**核心接口**:
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息
- `PUT /api/auth/me` - 更新用户信息

**快速测试**:
```bash
# 1. 注册用户
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test@1234",
    "nickname": "测试用户"
  }'

# 2. 登录获取Token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test@1234"
  }'

# 返回示例:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIs...",
#   "token_type": "bearer",
#   "expires_in": 3600
# }
```

### 💬 聊天模块 (`/api/chat`)

**核心接口**:
- `POST /api/chat/send` - 发送消息
- `GET /api/chat/history` - 获取历史记录
- `DELETE /api/chat/history` - 清空历史

**快速测试**:
```bash
# 发送消息（需要Token）
curl -X POST http://localhost:8000/api/chat/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "你好，陈筱雪！",
    "stream": false
  }'
```

### 🔌 MCP模块 (`/mcp`)

**核心接口**:
- `GET /mcp/info` - 服务器信息
- `GET /mcp/tools` - 工具列表
- `POST /mcp/execute` - 执行工具
- `POST /mcp/stream` - 流式执行

**快速测试**:
```bash
# 获取工具列表
curl http://localhost:8000/mcp/tools

# 执行聊天工具
curl -X POST http://localhost:8000/mcp/execute \
  -H "Content-Type: application/json" \
  -d '{
    "name": "chat_completion",
    "arguments": {
      "messages": [
        {"role": "user", "content": "你好"}
      ]
    }
  }'
```

---

## 🎯 在Swagger UI中测试

### 步骤1: 访问文档
打开 `http://localhost:8000/docs`

### 步骤2: 选择API分组
你会看到6个清晰的分组：
- 🔐 **auth** - 用户认证
- 💬 **chat** - 智能对话
- 🎭 **emotion** - 情感分析
- 🔌 **mcp** - MCP协议
- 🖼️ **resources** - 资源管理
- 🧠 **self-improving** - 自我进化

### 步骤3: 展开端点
点击任意端点（如 `POST /api/auth/register`）

### 步骤4: 点击 "Try it out"
右上角的蓝色按钮

### 步骤5: 填写参数
系统会提供示例值和字段说明

### 步骤6: 点击 "Execute"
发送请求并查看响应

### 步骤7: 查看结果
- **Response body**: JSON响应
- **Response headers**: 响应头
- **Curl**: 可复制的cURL命令

---

## 💡 实用技巧

### 技巧1: 保存Token
登录后，将Token复制到记事本，后续测试时使用：
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### 技巧2: 使用Authorize按钮
Swagger UI顶部有绿色的 "Authorize" 按钮：
1. 点击它
2. 输入: `Bearer YOUR_TOKEN`
3. 点击 "Authorize"
4. 之后的所有请求都会自动带上Token

### 技巧3: 查看模型定义
滚动到页面底部，可以看到所有Pydantic模型的详细定义：
- 字段类型
- 验证规则
- 示例值

### 技巧4: 下载OpenAPI Schema
访问 `http://localhost:8000/openapi.json` 可以：
- 生成客户端SDK
- 导入Postman
- 用于自动化测试

---

## 🐛 常见问题

### Q1: 为什么有些字段是红色的？
**A**: 表示必填字段，必须提供值才能执行。

### Q2: 如何查看详细的错误信息？
**A**: 在响应区域的 "Response body" 中查看，通常包含：
```json
{
  "detail": "具体的错误描述"
}
```

### Q3: Token过期了怎么办？
**A**: 重新调用 `/api/auth/login` 获取新Token。

### Q4: 如何测试流式响应？
**A**: 
1. 使用 `POST /mcp/stream` 端点
2. 或在代码中使用EventSource：
```javascript
const es = new EventSource('/mcp/stream');
es.onmessage = (e) => console.log(JSON.parse(e.data));
```

### Q5: 文档加载很慢？
**A**: 首次加载需要从CDN下载资源，后续会使用缓存。也可以：
- 清除浏览器缓存后刷新
- 使用无痕模式测试
- 检查网络连接

---

## 📚 进阶学习

### 阅读完整文档
- [API文档优化报告](./API_DOCS_OPTIMIZATION.md)
- [模型协作功能指南](./MODEL_COLLABORATION_GUIDE.md)
- [UI优化方案](./UI_OPTIMIZATION_PLAN.md)

### 查看源代码
- [主应用配置](../backend/app/main.py)
- [聊天路由](../backend/app/routers/chat.py)
- [MCP路由](../backend/app/routers/mcp.py)

### 外部资源
- [FastAPI官方文档](https://fastapi.tiangolo.com/zh/)
- [Swagger UI文档](https://swagger.io/docs/open-source-tools/swagger-ui/)
- [OpenAPI规范](https://swagger.io/specification/)

---

## 🎊 总结

优化后的API文档具备：

✅ **完全中文** - 所有文本、说明、错误消息  
✅ **结构清晰** - 6个功能分组，层次分明  
✅ **易于测试** - 交互式界面，一键执行  
✅ **示例丰富** - cURL、JavaScript代码示例  
✅ **视觉友好** - Emoji图标、代码高亮  

**立即体验**: http://localhost:8000/docs 🚀

---

*最后更新: 2026-05-06*  
*版本: v1.0.0*