# Chen筱雪 Reborn - 快速启动指南

## 🚀 一键启动

### Windows
```bash
scripts\dev.bat
```

这将同时启动后端和前端开发服务器。

---

## 📋 手动启动

### 1. 配置 API 密钥

编辑 `backend/.env` 文件（从 `.env.example` 复制）：

```env
# DeepSeek API
DEEPSEEK_API_KEY=sk-your-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# OpenAI API (可选)
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com

# 其他供应商...
```

### 2. 启动后端

```bash
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

访问 API 文档: http://localhost:8000/docs

### 3. 启动前端

```bash
cd frontend
npm run dev
```

访问应用: http://localhost:5173 (或自动分配的端口)

---

## 🎨 UI 特性

### 已实现的功能

✅ **动态背景轮播**
- 12 个精美的 GIF 背景
- 30 秒自动切换
- 半透明遮罩效果

✅ **角色动画面板**
- 6 个角色动画文件
- 随机眨眼效果
- 情感状态标签

✅ **ECG 心电图状态栏**
- Canvas 实时绘制波形
- 系统活跃状态指示
- 像素风格绿色波形

✅ **增强的聊天气泡**
- 用户/AI 消息区分
- 时间戳显示
- 模型信息标注
- 打字机效果

✅ **快速操作栏**
- 导出聊天
- 主题切换
- 清空对话

✅ **像素风格主题**
- 完整的颜色系统
- 自定义滚动条
- 响应式布局

---

## 📁 项目结构

```
chenxiaoxue-reborn/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── config/            # 配置管理
│   │   ├── services/          # 业务服务
│   │   ├── routers/           # API 路由
│   │   └── mcp/               # MCP 协议
│   └── requirements.txt
│
├── frontend/                   # React 前端
│   ├── src/
│   │   ├── components/        # UI 组件
│   │   │   ├── Background/    # 背景组件
│   │   │   ├── Chat/          # 聊天组件
│   │   │   ├── Common/        # 通用组件
│   │   │   ├── Emotion/       # 情感组件
│   │   │   └── Navigation/    # 导航组件
│   │   ├── hooks/             # React Hooks
│   │   ├── services/          # API 客户端
│   │   └── styles/            # CSS 样式
│   └── public/assets/         # 静态资源
│       ├── backgrounds/       # 背景图片
│       └── characters/        # 角色图片
│
└── scripts/                    # 启动脚本
    ├── setup.bat              # 安装依赖
    └── dev.bat                # 开发模式
```

---

## 🔧 技术栈

### 后端
- **FastAPI** 0.115.0 - 现代 Python Web 框架
- **SQLAlchemy** 2.0.35 - ORM 数据库
- **Pydantic** 2.9.0 - 数据验证
- **aiosqlite** - 异步 SQLite
- **httpx** - 异步 HTTP 客户端

### 前端
- **React** 18 - UI 框架
- **TypeScript** 5 - 类型安全
- **Vite** 4 - 构建工具
- **CSS Custom Properties** - 主题系统

### AI 集成
- **6 家 AI 供应商**: DeepSeek, OpenAI, Qwen, Doubao, Kimi, Claude
- **智能路由**: 自动选择最佳模型
- **故障转移**: 自动切换到备用模型
- **MCP 协议**: 标准化工具调用

---

## 🎯 核心功能

### 1. 智能对话
- 上下文理解
- 情感分析
- 多模型支持
- 打字机效果输出

### 2. 视觉体验
- 像素艺术风格
- GIF 背景轮播
- 角色动画
- ECG 状态指示

### 3. 数据管理
- SQLite 持久化
- 聊天记录导出
- 多格式支持 (JSON/TXT/CSV)

### 4. 扩展性
- REST API 接口
- MCP 工具协议
- 插件系统预留

---

## 🐛 常见问题

### Q: 前端端口被占用怎么办？
A: Vite 会自动尝试下一个可用端口（5173 → 5174 → 5175...）

### Q: 如何更换背景图片？
A: 将新的 GIF/PNG 文件放入 `frontend/public/assets/backgrounds/` 目录

### Q: 如何添加新角色？
A: 将角色图片放入 `frontend/public/assets/characters/`，然后在 `CharacterPanel.tsx` 中更新 `CHARACTER_IMAGES` 数组

### Q: API 请求失败？
A: 检查 `backend/.env` 中的 API Key 是否正确，确保网络连接正常

### Q: TypeScript 报错？
A: 运行 `npm run build` 查看详细错误信息，或检查组件 Props 类型定义

---

## 📊 性能优化建议

1. **图片优化**
   - 使用压缩的 GIF 文件
   - 考虑使用 WebP 格式
   - 实现懒加载

2. **代码分割**
   - 使用 React.lazy() 延迟加载组件
   - 路由级别的代码分割

3. **缓存策略**
   - 浏览器缓存静态资源
   - API 响应缓存
   - 图片预加载

---

## 🔗 相关链接

- **旧项目文档**: `../Chen Xiaoxue/README.md`
- **UI 完善报告**: `UI_IMPROVEMENTS.md`
- **API 文档**: http://localhost:8000/docs
- **FastAPI 文档**: https://fastapi.tiangolo.com/
- **React 文档**: https://react.dev/

---

**最后更新**: 2026-05-04  
**版本**: v1.0.0-beta  
**维护者**: Chen筱雪团队
