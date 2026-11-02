# 🌟 陈筱雪 Reborn

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Tauri](https://img.shields.io/badge/Tauri-2-24C8DB?style=flat-square&logo=tauri&logoColor=black)
![MCP](https://img.shields.io/badge/MCP-12%20tools-FF6B9D?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

**基于 FastAPI + React + Tauri 的多模型 AI 助手，内置 MCP 协议、像素美学与情感可视化。**

*从 PyQt5 像素风桌面应用迁移而来的现代 Web / 桌面全栈重构*

[快速开始](#-快速开始) · [API 全景](#-api-全景) · [架构](#-架构) · [故障排除](#-故障排除)

</div>

---

## 📖 目录

- [项目简介](#项目简介)
- [功能特性](#-功能特性)
- [架构](#-架构)
- [快速开始](#-快速开始)
- [服务地址](#-服务地址)
- [API 全景](#-api-全景)
- [MCP 工具](#-mcp-工具)
- [模型与路由策略](#-模型与路由策略)
- [仓库目录说明](#-仓库目录说明)
- [开发指南](#-开发指南)
- [故障排除](#-故障排除)
- [文档索引](#-文档索引)
- [项目统计](#-项目统计)
- [路线图](#-路线图)

---

## 项目简介

**陈筱雪 Reborn** 起始于 2025 年 8 月，是将原有 PyQt5 像素风桌面应用整体迁移到 **FastAPI + React + Tauri** 的全栈重构项目。

后端以 **多模型智能路由** 为核心，把 DeepSeek、OpenAI、通义千问、豆包、Kimi 五家供应商纳入统一调度，并对外以 **MCP（Model Context Protocol）** 暴露能力；前端延续像素美学，提供情感 ECG、梦境解析、星图可视化等交互层功能；Tauri 壳负责打包为原生桌面应用。

> 📌 **项目门户**：仓库根目录的 [`index.html`](./index.html) 是一份自包含的单文件门户页，双击即可在浏览器打开，含特性概览、目录结构、启动命令速查与 API 清单。

### 演进时间线

| 时间 | 里程碑 |
|------|--------|
| 2025.08 | 项目启动，确定 PyQt5 → FastAPI + React + Tauri 的架构迁移路线 |
| 2026.04 | 完成基础架构：多模型路由、MCP 协议、像素主题 |
| 2026.05 | UI 组件完善（CharacterPanel、ECGStatusBar、QuickActionBar） |
| 2026.05 | 用户认证上线（JWT + 多用户数据隔离） |
| 2026.05 | Humanizer AI 文本检测器集成 |
| 2026.05 | 模型协作、音频系统、历史管理、星图可视化 |
| 2026.07 | 知识脑（Brain）、自我进化记忆、梦境世界持续迭代 |

---

## ✨ 功能特性

### 🤖 多模型智能路由

`backend/app/services/ai_router.py` —— 系统的调度中枢。

- **自动选型**：依据任务类型与复杂度选择最合适的模型
- **故障转移**：供应商异常时自动切换备用模型
- **流式响应**：基于 SSE 的实时输出
- **模型协作**：复杂问题拆解为子任务，多模型分工后聚合结果

### 🔌 MCP 协议

`backend/app/mcp/` —— 标准 MCP 实现，支持 HTTP + SSE，可被外部 MCP 客户端发现调用，也支持接入第三方 MCP 服务器（见 `external_server.py`）。当前注册 **12 个工具**，详见 [MCP 工具](#-mcp-工具)。

### 🔐 用户认证

- JWT 认证（Access 7 天 / Refresh 30 天）+ bcrypt 密码散列
- 多用户数据完全隔离
- 像素风登录 / 注册界面

### ✍️ Humanizer AI 检测器

24 种 AI 写作模式检测与人性化改写建议，0–100% 可视化评分，规则参考 Wikipedia 写作指南。

### 💚 情感、梦境与星图

- **ECG 情感可视化**：真实心电波形（P 波 / QRS / T 波）Canvas 绘制，情感驱动配色与心率
- **梦境系统**：梦境解析、符号百科、梦境卡片、音景推荐、3D 梦境世界、信使小游戏
- **星图可视化**：历史对话与梦境映射为星点（`three.js`）

### 🧠 知识脑与自我进化

- **Brain 知识库**：分类条目 CRUD、附件、模板、全文检索
- **Self-Improving Memory**：HOT/WARM/COLD 分层记忆、心跳维护（晋升 / 降级）、主题遗忘、纠正记录

### 🎨 像素美学

- 自 PyQt5 时代延续的像素 CSS 主题（`frontend/src/styles/`）
- GIF 动态背景轮播、打字机消息渲染、ASCII 装饰与 CRT 扫描线
- 响应式适配（`responsive.css`）

---

## 🏗 架构

```
chenxiaoxue-reborn/
├── backend/                    # FastAPI 后端 (Python 3.10+)
│   ├── app/
│   │   ├── config/             # Pydantic Settings 配置
│   │   ├── models/             # ORM + Pydantic Schema
│   │   ├── services/           # 核心服务
│   │   │   ├── ai_router.py    # ⭐ 多模型智能路由（核心）
│   │   │   ├── emotion_service.py  # 混合情感分析
│   │   │   ├── humanizer_service.py # 24 种模式检测
│   │   │   ├── dream_service.py / brain_service.py
│   │   │   ├── memory_service.py / auth_service.py
│   │   │   └── database.py     # 异步数据库
│   │   ├── mcp/                # MCP 协议实现（12 个工具）
│   │   ├── routers/            # 9 个路由模块，52 个端点
│   │   └── utils/
│   ├── tests/                  # pytest 测试
│   └── requirements.txt
├── frontend/                   # React 18 + TypeScript 前端
│   ├── src/
│   │   ├── components/         # 34 个组件（Chat / Dream / Emotion / MCP ...）
│   │   ├── hooks/              # useChat / useMCP / useTheme / typewriterScheduler
│   │   ├── pages/              # Login / Register
│   │   ├── services/           # api / auth / httpClient / mcpClient
│   │   └── styles/             # 像素主题 CSS
│   └── package.json
├── src-tauri/                  # Tauri 2 桌面壳 (Rust)
├── resource/                   # 背景 / 角色 / ECG / 音效 / 星图素材
├── skills/                     # brain、humanizer 技能定义与模板
├── data/                       # 运行时数据（知识脑分类数据）
├── launcher.bat / launcher.py  # Windows 统一启动器
└── index.html                  # 项目门户页（单文件）
```

### 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端框架 | FastAPI 0.115 + Uvicorn | Python 3.10+，全异步路由 |
| 数据校验 | Pydantic 2.9 / pydantic-settings | 配置与 Schema 统一建模 |
| 数据存储 | SQLAlchemy 2.0 + aiosqlite | SQLite 异步读写，免部署数据库服务 |
| AI 接入 | httpx 0.27 | 异步调用各供应商接口 |
| 认证 | python-jose + passlib[bcrypt] | JWT 签发与密码散列 |
| 文本处理 | jieba + SnowNLP | 中文分词与情感 |
| 限流 / 缓存 | slowapi + cachetools | API 限流与资源列表 TTL 缓存 |
| 前端框架 | React 18 + TypeScript 5.5 | Vite 4 构建，react-router 6 |
| 3D 渲染 | three.js | 星图与梦境世界 |
| 桌面壳 | Tauri 2 (Rust) | devUrl 5173，frontendDist `../frontend/dist` |
| 协议 | MCP over HTTP + SSE | sse-starlette |

---

## 🚀 快速开始

### 1. 环境要求

| 组件 | 版本 | 备注 |
|------|------|------|
| Python | 3.10+ | 后端运行时 |
| Node.js | 16+ | Vite 4 要求；前端依赖安装 |
| Rust 工具链 | 稳定版 | **仅**打包 Tauri 桌面版时需要 |

### 2. 配置环境变量

在 `backend/` 目录下创建 `.env`（该文件已被 `.gitignore` 排除，不会入库）：

```ini
# ─── 服务 ───────────────────────────────
ENV=development                 # development | production
DEBUG=true
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# ─── JWT（必需，长度 >= 32 字符）─────────
# 生成方式：python -c "import secrets; print(secrets.token_urlsafe(48))"
SECRET_KEY=

# ─── 模型供应商（按需填写，留空则自动跳过）──
DEEPSEEK_API_KEY=
OPENAI_API_KEY=
QWEN_API_KEY=
DOUBAO_API_KEY=
KIMI_API_KEY=
CLAUDE_API_KEY=                 # 已预留，当前路由尚未接入

# ─── 可选 ───────────────────────────────
DATABASE_URL=sqlite+aiosqlite:///./data/chenxiaoxue.db
CORS_ORIGINS=                   # 额外允许的来源，逗号分隔
RESOURCE_DIR=                   # 资源目录，留空则自动探测
```

> ⚠️ **注意**：仓库中目前**没有** `backend/.env.example`，请按上表手动创建 `.env`。
> `SECRET_KEY` 长度不足 32 字符时，应用启动阶段会直接校验失败。

### 3. 安装与启动

**方式一：统一启动器（Windows，推荐）**

```bat
launcher.bat            :: 交互式菜单
launcher.bat setup      :: 一键安装依赖
launcher.bat dev        :: 后端 + 前端（双窗口）
launcher.bat backend    :: 仅后端 :8000
launcher.bat frontend   :: 仅前端 :5173
launcher.bat tauri      :: Tauri 桌面窗口
launcher.bat test       :: 测试模式
launcher.bat prod       :: 生产模式
launcher.bat stop       :: 释放 8000/5173 端口
```

> PowerShell 下建议用 `cmd /c launcher.bat dev` 调用。

**方式二：手动启动**

```bash
# 后端
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 前端（新终端）
cd frontend
npm install
npm run dev
```

### 4. 验证

打开 <http://localhost:5173> 进入应用；访问 <http://localhost:8000/health> 应返回健康状态。

---

## 🌐 服务地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端应用 | <http://localhost:5173> | Vite 开发服务器 |
| Swagger UI | <http://localhost:8000/docs> | 交互式 API 文档（已中文化） |
| ReDoc | <http://localhost:8000/redoc> | API 参考文档 |
| 健康检查 | <http://localhost:8000/health> | 服务存活探测 |
| MCP 信息 | <http://localhost:8000/mcp/info> | MCP 服务器元数据 |
| MCP 工具列表 | <http://localhost:8000/mcp/tools> | 工具定义清单 |

---

## 📡 API 全景

共 **52 个端点**，分布于 9 个路由模块。

<details>
<summary><b>🔐 /api/auth</b> — 认证（5）</summary>

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 创建账号 |
| POST | `/api/auth/login` | 登录并获取 JWT |
| GET | `/api/auth/me` | 获取当前用户信息 |
| PUT | `/api/auth/me` | 更新当前用户信息 |
| POST | `/api/auth/logout` | 登出 |

</details>

<details>
<summary><b>💬 /api/chat</b> — 对话（4）</summary>

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/chat/send` | 发送消息并获取 AI 回复 |
| GET | `/api/chat/history` | 获取聊天历史 |
| DELETE | `/api/chat/history/{conv_id}` | 删除指定对话 |
| DELETE | `/api/chat/history` | 清空全部历史 |

</details>

<details>
<summary><b>😊 /api/emotion</b> — 情感（1）</summary>

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/emotion/analyze` | 分析文本情感 |

</details>

<details>
<summary><b>✍️ /api/humanizer</b> — 文本人性化（3）</summary>

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/humanizer/analyze` | 检测 AI 写作模式 |
| POST | `/api/humanizer/humanize` | 自动人性化改写 |
| GET | `/api/humanizer/patterns` | 列出全部可检测模式 |

</details>

<details>
<summary><b>🌙 /api/dream</b> — 梦境（13）</summary>

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/dream/analyze` | 解析梦境并保存 |
| GET | `/api/dream/records` | 梦境记录列表 |
| GET | `/api/dream/months` | 有记录的月份 |
| GET | `/api/dream/stats` | 梦境统计 |
| DELETE | `/api/dream/records/{dream_id}` | 删除记录 |
| GET | `/api/dream/encyclopedia` | 符号百科 |
| POST | `/api/dream/card` | 生成梦境卡片 |
| POST | `/api/dream/soundscape` | 推荐音景 |
| POST | `/api/dream/world` | 生成 3D 梦境世界数据 |
| POST | `/api/dream/messenger/world` | 生成信使游戏世界 |
| POST | `/api/dream/messenger/score` | 提交信使分数 |
| GET | `/api/dream/starmap` | 梦境星图数据 |
| GET | `/api/dream/square` | 匿名梦境广场 |

</details>

<details>
<summary><b>🧠 /api/brain</b> — 知识库（11）</summary>

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/brain/entries` | 列出条目 |
| POST | `/api/brain/entries` | 创建条目 |
| GET | `/api/brain/entries/search` | 搜索条目 |
| GET | `/api/brain/entries/{category}/{slug}` | 条目详情 |
| PUT | `/api/brain/entries/{category}/{slug}` | 更新条目 |
| DELETE | `/api/brain/entries/{category}/{slug}` | 删除条目 |
| GET | `/api/brain/entries/{category}/{slug}/attachments` | 附件列表 |
| POST | `/api/brain/entries/{category}/{slug}/attachments` | 添加附件 |
| GET | `/api/brain/templates` | 模板列表 |
| GET | `/api/brain/templates/{category}` | 模板详情 |
| GET | `/api/brain/stats` | 统计信息 |

</details>

<details>
<summary><b>🔄 /api/self-improving</b> — 自我进化记忆（6）</summary>

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/self-improving/stats` | 记忆系统统计 |
| POST | `/api/self-improving/search` | 搜索记忆 |
| POST | `/api/self-improving/forget` | 遗忘指定主题 |
| POST | `/api/self-improving/heartbeat` | 手动触发心跳维护 |
| GET | `/api/self-improving/hot-memory` | HOT 层记忆 |
| GET | `/api/self-improving/corrections` | 最近纠正记录 |

</details>

<details>
<summary><b>🖼 /api/resources</b> — 资源（5）</summary>

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/resources/backgrounds` | 背景列表（5 分钟缓存） |
| GET | `/api/resources/characters` | 角色列表（5 分钟缓存） |
| GET | `/api/resources/star-maps` | 星图列表 |
| GET | `/api/resources/sounds` | 音频列表 |
| GET | `/api/resources/file/{category}/{filename}` | 获取资源文件 |

</details>

<details>
<summary><b>🔌 /mcp</b> — MCP 协议（4）</summary>

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/mcp/info` | MCP 服务器信息 |
| GET | `/mcp/tools` | 工具列表与详细定义 |
| POST | `/mcp/execute` | 同步执行工具 |
| POST | `/mcp/stream` | SSE 流式执行工具 |

</details>

---

## 🔧 MCP 工具

定义于 `backend/app/mcp/tools.py`，共 12 个：

| 工具 | 说明 |
|------|------|
| `chat_completion` | 通用对话补全 |
| `collaborative_chat` | 多模型协作对话 |
| `analyze_emotion` | 情感分析 |
| `analyze_dream` | 梦境解析 |
| `translate_text` | 文本翻译 |
| `get_model_list` | 获取可用模型列表 |
| `memory_store` | 写入记忆 |
| `memory_retrieve` | 检索记忆 |
| `search_memory` | 搜索记忆 |
| `forget_topic` | 遗忘主题 |
| `get_memory_stats` | 记忆统计 |
| `filter_stopwords` | 停用词过滤 |

---

## 🎛 模型与路由策略

配置见 `backend/app/config/settings.py`，已接入 5 家供应商：

| 供应商 | 可用模型 |
|--------|----------|
| DeepSeek | `deepseek-chat`、`deepseek-reasoner` |
| OpenAI | `gpt-4o`、`gpt-4o-mini`、`gpt-4-turbo` |
| 通义千问 | `qwen-max`、`qwen-plus`、`qwen-turbo` |
| 豆包 | `doubao-pro-32k`、`doubao-pro-128k` |
| Kimi | `moonshot-v1-8k`、`moonshot-v1-32k` |

- 未配置 API Key 的供应商会在启动时自动跳过，不会阻塞服务
- `CLAUDE_API_KEY` 已在配置中预留，路由层尚未接入

---

## 📁 仓库目录说明

| 路径 | 说明 |
|------|------|
| `skills/` | `brain`（含 9 类条目模板）与 `humanizer` 的技能定义，供 Agent 侧调用 |
| `data/` | 运行时数据，含知识脑分类数据（`events`、`games`、`ideas`、`media`、`orgs` 等） |
| `resource/` | 背景、角色、ECG、音效、星图素材与 `dream_symbols.json` |
| `backend/migrations/` | Alembic 迁移脚本 |
| `backend/examples/` | 后端示例脚本 |

> 📦 大体积素材（`resource/` 下的背景、音效、星图，以及 `frontend/public/assets/backgrounds/`，合计约 730MB）已在 `.gitignore` 中排除。
> 如需入库，删除 `.gitignore` 中对应几行即可。

---

## 🧪 开发指南

```bash
# 运行后端测试
cd backend
pytest

# 前端生产构建
cd frontend
npm run build

# Tauri 桌面打包
npm run tauri build
```

- 仓库配置了 **pre-commit**（见 `.pre-commit-config.yaml`）与统一编辑器配置（`.editorconfig`），提交前请通过钩子检查
- 后端依赖固定在 `backend/requirements.txt`；根目录 `requirements.txt` 通过 `-r` 引用，避免两处维护

---

## 🩺 故障排除

| 症状 | 原因与处理 |
|------|-----------|
| 后端启动报 `SECRET_KEY` 校验失败 | `SECRET_KEY` 未设置或长度 < 32 字符，重新生成强随机密钥 |
| 端口 8000 / 5173 被占用 | 执行 `launcher.bat stop` 释放端口 |
| 前端能开但无法对话 | 检查后端是否运行、`.env` 中是否至少配置一家供应商的 Key |
| `passlib` 与 bcrypt 报错 | 依赖已固定 `bcrypt==4.0.1`，bcrypt 5+ 会破坏 passlib 兼容性，请勿升级 |
| 背景 / 角色图片不显示 | 相关素材被 `.gitignore` 排除，克隆后需自行补齐到 `resource/` 与 `frontend/public/assets/` |
| `launcher.bat` 报找不到 Python | 安装 Python 3.10+ 并确保 `py` 或 `python` 在 PATH 中 |

---

## 📚 文档索引

按仓库实况核对，标注状态以免误点：

| 文档 | 状态 | 说明 |
|------|------|------|
| [`README.md`](./README.md) | ✅ 存在 | 本文件，项目主文档 |
| [`index.html`](./index.html) | ✅ 存在 | 项目门户页（单文件，双击打开） |
| [`launcher.py`](./launcher.py) | ✅ 存在 | 启动器主逻辑，8 个子命令 |
| [`backend/requirements.txt`](./backend/requirements.txt) | ✅ 存在 | 后端依赖清单 |
| `dosc/`（专题文档集） | ⏳ 未入库 | 规划中的 15 篇专题文档（模型协作、Humanizer、认证、ECG、星图等），目录尚未创建 |
| `DEVELOPMENT_LOG.md` | ⏳ 未入库 | 规划中的完整开发日志 |

---

## 📊 项目统计

| 指标 | 数量 |
|------|------|
| 后端 Python（`backend/app`） | 10,111 行 / 40 个文件 |
| 前端 TypeScript / CSS（`frontend/src`） | 13,160 行 |
| 前端组件 | 34 个 |
| Rust（`src-tauri/src`） | 52 行 |
| 测试代码 | 589 行 |
| **API 端点** | **52 个** |
| MCP 工具 | 12 个 |
| 路由模块 | 9 个 |
| 模型供应商 | 5 家已接入 |
| 开发周期 | 2025.08 — 至今 |

---

## 🗺 路线图

- [ ] 补齐 `dosc/` 专题文档与 `DEVELOPMENT_LOG.md`
- [ ] 补充 `backend/.env.example` 配置模板
- [ ] Claude 供应商接入路由层
- [ ] 清理 `main.py` 中 `humanizer` / `brain` 路由的重复注册
- [ ] 前端组件单元测试覆盖
- [ ] CI 流水线（后端 pytest + 前端构建）

---

<div align="center">

*陈筱雪 Reborn v2.0 · 让 AI 更智能，让协作更高效* 🚀

**维护者**：陈筱雪 AI 助手开发团队
**项目起始**：2025 年 8 月 · **最后更新**：2026 年 11 月
**许可证**：MIT License

</div>
