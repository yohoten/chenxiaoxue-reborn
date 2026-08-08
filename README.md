# 🌟 陈筱雪 Reborn

> **项目起始**: 2025年8月 | **当前版本**: v2.0 | **最后更新**: 2026-07-21
> 
> 基于 FastAPI + Tauri + React 的现代化多模型 AI 助手，支持 MCP 协议。
> 
> *从 PyQt5 像素风格桌面应用迁移到现代 Web/Tauri 架构*

## 📖 项目历史

陈筱雪 Reborn 项目起源于 **2025年8月**，是从原 PyQt5 像素风格桌面应用向现代 Web 技术栈的全面迁移与重构。

### 核心演进时间线
- **2025.08**: 项目启动，架构迁移决策（PyQt5 → FastAPI + React + Tauri）
- **2026.04.22**: 完成基础架构搭建（多模型路由、MCP 协议、像素主题）
- **2026.05.04**: UI 组件完善（CharacterPanel、ECGStatusBar、QuickActionBar）
- **2026.05.05**: 用户认证系统上线（JWT + 多用户数据隔离）
- **2026.05.08**: Humanizer AI 文本人性化检测器集成
- **2026.05.XX**: ECG 增强、登录页像素风强化、Self-Improving 多语言支持
- **2026.05.XX**: 模型协作功能、音频系统、历史管理、星图可视化
- **2026.07.21**: 持续迭代优化中

完整开发日志请查看 [DEVELOPMENT_LOG.md](./DEVELOPMENT_LOG.md) 📋

## 架构概览

```
chenxiaoxue-reborn/
├── backend/                    # FastAPI 后端 (Python 3.10+)
│   ├── app/
│   │   ├── config/             # 配置 (Pydantic Settings)
│   │   ├── models/             # ORM + Pydantic Schema
│   │   ├── services/           # 核心服务
│   │   │   ├── ai_router.py    # ⭐ 多模型智能路由 (核心)
│   │   │   ├── database.py     # 异步数据库
│   │   │   └── emotion_service.py  # 混合情感分析
│   │   ├── mcp/                # MCP 协议实现
│   │   ├── routers/            # API 路由
│   │   └── utils/              # 工具
│   └── requirements.txt
├── frontend/                   # React + TypeScript 前端
│   ├── src/
│   │   ├── components/         # UI 组件
│   │   ├── hooks/              # React Hooks
│   │   ├── services/           # API + MCP 客户端
│   │   └── styles/             # 像素风格主题
│   └── package.json
├── src-tauri/                  # Tauri 桌面壳 (Rust)
└── scripts/                    # 辅助脚本
```

## 核心特性

### 🤖 多模型智能路由 (`backend/app/services/ai_router.py`)
- **自动路由**: 根据任务类型和复杂度自动选择最佳模型
- **6 大供应商**: DeepSeek、OpenAI、通义千问、豆包、Kimi、Claude
- **故障转移**: 自动切换备用模型
- **流式响应**: 支持 SSE 实时流式输出
- **🆕 模型协作**: 复杂问题分解为多个子任务，多模型分工协作，智能聚合结果

### 🔌 MCP 协议 (`backend/app/mcp/`)
- 标准 MCP 工具定义：`chat_completion`、`analyze_emotion`、`translate`、`get_models`、**`collaborative_chat`**
- 支持 HTTP + SSE 协议
- 可被外部 MCP 客户端发现和调用

### 🎨 像素美学
- 从原 PyQt5 像素风格迁移的 CSS 主题
- 支持 GIF 动态背景轮播
- 打字机效果消息显示
- ASCII 艺术装饰 + CRT 扫描线效果

### 🔐 用户认证系统
- JWT Token 认证（Access: 7天, Refresh: 30天）
- bcrypt 密码加密
- 多用户数据完全隔离
- 像素风登录/注册界面

### ✍️ Humanizer AI 检测器
- 24 种 AI 写作模式检测
- 智能人性化改写建议
- 可视化评分系统（0-100%）
- 基于 Wikipedia 权威指南

### 💚 ECG 情感可视化
- 真实心电图波形渲染（P波、QRS、T波）
- 情感驱动的颜色和心率变化
- Canvas 实时绘制动画

### 🌟 更多功能
- 自我进化记忆系统（Self-Improving Memory）
- 梦境解析与符号分析
- 星图历史可视化
- 背景音乐与音效
- 外部 MCP 服务器支持

## 📊 项目统计

| 指标 | 数量 |
|------|------|
| 代码总量 | ~11,000+ 行 |
| 后端 Python | ~5,000+ 行 |
| 前端 TypeScript/React | ~3,000+ 行 |
| Rust (Tauri) | ~500+ 行 |
| 测试代码 | ~500+ 行 |
| 文档 Markdown | ~2,000+ 行 |
| API 端点 | 26+ 个 |
| 功能模块 | 12+ 个 |
| 开发周期 | 2025.08 - 至今 |

## 📦 部署方式
- **Web 模式**: 浏览器访问 `http://localhost:5173`
- **桌面模式**: Tauri 打包为原生桌面应用

## 快速开始

### 1. 配置 API 密钥

```bash
cd backend
cp .env.example .env
# 编辑 .env 填入你的 API Key
```

### 2. 安装 & 启动

**统一启动器 (推荐):**

```bash
# 双击 launcher.bat 或运行:
launcher.bat          # 交互式菜单
launcher.bat setup    # 一键安装
launcher.bat dev      # 启动开发模式
launcher.bat backend  # 仅后端
launcher.bat frontend # 仅前端
launcher.bat tauri    # Tauri 桌面
launcher.bat test     # 测试模式
launcher.bat prod     # 生产模式
```

> PowerShell 用户请用 `cmd /c launcher.bat dev` 运行（路径含 `&` 时需此方式）

**手动启动:**
```bash
# 后端
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 前端 (新终端)
cd frontend
npm install
npm run dev
```

### 3. 访问

- 前端: http://localhost:5173
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health
- MCP 信息: http://localhost:8000/mcp/info

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录 |
| GET | `/api/auth/me` | 获取当前用户 |
| POST | `/api/chat/send` | 发送聊天消息 |
| GET | `/api/chat/history` | 获取聊天历史 |
| DELETE | `/api/chat/history/{id}` | 删除单条记录 |
| DELETE | `/api/chat/history` | 清空所有记录 |
| POST | `/api/emotion/analyze` | 情感分析 |
| POST | `/api/humanizer/analyze` | AI 文本分析 |
| POST | `/api/humanizer/rewrite` | 人性化改写 |
| GET | `/api/resources/backgrounds` | 背景列表 |
| GET | `/api/resources/characters` | 角色列表 |
| GET | `/mcp/info` | MCP 服务器信息 |
| GET | `/mcp/tools` | MCP 工具列表 |
| POST | `/mcp/execute` | 执行 MCP 工具 |
| POST | `/mcp/stream` | 流式执行 MCP 工具 |

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI + Uvicorn |
| 编程语言 | Python 3.10+ |
| 数据库 | SQLAlchemy + aiosqlite (SQLite) |
| AI 路由 | httpx (异步 HTTP) |
| 前端框架 | React 18 + TypeScript |
| 构建工具 | Vite 4 |
| 桌面壳 | Tauri 2 (Rust) |
| 认证 | JWT (python-jose) + bcrypt |
| 协议 | MCP (Model Context Protocol) |
| 主题 | 像素风格 CSS (Custom Properties) |

## 📚 文档索引

### 📋 核心文档
- [📅 完整开发日志](./DEVELOPMENT_LOG.md) - **项目历史与演进时间线** ⭐ **新增**
- [🤖 AI模型协作与聚合功能](./dosc/MODEL_COLLABORATION_SUMMARY.md) - **完整实现方案**
- [📖 协作功能使用指南](./dosc/MODEL_COLLABORATION_GUIDE.md) - **详细教程**
- [⚡ 快速参考卡片](./dosc/MODEL_COLLABORATION_QUICKREF.md) - **5分钟上手**

### API文档与开发工具
- [📋 API文档优化报告](./dosc/API_DOCS_OPTIMIZATION.md) - **中文API文档优化详情**
- [🚀 API快速使用指南](./dosc/API_QUICKSTART.md) - **5分钟快速上手**
- [🔍 OpenAPI Schema查看器](./dosc/SCHEMA_VIEWER_GUIDE.md) - **可视化浏览API结构** ✨ **新增**

### 核心功能文档
- [✍️ Humanizer 使用指南](./dosc/HUMANIZER_GUIDE.md) - **AI 文本人性化检测器**
- [🔐 用户认证系统](./dosc/AUTH_README.md) - **JWT 认证与多用户隔离**
- [💚 ECG 状态栏增强](./dosc/ECG_ENHANCEMENT.md) - **真实心电图可视化**
- [🌟 星图功能](./dosc/STAR_MAP_USER_GUIDE.md) - **历史对话可视化**
- [🧠 Self-Improving 模块](./dosc/SELF_IMPROVING_SUMMARY.md) - **自我进化记忆系统**

### UI/UX 优化文档
- [🎨 用户菜单像素风改造](./dosc/USER_MENU_PIXEL_REFACTOR.md) - **白色现代→像素暗黑** ✨ **新增**
- [🖥️ 登录注册像素强化](./dosc/PIXEL_LOGIN_REFACTOR.md) - **ASCII艺术+CRT效果+像素动画** ✨ **新增**
- [✨ UI透明度优化](./dosc/UI_TRANSPARENCY_OPTIMIZATION.md) - **毛玻璃效果与分层透明度**
- [🎵 背景音乐配置](./dosc/BACKGROUND_MUSIC_GUIDE.md) - **多音轨与淡入淡出**

### 其他功能文档
- [💬 历史对话管理](./dosc/HISTORY_CHAT_GUIDE.md) - **搜索、过滤、分页**
- [🎭 情感系统增强](./dosc/ECG_ENHANCEMENT.md)
- [🔌 外部 MCP 指南](./dosc/EXTERNAL_MCP_GUIDE.md) - **第三方服务器支持**

### 开发文档
- [🚀 快速开始](./dosc/QUICKSTART.md)
- [📋 项目总览](./dosc/PROJECT_SUMMARY.md)
- [🔧 故障排除](./dosc/TROUBLESHOOTING_IMAGES.md)
- [📦 启动器指南](./LAUNCHER_GUIDE.md) - **Windows 一键启动**

---

*陈筱雪 Reborn v2.0 | 让AI更智能，让协作更高效！* 🚀

**维护者**: 陈筱雪 AI 助手开发团队  
**项目起始**: 2025年8月  
**许可证**: MIT License