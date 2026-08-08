# AI 模型协作与聚合功能使用指南

## 📋 概述

模型协作与聚合功能是陈筱雪 AI 助手的核心增强能力，通过将复杂问题分解为多个子任务，由不同专业模型分工处理，最后通过智能聚合模块整合结果，显著提升复杂问题的解决质量。

### 核心价值

- 🎯 **专业化分工**: 每个子任务由最擅长的模型处理
- 💰 **成本优化**: 智能分配高低成本模型
- 🛡️ **容错性强**: 单点故障不影响整体结果
- 📊 **透明度高**: 完整记录执行过程和置信度
- ⚡ **并行加速**: 无依赖任务真正并行执行

---

## 🏗️ 架构设计

```
用户输入复杂问题
    ↓
┌─────────────────────┐
│   任务分解器         │ ← 分析复杂度，拆分为子任务
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  子任务路由          │ ← 为每个子任务选择最佳模型
│  ┌──────┐ ┌──────┐  │
│  │检索  │ │推理  │  │ ← 并行/串行执行
│  └──────┘ └──────┘  │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   结果聚合器         │ ← 整合、去重、优化
└──────────┬──────────┘
           ↓
     最终高质量回答
```

---

## 🔧 核心组件

### 1. 任务分解器 (Task Decomposer)

**位置**: `backend/app/services/ai_router.py::_decompose_task()`

**功能**:
- 使用轻量级AI模型分析任务复杂度
- 识别所需的专业能力（检索、推理、代码等）
- 制定执行顺序和依赖关系
- 为每个子任务分配合适的模型

**支持的子任务类型**:

| 类型 | 说明 | 适用场景 |
|------|------|----------|
| `retrieval` | 信息检索 | 查找事实、数据、最新信息 |
| `reasoning` | 逻辑推理 | 因果分析、问题求解、推导 |
| `analysis` | 数据分析 | 模式识别、趋势判断、统计 |
| `synthesis` | 综合总结 | 整合多源信息、归纳概括 |
| `creation` | 创意生成 | 方案设计、内容创作、头脑风暴 |
| `verification` | 验证校验 | 检查正确性、一致性、完整性 |
| `coding` | 代码编写 | 编程、调试、优化、重构 |

### 2. 并行执行器 (Parallel Executors)

**位置**: `backend/app/services/ai_router.py::_execute_subtasks()`

**执行策略**:
- **无依赖任务**: 真正并行执行，最大化速度
- **有依赖任务**: 按依赖图顺序执行，确保数据流正确
- **智能路由**: 根据子任务类型自动选择最适合的模型

**示例**:
```python
# 任务A（检索）和任务B（推理）无依赖 → 并行执行
# 任务C（总结）依赖A和B → 等待完成后执行
subtasks = [
    {"type": "retrieval", "depends_on": []},      # 立即执行
    {"type": "reasoning", "depends_on": []},      # 立即执行
    {"type": "synthesis", "depends_on": [0, 1]},  # 等待0和1完成
]
```

### 3. 结果聚合器 (Result Aggregator)

**位置**: `backend/app/services/ai_router.py::_aggregate_results()`

**聚合策略**:

| 策略 | 说明 | 适用场景 |
|------|------|----------|
| `sequential` | 按顺序串联 | 有明确先后关系的任务链 |
| `parallel` | 并行合并 | 独立的子任务结果整合 |
| `voting` | 投票机制 | 对同一问题的多个答案择优 |

**聚合流程**:
1. 收集所有子任务结果
2. 去除重复和矛盾信息
3. 基于置信度加权融合
4. 生成连贯的最终回答
5. 附加执行摘要和元数据

---

## 💻 使用方法

### Python API 调用

```python
from app.services.ai_router import ai_router, TaskType

# ✅ 推荐：让系统自动判断是否启用协作
result = await ai_router.collaborative_chat(
    messages=[
        {"role": "user", "content": "请分析当前AI发展趋势并给出投资建议"}
    ],
    task_type=TaskType.COMPLEX,
    enable_collaboration=True  # 启用协作模式
)

# 查看结果
print("📝 最终回答:")
print(result["response"])

print("\n🤖 使用的模型:")
for model in result["models_used"]:
    print(f"  - {model}")

print("\n📊 执行详情:")
for subtask in result["subtask_results"]:
    print(f"  [{subtask['type']}] {subtask['model']}")
    print(f"    置信度: {subtask['confidence']:.2f}")
    print(f"    耗时: {subtask['execution_time_ms']:.0f}ms")
    print(f"    预览: {subtask['content_preview'][:100]}...")

print(f"\n💰 总成本: ${result['total_cost']:.4f}")
print(f"⏱️  总耗时: {result['latency_ms']:.0f}ms")
```

### MCP 协议调用

```bash
# HTTP POST 请求
curl -X POST http://localhost:8000/mcp/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "collaborative_chat",
    "arguments": {
      "messages": [
        {
          "role": "user",
          "content": "帮我设计一个电商系统的微服务架构"
        }
      ],
      "enable_collaboration": true
    }
  }'
```

### 前端集成示例

```typescript
// 在 ChatInput 组件中添加协作模式开关
const [useCollaboration, setUseCollaboration] = useState(false);

const handleSend = async (message: string) => {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      messages: [{ role: 'user', content: message }],
      use_collaboration: useCollaboration, // 传递协作标志
    }),
  });
  
  const data = await response.json();
  
  if (data.collaboration_used) {
    // 显示协作详情面板
    showCollaborationDetails(data.subtask_results);
  }
  
  displayMessage(data.response);
};
```

---

## 📊 返回结果详解

### 标准响应格式

```json
{
  "response": "最终的完整回答文本",
  "model_name": "collaborative-multi-model",
  "provider": "multi-provider",
  "usage": {
    "prompt_tokens": 1500,
    "completion_tokens": 800,
    "total_tokens": 2300
  },
  "latency_ms": 5200,
  "reasoning": "🤝 多模型协作完成\n   • 子任务数: 3\n   • 使用模型: deepseek/deepseek-chat, openai/gpt-4o, qwen/qwen-max\n   • 总耗时: 5200ms\n   • 预估成本: $0.0456",
  "collaboration_used": true,
  "subtask_results": [
    {
      "type": "retrieval",
      "model": "deepseek/deepseek-chat",
      "content_preview": "根据最新市场报告，2024年AI投资增长...",
      "confidence": 0.92,
      "execution_time_ms": 1200
    },
    {
      "type": "analysis",
      "model": "openai/gpt-4o",
      "content_preview": "从技术成熟度曲线来看，生成式AI处于...",
      "confidence": 0.88,
      "execution_time_ms": 1800
    },
    {
      "type": "synthesis",
      "model": "qwen/qwen-max",
      "content_preview": "综合以上分析，建议关注以下领域...",
      "confidence": 0.90,
      "execution_time_ms": 1500
    }
  ],
  "models_used": [
    "deepseek/deepseek-chat",
    "openai/gpt-4o",
    "qwen/qwen-max"
  ],
  "total_cost": 0.0456
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `response` | string | 最终聚合后的完整回答 |
| `collaboration_used` | boolean | 是否实际使用了协作模式 |
| `subtask_results` | array | 各子任务的详细结果 |
| `models_used` | array | 参与协作的模型列表 |
| `total_cost` | float | 总成本（美元） |
| `latency_ms` | float | 总耗时（毫秒） |

### 子任务结果字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | string | 子任务类型（retrieval/reasoning等） |
| `model` | string | 执行的模型（provider/model_name） |
| `content_preview` | string | 结果预览（前200字符） |
| `confidence` | float | 置信度（0-1） |
| `execution_time_ms` | float | 执行耗时（毫秒） |

---

## 🎯 适用场景

### ✅ 推荐使用协作模式

**1. 多维度分析问题**
```
用户: "请分析新能源汽车行业的现状、挑战和未来趋势"
→ 分解为: 现状调研 + 挑战分析 + 趋势预测 + 综合总结
```

**2. 跨领域综合任务**
```
用户: "帮我设计一个结合AI和区块链的供应链金融方案"
→ 分解为: AI应用分析 + 区块链架构 + 金融模型 + 方案整合
```

**3. 需要验证的关键决策**
```
用户: "这段代码是否有安全漏洞？如何优化？"
→ 分解为: 代码审查 + 安全扫描 + 性能分析 + 优化建议
```

**4. 长链条推理任务**
```
用户: "如果全球碳排放减少30%，对经济、环境、社会会有什么影响？"
→ 分解为: 数据检索 + 经济建模 + 环境影响 + 社会效应 + 综合评估
```

### ❌ 不推荐使用

**1. 简单对话**
```
用户: "你好" / "今天天气怎么样"
→ 直接使用标准对话模式
```

**2. 单一类型任务**
```
用户: "写一个Python快速排序函数"
→ 直接调用代码专用模型
```

**3. 实时交互**
```
用户: 需要秒级响应的聊天机器人
→ 协作模式会增加延迟
```

**4. 成本敏感场景**
```
用户: 大批量低价值文本处理
→ 使用低成本单一模型更经济
```

---

## ⚙️ 配置与优化

### 环境变量配置

在 `.env` 文件中添加：

```bash
# ==================== 协作模式配置 ====================

# 是否启用协作模式（默认 true）
ENABLE_COLLABORATION=true

# 最大子任务数量（防止过度分解，默认 5）
MAX_SUBTASKS=5

# 协作超时时间（秒，默认 120）
COLLABORATION_TIMEOUT=120

# 最小置信度阈值（低于此值会标记警告，默认 0.7）
MIN_CONFIDENCE=0.7

# 是否显示协作详情（默认 true）
SHOW_COLLABORATION_DETAILS=true

# 成本上限（美元，超过则降级为单模型，默认 1.0）
MAX_COLLABORATION_COST=1.0

# 缓存分解策略（默认 true）
CACHE_DECOMPOSITION=true
```

### 性能优化建议

**1. 缓存常见任务分解**
```python
# 对相似任务复用分解策略
cache_key = hash(user_message[:100])
if cache_key in decomposition_cache:
    return decomposition_cache[cache_key]
```

**2. 并行执行优化**
```python
# 使用 asyncio.gather 真正并行
results = await asyncio.gather(*[
    execute_subtask(task) 
    for task in independent_tasks
])
```

**3. 智能降级策略**
```python
# AI分解失败时切换到规则引擎
try:
    plan = await ai_decompose(message)
except Exception:
    plan = heuristic_decompose(message)  # 基于关键词的规则
```

**4. 成本控制**
```python
# 实时监控成本，超限时提前终止
if accumulated_cost > MAX_COST:
    logger.warning("成本超限，提前终止协作")
    return partial_aggregation(results)
```

---

## 📈 监控与调试

### 关键指标

建议在日志中记录以下指标：

```python
logger.info(f"""
🤝 协作模式执行报告
━━━━━━━━━━━━━━━━━━━━━━━
• 原始任务长度: {len(user_message)} 字符
• 子任务数量: {len(subtasks)}
• 使用模型: {', '.join(models_used)}
• 总耗时: {total_time_ms:.0f}ms
• 总成本: ${total_cost:.4f}
• 平均置信度: {avg_confidence:.2f}
• 聚合策略: {aggregation_strategy}
""")
```

### 调试技巧

**1. 查看详细分解过程**
```python
# 启用调试模式
import logging
logging.getLogger('ai_router').setLevel(logging.DEBUG)

# 输出示例:
# DEBUG:ai_router:任务分解开始: "分析AI趋势..."
# DEBUG:ai_router:识别到 3 个子任务: [retrieval, analysis, synthesis]
# DEBUG:ai_router:子任务0分配给 deepseek/deepseek-chat
# DEBUG:ai_router:子任务1分配给 openai/gpt-4o
# ...
```

**2. 模拟测试**
```python
# 单元测试示例
async def test_collaborative_chat():
    result = await ai_router.collaborative_chat(
        messages=[{"role": "user", "content": "测试任务"}],
        enable_collaboration=True
    )
    
    assert result["collaboration_used"] == True
    assert len(result["subtask_results"]) >= 1
    assert result["total_cost"] > 0
    print("✅ 协作模式测试通过")
```

**3. 性能分析**
```python
import time

start = time.time()
result = await ai_router.collaborative_chat(...)
elapsed = time.time() - start

print(f"⏱️  总耗时: {elapsed:.2f}s")
print(f"📊 Token消耗: {result['usage']['total_tokens']}")
print(f"💰 成本: ${result['total_cost']:.4f}")
```

---

## 🔍 常见问题

### Q1: 协作模式会比单模型慢多少？

**A**: 取决于任务复杂度：
- 简单任务（1-2个子任务）: 增加 30-50% 延迟
- 中等任务（3-4个子任务）: 增加 80-120% 延迟
- 复杂任务（5+子任务）: 增加 150-200% 延迟

但由于并行执行，实际延迟远低于串行累加。

### Q2: 成本会增加多少？

**A**: 通常增加 2-5 倍成本，因为：
- 多个模型同时调用
- 任务分解本身也消耗token
- 结果聚合需要额外计算

**优化建议**: 设置 `MAX_COLLABORATION_COST` 限制预算。

### Q3: 如何确保子任务结果的准确性？

**A**: 系统采用多重保障：
1. **置信度评分**: 每个子任务都有置信度（0-1）
2. **交叉验证**: 关键结论会被多个模型验证
3. **聚合过滤**: 低置信度结果会被标记或降权
4. **人工审核**: 可设置阈值，低于阈值的任务转人工

### Q4: 可以自定义子任务类型吗？

**A**: 可以！在 `SubTaskType` 枚举中添加新类型：

```python
class SubTaskType(str, Enum):
    # ... 现有类型 ...
    CUSTOM_ANALYSIS = "custom_analysis"  # 新增
```

然后在 `_decompose_task()` 中添加对应的提示词和处理逻辑。

### Q5: 协作模式失败怎么办？

**A**: 系统有多层降级策略：
1. **AI分解失败** → 切换到启发式规则分解
2. **单个模型失败** → 故障转移到备用模型
3. **聚合失败** → 使用简单拼接策略
4. **全部失败** → 降级为标准单模型对话

用户始终能获得回答，只是质量可能降低。

---

## 🚀 进阶用法

### 1. 自定义聚合策略

```python
# 实现自己的聚合逻辑
async def custom_aggregate(plan, results):
    # 例如：只保留高置信度的结果
    high_conf_results = [r for r in results if r.confidence > 0.8]
    
    # 或者：对冲突结果进行投票
    if has_conflict(results):
        return voting_aggregation(results)
    
    return standard_aggregation(results)
```

### 2. 动态调整模型选择

```python
# 根据历史表现动态调整
def select_model_with_history(task_type):
    candidates = get_available_models(task_type)
    
    # 优先选择历史成功率高的模型
    candidates.sort(key=lambda m: m.historical_success_rate, reverse=True)
    
    return candidates[0]
```

### 3. 增量式协作

```python
# 先快速得到一个初步答案，再逐步细化
async def incremental_collaboration(message):
    # 第1轮：快速概览
    overview = await single_model_chat(message, fast_model=True)
    
    # 第2轮：针对关键点深入
    key_points = extract_key_points(overview)
    detailed_results = await parallel_deep_dive(key_points)
    
    # 第3轮：整合
    final = await aggregate([overview] + detailed_results)
    
    return final
```

### 4. 用户反馈循环

```python
# 收集用户对协作结果的反馈
async def collect_feedback(result_id, user_rating):
    # 更新模型的权重
    for subtask in get_subtasks(result_id):
        model = subtask.model
        update_model_weight(model, user_rating)
    
    # 优化未来的任务分解策略
    if user_rating < 3:
        flag_for_review(result_id)
```

---

## 📚 相关文档

- [AI路由器核心实现](../backend/app/services/ai_router.py)
- [MCP工具定义](../backend/app/mcp/tools.py)
- [MCP服务器实现](../backend/app/mcp/server.py)
- [模型配置指南](./MODEL_CONFIGURATION.md)
- [性能优化最佳实践](./PERFORMANCE_OPTIMIZATION.md)

---

## 🎉 总结

模型协作与聚合功能将陈筱雪 AI 助手从"单一模型对话"升级为"多专家协同系统"，显著提升了复杂问题的解决能力。

**核心优势**:
- ✅ 专业化分工，各司其职
- ✅ 成本可控，灵活配置
- ✅ 容错性强，稳定可靠
- ✅ 透明度高，易于调试
- ✅ 可扩展性好，持续进化

**下一步计划**:
- [ ] 支持用户自定义子任务模板
- [ ] 实现真正的分布式并行执行
- [ ] 添加可视化任务分解图
- [ ] 集成更多专业模型（数学、法律、医疗等）
- [ ] 实现自适应学习，自动优化分解策略

---

*最后更新: 2026-05-06*  
*版本: v1.0.0*  
*作者: 陈筱雪 AI 助手开发团队*