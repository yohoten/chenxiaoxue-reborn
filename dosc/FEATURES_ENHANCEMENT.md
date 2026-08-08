# 陈筱雪 Reborn - 功能增强文档

## 📋 概述

本文档记录了从旧项目迁移的核心功能以及新增的 MCP 工具能力，将陈筱雪从一个简单的聊天机器人进化为全能的 AI 助手。

---

## 🔄 从旧项目迁移的功能

### 1. 停用词管理系统 (Stopwords Service)

**来源**: `stopwords_manager.py`  
**位置**: `backend/app/services/stopwords_service.py`

**功能特性**:
- ✅ 单例模式避免重复加载
- ✅ 支持多来源停用词文件（自动加载 `resource/stopwords/*.txt`）
- ✅ 提供添加/删除/查询接口
- ✅ 文本过滤功能
- ✅ 热重载支持

**使用示例**:
```python
from app.services.stopwords_service import stopwords_service

# 检查是否为停用词
if stopwords_service.is_stopword("的"):
    print("是停用词")

# 过滤文本
filtered = stopwords_service.filter_text("这是一个测试文本")
print(filtered)  # "测试文本"

# 获取统计信息
stats = stopwords_service.get_stats()
print(f"共 {stats['total_count']} 个停用词")
```

**MCP Tool**: `filter_stopwords`
```json
{
  "name": "filter_stopwords",
  "arguments": {
    "text": "这是一个测试文本",
    "separator": " "
  }
}
```

---

### 2. 梦境解析系统 (Dream Service)

**来源**: `dream_analyzer.py`, `dream_map_window.py`  
**位置**: `backend/app/services/dream_service.py`

**功能特性**:
- ✅ 内置 10+ 常见梦境符号数据库
- ✅ 基于关键词的智能检测
- ✅ 多维度解读（心理、象征、预示）
- ✅ 支持 AI 增强分析（可选）
- ✅ 可扩展的符号库（JSON 格式）

**前端页面**: `frontend/src/components/Dream/DreamSpace.tsx`
- 🌙 梦境输入界面
- 🔮 实时解析结果展示
- ✨ 符号高亮显示
- 🎯 AI/传统模式切换

**使用示例**:
```python
from app.services.dream_service import dream_service

result = dream_service.analyze_dream("我梦见自己在飞翔，周围是蓝天白云")
print(result['traditional_analysis'])
```

**MCP Tool**: `analyze_dream`
```json
{
  "name": "analyze_dream",
  "arguments": {
    "dream_text": "我梦见自己在飞翔...",
    "use_ai": true
  }
}
```

**返回格式**:
```json
{
  "dream_text": "我梦见自己在飞翔...",
  "detected_symbols": [
    {
      "symbol": "飞翔",
      "interpretations": ["象征着自由和解放..."],
      "selected": "象征着自由和解放，可能表示你渴望摆脱某些束缚。"
    }
  ],
  "traditional_analysis": "【飞翔】象征着自由和解放...\n\n💡 **总体建议**：...",
  "symbol_count": 1,
  "analysis_type": "ai_enhanced"
}
```

---

### 3. 记忆管理系统 (Memory Service)

**位置**: `backend/app/services/memory_service.py`

**功能特性**:
- ✅ 长期记忆存储（SQLite）
- ✅ 分类管理（fact/preference/event/conversation）
- ✅ 重要性评分（0-1）
- ✅ 标签系统
- ✅ 关键词搜索
- ✅ 访问计数追踪

**Phase 2 规划**:
- 🔜 集成向量数据库（ChromaDB/FAISS）
- 🔜 语义搜索
- 🔜 记忆关联图谱

**使用示例**:
```python
from app.services.memory_service import memory_service

# 存储记忆
memory = memory_service.store_memory(
    user_id="user123",
    content="用户喜欢像素风格",
    category="preference",
    importance=0.8,
    tags=["design", "preference"]
)

# 检索记忆
memories = memory_service.retrieve_memories(
    user_id="user123",
    category="preference",
    limit=5
)

# 搜索记忆
results = memory_service.search_memories(
    user_id="user123",
    keyword="像素"
)
```

**MCP Tools**:

#### `memory_store`
```json
{
  "name": "memory_store",
  "arguments": {
    "content": "用户喜欢像素风格",
    "category": "preference",
    "importance": 0.8,
    "tags": ["design", "preference"]
  }
}
```

#### `memory_retrieve`
```json
{
  "name": "memory_retrieve",
  "arguments": {
    "keyword": "像素",
    "category": "preference",
    "limit": 5
  }
}
```

---

## 🆕 新增 MCP 工具能力

### 当前可用工具列表

| 工具名称 | 分类 | 描述 | 状态 |
|---------|------|------|------|
| `chat_completion` | ai, chat | 与 AI 模型对话 | ✅ 已实现 |
| `analyze_emotion` | ai, emotion | 情感分析 | ✅ 已实现 |
| `translate_text` | ai, translate | 文本翻译 | ✅ 已实现 |
| `get_model_list` | system | 获取模型列表 | ✅ 已实现 |
| `analyze_dream` | ai, dream | 梦境解析 | ✅ 新增 |
| `memory_store` | memory | 存储记忆 | ✅ 新增 |
| `memory_retrieve` | memory | 检索记忆 | ✅ 新增 |
| `filter_stopwords` | text | 停用词过滤 | ✅ 新增 |

### Phase 2 规划工具

| 工具名称 | 描述 | 技术栈 | 优先级 |
|---------|------|--------|--------|
| `web_search` | 网络搜索 | SerpAPI/Bing API | ⭐⭐⭐ |
| `generate_diagram` | Mermaid 图表生成 | Mermaid.js + Puppeteer | ⭐⭐⭐ |
| `browse_website` | 浏览器自动化 | Playwright | ⭐⭐ |
| `execute_code` | 代码执行沙箱 | Docker/Pyodide | ⭐⭐ |
| `read_file` | 文件处理 | PyPDF2/python-docx | ⭐⭐ |
| `analyze_data` | 数据分析 | Pandas/Matplotlib | ⭐ |
| `add_event` | 日程管理 | ICS/Google Calendar | ⭐ |

---

## 🎭 情感系统增强计划

### 当前状态
- 9 种基础情感标签
- 规则 + AI 混合分析

### 增强方案

#### 多层次情感模型
```
一级情感 (7种): 喜、怒、哀、乐、惊、恐、厌
  ↓
二级情感 (36种): 
  - 喜 → 开心、兴奋、满足、狂喜、欣慰...
  - 怒 → 生气、愤怒、恼怒、暴怒...
  - ...
```

#### 情感上下文记忆
- 记录对话中的情感变化曲线
- 基于历史情感调整回复风格
- 情感传染效应

#### 情感驱动行为
- 不同情感对应不同的回复模板
- 情感影响回复长度和详细程度
- 特殊情感触发特殊动画（ECG 波形变化）

---

## 💬 对话规则系统

### 角色一致性规则
- ✅ 保持"陈筱雪"人设不变
- ✅ 记忆用户的称呼和偏好
- ❌ 避免 OOC (Out of Character)

### 安全过滤规则
- 🔒 敏感话题检测和引导
- 🔒 不当内容拦截
- 🔒 伦理边界设定

### 对话风格规则
- 🎨 像素风格语言特征
- 😊 适度的 emoji 使用
- 💬 口语化但不失礼貌

### 上下文连贯性
- 🧠 短期记忆（最近 10 轮对话）
- 🧠 长期记忆（重要事实）
- 🔄 话题追踪和自然过渡

---

## 📁 项目结构更新

```
backend/app/
├── services/
│   ├── stopwords_service.py      # ✅ 新增：停用词管理
│   ├── dream_service.py          # ✅ 新增：梦境解析
│   ├── memory_service.py         # ✅ 新增：记忆管理
│   ├── emotion_service.py        # 现有：情感分析
│   └── ai_router.py              # 现有：AI 路由
├── mcp/
│   ├── tools.py                  # ✅ 扩展：新增工具定义
│   └── server.py                 # ✅ 扩展：新增工具处理器
└── data/
    ├── stopwords/                # 📁 新建：停用词文件目录
    └── dream_symbols.json        # 📁 新建：梦境符号库

frontend/src/
├── components/
│   ├── Dream/
│   │   └── DreamSpace.tsx        # ✅ 新增：梦境空间页面
│   ├── Chat/
│   ├── Emotion/
│   └── Common/
├── services/
│   └── api.ts                    # ✅ 扩展：新增梦境解析API
└── types/
    └── index.ts                  # ✅ 扩展：新增梦境类型
```

---

## 🚀 快速开始

### 1. 启动后端
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 2. 启动前端
```bash
cd frontend
npm run dev
```

### 3. 测试新功能

#### 梦境解析
1. 打开应用
2. 点击左侧导航栏 "🌙 梦境"
3. 输入梦境描述
4. 点击 "✨ 解析梦境"

#### MCP 工具调用
```bash
# 获取工具列表
curl http://localhost:8000/mcp/tools

# 执行梦境解析
curl -X POST http://localhost:8000/mcp/execute \
  -H "Content-Type: application/json" \
  -d '{
    "name": "analyze_dream",
    "arguments": {
      "dream_text": "我梦见在飞翔",
      "use_ai": true
    }
  }'
```

---

## 📊 实施进度

### Phase 1 (已完成) ✅
- [x] 停用词服务迁移
- [x] 梦境解析 MCP Tool
- [x] 记忆系统基础版
- [x] 前端梦境空间页面

### Phase 2 (进行中) 🔄
- [ ] 网页搜索工具
- [ ] Mermaid 图表生成
- [ ] 情感系统增强（36种情感）

### Phase 3 (规划中) 📋
- [ ] 浏览器自动化
- [ ] 代码执行沙箱
- [ ] 文件处理能力

### Phase 4 (愿景) 🔮
- [ ] 完整插件生态系统
- [ ] 多模态能力（图片、音频）
- [ ] 自主学习和进化

---

## 🤝 贡献指南

欢迎贡献新的 MCP 工具或增强现有功能！

### 添加新 MCP Tool 的步骤

1. **定义工具** (`backend/app/mcp/tools.py`)
```python
NEW_TOOL = MCPTool(
    name="my_new_tool",
    description="工具描述",
    input_schema={...},
    handler=None,
    categories=["category1", "category2"],
)
```

2. **实现处理器** (`backend/app/mcp/server.py`)
```python
async def _handle_my_new_tool(self, param1: str, **kwargs) -> str:
    # 实现逻辑
    result = do_something(param1)
    return json.dumps(result, ensure_ascii=False)
```

3. **注册处理器** (`MCPServer._init_handlers`)
```python
ALL_TOOLS["my_new_tool"].handler = self._handle_my_new_tool
```

4. **创建前端组件** (可选)
5. **更新 API 服务** (`frontend/src/services/api.ts`)
6. **添加类型定义** (`frontend/src/types/index.ts`)

---

## 📝 许可证

本项目遵循 MIT 许可证。

---

## 🙏 致谢

- 旧项目 "Chen Xiaoxue" 提供的核心功能基础
- FastAPI、React、Tauri 等开源社区
- 所有贡献者和用户

---

**最后更新**: 2026-05-05  
**版本**: 1.1.0 (功能增强版)