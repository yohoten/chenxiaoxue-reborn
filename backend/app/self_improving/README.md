# Self-Improving Module (自我改进模块)

陈筱雪 AI 助手的自我学习和记忆系统，基于 **Self-Improving + Proactive Agent** 技能实现。

## 📂 目录结构

```
backend/app/self_improving/
├── __init__.py           # 模块入口和单例管理
├── storage.py            # 三级存储系统（HOT/WARM/COLD）
├── manager.py            # 核心管理器（信号检测、反思、晋升/降级）
├── projects/             # WARM: 项目级记忆
├── domains/              # WARM: 领域级记忆
└── archive/              # COLD: 归档记忆
```

## 🧠 核心概念

### 三级存储架构

| 层级 | 文件位置 | 大小限制 | 加载策略 |
|------|---------|---------|---------|
| **HOT** | `memory.md` | ≤100 行 | 每次对话前自动加载 |
| **WARM** | `projects/*.md`, `domains/*.md` | ≤200 行/文件 | 根据上下文按需加载 |
| **COLD** | `archive/*.md` | 无限制 | 仅在显式查询时加载 |

### 学习信号

系统会自动检测以下用户输入模式：

#### 纠正信号（记录到 corrections.md）
- "No, that's not right..."
- "Actually, it should be..."
- "You're wrong about..."
- "I told you before..."
- "Stop doing X"

#### 偏好信号（记录到 memory.md）
- "I like when you..."
- "Always do X for me"
- "Never do Y"
- "My style is..."
- "For [project], use..."

### 自我反思

在完成重要任务后，系统可以评估自己的表现并记录：
- **CONTEXT**: 任务类型
- **REFLECTION**: 发现的问题
- **LESSON**: 下次如何改进

## 🔌 API 端点

### 1. 获取记忆统计
```http
GET /api/self-improving/stats
```

**响应示例：**
```json
{
  "success": true,
  "stats": {
    "hot": {
      "file": "memory.md",
      "lines": 15,
      "size_kb": 0.8
    },
    "warm": {
      "projects": 2,
      "domains": 1
    },
    "cold": {
      "archived": 5
    },
    "corrections": {
      "entries": 12
    }
  }
}
```

### 2. 搜索记忆
```http
POST /api/self-improving/search
Content-Type: application/json

{
  "query": "代码风格",
  "tier": "all"
}
```

### 3. 遗忘主题
```http
POST /api/self-improving/forget
Content-Type: application/json

{
  "topic": "旧偏好",
  "confirm": true
}
```

### 4. 获取 HOT 记忆
```http
GET /api/self-improving/hot-memory
```

### 5. 获取纠正记录
```http
GET /api/self-improving/corrections?limit=50
```

### 6. 手动触发心跳维护
```http
POST /api/self-improving/heartbeat
```

## 🛠️ MCP 工具

系统提供了三个新的 MCP 工具：

### 1. get_memory_stats
获取记忆系统的统计信息。

### 2. search_memory
在所有记忆层级中搜索特定主题。

**参数：**
- `query` (required): 搜索关键词
- `tier` (optional): 搜索范围（all/hot/warm/cold）

### 3. forget_topic
从所有记忆层级中删除指定主题。

**参数：**
- `topic` (required): 要遗忘的主题
- `confirm` (required): 必须为 true 才能执行删除

## 💡 使用示例

### 示例 1：用户纠正
```
用户: "不，我更喜欢用 Tabs 而不是 Spaces 来缩进代码"

系统检测到纠正信号 → 记录到 corrections.md
如果同一纠正出现 3 次 → 晋升到 memory.md (HOT)
```

### 示例 2：查看记忆统计
```bash
curl http://localhost:8000/api/self-improving/stats
```

### 示例 3：搜索记忆
```bash
curl -X POST http://localhost:8000/api/self-improving/search \
  -H "Content-Type: application/json" \
  -d '{"query": "代码风格", "tier": "all"}'
```

## 🔄 心跳维护

心跳机制会定期执行以下操作：

1. **晋升规则**：7 天内使用 3 次的模式 → 晋升到 HOT
2. **降级规则**：30 天未使用的模式 → 降级到 WARM
3. **归档规则**：90 天未使用的模式 → 归档到 COLD
4. **文件压缩**：合并相似的纠正条目，总结冗长的内容

可以通过以下方式手动触发：
```bash
curl -X POST http://localhost:8000/api/self-improving/heartbeat
```

## 📝 记忆文件格式

### memory.md (HOT)
```markdown
# Self-Improving Memory (HOT Tier)

## Confirmed Preferences
- 代码风格：优先使用显式而非隐式 (confirmed 2026-05)
- 沟通方式：直接，不要废话 (confirmed 2026-05)

## Active Patterns
- 总是使用 TypeScript 严格模式 (promoted from corrections)
- 优先使用 pnpm 而非 npm (promoted from corrections)

## Recent (last 7 days)
- 新项目默认使用 SQLite (corrected 2026-05-05)
```

### corrections.md
```markdown
# Corrections Log

## 2026-05-05 18:30
### Communication
- **Correction:** "不，我更喜欢用 Tabs 而不是 Spaces 来缩进代码"
- **Context:** chat conversation
- **Count:** 1 (first occurrence)
```

## 🔒 安全边界

系统遵循以下安全原则：

- ❌ **永不存储**：密码、API 密钥、财务信息、医疗数据、生物特征
- ⚠️ **谨慎存储**：工作上下文、情感状态、关系角色、日程模式
- ✅ **透明性**：用户可以随时查询、导出或删除所有记忆
- 🗑️ **遗忘开关**：用户说"忘记一切"时，导出后清空所有记忆

## 🚀 下一步计划

- [ ] 前端可视化面板（显示记忆统计和可管理的偏好列表）
- [ ] 自动定时心跳任务（使用 APScheduler）
- [ ] 向量搜索支持（集成 ChromaDB）
- [ ] 记忆导出功能（ZIP 打包所有文件）
- [ ] 每周记忆摘要通知

---

**Made with ❤️ by Chen筱雪 Reborn Team**
