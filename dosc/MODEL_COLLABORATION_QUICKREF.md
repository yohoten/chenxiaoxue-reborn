# AI 模型协作功能 - 快速参考卡片

## 🚀 5分钟快速上手

### 1️⃣ Python API（最简单）

```python
from app.services.ai_router import ai_router, TaskType

result = await ai_router.collaborative_chat(
    messages=[{"role": "user", "content": "你的复杂问题"}]
)

print(result["response"])
```

### 2️⃣ MCP协议调用

```bash
curl -X POST http://localhost:8000/mcp/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "collaborative_chat",
    "arguments": {
      "messages": [{"role": "user", "content": "问题"}],
      "enable_collaboration": true
    }
  }'
```

### 3️⃣ 运行示例脚本

```bash
cd backend
python examples/collaborative_chat_demo.py
```

---

## 📊 返回结果结构

```json
{
  "response": "最终回答",
  "collaboration_used": true,
  "subtask_results": [
    {
      "type": "retrieval|reasoning|analysis|...",
      "model": "provider/model_name",
      "confidence": 0.92,
      "execution_time_ms": 1200
    }
  ],
  "models_used": ["deepseek/chat", "openai/gpt-4o"],
  "total_cost": 0.0456,
  "latency_ms": 5200
}
```

---

## 🎯 何时使用协作模式？

✅ **推荐**:
- 多维度分析问题
- 跨领域综合任务
- 需要验证的关键决策
- 长链条推理

❌ **不推荐**:
- 简单对话
- 单一类型任务
- 实时交互
- 成本敏感

---

## ⚙️ 关键配置

```bash
# .env 文件
MAX_SUBTASKS=5              # 最大子任务数
COLLABORATION_TIMEOUT=120   # 超时时间（秒）
MIN_CONFIDENCE=0.7          # 最小置信度
MAX_COLLABORATION_COST=1.0  # 成本上限（美元）
```

---

## 🔍 调试技巧

```python
# 启用详细日志
import logging
logging.getLogger('ai_router').setLevel(logging.DEBUG)

# 查看执行详情
print(f"子任务数: {len(result['subtask_results'])}")
print(f"使用模型: {result['models_used']}")
print(f"总耗时: {result['latency_ms']:.0f}ms")
print(f"总成本: ${result['total_cost']:.4f}")
```

---

## 📚 完整文档

- 📖 [使用指南](./MODEL_COLLABORATION_GUIDE.md)
- 📋 [方案总结](./MODEL_COLLABORATION_SUMMARY.md)
- 💻 [Python示例](../backend/examples/collaborative_chat_demo.py)
- 🎨 [前端组件](../frontend/src/components/Chat/CollaborationPanel.tsx)

---

*快速参考 v1.0 | 最后更新: 2026-05-06*