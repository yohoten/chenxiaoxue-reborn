"""
Chen筱雪 Reborn - FastAPI 应用入口

启动方式:
    uvicorn app.main:app --reload --port 8000
"""

from __future__ import annotations

import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

# 确保 app 包可被导入：无论从 backend 还是 backend/app 目录直接运行 python main.py，
# 都将 backend/ 加入 sys.path（app 包的父目录）
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config.settings import settings
from app.routers import chat, emotion, mcp, resources, self_improving, auth, humanizer, brain, dream
from app.services.database import init_db, close_db
from app.utils.logger import logger

# ── 限流器 ──────────────────────────────────────────────────
# 暂时禁用，避免 .env 编码问题
# limiter = Limiter(
#     key_func=get_remote_address,
#     default_limits=["60/minute"],
#     headers_enabled=True,
# )
limiter = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("🚀 Chen筱雪 Reborn 启动中...")
    await init_db()
    logger.info("✅ 数据库初始化完成")

    # 初始化外部 MCP 服务器
    from app.mcp.server import mcp_server
    await mcp_server.initialize_external_servers()

    logger.info(f"🔌 MCP Server 已就绪: {settings.HOST}:{settings.PORT}/mcp")
    logger.info(f"📚 API 文档: {settings.HOST}:{settings.PORT}/docs")
    yield
    # 关闭时
    await close_db()

    # 关闭外部 MCP 服务器
    from app.mcp.external_server import external_mcp_manager
    await external_mcp_manager.shutdown_all()

    # 关闭 AI Router HTTP 连接池
    from app.services.ai_router import ai_router
    await ai_router.close_http_client()

    logger.info("👋 Chen筱雪 Reborn 已关闭")


app = FastAPI(
    title="陈筱雪 Reborn API",
    description="""
## 🌟 陈筱雪 AI 助手后端 API

基于 FastAPI + MCP 协议的多模型智能 AI 助手后端服务。

### ✨ 核心特性

- **🤖 多模型智能路由**: 支持 DeepSeek、OpenAI、通义千问、豆包、Kimi、Claude 等6大供应商
- **🔌 MCP 协议支持**: 标准化的 Model Context Protocol 工具调用
- **💬 智能对话**: SSE 流式响应，支持历史管理和情感分析
- **🎯 模型协作**: 复杂问题分解为多个子任务，多模型分工协作
- **📊 资源管理**: GIF 动态背景轮播和角色动画管理

### 📚 API 分组

1. **认证模块** (`/api/auth`) - 用户注册、登录、Token管理
2. **聊天模块** (`/api/chat`) - 消息发送、历史记录、流式响应
3. **情感模块** (`/api/emotion`) - 情感分析、ECG状态
4. **MCP模块** (`/mcp`) - 工具发现、执行、流式调用
5. **资源模块** (`/api/resources`) - 背景图片、角色动画
6. **自我进化** (`/api/self-improving`) - 记忆管理、学习反馈
7. **文本人性化** (`/api/humanizer`) - AI 文本检测与人性化改写
8. **第二大脑** (`/api/brain`) - 个人知识管理与实体记忆

### 🔧 快速开始

```bash
# 启动后端服务
cd backend
uvicorn app.main:app --reload --port 8000

# 访问文档
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### 📖 相关文档

- [项目 README](/)
- [MCP 协议说明](/mcp/info)
- [GitHub Repository](https://github.com/your-repo)

---

*版本: 1.0.0 | 最后更新: 2026-05-06*
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_url="/openapi.json",  # OpenAPI schema
    openapi_tags=[
        {
            "name": "auth",
            "description": "🔐 用户认证 - 注册、登录、Token管理",
        },
        {
            "name": "chat",
            "description": "💬 智能对话 - 消息发送、历史记录、流式响应",
        },
        {
            "name": "emotion",
            "description": "🎭 情感分析 - 情感识别、ECG状态展示",
        },
        {
            "name": "mcp",
            "description": "🔌 MCP协议 - 工具发现、执行、流式调用",
        },
        {
            "name": "resources",
            "description": "🖼️ 资源管理 - 背景图片、角色动画",
        },
        {
            "name": "self-improving",
            "description": "🧠 自我进化 - 记忆存储、检索、遗忘",
        },
        {
            "name": "humanizer",
            "description": "✍️ 文本人性化 - AI 写作模式检测与人性化改写",
        },
        {
            "name": "brain",
            "description": "🧠 第二大脑 - 个人知识库管理与实体记忆",
        },
    ],
    contact={
        "name": "陈筱雪 AI 助手开发团队",
        "url": "https://github.com/your-repo",
        "email": "dev@chenxiaoxue.ai",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# ── CORS 配置 ──────────────────────────────────────────────
# 浏览器不允许 allow_credentials=True 与 allow_origins=["*"] 同时使用
ALLOWED_ORIGINS: list[str] = [
    "http://localhost:5173",       # Vite 开发服务器
    "http://localhost:1420",       # Tauri 开发窗口
    "http://localhost:8000",       # API 文档
    "tauri://localhost",           # Tauri 生产环境
    "https://tauri.localhost",     # Tauri 生产环境 (https)
]

# 从环境变量追加额外的来源（逗号分隔）
if settings.CORS_ORIGINS:
    ALLOWED_ORIGINS.extend(o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip())

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"] if settings.is_production else ["*"],
    allow_headers=["*"],
)

# ── 添加 X-Request-ID 中间件 ─────────────────────────────────
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """为每个请求注入唯一 ID，方便问题追踪"""
    import uuid
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """添加安全响应头"""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    if settings.is_production:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# ── 请求体大小限制中间件 ──────────────────────────────────
from fastapi import Request, status
from fastapi.responses import JSONResponse

MAX_BODY_SIZE = 5 * 1024 * 1024  # 5 MB


@app.middleware("http")
async def limit_body_size(request: Request, call_next):
    """限制请求体大小，防止大 payload 攻击"""
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > MAX_BODY_SIZE:
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={"detail": f"请求体过大，最大允许 {MAX_BODY_SIZE // 1024 // 1024} MB"},
                )
        except ValueError:
            pass
    return await call_next(request)


# ── 限流器 ──────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── 注册路由 ───────────────────────────────────────────────
app.include_router(auth.router)  # 认证路由（优先注册）
app.include_router(chat.router)
app.include_router(emotion.router)
app.include_router(mcp.router)
app.include_router(resources.router)
app.include_router(self_improving.router)
app.include_router(humanizer.router)
app.include_router(brain.router)
app.include_router(humanizer.router)
app.include_router(brain.router)
app.include_router(dream.router)


# ── 健康检查端点 ───────────────────────────────────────────
@app.get("/health", include_in_schema=True, tags=["system"])
async def health_check():
    """系统健康检查"""
    from app.services.ai_router import ai_router

    models_available = len([m for m in ai_router.models if m.is_available])
    db_ok = True  # 如果数据库有问题，前面的 init_db 已经抛异常了

    return {
        "status": "ok",
        "version": "1.0.0",
        "env": settings.ENV,
        "db": "connected" if db_ok else "disconnected",
        "models_available": models_available,
        "timestamp": time.time(),
    }


# ── 自定义 Swagger UI 配置 ─────────────────────────────────
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    """自定义OpenAPI schema，添加中文优化"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # 添加自定义配置
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png",
        "altText": "陈筱雪 AI 助手"
    }
    
    # 添加服务器信息
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "本地开发环境"
        },
        {
            "url": "https://api.chenxiaoxue.ai",
            "description": "生产环境"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    自定义 Swagger UI - 中文版
    
    提供优化的中文界面和更好的用户体验
    """
    from fastapi.openapi.docs import get_swagger_ui_html
    
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="陈筱雪 AI 助手 - API 文档",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """
    ReDoc 文档 - 中文版
    
    提供更美观、更易读的API文档
    """
    from fastapi.openapi.docs import get_redoc_html
    
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="陈筱雪 AI 助手 - API 参考文档",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
        redoc_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )


@app.get("/schema", include_in_schema=False)
async def schema_viewer_html():
    """
    OpenAPI Schema 可视化查看器
    
    提供友好的JSON格式化和导航功能
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>陈筱雪 API - Schema 查看器</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 28px;
                margin-bottom: 10px;
            }
            
            .header p {
                font-size: 14px;
                opacity: 0.9;
            }
            
            .toolbar {
                background: #f8f9fa;
                padding: 15px 30px;
                border-bottom: 1px solid #e9ecef;
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 15px;
                flex-wrap: wrap;
            }
            
            .toolbar-group {
                display: flex;
                gap: 10px;
                align-items: center;
            }
            
            .btn {
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.3s;
                display: inline-flex;
                align-items: center;
                gap: 6px;
            }
            
            .btn-primary {
                background: #667eea;
                color: white;
            }
            
            .btn-primary:hover {
                background: #5568d3;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }
            
            .btn-secondary {
                background: #6c757d;
                color: white;
            }
            
            .btn-secondary:hover {
                background: #5a6268;
            }
            
            .btn-success {
                background: #28a745;
                color: white;
            }
            
            .btn-success:hover {
                background: #218838;
            }
            
            .stats {
                display: flex;
                gap: 20px;
                font-size: 13px;
                color: #6c757d;
            }
            
            .stat-item {
                display: flex;
                align-items: center;
                gap: 5px;
            }
            
            .content {
                padding: 30px;
            }
            
            .tabs {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
                border-bottom: 2px solid #e9ecef;
            }
            
            .tab {
                padding: 12px 24px;
                cursor: pointer;
                border: none;
                background: transparent;
                font-size: 14px;
                color: #6c757d;
                border-bottom: 3px solid transparent;
                transition: all 0.3s;
            }
            
            .tab.active {
                color: #667eea;
                border-bottom-color: #667eea;
                font-weight: 600;
            }
            
            .tab:hover {
                color: #667eea;
            }
            
            .tab-content {
                display: none;
            }
            
            .tab-content.active {
                display: block;
            }
            
            pre {
                background: #1e1e2e;
                color: #cdd6f4;
                padding: 20px;
                border-radius: 8px;
                overflow-x: auto;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
                line-height: 1.6;
                max-height: 600px;
                overflow-y: auto;
            }
            
            .info-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .info-card {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }
            
            .info-card h3 {
                color: #667eea;
                margin-bottom: 10px;
                font-size: 16px;
            }
            
            .info-card p {
                color: #6c757d;
                font-size: 14px;
                line-height: 1.6;
            }
            
            .endpoints-list {
                display: grid;
                gap: 15px;
            }
            
            .endpoint-item {
                background: #f8f9fa;
                padding: 15px 20px;
                border-radius: 8px;
                border-left: 4px solid #28a745;
                transition: all 0.3s;
            }
            
            .endpoint-item:hover {
                transform: translateX(5px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }
            
            .endpoint-method {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                margin-right: 10px;
            }
            
            .method-get { background: #28a745; color: white; }
            .method-post { background: #007bff; color: white; }
            .method-put { background: #ffc107; color: black; }
            .method-delete { background: #dc3545; color: white; }
            
            .endpoint-path {
                font-family: monospace;
                color: #495057;
                font-size: 14px;
            }
            
            .endpoint-desc {
                color: #6c757d;
                font-size: 13px;
                margin-top: 8px;
            }
            
            .loading {
                text-align: center;
                padding: 40px;
                color: #6c757d;
            }
            
            .spinner {
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .search-box {
                padding: 8px 16px;
                border: 1px solid #ced4da;
                border-radius: 6px;
                font-size: 14px;
                width: 250px;
                transition: all 0.3s;
            }
            
            .search-box:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌟 陈筱雪 AI 助手 - OpenAPI Schema</h1>
                <p>API 规范定义与接口详情</p>
            </div>
            
            <div class="toolbar">
                <div class="toolbar-group">
                    <button class="btn btn-primary" onclick="copySchema()">
                        📋 复制JSON
                    </button>
                    <button class="btn btn-success" onclick="downloadSchema()">
                        💾 下载文件
                    </button>
                    <button class="btn btn-secondary" onclick="formatJSON()">
                        ✨ 格式化
                    </button>
                    <button class="btn btn-secondary" onclick="minifyJSON()">
                        🗜️ 压缩
                    </button>
                </div>
                
                <div class="toolbar-group">
                    <input type="text" class="search-box" id="searchBox" 
                           placeholder="🔍 搜索端点..." onkeyup="searchEndpoints()">
                </div>
                
                <div class="stats" id="stats">
                    <div class="stat-item">
                        <span>📊</span>
                        <span id="endpointCount">加载中...</span>
                    </div>
                </div>
            </div>
            
            <div class="content">
                <div class="tabs">
                    <button class="tab active" onclick="switchTab('overview')">📋 概览</button>
                    <button class="tab" onclick="switchTab('endpoints')">🔌 端点列表</button>
                    <button class="tab" onclick="switchTab('schemas')">📦 数据模型</button>
                    <button class="tab" onclick="switchTab('raw')">📄 原始JSON</button>
                </div>
                
                <div id="loading" class="loading">
                    <div class="spinner"></div>
                    <p>正在加载 API Schema...</p>
                </div>
                
                <div id="tab-overview" class="tab-content active">
                    <div class="info-grid" id="infoGrid">
                        <!-- 动态填充 -->
                    </div>
                </div>
                
                <div id="tab-endpoints" class="tab-content">
                    <div class="endpoints-list" id="endpointsList">
                        <!-- 动态填充 -->
                    </div>
                </div>
                
                <div id="tab-schemas" class="tab-content">
                    <pre id="schemasContent">加载中...</pre>
                </div>
                
                <div id="tab-raw" class="tab-content">
                    <pre id="rawJson">加载中...</pre>
                </div>
            </div>
        </div>
        
        <script>
            let schemaData = null;
            
            // 加载Schema数据
            async function loadSchema() {
                try {
                    const response = await fetch('/openapi.json');
                    schemaData = await response.json();
                    
                    document.getElementById('loading').style.display = 'none';
                    renderOverview();
                    renderEndpoints();
                    renderSchemas();
                    renderRawJson();
                    updateStats();
                } catch (error) {
                    console.error('加载失败:', error);
                    document.getElementById('loading').innerHTML = 
                        '<p style="color: red;">❌ 加载失败，请刷新页面重试</p>';
                }
            }
            
            // 渲染概览
            function renderOverview() {
                const info = schemaData.info;
                const servers = schemaData.servers || [];
                
                const html = `
                    <div class="info-card">
                        <h3>📝 API 信息</h3>
                        <p><strong>标题:</strong> ${info.title}</p>
                        <p><strong>版本:</strong> ${info.version}</p>
                        <p><strong>描述:</strong> ${info.description ? info.description.substring(0, 100) + '...' : '无'}</p>
                    </div>
                    
                    <div class="info-card">
                        <h3>👥 联系方式</h3>
                        <p><strong>名称:</strong> ${info.contact?.name || '未提供'}</p>
                        <p><strong>邮箱:</strong> ${info.contact?.email || '未提供'}</p>
                        <p><strong>网址:</strong> ${info.contact?.url || '未提供'}</p>
                    </div>
                    
                    <div class="info-card">
                        <h3>🌐 服务器</h3>
                        ${servers.map(s => `
                            <p><strong>${s.description || '默认'}:</strong><br>
                            <code>${s.url}</code></p>
                        `).join('')}
                    </div>
                    
                    <div class="info-card">
                        <h3>📜 许可证</h3>
                        <p><strong>名称:</strong> ${info.license?.name || '未提供'}</p>
                        <p><strong>URL:</strong> ${info.license?.url || '未提供'}</p>
                    </div>
                `;
                
                document.getElementById('infoGrid').innerHTML = html;
            }
            
            // 渲染端点列表
            function renderEndpoints() {
                const paths = schemaData.paths || {};
                let html = '';
                
                for (const [path, methods] of Object.entries(paths)) {
                    for (const [method, details] of Object.entries(methods)) {
                        if (typeof details === 'object' && details.summary) {
                            html += `
                                <div class="endpoint-item" data-path="${path}" data-method="${method}">
                                    <span class="endpoint-method method-${method}">${method.toUpperCase()}</span>
                                    <span class="endpoint-path">${path}</span>
                                    <div class="endpoint-desc">${details.summary}</div>
                                </div>
                            `;
                        }
                    }
                }
                
                document.getElementById('endpointsList').innerHTML = html || '<p>暂无端点</p>';
            }
            
            // 渲染数据模型
            function renderSchemas() {
                const schemas = schemaData.components?.schemas || {};
                document.getElementById('schemasContent').textContent = 
                    JSON.stringify(schemas, null, 2);
            }
            
            // 渲染原始JSON
            function renderRawJson() {
                document.getElementById('rawJson').textContent = 
                    JSON.stringify(schemaData, null, 2);
            }
            
            // 更新统计信息
            function updateStats() {
                const paths = schemaData.paths || {};
                let endpointCount = 0;
                
                for (const methods of Object.values(paths)) {
                    endpointCount += Object.keys(methods).length;
                }
                
                document.getElementById('endpointCount').textContent = 
                    `${endpointCount} 个端点`;
            }
            
            // 切换标签
            function switchTab(tabName) {
                // 隐藏所有内容
                document.querySelectorAll('.tab-content').forEach(el => {
                    el.classList.remove('active');
                });
                
                // 移除所有活动标签
                document.querySelectorAll('.tab').forEach(el => {
                    el.classList.remove('active');
                });
                
                // 显示选中内容
                document.getElementById(`tab-${tabName}`).classList.add('active');
                
                // 激活对应标签
                event.target.classList.add('active');
            }
            
            // 复制Schema
            function copySchema() {
                navigator.clipboard.writeText(JSON.stringify(schemaData, null, 2))
                    .then(() => alert('✅ 已复制到剪贴板'))
                    .catch(err => alert('❌ 复制失败: ' + err));
            }
            
            // 下载Schema
            function downloadSchema() {
                const blob = new Blob([JSON.stringify(schemaData, null, 2)], 
                                     { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'openapi-schema.json';
                a.click();
                URL.revokeObjectURL(url);
            }
            
            // 格式化JSON
            function formatJSON() {
                document.getElementById('rawJson').textContent = 
                    JSON.stringify(schemaData, null, 2);
            }
            
            // 压缩JSON
            function minifyJSON() {
                document.getElementById('rawJson').textContent = 
                    JSON.stringify(schemaData);
            }
            
            // 搜索端点
            function searchEndpoints() {
                const searchTerm = document.getElementById('searchBox').value.toLowerCase();
                const items = document.querySelectorAll('.endpoint-item');
                
                items.forEach(item => {
                    const path = item.getAttribute('data-path').toLowerCase();
                    const method = item.getAttribute('data-method').toLowerCase();
                    const desc = item.querySelector('.endpoint-desc')?.textContent.toLowerCase() || '';
                    
                    if (path.includes(searchTerm) || method.includes(searchTerm) || desc.includes(searchTerm)) {
                        item.style.display = 'block';
                    } else {
                        item.style.display = 'none';
                    }
                });
            }
            
            // 页面加载时初始化
            window.addEventListener('DOMContentLoaded', loadSchema);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/")
async def root():
    """根路径 - API 状态检查"""